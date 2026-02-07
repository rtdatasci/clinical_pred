import os
import requests
import pandas as pd
import numpy as np
import logging
from tabulate import tabulate
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# --- DATA FETCHING ---
def download_file(url, target_path):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    if os.path.exists(target_path):
        logging.info(f"Skipping download, file exists: {target_path}")
        return
    logging.info(f"Downloading {url} to {target_path}...")
    response = requests.get(url)
    response.raise_for_status()
    with open(target_path, 'wb') as f:
        f.write(response.content)

# --- DATA CLEANING ---
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
    
    # Load raw, handling '?' as NaN immediately if present (though Pima usually uses 0 for missing)
    df_raw = pd.read_csv(raw_path, names=cols, na_values=['?', ''])
    
    # Canonical: Treat 0s as NaNs for biological columns where 0 is impossible
    df_can = df_raw.copy()
    cbz = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    for col in cbz:
        df_can[col] = df_can[col].replace(0, np.nan)
    
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
    # Pregnancies, Age, Outcome should be ints. logic: cast to round then int. 
    # However, imputation returns floats.
    for col in ['Pregnancies', 'Outcome', 'Age']:
        df_ml[col] = df_ml[col].round().astype(int)
        
    df_ml.to_csv(ml_path, index=False)
    return get_missingness_stats(df_can, df_ml, cols)

# --- QUALITY REPORTING ---
def detect_outliers_iqr(df, columns):
    stats = []
    for col in columns:
        if df[col].dtype in [np.float64, np.int64]:
            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            iqr = q3 - q1
            out = df[(df[col] < q1 - 1.5*iqr) | (df[col] > q3 + 1.5*iqr)]
            stats.append({'Variable': col, 'Outliers': len(out), '%': f"{len(out)/len(df):.1%}"})
    return pd.DataFrame(stats)

def check_clinical_ranges(df, name):
    ranges = {'Diabetes': {'Glucose': (40, 400), 'BloodPressure': (40, 200), 'BMI': (15, 60)}}
    issues = []
    for col, (l, h) in ranges.get(name, {}).items():
        if col in df.columns:
            inv = df[(df[col] < l) | (df[col] > h)]
            if not inv.empty: issues.append({'Variable': col, 'Range': f"[{l}, {h}]", 'Violations': len(inv)})
    return pd.DataFrame(issues)

def run_report(can_p, ml_p, name, log_file):
    df_can, df_ml = pd.read_csv(can_p), pd.read_csv(ml_p)
    with open(log_file, 'a') as f:
        f.write(f"\n## {name} Quality Audit\n")
        f.write("\n### 1. Distribution Shift (Imputation Effect)\n")
        shift = []
        for c in df_can.columns:
            if df_can[c].dtype in [np.float64, np.int64] and c not in ['Outcome']:
                shift.append({
                    'Var': c, 
                    'Can Mean': f"{df_can[c].mean():.2f}", 
                    'ML Mean': f"{df_ml[c].mean():.2f}", 
                    'Shift': f"{df_ml[c].mean()-df_can[c].mean():+.2f}"
                })
        f.write(tabulate(shift, headers='keys', tablefmt='github') + "\n")
        f.write("\n### 2. Outliers & Clinical Ranges\n")
        out = detect_outliers_iqr(df_ml, [c for c in df_ml.columns if c not in ['Outcome']])
        f.write(tabulate(out, headers='keys', tablefmt='github') + "\n")
        clin = check_clinical_ranges(df_ml, name)
        if not clin.empty: f.write("\n**Clinical Range Violations:**\n" + tabulate(clin, headers='keys', tablefmt='github') + "\n")

def main():
    report_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/audit_report.md'))
    if os.path.exists(report_file): os.remove(report_file)
    with open(report_file, 'w') as f: f.write("# Clinical Data Audit Results\n")
    
    # 1. Pipeline Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, 'data/raw')
    can_dir = os.path.join(base_dir, 'data/canonical')
    proc_dir = os.path.join(base_dir, 'data/processed')
    
    for d in [raw_dir, can_dir, proc_dir]: os.makedirs(d, exist_ok=True)
    
    # Diabetes Workflow
    logging.info("Processing Diabetes Dataset...")
    download_file("https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv", os.path.join(raw_dir, "diabetes_raw.csv"))
    
    clean_diabetes(
        os.path.join(raw_dir, "diabetes_raw.csv"), 
        os.path.join(can_dir, "diabetes_canonical.csv"), 
        os.path.join(proc_dir, "diabetes_clean.csv")
    )
    
    run_report(
        os.path.join(can_dir, "diabetes_canonical.csv"), 
        os.path.join(proc_dir, "diabetes_clean.csv"), 
        'Diabetes', 
        report_file
    )
    
    logging.info(f"Audit complete. Results saved to {report_file}")

if __name__ == "__main__":
    main()
