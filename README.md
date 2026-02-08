# Clinical Data Quality Audit Demo

This project demonstrates clinical reasoning about data validity and explicit handling of missingness in medical datasets. It follows a tiered architecture to ensure traceability and replaces basic prediction with a comprehensive **Data Quality Audit**.

## Project Philosophy: Clinical Validity
Clinical datasets are rarely "ML-ready." This project emphasizes three core principles:
1. **Clinical Reasoning**: Understanding the biological meaning of data (e.g., Blood Pressure = 0 is a missing value, not a measurement).
2. **Explicit Missingness Handling**: Distinguishing between structural missingness (symbols) and biological missingness (impossible values).
3. **Quality Audit**: Moving beyond accuracy to inspect distribution shifts and clinical range violations.

## Data Architecture (Tiered)
- **Raw Layer (`data/raw/`)**: Byte-for-byte copies of original datasets.
- **Canonical Layer (`data/canonical/`)**: Standardized schema, non-standard missing values converted to `NaN`. Original labels are preserved.
- **ML-Ready Layer (`data/processed/`)**: Imputed values and derived features (e.g., binarized targets) optimized for machine learning.

## 1. Missingness Audit
We explicitly identify and handle "non-standard missing value encoding" to avoid skewing clinical analysis.


### Diabetes (Pima Indians)
**Data Source**: [Pima Indians Diabetes Database (Kaggle / UCI)](https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database)

Focuses on "Biological Impossible Zeros" treated as missing.
| Variable      | Missing (Raw) | Type                          |
|:--------------|:--------------|:------------------------------|
| Glucose       | 5 (0.7%)      | Biological (Impossible zeros) |
| BloodPressure | 35 (4.6%)     | Biological (Impossible zeros) |
| SkinThickness | 227 (29.6%)   | Biological (Impossible zeros) |
| Insulin       | 374 (48.7%)   | Biological (Impossible zeros) |
| BMI           | 11 (1.4%)     | Biological (Impossible zeros) |


## 2. Data Processing & Imputation
We use a tiered approach to handle missingness without data loss.

### Imputation Strategy (MICE)
- **Method**: Multivariate Imputation by Chained Equations (IterativeImputer with BayesianRidge).
- **Why**: Dropping rows with missing values (e.g., Insulin, which has ~49% zeros) would discard half the dataset. MICE uses correlations between variables (e.g., Glucose & BMI) to estimate missing values probabilistically, preserving the dataset structure.
- **Example**: A patient with `Insulin = 0` (missing) but high `Glucose` will likely have a higher imputed Insulin value than a patient with low Glucose, rather than filling with a global mean.
    - *Observed Shift*: The mean Insulin value shifted slightly (+0.29) after imputation, indicating the missing values were estimated to be consistent with the observed population.

### Target Processing
- **Binary Target**: The `Outcome` variable (0 = No Diabetes, 1 = Diabetes) is preserved from the raw data.
    - We cast this to integer to ensure clean downstream processing.
- **Why**: No derivation from a multi-class scale was needed for this dataset (unlike Cleveland Heart Disease), preserving the original ground truth.

## 3. Clinical Quality Report
The `audit_quality.py` script identifies artifacts introduced during cleaning and verifies biological plausibility.

### Distribution Shifts
Imputation can shift the mean. For example, in the Diabetes dataset, imputing **Insulin** (which had ~49% zeros) resulted in a shift of **+0.29** in the mean, identifying a significant "cleaning artifact" that researchers should be aware of.

### Clinical Range Violations
We check for values that fall outside conservative biological limits (e.g., Blood Pressure < 40).
- **Diabetes**: Found 4 violations in Blood Pressure (min 24.0) and 1 in BMI (max 67.1). These represent extreme cases or sensor errors that require human review.


## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Run the Full Pipeline: `python scripts/run_pipeline.py`
3. View Results: Open `data/audit_report.md` for the detailed clinical quality findings.
