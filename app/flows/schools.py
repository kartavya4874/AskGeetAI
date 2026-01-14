from ..data_loader import get_schools
from ..session import update_session_state
from . import courses  # Will be implemented next

def get_main_menu(name, session_id=""):
    schools_list = get_schools()
    buttons = [{"text": s["name"], "value": f"school_{s['id']}"} for s in schools_list]
    buttons.append({"text": "Back to Main Menu", "value": "main_menu"})
    
    return {
        "session_id": session_id,
        "messages": ["Here are the various Schools at Geeta University.", "Please select one to view its courses."],
        "buttons": buttons,
        "input_type": "button"
    }

def handle_flow(session, user_choice):
    session_id = session.get("id", "")
    # User selected a school (e.g. "school_cse")
    if user_choice.startswith("school_"):
        school_id = user_choice.replace("school_", "")
        
        # Save selected school to context
        update_session_state(session_id, "course_selection", {"selected_school": school_id})
        
        # Delegate to courses module to list courses
        response = courses.get_courses_menu(session["name"], school_id, session_id)
        return response
        
    return {
        "session_id": session_id,
        "messages": ["Invalid selection."],
        "buttons": [{"text": "Back", "value": "flow_schools"}],
        "input_type": "button"
    }
