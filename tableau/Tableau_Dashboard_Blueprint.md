# Tableau Dashboard Specification & Implementation Blueprint

## Overview
This document provides complete, step-by-step technical specifications to build a **Tableau Desktop / Tableau Public Workbook** for the **UEH Advanced Data Analytics & EDA System (Lab 01)**.

---

## 1. Data Source Connection Setup

1. Open Tableau Desktop / Tableau Public.
2. Under **Connect to a Server / To a File**:
   - Select **SQLite** or **Text File**.
   - Point to `data/ueh_lab01.db` or `data/diabetes_clean.csv` and `data/wine_quality_clean.csv`.
3. Set up Data Connection:
   - For **Diabetes Dashboard**: Drag `diabetes_patients` table onto the logical canvas.
   - For **Wine Quality Dashboard**: Drag `wine_quality` table onto the logical canvas.
   - Ensure data types are detected correctly:
     - `Outcome`: Change from Numeric to **Dimension** (Categorical: `0 = Healthy`, `1 = Diabetic`).
     - `Quality`: Integer Dimension (Values 3 through 9).
     - `Type`: String Dimension ('Red', 'White').

---

## 2. Calculated Fields & LOD Expressions Syntax

Create the following **Calculated Fields** in Tableau:

### A. Diabetes Module Calculated Fields

1. **`[Diabetic Status]`** (String Dimension)
   ```tableau
   IF [Outcome] = 1 THEN "Diabetic"
   ELSE "Healthy"
   END
   ```

2. **`[Age Group]`** (Dimension)
   ```tableau
   IF [Age] <= 30 THEN "21-30"
   ELSEIF [Age] <= 40 THEN "31-40"
   ELSEIF [Age] <= 50 THEN "41-50"
   ELSE "51+"
   END
   ```

3. **`[Glucose Median (LOD)]`** (Measure - Level of Detail)
   ```tableau
   { FIXED [Diabetic Status] : MEDIAN([Glucose]) }
   ```

4. **`[Insulin IQR]`** (Measure - Level of Detail)
   ```tableau
   { FIXED : PERCENTILE([Insulin], 0.75) } - { FIXED : PERCENTILE([Insulin], 0.25) }
   ```

5. **`[Insulin Outlier Flag]`** (Dimension)
   ```tableau
   IF [Insulin] > ({ FIXED : PERCENTILE([Insulin], 0.75) } + 1.5 * [Insulin IQR]) THEN "High Outlier"
   ELSE "Normal"
   END
   ```

### B. Wine Quality Module Calculated Fields

1. **`[Quality Tier]`** (Dimension)
   ```tableau
   IF [Quality] >= 7 THEN "Premium (7-9)"
   ELSEIF [Quality] <= 4 THEN "Low (3-4)"
   ELSE "Standard (5-6)"
   END
   ```

2. **`[Alcohol Level LOD]`** (Measure)
   ```tableau
   { FIXED [Type], [Quality] : AVG([Alcohol]) }
   ```

---

## 3. Worksheet Construction Guide (6 Core Views)

### Sheet 1: Diabetes KPI Summary Cards
- **Mark Type**: Text / Metric Cards.
- **Measures**: `COUNTD([PatientID])`, `SUM([Outcome]) / COUNT([PatientID])` (Formatted as %), `AVG([Glucose])`, `AVG([BMI])`.
- **Formatting**: Dark background `#0F172A`, bold colored KPI numbers (`#38BDF8` Total Patients, `#F43F5E` Prevalence Rate, `#F59E0B` Avg Glucose, `#10B981` Avg BMI).

### Sheet 2: Univariate Glucose Distribution (Histogram)
- **Rows**: `COUNT([PatientID])`
- **Columns**: `Glucose (bin)` (Bin size = 15 mg/dL)
- **Color**: Gradient Blue `#3B82F6` with opacity 80%.
- **Annotation**: Add reference line for Median Glucose (`117 mg/dL`).

### Sheet 3: Bivariate Health Profile Comparison (Grouped Bar Chart)
- **Rows**: `AVG([Value])` (Measure Values: Glucose, Blood Pressure, BMI, Insulin)
- **Columns**: `Measure Names`
- **Color**: `[Diabetic Status]` (`Healthy = #10B981` Emerald, `Diabetic = #F43F5E` Rose).

### Sheet 4: Age Group Prevalence (Stacked Bar Chart)
- **Rows**: `COUNT([PatientID])`
- **Columns**: `[Age Group]`
- **Color**: `[Diabetic Status]` (`Healthy = #3B82F6` Blue, `Diabetic = #F59E0B` Amber).

### Sheet 5: Wine Alcohol vs Quality Score Trend (Dual Line Chart)
- **Rows**: `AVG([Alcohol])`
- **Columns**: `[Quality]`
- **Color**: `[Type]` (`Red = #F43F5E` Rose, `White = #F59E0B` Amber).
- **Line Style**: Monotone curve with circle data points enabled.

### Sheet 6: Full Descriptive Statistical Matrix Table
- **Rows**: `Measure Names` (Fixed Acidity, Volatile Acidity, Citric Acid, Residual Sugar, Chlorides, Free SO2, Total SO2, Density, pH, Sulphates, Alcohol)
- **Columns**: `Measure Values` (Mean, Median, Std Dev, Min, 25th Percentile, 75th Percentile, Max)
- **Filter**: `[Type]` Quick Filter (Red Wine vs White Wine).

---

## 4. Interactive Dashboard Layout & Design Tokens

### Color System Tokens
- **Canvas Background**: `#090D16` (Ultra Dark Slate)
- **Card Background**: `#0F172A` / `#1E293B`
- **Primary Text**: `#F8FAFC`
- **Accent Emerald**: `#10B981`
- **Accent Rose**: `#F43F5E`
- **Accent Amber**: `#F59E0B`
- **Accent Purple**: `#A855F7`

### Dashboard Action Filters & Interactivity
1. **Filter Action on Age Group**: Clicking an Age Group bar in Sheet 4 filters Sheets 1, 2, and 3 instantly.
2. **Filter Action on Wine Type**: Toggle between Red and White Wine updates the statistical matrix and trend lines dynamically.
3. **Hover Tooltip Setup**: Tooltips formatted with clean typography, displaying Sample Size, Median, Mean, and IQR.
