import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

def train():
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "passwords_dataset.csv")
    if not os.path.exists(data_path):
        print(f"Dataset not found at {data_path}. Please run generate_dataset.py first.")
        return

    df = pd.read_csv(data_path)
    
    X = df.drop(columns=['label'])
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Weak", "Medium", "Strong"]))
    
    # Save the model
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rf_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"Model saved to '{model_path}'")

if __name__ == "__main__":
    train()
