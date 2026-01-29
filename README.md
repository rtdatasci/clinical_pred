# Clinical Data Cleaning & Prediction Demo

This project demonstrates how to handle common data quality issues in clinical datasets and prepare them for machine learning.

## Datasets
1.  **UCI Heart Disease (Cleveland)**: Predicting heart disease presence.
2.  **Pima Indians Diabetes**: Predicting diabetes onset.

## Data Quality Issues: The "Raw Dirty Data"
Clinical datasets are rarely "ML-ready" out of the box. This project handles:
- **Hidden Missing Values (Symbols)**: In the Heart Disease data, missing attributes are marked with `?`. Loading this directly into an ML model causes a crash. I translate these to nulls and impute them.
- **Biologically Impossible Zeros**: In the Diabetes data, features like `Insulin`, `BMI`, and `Glucose` have `0` values. Since a living human cannot have a BMI or blood sugar of zero, these are effectively "stealth" missing values that would skew model averages if not handled.
- **Label Inconsistency**: The raw Heart Disease labels range from 0 (healthy) to 4 (severe disease). For a basic screening demo, I consolidate categories 1-4 into a single "Positive" class.

### Spotting the Dirty Data (Examples)
| Dataset | Feature | Raw Value (Dirty) | Cleaned Value | Reason |
| :--- | :--- | :--- | :--- | :--- |
| **Heart Disease** | `ca` | `?` | `0.0` (Mode) | Models cannot process symbols |
| **Diabetes** | `Insulin` | `0` | `125.0` (Median) | Biologically impossible value |
| **Diabetes** | `BMI` | `0` | `32.3` (Median) | Hidden missing value |
| **Heart Disease** | `target` | `2` | `1` | Target binarization for screening |

## Why Random Forest?
I chose the **Random Forest Classifier** for this clinical demo for several reasons:
1. **Robustness to Outliers**: Clinical data often has extreme values (e.g., very high cholesterol). Random Forests are less sensitive to these than linear models.
2. **No Scaling Required**: Unlike Support Vector Machines or Neural Networks, Random Forests don't require the data to be normalized (e.g., age 0-100 vs cholesterol 100-500), making the pipeline simpler.
3. **Captures Non-Linearity**: Medical conditions are often determined by the *interaction* of multiple factors (e.g., Age combined with Blood Pressure) rather than just a single factor. Random Forest excels at finding these connections.

## What Do the Results Mean?
When you run `predict.py`, you see an **Accuracy** score (e.g., ~87% for Heart Disease). In a clinical context:
- **High Accuracy** suggests the model is a strong candidate for a preliminary "screening" tool.
- **Precision vs. Recall**: In medicine, **Recall** is critical. It measures how many *actual* sick patients the model correctly identified. Missing a sick patient (False Negative) is usually much more costly than a False Positive (which might just lead to a follow-up test).
- **The Baseline**: My result proves that even with simple median imputation and basic cleaning, I can achieve high predictive power on real-world clinical data.

## Project Structure
- `data/raw/`: Original files containing the "dirty" data (symbols, impossible zeros).
- `data/processed/`: Cleaned, imputed, and ML-ready versions.
- `scripts/fetch_data.py`: Downloads the raw datasets from UCI and mirrors.
- `scripts/clean_data.py`: The ETL bridge that fixes the data quality issues.
- `scripts/predict.py`: Trains and evaluates the Random Forest model.

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Fetch data: `python scripts/fetch_data.py`
3. Clean data: `python scripts/clean_data.py`
4. Run prediction: `python scripts/predict.py`
