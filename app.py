from flask import Flask, render_template, request, jsonify
from core.feature_extractor import extract_features, get_feedback, is_common_password
from core.biometrics import analyze_keystrokes
from core.database import register_user, authenticate_user, save_keystroke_profile, init_db
import pickle
import os

app = Flask(__name__)

# Initialize Local Database
init_db()

# Load the model globally
MODEL_PATH = os.path.join(os.path.dirname(__file__), "core", "rf_model.pkl")
model = None

if os.path.exists(MODEL_PATH):
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
    except Exception as e:
        print(f"Error loading model: {e}")
else:
    print(f"Warning: Model not found at {MODEL_PATH}. Prediction will fall back to rule-based.")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")
    
    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"})
        
    success, message = register_user(username, password)
    return jsonify({"success": success, "message": message})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")
    keystroke_data = data.get("keystrokes", {})
    
    if not username or not password:
        return jsonify({"success": False, "status": "FAILED", "message": "Missing credentials"})
        
    # 1. Validate Password
    is_valid, user_id = authenticate_user(username, password)
    
    if not is_valid:
         return jsonify({"success": False, "status": "FAILED", "message": "Invalid password"})
         
    # 2. Extract Keystroke Features
    try:
        # 3. Analyze Behavior 
        is_suspicious, distance, biometrics_message = analyze_keystrokes(user_id, keystroke_data)
        
        # Security Auditing Log
        if is_suspicious:
            print(f"SUSPICIOUS ACTIVITY LOG - User: {username} - Reason: {biometrics_message} - Metric Diff: {distance:.2f}")

        # 4. Save to profile
        save_keystroke_profile(user_id, keystroke_data)
        
        if is_suspicious:
            return jsonify({
                "success": False, 
                "status": "SUSPICIOUS", 
                "message": "Unusual typing behavior detected. Verify identity. (" + biometrics_message + ")",
                "distance": distance
            })
            
        return jsonify({
            "success": True, 
            "status": "SUCCESS", 
            "message": "Login successful - Behavior matched.",
            "distance": distance
        })
        
    except Exception as e:
        print(f"Login error processing biometrics: {e}")
        return jsonify({"success": False, "status": "FAILED", "message": "System error processing login"})

@app.route("/api/verify_otp", methods=["POST"])
def verify_otp():
    # Mock OTP verification
    data = request.get_json()
    otp = data.get("otp", "")
    
    if otp == "1234":
         return jsonify({"success": True, "message": "Identity verified successfully"})
         
    return jsonify({"success": False, "message": "Invalid verification code"})

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    password = data.get("password", "")
    
    if not password:
        return jsonify({"empty": True})
        
    features = extract_features(password)
    feedback = get_feedback(password)
    
    # Construct feature vector
    feature_vector = [[
        features['length'],
        features['num_upper'],
        features['num_lower'],
        features['num_digits'],
        features['num_special'],
        features['repeated'],
        features['sequential'],
        features['common'],
        features['entropy']
    ]]
    
    strength_label = "Unknown"
    score = 0
    probabilities = [0.0, 0.0, 0.0]
    
    if model:
        prediction = model.predict(feature_vector)[0]
        prob = model.predict_proba(feature_vector)[0]
        
        if prediction == 0:
            strength_label = "Weak"
        elif prediction == 1:
            strength_label = "Medium"
        elif prediction == 2:
            strength_label = "Strong"
            
        score = prob[prediction] * 100
        probabilities = [float(p) for p in prob]
    else:
        # Fallback to rule-based if model is missing
        if len(password) < 8 or is_common_password(password):
            strength_label = "Weak"
            score = 30
        elif len(password) >= 12 and features['num_upper'] > 0 and features['num_special'] > 0:
            strength_label = "Strong"
            score = 90
        else:
            strength_label = "Medium"
            score = 60
            
    # Rule overrides just in case ML prediction is too confident on weak pass
    if len(password) < 8 or "avoid using it" in " ".join(feedback):
        strength_label = "Weak"
            
    response = {
        "empty": False,
        "strength": strength_label,
        "score": int(score),
        "probabilities": probabilities,
        "features": features,
        "feedback": feedback
    }
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
