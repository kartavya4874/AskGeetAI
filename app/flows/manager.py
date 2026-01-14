from . import schools, courses, scholarships, campus, cocurricular, placements
from ..session import update_session_state

def handle_request(session, user_choice):
    """
    Dispatches the user choice to the appropriate flow handler based on current state or global menu options.
    """
    print(f"DEBUG: Handling request for user_choice: {user_choice}, session_id: {session['id']}")
    state = session["state"]
    name = session["name"]
    
    try:
        # Global Back/Exit handlers (if applicable, though usually handled per flow if state context matters)
        if user_choice == "exit":
            return {
                "session_id": "", # Clear session on client
                "messages": [f"Goodbye, {name}! It was a pleasure assisting you.", "Feel free to return anytime."],
                "buttons": [{"text": "Start Over", "value": "restart"}],
                "input_type": "button"
            }
        
        if user_choice == "restart":
             # This should strictly be handled by client re-hitting /api/start usually, but here for safety
             return {
                "session_id": "",
                "messages": ["Restarting..."],
                "buttons": [],
                "input_type": "text" # Force restart
             }
    
        session_id = session.get("id")
        if not session_id:
            print("ERROR: Session ID missing in manager handle_request")
            return {
                "session_id": "",
                "messages": ["Session error. Please restart."],
                "buttons": [{"text": "Restart", "value": "restart"}],
                "input_type": "button"
            }

        # Main Menu Routing
        if user_choice == "flow_schools":
            update_session_state(session_id, "schools_menu")
            response = schools.get_main_menu(name, session_id)
            add_exit_button(response)
            return response
        
        if user_choice == "flow_scholarships":
            update_session_state(session_id, "scholarships_view")
            response = scholarships.get_scholarships_info(name, session_id)
            add_exit_button(response)
            return response
    
        if user_choice == "flow_campus":
            update_session_state(session_id, "campus_menu")
            response = campus.get_main_menu(name, session_id)
            add_exit_button(response)
            return response
            
        if user_choice == "flow_cocurricular":
            update_session_state(session_id, "cocurricular_view")
            response = cocurricular.get_activities_info(name, session_id)
            add_exit_button(response)
            return response
            
        if user_choice == "flow_placements":
            update_session_state(session_id, "placements_view")
            response = placements.get_placements_info(name, session_id)
            add_exit_button(response)
            return response
            
        if user_choice == "flow_contact":
            response = {
                "session_id": session_id,
                "messages": [
                     "Here is the official contact information for Geeta University:",
                     "Phone: +91-99960-51000",
                     "Email: info@geetauniversity.edu.in",
                     "Address: NH-71, Naultha, Panipat, Haryana"
                ],
                "buttons": [{"text": "Back to Main Menu", "value": "main_menu"}],
                "input_type": "button"
            }
            add_exit_button(response)
            return response
    
        if user_choice == "main_menu":
            update_session_state(session_id, "main_menu")
            return {
                "session_id": session_id,
                "messages": ["Welcome back to the Main Menu. What would you like to explore?"],
                "buttons": [
                    {"text": "Explore Schools & Courses", "value": "flow_schools"},
                    {"text": "Scholarships & Financial Aid", "value": "flow_scholarships"},
                    {"text": "Campus & Facilities", "value": "flow_campus"},
                    {"text": "Co-curricular & Student Activities", "value": "flow_cocurricular"},
                    {"text": "Placements Overview", "value": "flow_placements"},
                    {"text": "Contact University", "value": "flow_contact"},
                    {"text": "Exit", "value": "exit"}
                ],
                "input_type": "button"
            }
    
        # Handle back to school navigation
        if user_choice.startswith("school_"):
            school_id = user_choice.replace("school_", "")
            update_session_state(session_id, "course_selection", {"selected_school": school_id})
            response = courses.get_courses_menu("", school_id, session_id)
            add_exit_button(response)
            return response
    
        # Dispatch to specific module handlers based on current state
        if state.startswith("schools_"):
            response = schools.handle_flow(session, user_choice)
            add_exit_button(response)
            return response
    
        if state.startswith("course_selection"):
            # User is selecting a course from the list
            response = courses.handle_flow(session, user_choice)
            add_exit_button(response)
            return response
            
        if state.startswith("course_detail_"):
            # User is viewing details of a course (Curriculum, etc.)
            response = courses.handle_detail_view(session, user_choice)
            add_exit_button(response)
            return response
        
        if state.startswith("scholarships_"):
            response = scholarships.handle_flow(session, user_choice)
            add_exit_button(response)
            return response
            
        if state.startswith("campus_"):
            response = campus.handle_flow(session, user_choice)
            add_exit_button(response)
            return response
             
        if state.startswith("cocurricular_"):
            response = cocurricular.handle_flow(session, user_choice)
            add_exit_button(response)
            return response
             
        if state.startswith("placements_"):
            response = placements.handle_flow(session, user_choice)
            add_exit_button(response)
            return response
    
        # Fallback
        response = {
            "session_id": session_id,
            "messages": ["I'm sorry, I didn't catch that.", "Please select an option from the menu."],
            "buttons": [{"text": "Back to Main Menu", "value": "main_menu"}],
            "input_type": "button"
        }
        add_exit_button(response)
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        session_id = session.get("id", "") if session else ""
        response = {
            "session_id": session_id,
            "messages": [f"Error: {str(e)}", "Please check server logs."],
            "buttons": [{"text": "Main Menu", "value": "main_menu"}, {"text": "Exit", "value": "exit"}],
            "input_type": "button"
        }
        return response

def add_exit_button(response):
    """Adds Exit button to the response if not already present (except on main menu)."""
    if response.get("buttons") and not any(btn.get("value") == "exit" for btn in response["buttons"]):
        response["buttons"].append({"text": "Exit", "value": "exit"})

def get_session_id(session):
    return session.get("id", "")
