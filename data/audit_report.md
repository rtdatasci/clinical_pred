# Clinical Data Audit Results

## Diabetes Quality Audit

### 1. Distribution Shift (Imputation Effect)
| Var                      |   Can Mean |   ML Mean |   Shift |
|--------------------------|------------|-----------|---------|
| Pregnancies              |       3.85 |      3.85 |    0    |
| Glucose                  |     121.69 |    121.62 |   -0.06 |
| BloodPressure            |      72.41 |     72.39 |   -0.01 |
| SkinThickness            |      29.15 |     28.88 |   -0.27 |
| Insulin                  |     155.55 |    155.84 |    0.29 |
| BMI                      |      32.46 |     32.45 |   -0.01 |
| DiabetesPedigreeFunction |       0.47 |      0.47 |    0    |
| Age                      |      33.24 |     33.24 |    0    |

### 2. Outliers & Clinical Ranges
|    | Variable                 |   Outliers | %    |
|----|--------------------------|------------|------|
|  0 | Pregnancies              |          4 | 0.5% |
|  1 | Glucose                  |          0 | 0.0% |
|  2 | BloodPressure            |         14 | 1.8% |
|  3 | SkinThickness            |          5 | 0.7% |
|  4 | Insulin                  |         24 | 3.1% |
|  5 | BMI                      |          8 | 1.0% |
|  6 | DiabetesPedigreeFunction |         29 | 3.8% |
|  7 | Age                      |          9 | 1.2% |

**Clinical Range Violations:**
|    | Variable      | Range     |   Violations |
|----|---------------|-----------|--------------|
|  0 | BloodPressure | [40, 200] |            4 |
|  1 | BMI           | [15, 60]  |            1 |
