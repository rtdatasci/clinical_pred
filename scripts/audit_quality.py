import os
import pandas as pd
import numpy as np
import logging
from tabulate import tabulate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

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
    if not os.path.exists(can_p) or not os.path.exists(ml_p):
        logging.error(f"Data files missing for report: {can_p} or {ml_p}")
        return

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
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    can_dir = os.path.join(base_dir, 'data/canonical')
    proc_dir = os.path.join(base_dir, 'data/processed')
    
    logging.info("Generating Audit Report...")
    run_report(
        os.path.join(can_dir, "diabetes_canonical.csv"), 
        os.path.join(proc_dir, "diabetes_clean.csv"), 
        'Diabetes', 
        report_file
    )
    logging.info(f"Audit complete. Results saved to {report_file}")

if __name__ == "__main__":
    main()
