# AI Password Pattern & Weakness Detection System 🔐

A full-stack, AI-driven machine learning application that intelligently analyzes passwords in real-time, detecting critical vulnerabilities, patterns, and estimating security strength. Built as an academic mini-project demonstrating applied machine learning in cybersecurity!

> **Note:** This project is built with privacy by design. User passwords are *never* stored, logged, or cached. All analysis is completed entirely in-memory dynamically as the user types.

## ✨ Features

- **Real-Time ML Classification:** Utilizes a `RandomForestClassifier` trained on thousands of dynamically generated patterns to score passwords as Weak, Medium, or Strong.
- **Rule-Based Fallback Analysis:** Actively calculates Shannon Entropy (Bits), parses casing distribution, and identifies repeating keyboard patterns (like `123`, `qwerty`, or `aaa`).
- **Dictionary Attack Prevention:** Cross-references patterns against a local subset of heavily breached/common dictionary passwords.
- **Dynamic Aesthetic UI:** A beautifully responsive frontend using Glassmorphism, smooth color-state transitions, and micro-animations (such as UI shaking algorithms for weak inputs).

## 🛠️ Tech Stack

- **Backend / API Server:** Python, Flask
- **Machine Learning Layer:** `scikit-learn`, `pandas`, `numpy`
- **Frontend Interactivity:** HTML5, CSS3, Vanilla JavaScript, FontAwesome
- **Environment Management:** Python `venv` 

## 🧠 How The ML Works
Since obtaining a large dataset of *real* plaintext passwords is a major security violation, this project includes a synthetic dataset generation script (`data/generate_dataset.py`). The script procedurally creates exactly 3,000 uniquely structured passwords along with their mathematically extracted features, which were then utilized to train the local `rf_model.pkl` Random Forest model.

## 🚀 Local Installation & Setup 

Follow these instructions to run the web application locally on your machine for demonstration purposes.

### 1. Clone the repository
```bash
git clone https://github.com/tharun-1365/ai-password-analyzer.git
cd ai-password-analyzer
```

### 2. Set up the Virtual Environment & Dependencies
```bash
# Create the environment
python -m venv .venv

# Activate it (Windows)
.\.venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. (Optional) Retrain the Machine Learning Model
The model is already pre-trained and compressed inside `core/rf_model.pkl`. If you'd like to regenerate the data yourself, run:
```bash
python data/generate_dataset.py
python core/train_model.py
```

### 4. Start the Application
```bash
python app.py
```
*Open your browser and navigate to **http://127.0.0.1:5000***
