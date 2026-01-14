from ..data_loader import get_scholarships

def get_scholarships_info(name, session_id=""):
    # Retrieve the list of scholarships
    scholarships = get_scholarships()
    
    # We can display them as a carousel in messages or just a list.
    # Given button-based UI, we can list them as buttons to "Read More" about each,
    # or just show a summary message.
    # Requirement: "Informational only. No fee amounts."
    
    messages = [f"Geeta University offers {len(scholarships)} types of scholarships."]
    buttons = []
    
    for s in scholarships:
        buttons.append({"text": s["title"], "value": f"scholarship_{s['title']}"})
        
    buttons.append({"text": "Back to Main Menu", "value": "main_menu"})
    
    return {
        "session_id": session_id,
        "messages": messages,
        "buttons": buttons,
        "input_type": "button"
    }

def handle_flow(session, user_choice):
    session_id = session.get("id", "")
    if user_choice.startswith("scholarship_"):
        title = user_choice.replace("scholarship_", "")
        all_scholarships = get_scholarships()
        
        selected = next((s for s in all_scholarships if s["title"] == title), None)
        
        if selected:
            return {
                "session_id": session_id,
                "messages": [f"**{selected['title']}**", selected["description"]],
                "buttons": [
                    {"text": "View Other Scholarships", "value": "flow_scholarships"},
                    {"text": "Main Menu", "value": "main_menu"}
                ],
                "input_type": "button"
            }
            
    return {
        "session_id": session_id,
        "messages": ["Invalid selection."],
        "buttons": [{"text": "Back", "value": "flow_scholarships"}],
        "input_type": "button"
    }
