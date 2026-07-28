-- =============================================================================
-- UEH Advanced Data Analytics Portal - Analytical & BI Query Suite
-- Designed for Tableau Data Sources, PowerBI, and SQL Data Warehouses
-- =============================================================================

-- -----------------------------------------------------------------------------
-- QUERY 1: Comprehensive Statistical Metrics Calculation for Diabetes Features
-- Calculates Mean, Min, Max, and Variance across Clinical Features
-- -----------------------------------------------------------------------------
SELECT 
    'Glucose' AS Feature,
    COUNT(Glucose) AS N,
    ROUND(AVG(Glucose), 2) AS Mean,
    ROUND(MIN(Glucose), 2) AS MinValue,
    ROUND(MAX(Glucose), 2) AS MaxValue,
    ROUND(AVG((Glucose - (SELECT AVG(Glucose) FROM diabetes_patients)) * (Glucose - (SELECT AVG(Glucose) FROM diabetes_patients))), 2) AS Variance
FROM diabetes_patients

UNION ALL

SELECT 
    'BloodPressure' AS Feature,
    COUNT(BloodPressure) AS N,
    ROUND(AVG(BloodPressure), 2) AS Mean,
    ROUND(MIN(BloodPressure), 2) AS MinValue,
    ROUND(MAX(BloodPressure), 2) AS MaxValue,
    ROUND(AVG((BloodPressure - (SELECT AVG(BloodPressure) FROM diabetes_patients)) * (BloodPressure - (SELECT AVG(BloodPressure) FROM diabetes_patients))), 2) AS Variance
FROM diabetes_patients

UNION ALL

SELECT 
    'BMI' AS Feature,
    COUNT(BMI) AS N,
    ROUND(AVG(BMI), 2) AS Mean,
    ROUND(MIN(BMI), 2) AS MinValue,
    ROUND(MAX(BMI), 2) AS MaxValue,
    ROUND(AVG((BMI - (SELECT AVG(BMI) FROM diabetes_patients)) * (BMI - (SELECT AVG(BMI) FROM diabetes_patients))), 2) AS Variance
FROM diabetes_patients;


-- -----------------------------------------------------------------------------
-- QUERY 2: Bivariate Health Profile Comparison (Healthy vs Diabetic)
-- Directly feeds Tableau Bar Chart & Bivariate comparison views
-- -----------------------------------------------------------------------------
SELECT 
    CASE Outcome WHEN 1 THEN 'Diabetic' ELSE 'Healthy' END AS DiabeticStatus,
    COUNT(*) AS PatientCount,
    ROUND(AVG(Glucose), 2) AS AvgGlucose_mgdL,
    ROUND(AVG(BloodPressure), 2) AS AvgBloodPressure_mmHg,
    ROUND(AVG(BMI), 2) AS AvgBMI_kgm2,
    ROUND(AVG(Insulin), 2) AS AvgInsulin_uUmL,
    ROUND(AVG(Age), 1) AS AvgAge_Years
FROM diabetes_patients
GROUP BY Outcome;


-- -----------------------------------------------------------------------------
-- QUERY 3: Age Group Binning & Prevalence Rate (Cross-tabulation Query)
-- Feeds Tableau Stacked Density Bar & Cross-Tabulation Visualizations
-- -----------------------------------------------------------------------------
WITH AgeBinned AS (
    SELECT 
        PatientID,
        Outcome,
        CASE 
            WHEN Age BETWEEN 21 AND 30 THEN '1. 21-30'
            WHEN Age BETWEEN 31 AND 40 THEN '2. 31-40'
            WHEN Age BETWEEN 41 AND 50 THEN '3. 41-50'
            ELSE '4. 51+'
        END AS AgeGroup
    FROM diabetes_patients
)
SELECT 
    AgeGroup,
    SUM(CASE WHEN Outcome = 0 THEN 1 ELSE 0 END) AS HealthyCount,
    SUM(CASE WHEN Outcome = 1 THEN 1 ELSE 0 END) AS DiabeticCount,
    COUNT(*) AS TotalPatients,
    ROUND(CAST(SUM(CASE WHEN Outcome = 1 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) AS DiabeticPrevalencePct
FROM AgeBinned
GROUP BY AgeGroup
ORDER BY AgeGroup;


-- -----------------------------------------------------------------------------
-- QUERY 4: Outlier Detection Logic (IQR Method using CTE & Quantile Ranking)
-- Identifies Extreme Outliers in Insulin & Glucose for Clinical Auditing
-- -----------------------------------------------------------------------------
WITH OrderedInsulin AS (
    SELECT 
        Insulin,
        ROW_NUMBER() OVER (ORDER BY Insulin) AS RowNum,
        COUNT(*) OVER () AS TotalCount
    FROM diabetes_patients
),
Quantiles AS (
    SELECT 
        MAX(CASE WHEN RowNum = CAST(0.25 * TotalCount AS INT) THEN Insulin END) AS Q1,
        MAX(CASE WHEN RowNum = CAST(0.75 * TotalCount AS INT) THEN Insulin END) AS Q3
    FROM OrderedInsulin
)
SELECT 
    p.PatientID,
    p.Age,
    p.Insulin,
    q.Q1,
    q.Q3,
    (q.Q3 - q.Q1) AS IQR,
    (q.Q3 + 1.5 * (q.Q3 - q.Q1)) AS UpperFence,
    CASE WHEN p.Insulin > (q.Q3 + 1.5 * (q.Q3 - q.Q1)) THEN 'High Outlier' ELSE 'Normal' END AS OutlierStatus
FROM diabetes_patients p, Quantiles q
WHERE p.Insulin > (q.Q3 + 1.5 * (q.Q3 - q.Q1))
LIMIT 10;


-- -----------------------------------------------------------------------------
-- QUERY 5: Wine Chemical Profile & Alcohol-Quality Bivariate Trend Query
-- Feeds Tableau Dual Trend Line (Red Wine vs White Wine Alcohol Comparison)
-- -----------------------------------------------------------------------------
SELECT 
    Quality,
    ROUND(AVG(CASE WHEN Type = 'Red' THEN Alcohol END), 2) AS RedWine_AvgAlcohol,
    ROUND(AVG(CASE WHEN Type = 'White' THEN Alcohol END), 2) AS WhiteWine_AvgAlcohol,
    ROUND(AVG(CASE WHEN Type = 'Red' THEN VolatileAcidity END), 2) AS RedWine_AvgVolatileAcidity,
    ROUND(AVG(CASE WHEN Type = 'White' THEN VolatileAcidity END), 2) AS WhiteWine_AvgVolatileAcidity,
    COUNT(CASE WHEN Type = 'Red' THEN 1 END) AS RedWine_Count,
    COUNT(CASE WHEN Type = 'White' THEN 1 END) AS WhiteWine_Count
FROM wine_quality
GROUP BY Quality
ORDER BY Quality;


-- -----------------------------------------------------------------------------
-- QUERY 6: Comparative Quality Segment Analysis (Premium >= 7 vs Low <= 4)
-- Oenological Comparison for Wine Quality Diagnostics
-- -----------------------------------------------------------------------------
SELECT 
    Type,
    CASE 
        WHEN Quality >= 7 THEN 'Premium (7-9)'
        WHEN Quality <= 4 THEN 'Low (3-4)'
        ELSE 'Standard (5-6)'
    END AS QualityTier,
    COUNT(*) AS SampleCount,
    ROUND(AVG(Alcohol), 2) AS AvgAlcohol,
    ROUND(AVG(ResidualSugar), 2) AS AvgSugar,
    ROUND(AVG(VolatileAcidity), 3) AS AvgVolatileAcidity,
    ROUND(AVG(pH), 2) AS AvgpH,
    ROUND(AVG(Sulphates), 2) AS AvgSulphates
FROM wine_quality
GROUP BY Type, QualityTier
ORDER BY Type, QualityTier;
