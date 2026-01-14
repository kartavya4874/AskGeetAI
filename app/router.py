from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict
from .session import create_session, get_session, update_session_state, delete_session
# We will import flow handlers dynamically or staticly here
# For now, we will just setup the structure

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
    input_type: str = "button" # 'text' (only for start) or 'button'

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
        messages=["Hello! Welcome to ASK GEETA AI. \nI am your virtual guide for Geeta University.", "May I know your name so I can address you properly?"],
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
        # Verify creation
        if not session:
             raise HTTPException(status_code=500, detail="Session failed")
             
        # Welcome user and show Main Menu
        return BotResponse(
            session_id=session_id,
            messages=[f"Nice to meet you, {text}!", "How can I help you today?"],
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

    session = get_session(session_id)
    print(f"DEBUG: router.chat_message - Session ID: {session_id}, Session Found: {session is not None}")
    
    if not session:
        return BotResponse(session_id="", messages=["Session expired. Please restart."], buttons=[{"text": "Restart", "value": "restart"}], input_type="button")

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
