-- =============================================================================
-- UEH Advanced Data Analytics Portal - Database Schema Definitions (DDL)
-- Compatible with SQLite, PostgreSQL, DuckDB, MySQL, and BigQuery
-- =============================================================================

-- Drop tables if they exist
DROP TABLE IF EXISTS diabetes_patients;
DROP TABLE IF EXISTS wine_quality;

-- 1. Diabetes Patients Table Schema
CREATE TABLE diabetes_patients (
    PatientID INTEGER PRIMARY KEY,
    Pregnancies INTEGER NOT NULL DEFAULT 0,
    Glucose REAL NOT NULL,
    BloodPressure REAL NOT NULL,
    SkinThickness REAL NOT NULL,
    Insulin REAL NOT NULL,
    BMI REAL NOT NULL,
    DiabetesPedigreeFunction REAL NOT NULL,
    Age INTEGER NOT NULL,
    Outcome INTEGER NOT NULL CHECK (Outcome IN (0, 1))
);

-- Indexes for Diabetes Analytical Queries
CREATE INDEX idx_diabetes_outcome ON diabetes_patients(Outcome);
CREATE INDEX idx_diabetes_age ON diabetes_patients(Age);
CREATE INDEX idx_diabetes_glucose ON diabetes_patients(Glucose);
CREATE INDEX idx_diabetes_bmi ON diabetes_patients(BMI);

-- 2. Wine Quality Table Schema
CREATE TABLE wine_quality (
    WineID INTEGER PRIMARY KEY,
    Type TEXT NOT NULL CHECK (Type IN ('Red', 'White')),
    FixedAcidity REAL NOT NULL,
    VolatileAcidity REAL NOT NULL,
    CitricAcid REAL NOT NULL,
    ResidualSugar REAL NOT NULL,
    Chlorides REAL NOT NULL,
    FreeSulfurDioxide REAL NOT NULL,
    TotalSulfurDioxide REAL NOT NULL,
    Density REAL NOT NULL,
    pH REAL NOT NULL,
    Sulphates REAL NOT NULL,
    Alcohol REAL NOT NULL,
    Quality INTEGER NOT NULL CHECK (Quality BETWEEN 1 AND 10)
);

-- Indexes for Wine Quality Analytical Queries
CREATE INDEX idx_wine_type ON wine_quality(Type);
CREATE INDEX idx_wine_quality ON wine_quality(Quality);
CREATE INDEX idx_wine_type_quality ON wine_quality(Type, Quality);
CREATE INDEX idx_wine_alcohol ON wine_quality(Alcohol);

-- View: Diabetes Health Risk Summary
CREATE VIEW vw_diabetes_risk_summary AS
SELECT 
    CASE 
        WHEN Age <= 30 THEN '21-30'
        WHEN Age <= 40 THEN '31-40'
        WHEN Age <= 50 THEN '41-50'
        ELSE '51+'
    END AS AgeGroup,
    COUNT(*) AS TotalPatients,
    SUM(CASE WHEN Outcome = 1 THEN 1 ELSE 0 END) AS DiabeticCases,
    SUM(CASE WHEN Outcome = 0 THEN 1 ELSE 0 END) AS HealthyCases,
    ROUND(AVG(Glucose), 2) AS AvgGlucose,
    ROUND(AVG(BMI), 2) AS AvgBMI,
    ROUND(CAST(SUM(CASE WHEN Outcome = 1 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) AS PrevalenceRatePct
FROM diabetes_patients
GROUP BY AgeGroup;

-- View: Wine Quality Chemical Profile
CREATE VIEW vw_wine_chemical_profile AS
SELECT 
    Type,
    Quality,
    COUNT(*) AS SampleCount,
    ROUND(AVG(Alcohol), 2) AS AvgAlcohol,
    ROUND(AVG(VolatileAcidity), 2) AS AvgVolatileAcidity,
    ROUND(AVG(ResidualSugar), 2) AS AvgResidualSugar,
    ROUND(AVG(pH), 2) AS AvgPH,
    ROUND(AVG(Density), 4) AS AvgDensity
FROM wine_quality
GROUP BY Type, Quality;
