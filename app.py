from flask import Flask, render_template, request, jsonify
from core.feature_extractor import extract_features, get_feedback, is_common_password
import pickle
import os

app = Flask(__name__)

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
