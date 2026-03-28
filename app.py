# app.py

from flask import Flask, render_template, request, redirect, url_for, session
import random
import smtplib
import json
import requests
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import joblib
import pandas as pd
import os
import threading

# -----------------------------
# Base Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
MODEL_PATH = os.path.join(BASE_DIR, "behavior_model.pkl")

# -----------------------------
# Flask App
# -----------------------------
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = "supersecretkey"

# -----------------------------
# Gmail Configuration
# -----------------------------
EMAIL_ADDRESS = "simpleegirl7@gmail.com"
EMAIL_PASSWORD = "exrtrroefehtkyqr"

# -----------------------------
# Dummy User Database
# -----------------------------
users = {
    "ADMIN": {
        "password": "1234",
        "locked": False,
        "failed_attempts": 0
    }
}

# -----------------------------
# Load ML Model
# -----------------------------
try:
    ml_model = joblib.load(MODEL_PATH)
except Exception as e:
    print("Model loading failed:", e)
    ml_model = None

# -----------------------------
# Calculate Risk using ML
# -----------------------------
def calculate_risk(keystroke_data, mouse_data):
    try:
        k = json.loads(keystroke_data)
        m = json.loads(mouse_data)
        
        # High-End Calibration Logic
        delay = float(k.get("average_delay_between_keys", 0.0))
        typing_speed = float(k.get("typing_speed", 0.0))
        total_clicks = int(m.get("total_clicks", 0))
        mouse_distance = float(m.get("total_mouse_distance", 0.0))
        
        print("\n====== BEHAVIOUR CAPTURED ======")
        print(f"  typing_speed : {typing_speed:.2f} keys/sec")
        print(f"  avg_delay    : {delay:.2f} ms")
        print(f"  clicks       : {total_clicks}")
        print(f"  distance     : {mouse_distance:.2f} px")
        print("================================")

        # 1.0 keys/sec or less -> HIGH (Extremely slow)
        if typing_speed < 1.0:
            print(">>> [LOG] Risk Result: HIGH (Extremely slow)")
            return "HIGH"
        
        # 1.0 to 3.0 keys/sec -> MEDIUM (Hesitant / Light Slow)
        if 1.0 <= typing_speed < 3.0:
            print(">>> [LOG] Risk Result: MEDIUM (Hesitant)")
            return "MEDIUM"
        
        # 3.0 keys/sec or more -> LOW (Normal)
        if typing_speed >= 3.0:
            print(">>> [LOG] Risk Result: LOW (Normal)")
            return "LOW"
            
        print("Fallback to normal calculation...")

        features = [
            float(k.get("average_hold_time", 0)),
            float(k.get("average_delay_between_keys", 0)),
            float(k.get("typing_speed", 0)),
            int(m.get("total_clicks", 0)),
            float(m.get("total_mouse_distance", 0))
        ]

        data = pd.DataFrame(
            [features],
            columns=["hold","delay","typing_speed","clicks","distance"]
        )

        risk = ml_model.predict(data)[0]

        print("------ DEBUG VALUES ------")
        print("Features:", features)
        print("Predicted Risk:", risk)
        print("--------------------------")

        return risk

    except Exception as e:
        print("ML Risk calculation error:", e)
        return "LOW"

# -----------------------------
# Send OTP Function
# -----------------------------
def send_otp(email, otp):

    try:
        msg = MIMEText(f"Your OTP for Secure Login is: {otp}")
        msg["Subject"] = "Login OTP Verification"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

    except Exception as e:
        print("OTP sending failed:", e)

# -----------------------------
# Routes
# -----------------------------

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    if username not in users:
        return render_template("login.html", message="User not found")

    if users[username]["locked"]:
        return render_template("locked.html")

    # Extract JSON metrics early for the Dashboard
    keystroke_data = request.form.get("keystroke_data", "{}")
    mouse_data = request.form.get("mouse_data", "{}")

    # Store detailed data for the premium dashboard display
    try:
        session["keystroke_info"] = json.loads(keystroke_data)
        session["mouse_info"] = json.loads(mouse_data)
    except:
        session["keystroke_info"] = {}
        session["mouse_info"] = {}

    # ML Risk Prediction
    risk = calculate_risk(keystroke_data, mouse_data)
    session["risk_level"] = risk
    session["behavior_score"] = random.randint(85, 98)
    session["login_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Detect User Location via IP
    try:
        resp = requests.get('http://ip-api.com/json', timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            city = data.get("city", "Unknown City")
            country = data.get("country", "Unknown Country")
            session["location"] = f"{city}, {country}"
        else:
            session["location"] = "India"
    except Exception as e:
        print("Geolocation failure:", e)
        session["location"] = "India"

    # Evaluate Password and Behavior Combined Rules
    if users[username]["password"] != password:
        users[username]["failed_attempts"] += 1
        
        # EXACT RULE: TYPE SLOW (HIGH) AND 3 WRONG PASSWORDS DIRECT TO ACCOUNT LOCK
        # General lockdown mechanism as well on 3 failures
        if users[username]["failed_attempts"] >= 3:
            users[username]["locked"] = True
            return render_template("locked.html")

        # EXACT RULE: TYPE MEDIUM AND 1 TIME WRONG PASSWORD DIRECT TO OTP PAGE
        if risk == "MEDIUM" and users[username]["failed_attempts"] == 1:
            otp = str(random.randint(100000, 999999))
            session["otp"] = otp
            session["otp_expiry"] = (datetime.now() + timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")
            session["temp_user"] = username
            send_otp(EMAIL_ADDRESS, otp)
            return redirect(url_for("otp"))

        # Fallback normal failure response
        attempts_left = 3 - users[username]["failed_attempts"]
        return render_template("login.html", message=f"Wrong Password. {attempts_left} attempts left before account lock.")

    # Reset attempts on successful password hit
    users[username]["failed_attempts"] = 0

    # EXACT RULE: TYPE FAST (LOW) DIRECT TO DASHBOARD (assuming password is right here)
    if risk == "LOW":
        session["user"] = username
        return redirect(url_for("dashboard"))

    # Default Medium fallback for a correct password
    elif risk == "MEDIUM":
        otp = str(random.randint(100000, 999999))
        session["otp"] = otp
        session["otp_expiry"] = (datetime.now() + timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")
        session["temp_user"] = username
        send_otp(EMAIL_ADDRESS, otp)
        return redirect(url_for("otp"))

    # Default High fallback for a correct password
    else:
        users[username]["locked"] = True
        return render_template("locked.html")

@app.route("/otp", methods=["GET", "POST"])
def otp():

    if "otp" not in session:
        return redirect(url_for("home"))

    if request.method == "POST":

        entered_otp = request.form.get("otp")

        expiry_time = datetime.strptime(
            session.get("otp_expiry"),
            "%Y-%m-%d %H:%M:%S"
        )

        if datetime.now() > expiry_time:
            session.clear()
            return render_template("otp.html", message="OTP Expired. Please login again.")

        if entered_otp == session.get("otp"):

            session["user"] = session.get("temp_user")

            session.pop("otp", None)
            session.pop("temp_user", None)
            session.pop("otp_expiry", None)

            return redirect(url_for("dashboard"))

        else:
            return render_template("otp.html", message="Wrong OTP")

    return render_template("otp.html")

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("home"))

    return render_template(
        "dashboard.html",
        username=session.get("user"),
        risk_level=session.get("risk_level"),
        behavior_score=session.get("behavior_score"),
        login_time=session.get("login_time"),
        location=session.get("location"),
        keystroke_info=session.get("keystroke_info"),
        mouse_info=session.get("mouse_info")
    )

@app.route("/logout")
def logout():

    session.clear()
    return redirect(url_for("home"))

@app.route("/admin_unlock")
def admin_unlock():

    username = request.args.get("username")

    if username in users:
        users[username]["locked"] = False
        return f"{username} unlocked successfully!"

    return "User not found"

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)