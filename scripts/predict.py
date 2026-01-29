import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import os

def run_prediction(data_path, target_col, name):
    print(f"\n--- Prediction Demo: {name} ---")
    df = pd.read_csv(data_path)
    
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

def main():
    processed_dir = 'data/processed'
    
    heart_clean = os.path.join(processed_dir, "heart_disease_clean.csv")
    if os.path.exists(heart_clean):
        run_prediction(heart_clean, 'target', 'Heart Disease')
    
    diabetes_clean = os.path.join(processed_dir, "diabetes_clean.csv")
    if os.path.exists(diabetes_clean):
        run_prediction(diabetes_clean, 'Outcome', 'Diabetes')

if __name__ == "__main__":
    main()
