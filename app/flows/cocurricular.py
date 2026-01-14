from ..data_loader import get_cocurricular

def get_activities_info(name, session_id=""):
    # List events
    events = get_cocurricular()
    
    buttons = []
    for event in events:
        buttons.append({"text": event["name"], "value": f"event_{event['name']}"})
        
    buttons.append({"text": "Back to Main Menu", "value": "main_menu"})
    
    return {
        "session_id": session_id,
        "messages": ["Experence life beyond academics at Geeta University.", "Select an event to know more:"],
        "buttons": buttons,
        "input_type": "button"
    }

def handle_flow(session, user_choice):
    session_id = session.get("id", "")
    if user_choice.startswith("event_"):
        event_name = user_choice.replace("event_", "")
        events = get_cocurricular()
        
        selected = next((e for e in events if e["name"] == event_name), None)
        
        if selected:
            return {
                "session_id": session_id,
                "messages": [
                    f"**{selected['name']}** ({selected['type']})",
                    selected["description"]
                ],
                "buttons": [
                    {"text": "View Other Events", "value": "flow_cocurricular"},
                    {"text": "Main Menu", "value": "main_menu"}
                ],
                "input_type": "button"
            }
            
    return {
        "session_id": session_id,
        "messages": ["Invalid selection."],
        "buttons": [{"text": "Back", "value": "flow_cocurricular"}],
        "input_type": "button"
    }
