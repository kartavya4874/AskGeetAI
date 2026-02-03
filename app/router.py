from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict
from .session import create_session, get_session, update_session_state, delete_session
from .database import create_db_and_tables, save_user
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv
import os
from pathlib import Path

# Robust .env loading
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID")

print(f"DEBUG: Looking for .env at: {env_path}")
print(f"DEBUG: .env exists: {env_path.exists()}")
print(f"DEBUG: TWILIO_ACCOUNT_SID: {'Set' if TWILIO_ACCOUNT_SID else 'Not Set'}")
print(f"DEBUG: TWILIO_AUTH_TOKEN: {'Set' if TWILIO_AUTH_TOKEN else 'Not Set'}")
print(f"DEBUG: TWILIO_VERIFY_SERVICE_SID: {'Set' if TWILIO_VERIFY_SERVICE_SID else 'Not Set'}")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID else None

# Initialize DB on startup
create_db_and_tables()

router = APIRouter()

class UserInput(BaseModel):
    name: Optional[str] = None
    session_id: Optional[str] = None
    message: Optional[str] = None # For button value or text
    payload: Optional[str] = None # specific action payload if needed

class BotResponse(BaseModel):
    session_id: str
    messages: List[str] # List of text bubbles
    buttons: List[Dict[str, str]] # List of {text: "Label", value: "payload"}
    input_type: str = "button" # 'text', 'button', 'tel'
    placeholder: Optional[str] = None

@router.post("/api/start", response_model=BotResponse)
async def start_chat(user_input: UserInput):
    """
    Initializes chat. Expects user name in 'name' field if it's the very first step,
    or just starts the handshake.
    Actually, per requirements: Start -> Ask User Name.
    So this endpoint might just return the "Hi, what is your name?" prompt.
    """
    # Create a temporary session or just return the prompt
    # But we need a session to store the name later.
    # Let's say the client calls this to get the greeting.
    
    # We can just return the "Welcome" state without a session yet, 
    # and create session when they send the name.
    # OR create a pre-session.
    
    # Simplest: Return instructions to UI to show Name Input.
    return BotResponse(
        session_id="", 
        messages=["Hello! Welcome to ASKGEETAI. \nI am your virtual guide for Geeta University.", "May I know your name so I can address you properly?"],
        buttons=[],
        input_type="text"
    )

@router.post("/api/restart", response_model=BotResponse)
async def restart_chat(user_input: UserInput):
    """
    Clears the current session and starts fresh.
    """
    session_id = user_input.session_id
    if session_id:
        delete_session(session_id)
    
    # Return the welcome message to restart
    return BotResponse(
        session_id="", 
        messages=["Hello! Welcome to ASKGEETAI. \nI am your virtual guide for Geeta University.", "May I know your name so I can address you properly?"],
        buttons=[],
        input_type="text"
    )

@router.post("/api/message", response_model=BotResponse)
async def chat_message(user_input: UserInput):
    session_id = user_input.session_id
    text = user_input.message
    
    # Check if this is the Name submission
    if not session_id and text:
        # Create session now
        session_id = create_session(text)
        session = get_session(session_id)
        
        # Instead of going to main menu, ask for mobile number
        update_session_state(session_id, "AWAITING_MOBILE")
        return BotResponse(
            session_id=session_id,
            messages=[f"Nice to meet you, {text}!", "Please enter your mobile number (with country code, e.g., +91...) for verification."],
            buttons=[],
            input_type="tel",
            placeholder="+91..."
        )

    session = get_session(session_id)
    if not session:
        return BotResponse(session_id="", messages=["Session expired. Please restart."], buttons=[{"text": "Restart", "value": "restart"}], input_type="button")

    # Handle Verification Flow
    state = session.get("state")
    
    if state == "AWAITING_MOBILE":
        # Sanitize and format mobile number
        mobile = text.strip().replace(" ", "")
        
        # If it's a 10-digit number, assume +91 (India) as default
        if len(mobile) == 10 and mobile.isdigit():
            mobile = f"+91{mobile}"
        elif not mobile.startswith("+"):
            return BotResponse(
                session_id=session_id,
                messages=["Please include your country code (e.g., +91 for India).", "Example: +91 9876543210"],
                buttons=[],
                input_type="tel",
                placeholder="+91..."
            )

        if client and TWILIO_VERIFY_SERVICE_SID:
            try:
                verification = client.verify.v2.services(TWILIO_VERIFY_SERVICE_SID) \
                    .verifications \
                    .create(to=mobile, channel='sms')
                
                update_session_state(session_id, "AWAITING_OTP", {"mobile": mobile})
                return BotResponse(
                    session_id=session_id,
                    messages=[f"I've sent a verification code to {mobile}.", "Please enter the 6-digit code below."],
                    buttons=[],
                    input_type="text",
                    placeholder="Enter OTP"
                )
            except TwilioRestException as e:
                 # Map specific Twilio errors to user-friendly messages
                 error_msg = "Something went wrong while sending the code. Please double-check your number."
                 if e.code == 60200:
                     error_msg = f"The number '{mobile}' is invalid. Please enter a valid mobile number with country code."
                 elif e.code == 60203:
                     error_msg = "This number is not supported for SMS verification."
                 
                 return BotResponse(
                    session_id=session_id,
                    messages=[error_msg, "Please try entering your mobile number again."],
                    buttons=[],
                    input_type="tel",
                    placeholder="+91..."
                )
            except Exception as e:
                 return BotResponse(
                    session_id=session_id,
                    messages=["An unexpected error occurred. Please try again later.", "Please enter your mobile number again."],
                    buttons=[],
                    input_type="tel",
                    placeholder="+91..."
                )
        else:
            # Bypass for local dev if no Twilio creds
            update_session_state(session_id, "AWAITING_OTP", {"mobile": mobile})
            return BotResponse(
                session_id=session_id,
                messages=["[DEV MODE] Twilio not configured.", "Enter any 6 digits to proceed."],
                buttons=[],
                input_type="text",
                placeholder="123456"
            )

    if state == "AWAITING_OTP":
        mobile = session.get("context", {}).get("mobile")
        otp = text
        
        verified = False
        if client and TWILIO_VERIFY_SERVICE_SID and not (otp == "123456" and not TWILIO_AUTH_TOKEN):
            try:
                verification_check = client.verify.v2.services(TWILIO_VERIFY_SERVICE_SID) \
                    .verification_checks \
                    .create(to=mobile, code=otp)
                if verification_check.status == "approved":
                    verified = True
            except Exception as e:
                return BotResponse(
                    session_id=session_id,
                    messages=[f"Error verifying OTP: {str(e)}", "Please try again."],
                    buttons=[],
                    input_type="text"
                )
        else:
            # Mock verification
            if otp == "123456": verified = True

        if verified:
            # Save to DB
            save_user(session.get("name"), mobile)
            
            # Move to Main Menu
            update_session_state(session_id, "main_menu")
            return BotResponse(
                session_id=session_id,
                messages=["Verification successful!", "How can I help you today?"],
                buttons=[
                    {"text": "Explore Schools & Courses", "value": "flow_schools"},
                    {"text": "Scholarships & Financial Aid", "value": "flow_scholarships"},
                    {"text": "Campus & Facilities", "value": "flow_campus"},
                    {"text": "Co-curricular & Student Activities", "value": "flow_cocurricular"},
                    {"text": "Placements Overview", "value": "flow_placements"},
                    {"text": "Contact University", "value": "flow_contact"},
                    {"text": "Exit", "value": "exit"}
                ],
                input_type="button"
            )
        else:
            return BotResponse(
                session_id=session_id,
                messages=["Invalid verification code.", "Please try again."],
                buttons=[],
                input_type="text"
            )

    # Dispatch logic based on payload/message
    # We will implement a dispatcher here.
    # For now, just echo logic until flows are ready.
    
    print(f"DEBUG: calling process_flow with text: {text}")
    response = await process_flow(session, text)
    print("DEBUG: process_flow returned successfully")
    return response

# Placeholder for the dispatcher
from .flows import manager

async def process_flow(session, user_choice):
    # This function will eventually call specific flow handlers
    response = manager.handle_request(session, user_choice)
    # Ensure session_id is in the response
    if 'session_id' not in response:
        response['session_id'] = session.get('id', '')
    return response
