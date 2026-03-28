import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_login(username, password, typing_speed, hold_time=100, delay_time=150, description=""):
    print(f"\n>>> TEST: {description} (Typing Speed: {typing_speed} keys/sec)")
    
    keystroke_data = {
        "average_hold_time": str(hold_time),
        "average_delay_between_keys": str(delay_time),
        "typing_speed": str(typing_speed)
    }
    
    mouse_data = {
        "total_clicks": "3",
        "total_mouse_distance": "500.00"
    }
    
    payload = {
        "username": username,
        "password": password,
        "keystroke_data": json.dumps(keystroke_data),
        "mouse_data": json.dumps(mouse_data)
    }
    
    with requests.Session() as s:
        response = s.post(f"{BASE_URL}/login", data=payload, allow_redirects=False)
        
        if response.status_code == 302:
            location = response.headers.get("Location")
            print(f"Redirected to: {location}")
            if "dashboard" in location and description == "Normal Type":
                 print("RESULT: [LOW RISK] -> Dashboard Access Granted [PASS]")
            elif "otp" in location and description == "Light Slow":
                 print("RESULT: [MEDIUM RISK] -> OTP Verification Required [PASS]")
            else:
                 print(f"RESULT: [FAIL] -> Unexpected Redirect to {location} for {description}")
        elif response.status_code == 200:
            if ("Locked" in response.text or "locked" in response.text) and description == "Very Slow":
                print("RESULT: [HIGH RISK] -> Account Locked [PASS]")
            else:
                print(f"RESULT: [FAIL] -> Stayed on page or Locked unexpectedly for {description}")
        else:
            print(f"RESULT: [FAIL] -> Status {response.status_code}")

def test_wrong_passwords():
    print("\n>>> TEST: 3 Continuous Wrong Passwords")
    username = "ADMIN"
    password = "WRONG_PASSWORD"
    
    keystroke_data = {"typing_speed": "5.0", "average_hold_time": "100", "average_delay_between_keys": "150"}
    mouse_data = {"total_clicks": "3", "total_mouse_distance": "500.00"}
    payload = {
        "username": username,
        "password": password,
        "keystroke_data": json.dumps(keystroke_data),
        "mouse_data": json.dumps(mouse_data)
    }
    
    with requests.Session() as s:
        for i in range(1, 4):
            print(f"Attempt {i} with wrong password...")
            response = s.post(f"{BASE_URL}/login", data=payload, allow_redirects=False)
            if response.status_code == 200 and "Invalid password" in response.text:
                print(f"  Attempt {i}: Refreshed Login Page with Error (Correct) [PASS]")
            elif response.status_code == 200 and ("Locked" in response.text or "locked" in response.text):
                print(f"  Attempt {i}: ACCOUNT LOCKED (Correct for Attempt 3) [PASS]")
                break
            else:
                print(f"  Attempt {i}: Unexpected response (Status {response.status_code})")

if __name__ == "__main__":
    try:
        # Reset server state by visiting admin_unlock (if possible) or just assume fresh start
        # requests.get(f"{BASE_URL}/admin_unlock?username=ADMIN")
        
        # 1. Test NORMAL -> Dashboard (LOW >= 3.0)
        requests.get(f"{BASE_URL}/admin_unlock?username=ADMIN")
        test_login("ADMIN", "1234", typing_speed=3.5, description="Normal Type")
        
        # 2. Test LIGHT SLOW -> OTP (1.0 <= MEDIUM < 3.0)
        requests.get(f"{BASE_URL}/admin_unlock?username=ADMIN")
        test_login("ADMIN", "1234", typing_speed=2.0, description="Light Slow")
        
        # 3. Test VERY SLOW -> Locked (HIGH < 1.0)
        requests.get(f"{BASE_URL}/admin_unlock?username=ADMIN")
        test_login("ADMIN", "1234", typing_speed=0.5, description="Very Slow")
        
        # 4. Test 3 Wrong Passwords -> Locked
        # First unlock the user in case they were locked by step 3
        requests.get(f"{BASE_URL}/admin_unlock?username=ADMIN")
        test_wrong_passwords()
        
    except Exception as e:
        print(f"Error: {e}. Is the Flask app running?")
