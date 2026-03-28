Behaviour Based Login System

An AI-powered smart login security system that goes **beyond passwords**! Even if someone **knows your password**, the system detects them as an intruder based on their **typing speed, mouse movements, and behavioral patterns** — and blocks them automatically!

 How It Works

User enters correct password
        ↓
System silently tracks behavior in real-time:
     Typing speed & rhythm
     Mouse movements & clicks
     Key hold time & delay
     Location
        ↓
ML Model analyzes the behavior pattern
        ↓
   NORMAL      →  Login to Dashboard
   SLIGHTLY    →  OTP Verification Required
   ABNORMAL
   HIGHLY      →  Account Locked!
   ABNORMAL


 3 Security Levels

Level 1 — Normal Behavior (Owner Detected)
- Typing pattern matches the owner
- Mouse movements are familiar
- Result: Direct access to Dashboard

Level 2 — Slightly Abnormal (Suspicious)
- Typing speed is a bit different
- Mouse behavior is slightly off
- Result: OTP sent for extra verification

Level 3 — Highly Abnormal (Intruder!)
- Typing pattern completely different
- Mouse movements don't match owner
- Result: Account is locked immediately!

 Dashboard Shows

After successful login, the dashboard displays:

| Info | Description |

| Key Delay | Time between each keystroke |
| Mouse Movements | Distance and speed of mouse |
| Mouse Clicks | Number and pattern of clicks |
| Hold Time | How long each key was held |
| Typing Speed | Words per minute analysis |
| Location | Current login location |
| Risk Level | LOW / MEDIUM / HIGH |

 Behavior Parameters Tracked

| Parameter | Range | Description |

| hold | 250ms - 800ms | How long a key is held |
| delay | 500ms - 4000ms | Time between keystrokes |
| typing_speed | 0.01 - 1.0 | Speed of typing |
| clicks | 1 - 15 | Number of mouse clicks |
| distance | 100 - 4000px | Mouse movement distance |
| risk | LOW / MEDIUM / HIGH | Final risk classification |

 Features

- Typing Speed Detection — Analyzes how fast/slow the user types
- Mouse Behavior Tracking — Tracks mouse movement and clicks in real-time
- Key Hold & Delay Analysis — Measures keystroke timing patterns
- ML Risk Classification — LOW / MEDIUM / HIGH risk detection
- 3-Level Security — Dashboard / OTP / Account Lock
- Location Tracking — Shows login location on dashboard
- Behavior Dashboard — Visual display of all behavioral data
- Auto Account Lock — Instantly locks if intruder detected

 Technologies Used

| Technology | Purpose |

| Python | Backend & ML logic |
| Flask | Web framework |
| Machine Learning | Behavior analysis model |
| HTML | Frontend structure |
| CSS | Styling |
| JavaScript | Real-time behavior tracking |
| SQLite3 | Database |

 Project Structure

Behaviour_based_login_system/
├── app.py                   # Main Flask application
├── train_model.py           # ML model training
├── prepare_dataset.py       # Dataset preparation
├── test_model.py            # Model testing
├── test_risk_levels.py      # Risk level testing
├── behavior_model.pkl       # Trained ML model
├── behavior_dataset.csv     # Training dataset
├── requirements.txt         # Dependencies
├── static/
│   └── js/
│       └── behavior.js      # Real-time behavior tracking
├── templates/
│   ├── login.html           # Login page
│   ├── dashboard.html       # Success dashboard
│   ├── locked.html          # Account locked page
│   └── otp.html             # OTP verification page
└── .gitignore

 How to Run

Prerequisites
- Python 3.x installed
- pip installed

Steps

bash
1. Clone the repository
git clone https://github.com/hemadharshiniR/Behaviour_based_login_system.git

2. Go into the project folder
cd Behaviour_based_login_system

3. Install dependencies
pip install -r requirements.txt

4. Train the model (if needed)
python train_model.py

5. Start the application
python app.py

Then open your browser and go to:

http://127.0.0.1:5000


 Why This Project?

- Problem — Passwords can be stolen, guessed, or hacked
- Solution — Every person has a unique behavioral pattern that cannot be copied
- Result — Even if someone knows your password, the system detects and blocks them!

> "Your password can be stolen. Your behavior cannot."

 Developer
Hemadharshini R
GitHub: [@hemadharshiniR](https://github.com/hemadharshiniR)

 Note
> Behavioural biometrics is a cutting-edge security technique used by banks and cybersecurity firms worldwide to detect unauthorized access. This project brings that technology to life!
