# Clinical Data Audit Results

## Heart Disease Quality Audit

### 1. Distribution Shift
| Var      |   Can Mean |   ML Mean |   Shift |
|----------|------------|-----------|---------|
| age      |      54.44 |     54.44 |    0    |
| sex      |       0.68 |      0.68 |    0    |
| cp       |       3.16 |      3.16 |    0    |
| trestbps |     131.69 |    131.69 |    0    |
| chol     |     246.69 |    246.69 |    0    |
| fbs      |       0.15 |      0.15 |    0    |
| restecg  |       0.99 |      0.99 |    0    |
| thalach  |     149.61 |    149.61 |    0    |
| exang    |       0.33 |      0.33 |    0    |
| oldpeak  |       1.04 |      1.04 |    0    |
| slope    |       1.6  |      1.6  |    0    |
| ca       |       0.67 |      0.66 |   -0.01 |
| thal     |       4.73 |      4.72 |   -0.01 |

### 2. Outliers & Clinical Ranges
|    | Variable   |   Outliers | %     |
|----|------------|------------|-------|
|  0 | age        |          0 | 0.0%  |
|  1 | sex        |          0 | 0.0%  |
|  2 | cp         |         23 | 7.6%  |
|  3 | trestbps   |          9 | 3.0%  |
|  4 | chol       |          5 | 1.7%  |
|  5 | fbs        |         45 | 14.9% |
|  6 | restecg    |          0 | 0.0%  |
|  7 | thalach    |          1 | 0.3%  |
|  8 | exang      |          0 | 0.0%  |
|  9 | oldpeak    |          5 | 1.7%  |
| 10 | slope      |          0 | 0.0%  |
| 11 | ca         |         20 | 6.6%  |
| 12 | thal       |          0 | 0.0%  |

## Diabetes Quality Audit

### 1. Distribution Shift
| Var                      |   Can Mean |   ML Mean |   Shift |
|--------------------------|------------|-----------|---------|
| Pregnancies              |       3.85 |      3.85 |    0    |
| Glucose                  |     121.69 |    121.66 |   -0.03 |
| BloodPressure            |      72.41 |     72.39 |   -0.02 |
| SkinThickness            |      29.15 |     29.11 |   -0.05 |
| Insulin                  |     155.55 |    140.67 |  -14.88 |
| BMI                      |      32.46 |     32.46 |   -0    |
| DiabetesPedigreeFunction |       0.47 |      0.47 |    0    |
| Age                      |      33.24 |     33.24 |    0    |

### 2. Outliers & Clinical Ranges
|    | Variable                 |   Outliers | %     |
|----|--------------------------|------------|-------|
|  0 | Pregnancies              |          4 | 0.5%  |
|  1 | Glucose                  |          0 | 0.0%  |
|  2 | BloodPressure            |         14 | 1.8%  |
|  3 | SkinThickness            |         87 | 11.3% |
|  4 | Insulin                  |        346 | 45.1% |
|  5 | BMI                      |          8 | 1.0%  |
|  6 | DiabetesPedigreeFunction |         29 | 3.8%  |
|  7 | Age                      |          9 | 1.2%  |

**Clinical Range Violations:**
|    | Variable      | Range     |   Violations |
|----|---------------|-----------|--------------|
|  0 | BloodPressure | [40, 200] |            4 |
|  1 | BMI           | [15, 60]  |            1 |
