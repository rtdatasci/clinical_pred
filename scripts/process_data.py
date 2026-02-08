import os
import pandas as pd
import numpy as np
import logging
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_missingness_stats(df_raw, df_cleaned, columns):
    stats = []
    for col in columns:
        # Check for NaN as missing in raw
        raw_missing = df_raw[col].isnull().sum()
        cleaned_missing = df_cleaned[col].isnull().sum()
        total = len(df_raw)
        m_type = 'None'
        if col in ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']: m_type = 'Biological'
        stats.append({'Variable': col, 'Missing (Raw)': f"{raw_missing} ({raw_missing/total:.1%})", 'Missing (Clean)': f"{cleaned_missing} ({cleaned_missing/total:.1%})", 'Type': m_type})
    return pd.DataFrame(stats)

def clean_diabetes(raw_path, canonical_path, ml_path):
    cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age', 'Outcome']
    
    if not os.path.exists(raw_path):
        logging.error(f"Raw file not found: {raw_path}")
        return None

    # Load raw, handling '?' as NaN immediately if present (though Pima usually uses 0 for missing)
    df_raw = pd.read_csv(raw_path, names=cols, na_values=['?', ''])
    
    # Canonical: Treat 0s as NaNs for biological columns where 0 is impossible
    df_can = df_raw.copy()
    cbz = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    for col in cbz:
        df_can[col] = df_can[col].replace(0, np.nan)
    
    os.makedirs(os.path.dirname(canonical_path), exist_ok=True)
    df_can.to_csv(canonical_path, index=False)
    
    # ML-Ready: Probabilistic Imputation (MICE)
    df_ml = df_can.copy()
    
    # Initialize IterativeImputer
    # We use BayesianRidge estimator by default which is generally robust
    imputer = IterativeImputer(max_iter=10, random_state=42, sample_posterior=True) 
    
    # Fit and transform
    # Note: Outcome is included to help imputation but should not be imputed if it were missing (it's not here)
    df_imputed = imputer.fit_transform(df_ml)
    df_ml = pd.DataFrame(df_imputed, columns=cols)
    
    # Post-imputation: Clip negative values for biological columns (cannot be negative)
    for col in cbz:
        df_ml[col] = df_ml[col].clip(lower=df_can[col].min())

    # Round imputed values for integer columns where appropriate
    for col in ['Pregnancies', 'Outcome', 'Age']:
        df_ml[col] = df_ml[col].round().astype(int)
        
    os.makedirs(os.path.dirname(ml_path), exist_ok=True)
    df_ml.to_csv(ml_path, index=False)
    return get_missingness_stats(df_can, df_ml, cols)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, 'data/raw')
    can_dir = os.path.join(base_dir, 'data/canonical')
    proc_dir = os.path.join(base_dir, 'data/processed')
    
    logging.info("Processing Diabetes Dataset...")
    clean_diabetes(
        os.path.join(raw_dir, "diabetes_raw.csv"), 
        os.path.join(can_dir, "diabetes_canonical.csv"), 
        os.path.join(proc_dir, "diabetes_clean.csv")
    )
    logging.info("Processing complete.")

if __name__ == "__main__":
    main()
