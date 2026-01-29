import pandas as pd
import numpy as np
import os

def clean_heart_disease(raw_path, processed_path):
    print(f"Cleaning Heart Disease data from {raw_path}...")
    
    # Column names based on UCI documentation
    columns = [
        'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
        'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target'
    ]
    
    # Raw data uses '?' for missing values
    df = pd.read_csv(raw_path, names=columns, na_values='?')
    
    print(f"Initial shape: {df.shape}")
    print(f"Missing values found:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    
    # Demo Issue 1: Missing values represented by '?'
    # We will impute 'ca' and 'thal' with their modes for this demo
    df['ca'] = df['ca'].fillna(df['ca'].mode()[0])
    df['thal'] = df['thal'].fillna(df['thal'].mode()[0])
    
    # Demo Issue 2: Categorical encoding for transparency
    # Mapping integers to descriptive strings for better readability/processing demo
    # target: 0 = no disease, 1-4 = disease
    df['target'] = df['target'].apply(lambda x: 1 if x > 0 else 0)
    
    df.to_csv(processed_path, index=False)
    print(f"Cleaned Heart Disease data saved to {processed_path}")

def clean_diabetes(raw_path, processed_path):
    print(f"Cleaning Diabetes data from {raw_path}...")
    
    columns = [
        'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
        'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age', 'Outcome'
    ]
    df = pd.read_csv(raw_path, names=columns)
    
    print(f"Initial shape: {df.shape}")
    
    # Demo Issue 3: Biologically impossible zeros
    cols_with_zeros = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    print("Zero counts in key columns (hidden missing values):")
    for col in cols_with_zeros:
        count = (df[col] == 0).sum()
        print(f"  {col}: {count}")
        # Replace 0 with NaN
        df[col] = df[col].replace(0, np.nan)
    
    # Simple imputation: Median (less sensitive to outliers)
    for col in cols_with_zeros:
        df[col] = df[col].fillna(df[col].median())
        
    df.to_csv(processed_path, index=False)
    print(f"Cleaned Diabetes data saved to {processed_path}")

def main():
    raw_dir = 'data/raw'
    processed_dir = 'data/processed'
    os.makedirs(processed_dir, exist_ok=True)
    
    heart_raw = os.path.join(raw_dir, "heart_disease_raw.csv")
    heart_clean = os.path.join(processed_dir, "heart_disease_clean.csv")
    if os.path.exists(heart_raw):
        clean_heart_disease(heart_raw, heart_clean)
        
    diabetes_raw = os.path.join(raw_dir, "diabetes_raw.csv")
    diabetes_clean = os.path.join(processed_dir, "diabetes_clean.csv")
    if os.path.exists(diabetes_raw):
        clean_diabetes(diabetes_raw, diabetes_clean)

if __name__ == "__main__":
    main()
