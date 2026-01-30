import os
import requests
import pandas as pd
import numpy as np
import logging
from tabulate import tabulate

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
        raw_missing = df_raw[col].isnull().sum()
        cleaned_missing = df_cleaned[col].isnull().sum()
        total = len(df_raw)
        m_type = 'None'
        if col in ['ca', 'thal']: m_type = 'Structural'
        elif col in ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']: m_type = 'Biological'
        stats.append({'Variable': col, 'Missing (Raw)': f"{raw_missing} ({raw_missing/total:.1%})", 'Missing (Clean)': f"{cleaned_missing} ({cleaned_missing/total:.1%})", 'Type': m_type})
    return pd.DataFrame(stats)

def clean_heart_disease(raw_path, canonical_path, ml_path):
    cols = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target']
    df_can = pd.read_csv(raw_path, names=cols, na_values='?')
    df_can.to_csv(canonical_path, index=False)
    df_ml = df_can.copy()
    df_ml['target_original'] = df_ml['target']
    df_ml['target'] = df_ml['target'].apply(lambda x: 1 if x > 0 else 0)
    for col in ['ca', 'thal']: df_ml[col] = df_ml[col].fillna(df_ml[col].mode()[0])
    df_ml.to_csv(ml_path, index=False)
    return get_missingness_stats(df_can, df_ml, cols)

def clean_diabetes(raw_path, canonical_path, ml_path):
    cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age', 'Outcome']
    df_raw = pd.read_csv(raw_path, names=cols)
    df_can = df_raw.copy()
    cbz = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    for col in cbz: df_can[col] = df_can[col].replace(0, np.nan)
    df_can.to_csv(canonical_path, index=False)
    df_ml = df_can.copy()
    for col in cbz: df_ml[col] = df_ml[col].fillna(df_ml[col].median())
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
    ranges = {'Diabetes': {'Glucose': (40, 400), 'BloodPressure': (40, 200), 'BMI': (15, 60)}, 'Heart Disease': {'trestbps': (80, 250), 'chol': (100, 600)}}
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
        f.write("\n### 1. Distribution Shift\n")
        shift = []
        for c in df_can.columns:
            if df_can[c].dtype in [np.float64, np.int64] and c not in ['target', 'Outcome', 'target_original']:
                shift.append({'Var': c, 'Can Mean': f"{df_can[c].mean():.2f}", 'ML Mean': f"{df_ml[c].mean():.2f}", 'Shift': f"{df_ml[c].mean()-df_can[c].mean():+.2f}"})
        f.write(tabulate(shift, headers='keys', tablefmt='github') + "\n")
        f.write("\n### 2. Outliers & Clinical Ranges\n")
        out = detect_outliers_iqr(df_ml, [c for c in df_ml.columns if c not in ['target', 'Outcome', 'target_original']])
        f.write(tabulate(out, headers='keys', tablefmt='github') + "\n")
        clin = check_clinical_ranges(df_ml, name)
        if not clin.empty: f.write("\n**Clinical Range Violations:**\n" + tabulate(clin, headers='keys', tablefmt='github') + "\n")

def main():
    report_file = 'data/audit_report.md'
    if os.path.exists(report_file): os.remove(report_file)
    with open(report_file, 'w') as f: f.write("# Clinical Data Audit Results\n")
    
    # 1. Pipeline
    raw_dir, can_dir, proc_dir = 'data/raw', 'data/canonical', 'data/processed'
    for d in [raw_dir, can_dir, proc_dir]: os.makedirs(d, exist_ok=True)
    
    # Heart Disease
    download_file("https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data", os.path.join(raw_dir, "heart_disease_raw.csv"))
    clean_heart_disease(os.path.join(raw_dir, "heart_disease_raw.csv"), os.path.join(can_dir, "heart_disease_canonical.csv"), os.path.join(proc_dir, "heart_disease_clean.csv"))
    run_report(os.path.join(can_dir, "heart_disease_canonical.csv"), os.path.join(proc_dir, "heart_disease_clean.csv"), 'Heart Disease', report_file)
    
    # Diabetes
    download_file("https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv", os.path.join(raw_dir, "diabetes_raw.csv"))
    clean_diabetes(os.path.join(raw_dir, "diabetes_raw.csv"), os.path.join(can_dir, "diabetes_canonical.csv"), os.path.join(proc_dir, "diabetes_clean.csv"))
    run_report(os.path.join(can_dir, "diabetes_canonical.csv"), os.path.join(proc_dir, "diabetes_clean.csv"), 'Diabetes', report_file)
    
    logging.info(f"Audit complete. Results saved to {report_file}")

if __name__ == "__main__":
    main()
