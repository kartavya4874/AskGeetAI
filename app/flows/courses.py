from ..data_loader import get_courses
from ..session import update_session_state

def get_courses_menu(user_name, school_id, session_id=""):
    all_courses = get_courses()
    school_courses = all_courses.get(school_id, [])
    
    if not school_courses:
        return {
            "session_id": session_id,
            "messages": ["No courses found for this school yet."],
            "buttons": [{"text": "Back to Schools", "value": "flow_schools"}],
            "input_type": "button"
        }
        
    buttons = [{"text": c["name"], "value": f"course_{c['id']}"} for c in school_courses]
    buttons.append({"text": "Back to Schools", "value": "flow_schools"})
    
    return {
        "session_id": session_id,
        "messages": [f"Here are the courses offered."],
        "buttons": buttons,
        "input_type": "button"
    }

def handle_flow(session, user_choice):
    session_id = session.get("id", "")
    # User selected a course (e.g. "course_btech_cse")
    # This function is called by manager when state starts with "course_" 
    # BUT wait, manager logic: if state.startswith("schools_") or state.startswith("course_") -> schools.handle_flow
    # I need to adjust manager.py to route "course_" states to THIS module.
    # OR schools.py needs to delegate again.
    # Let's fix manager.py later. For now, assume this is called.
    
    course_id = user_choice.replace("course_", "")
    
    # Retrieve course details
    school_id = session["context"].get("selected_school")
    all_courses = get_courses()
    courses_list = all_courses.get(school_id, [])
    
    course = next((c for c in courses_list if c["id"] == course_id), None)
    
    if not course:
        return {
             "session_id": session_id,
             "messages": ["Course details not found."],
             "buttons": [{"text": "Back", "value": f"school_{school_id}"}],
             "input_type": "button"
        }
        
    # Check if it has detailed flow
    if course.get("has_details"):
        details = course["details"]
        # Show Course Menu
        update_session_state(session_id, f"course_detail_{course_id}", {"selected_course": course_id})
        
        return {
            "session_id": session_id,
            "messages": [f"**{course['name']}**", details["overview"], "What would you like to know?"],
            "buttons": [
                {"text": "Curriculum / Subjects", "value": "detail_curriculum"},
                {"text": "Career Prospects", "value": "detail_career"},
                {"text": "Eligibility", "value": "detail_eligibility"},
                {"text": "Scholarships", "value": "detail_scholarships"},
                {"text": "Fees", "value": "detail_fees"},
                {"text": "Back to Courses", "value": f"school_{school_id}"}
            ],
            "input_type": "button"
        }
    else:
        # Simple view for non-detailed courses
        return {
            "session_id": session_id,
            "messages": [f"**{course['name']}**", "Detailed information is currently being updated.", "Please contact the university for more details."],
            "buttons": [
                {"text": "Back to Courses", "value": f"school_{school_id}"},
                {"text": "Contact University", "value": "flow_contact"}
            ],
            "input_type": "button"
        }

def handle_detail_view(session, user_choice):
    session_id = session.get("id", "")
    course_id = session["context"].get("selected_course")
    school_id = session["context"].get("selected_school")
    
    all_courses = get_courses()
    courses_list = all_courses.get(school_id, [])
    course = next((c for c in courses_list if c["id"] == course_id), None)
    
    if not course or "details" not in course:
         return {
            "session_id": session_id,
            "messages": ["Error retrieving details."],
             "buttons": [{"text": "Back", "value": f"school_{school_id}"}],
             "input_type": "button"
         }
         
    details = course["details"]
    messages = []
    
    if user_choice == "detail_curriculum":
        messages.append("**Curriculum Highlights:**")
        messages.extend([f"- {item}" for item in details["curriculum"]])
        
    elif user_choice == "detail_career":
        messages.append("**Career Prospects:**")
        messages.extend([f"- {item}" for item in details["career_prospects"]])
        
    elif user_choice == "detail_eligibility":
        messages.append("**Eligibility Criteria:**")
        messages.append(details["eligibility"])
        
    elif user_choice == "detail_scholarships":
        messages.append("**Scholarships:**")
        messages.append(details["scholarships"])
        
    elif user_choice == "detail_fees":
        messages.append("**Program Fees:**")
        if "fees" in details:
            fees = details["fees"]
            messages.append(f"**Program Fee per Semester:** ₹{fees['prog_fee_per_sem']:,}")
            messages.append(f"**Tuition Fee:** ₹{fees['tuition_fee']:,}")
            if "level" in fees:
                messages.append(f"**Level:** {fees['level']}")
        else:
            messages.append("Fee information is not available for this program.")
        
    buttons = [
        {"text": "Back to Course Menu", "value": f"course_{course_id}"},
        {"text": "Main Menu", "value": "main_menu"}
    ]
    
    return {
        "session_id": session_id,
        "messages": messages,
        "buttons": buttons,
        "input_type": "button"
    }
