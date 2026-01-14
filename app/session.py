import uuid
import time
from typing import Dict, Any

# In-memory session store
# Structure: { session_id: { "name": str, "state": str, "timestamp": float, ... } }
sessions: Dict[str, Dict[str, Any]] = {}

SESSION_TIMEOUT = 3600  # 1 hour expiry for cleanup (optional safety)

def create_session(name: str) -> str:
    """Creates a new session for a user and returns the session ID."""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "id": session_id,
        "name": name,
        "state": "main_menu", # Initial state after welcome
        "context": {}, # To store temporary selections (e.g. selected_school_id)
        "timestamp": time.time()
    }
    return session_id

def get_session(session_id: str):
    """Retrieves a session by ID."""
    if session_id in sessions:
        # Update timestamp on access
        sessions[session_id]["timestamp"] = time.time()
        return sessions[session_id]
    return None

def delete_session(session_id: str):
    """Deletes a session by ID."""
    if session_id in sessions:
        del sessions[session_id]
        print(f"DEBUG: Session {session_id} deleted")

def update_session_state(session_id: str, new_state: str, context_update: Dict = None):
    """Updates the state and context of a session."""
    if session_id in sessions:
        sessions[session_id]["state"] = new_state
        if context_update:
            sessions[session_id]["context"].update(context_update)

def cleanup_sessions():
    """Removes old sessions."""
    current_time = time.time()
    to_remove = [sid for sid, data in sessions.items() if current_time - data["timestamp"] > SESSION_TIMEOUT]
    for sid in to_remove:
        del sessions[sid]