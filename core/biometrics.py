import numpy as np
import json
from .database import get_keystroke_profiles, save_keystroke_profile

# Minimum number of successful logins needed to build a "baseline" profile for behavior tracking
BASELINE_THRESHOLD = 3 

# Threshold for Euclidean distance to flag as suspicious
# (Configurable based on real-world data collection, lower is stricter)
ANOMALY_THRESHOLD = 1500 

def extract_vector(features):
    """
    Extracts relevant floats into a normalized numeric vector to calculate Euclidean distances.
    `features` comes from frontend calculation.
    """
    try:
        dwell_avg = features.get('avg_dwell', 0)
        flight_avg = features.get('avg_flight', 0)
        speed = features.get('typing_speed', 0)
        error_rate = features.get('error_rate', 0)
        
        # Simple extraction for now - could add total_time, dwell array variance, etc.
        return np.array([dwell_avg, flight_avg, speed, error_rate], dtype=float)
    except Exception as e:
        print(f"Error parsing biometrics features: {e}")
        return np.zeros(4)


def analyze_keystrokes(user_id, current_features):
    """
    Compares the current_features to the historical baseline of the user and enforces hard rules for typos/hesitation.
    Returns: (is_suspicious_boolean, confidence_score_float, message)
    """
    history = get_keystroke_profiles(user_id)
    
    backspace_count = current_features.get('backspace_count', 0)
    delete_count = current_features.get('delete_count', 0)
    hesitation_count = current_features.get('hesitation_count', 0)

    # --- Rule Based Hard Checks ---
    if backspace_count > 4:
        return True, 100.0, "Excessive backspaces used."
    if delete_count > 2:
        return True, 100.0, "Multiple corrections made via Delete."
    if hesitation_count > 3:
        return True, 100.0, "Repeated significant typing pauses detected."

    # Not enough data for baseline yet -> allow it
    if len(history) < BASELINE_THRESHOLD:
        return False, 100.0, f"Learning baseline... ({len(history)}/{BASELINE_THRESHOLD} completed)"
        
    # Calculate baseline average vector
    history_vectors = [extract_vector(f) for f in history[-10:]] # Use last 10 logins for rolling average
    
    if not history_vectors:
        return False, 100.0, "Error building baseline, allowing entry."
        
    baseline_array = np.mean(history_vectors, axis=0) # Averaged historically
    current_vector = extract_vector(current_features)
    
    # Calculate Euclidean distance between the current login vector and the historical average vector
    # Larger distance = more suspicious
    distance = np.linalg.norm(current_vector - baseline_array)
    print(f"User {user_id} Typing Distance: {distance:.2f}")
    
    is_suspicious = distance > ANOMALY_THRESHOLD
    
    return is_suspicious, distance, "Behavior analysis complete."
