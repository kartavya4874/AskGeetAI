from ..data_loader import get_campus
from ..session import update_session_state

def get_main_menu(name, session_id=""):
    return {
        "session_id": session_id,
        "messages": ["Explore our World Class Infrastructure and Facilities."],
        "buttons": [
            {"text": "Academic Infrastructure", "value": "campus_infrastructure"},
            {"text": "Student Facilities", "value": "campus_facilities"},
            {"text": "Back to Main Menu", "value": "main_menu"}
        ],
        "input_type": "button"
    }

def handle_flow(session, user_choice):
    session_id = session.get("id", "")
    data = get_campus()
    
    if user_choice == "campus_infrastructure":
        items = data.get("infrastructure", [])
        messages = ["**Academic Infrastructure**"]
        for item in items:
            messages.append(f"**{item['title']}**: {item['description']}")
            
        return {
            "session_id": session_id,
            "messages": messages,
            "buttons": [
                {"text": "View Facilities", "value": "campus_facilities"},
                {"text": "Back to Campus Menu", "value": "flow_campus"},
                 {"text": "Main Menu", "value": "main_menu"}
            ],
            "input_type": "button"
        }
        
    if user_choice == "campus_facilities":
        items = data.get("facilities", [])
        messages = ["**Student Facilities**"]
        for item in items:
             messages.append(f"**{item['title']}**: {item['description']}")
             
        return {
            "session_id": session_id,
            "messages": messages,
            "buttons": [
                {"text": "View Infrastructure", "value": "campus_infrastructure"},
                {"text": "Back to Campus Menu", "value": "flow_campus"},
                {"text": "Main Menu", "value": "main_menu"}
            ],
            "input_type": "button"
        }
        
    return {
        "session_id": session_id,
        "messages": ["Invalid selection."],
        "buttons": [{"text": "Back", "value": "flow_campus"}],
        "input_type": "button"
    }
