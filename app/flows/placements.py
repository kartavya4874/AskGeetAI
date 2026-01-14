from ..data_loader import get_placements

def get_placements_info(name, session_id=""):
    data = get_placements()
    stats = data["statistics"]
    
    return {
        "session_id": session_id,
        "messages": [
            "**Placement Overview**",
            data["overview"],
            f"**Highest Package**: {stats['highest_package']}",
            f"**Average Package**: {stats['average_package']}",
            f"**Companies Visited**: {stats['companies_visited']}"
        ],
        "buttons": [
            {"text": "Top Recruiters", "value": "placements_recruiters"},
            {"text": "Training Activities", "value": "placements_activities"},
            {"text": "Back to Main Menu", "value": "main_menu"}
        ],
        "input_type": "button"
    }

def handle_flow(session, user_choice):
    session_id = session.get("id", "")
    data = get_placements()
    
    if user_choice == "placements_recruiters":
        recruiters = ", ".join(data["top_recruiters"])
        return {
            "session_id": session_id,
            "messages": ["**Top Recruiters**", recruiters],
            "buttons": [
                {"text": "Training Activities", "value": "placements_activities"},
                {"text": "Back", "value": "flow_placements"}
            ],
            "input_type": "button"
        }
        
    if user_choice == "placements_activities":
        activities = "\n- ".join(dt for dt in data["activities"])
        return {
            "session_id": session_id,
            "messages": ["**Placement Support Activities**", f"- {activities}"],
            "buttons": [
                {"text": "Top Recruiters", "value": "placements_recruiters"},
                {"text": "Back", "value": "flow_placements"}
            ],
            "input_type": "button"
        }
        
    return {
        "session_id": session_id,
        "messages": ["Invalid selection."],
        "buttons": [{"text": "Back", "value": "flow_placements"}],
        "input_type": "button"
    }
