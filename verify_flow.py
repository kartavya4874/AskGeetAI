import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_flow():
    # 1. Start Chat
    print("1. Testing /api/start...")
    try:
        resp = requests.post(f"{BASE_URL}/api/start", json={})
        data = resp.json()
        print(f"   Response: {data['messages']}")
        if data['input_type'] != 'text': 
            print("   FAIL: Expected text input for name.")
            return
            
    except Exception as e:
        print(f"   FATAL: Could not connect to server. Ensure it is running. Error: {e}")
        return

    # 2. Send Name
    print("\n2. Sending Name 'Rohan'...")
    resp = requests.post(f"{BASE_URL}/api/message", json={"session_id": "", "message": "Rohan"})
    data = resp.json()
    session_id = data['session_id']
    print(f"   Session ID: {session_id}")
    print(f"   Response: {data['messages'][0]}")
    
    if not session_id:
        print("   FAIL: No session ID returned.")
        return

    # 3. Select 'Explore Schools'
    print("\n3. Selecting 'Explore Schools & Courses'...")
    resp = requests.post(f"{BASE_URL}/api/message", json={"session_id": session_id, "message": "flow_schools"})
    data = resp.json()
    buttons = [b['text'] for b in data['buttons']]
    print(f"   Schools found: {buttons[:3]}...")
    
    if "School of Computer Science & Engineering" not in buttons:
        print("   FAIL: CSE School not found.")
        return
        
    cse_val = next(b['value'] for b in data['buttons'] if "Computer Science" in b['text'])

    # 4. Select CSE
    print(f"\n4. Selecting CSE School ({cse_val})...")
    resp = requests.post(f"{BASE_URL}/api/message", json={"session_id": session_id, "message": cse_val})
    data = resp.json()
    buttons = [b['text'] for b in data['buttons']]
    print(f"   Courses found: {buttons}")
    
    if "B.Tech. Hons. CSE" not in buttons:
        print("   FAIL: B.Tech CSE not found.")
        return

    btech_val = next(b['value'] for b in data['buttons'] if "B.Tech" in b['text'])

    # 5. Select B.Tech CSE
    print(f"\n5. Selecting B.Tech CSE ({btech_val})...")
    resp = requests.post(f"{BASE_URL}/api/message", json={"session_id": session_id, "message": btech_val})
    data = resp.json()
    messages = data['messages']
    print(f"   Course Info: {messages[1][:50]}...") # Print first 50 chars of description
    
    # 6. Select Curriculum
    print("\n6. Selecting Curriculum...")
    resp = requests.post(f"{BASE_URL}/api/message", json={"session_id": session_id, "message": "detail_curriculum"})
    data = resp.json()
    print(f"   Curriculum Info: {data['messages']}")
    
    if "Computer Science Fundamentals" not in str(data['messages']):
         print("   FAIL: Curriculum details missing.")
         return

    print("\n✅ VERIFICATION SUCCESSFUL: Critical flow (Start -> Name -> School -> Course -> Details) works.")

if __name__ == "__main__":
    test_flow()
