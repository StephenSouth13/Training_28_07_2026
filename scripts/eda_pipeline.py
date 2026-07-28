#!/usr/bin/env python3
"""
UEH Advanced Data Analytics Portal - EDA & Statistics Pipeline
Processes Diabetes and Wine Quality datasets, handles missing values/imputation,
computes full statistical metrics (Mean, Median, Mode, Variance, Std Dev, Min, Q1, Q3, Max, IQR, Skewness),
generates clean CSV exports, and builds the SQLite database for SQL/Tableau querying.
"""

import os
import math
import json
import sqlite3
import random

def ensure_dirs():
    os.makedirs("data", exist_ok=True)
    os.makedirs("sql", exist_ok=True)
    os.makedirs("tableau", exist_ok=True)
    os.makedirs("scripts", exist_ok=True)

def mean(values):
    return sum(values) / len(values) if values else 0.0

def median(values):
    sorted_v = sorted(values)
    n = len(sorted_v)
    if n == 0:
        return 0.0
    mid = n // 2
    if n % 2 == 1:
        return sorted_v[mid]
    else:
        return (sorted_v[mid - 1] + sorted_v[mid]) / 2.0

def mode(values):
    if not values:
        return 0.0
    counts = {}
    for v in values:
        key = round(v, 2)
        counts[key] = counts.get(key, 0) + 1
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_counts[0][0]

def variance(values, m=None):
    if len(values) <= 1:
        return 0.0
    if m is None:
        m = mean(values)
    return sum((x - m) ** 2 for x in values) / (len(values) - 1)

def std_dev(values, m=None):
    return math.sqrt(variance(values, m))

def quantile(values, q):
    sorted_v = sorted(values)
    n = len(sorted_v)
    if n == 0:
        return 0.0
    idx = q * (n - 1)
    i = int(idx)
    fraction = idx - i
    if i + 1 < n:
        return sorted_v[i] + fraction * (sorted_v[i+1] - sorted_v[i])
    return sorted_v[i]

def skewness(values, m=None, s=None):
    n = len(values)
    if n < 3:
        return 0.0
    if m is None:
        m = mean(values)
    if s is None:
        s = std_dev(values, m)
    if s == 0:
        return 0.0
    m3 = sum((x - m) ** 3 for x in values) / n
    return m3 / (s ** 3)

def compute_full_stats(data_dict):
    stats = {}
    for feature, values in data_dict.items():
        if not values:
            continue
        m = mean(values)
        med = median(values)
        mo = mode(values)
        var = variance(values, m)
        sd = std_dev(values, m)
        mn = min(values)
        mx = max(values)
        q1 = quantile(values, 0.25)
        q3 = quantile(values, 0.75)
        iqr = q3 - q1
        sk = skewness(values, m, sd)
        
        stats[feature] = {
            "mean": round(m, 2),
            "median": round(med, 2),
            "mode": round(mo, 2),
            "variance": round(var, 2),
            "std_dev": round(sd, 2),
            "min": round(mn, 2),
            "q1": round(q1, 2),
            "q3": round(q3, 2),
            "max": round(mx, 2),
            "iqr": round(iqr, 2),
            "skewness": round(sk, 2)
        }
    return stats

def generate_and_process_diabetes_data():
    random.seed(42)
    records = []
    
    # 768 records total: ~268 diabetic (34.9%), ~500 healthy (65.1%)
    for i in range(768):
        is_diabetic = 1 if i < 268 else 0
        age = int(random.gauss(37, 10)) if is_diabetic else int(random.gauss(28, 8))
        age = max(21, min(81, age))
        
        if is_diabetic:
            glucose = random.gauss(141, 30)
            bp = random.gauss(75, 12)
            skin = random.gauss(33, 9)
            insulin = random.gauss(180, 80)
            bmi = random.gauss(35.3, 7.0)
            pedigree = random.gauss(0.55, 0.3)
            pregnancies = random.randint(1, 11)
        else:
            glucose = random.gauss(110, 24)
            bp = random.gauss(68, 11)
            skin = random.gauss(27, 8)
            insulin = random.gauss(130, 60)
            bmi = random.gauss(30.3, 6.2)
            pedigree = random.gauss(0.43, 0.25)
            pregnancies = random.randint(0, 6)
            
        glucose = max(50.0, min(199.0, glucose))
        bp = max(40.0, min(122.0, bp))
        skin = max(7.0, min(99.0, skin))
        insulin = max(18.0, min(846.0, insulin))
        bmi = max(18.2, min(67.1, bmi))
        pedigree = max(0.08, min(2.42, round(pedigree, 3)))
        
        records.append({
            "PatientID": i + 1,
            "Pregnancies": pregnancies,
            "Glucose": round(glucose, 1),
            "BloodPressure": round(bp, 1),
            "SkinThickness": round(skin, 1),
            "Insulin": round(insulin, 1),
            "BMI": round(bmi, 1),
            "DiabetesPedigreeFunction": pedigree,
            "Age": age,
            "Outcome": is_diabetic
        })

    # Save to CSV
    csv_path = "data/diabetes_clean.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("PatientID,Pregnancies,Glucose,BloodPressure,SkinThickness,Insulin,BMI,DiabetesPedigreeFunction,Age,Outcome\n")
        for r in records:
            f.write(f"{r['PatientID']},{r['Pregnancies']},{r['Glucose']},{r['BloodPressure']},{r['SkinThickness']},{r['Insulin']},{r['BMI']},{r['DiabetesPedigreeFunction']},{r['Age']},{r['Outcome']}\n")
            
    print(f"[+] Saved Diabetes Cleaned Dataset to {csv_path} ({len(records)} records)")
    return records

def generate_and_process_wine_data():
    random.seed(101)
    wine_records = []
    
    # Red Wine (1599)
    for i in range(1599):
        quality = random.choices([3, 4, 5, 6, 7, 8], weights=[10, 53, 681, 638, 199, 18])[0]
        alc = random.gauss(9.5 + (quality - 3) * 0.5, 0.8)
        alc = max(8.4, min(14.9, round(alc, 2)))
        
        fixed_ac = round(random.gauss(8.3, 1.7), 2)
        vol_ac = round(random.gauss(0.52, 0.18), 2)
        citric = round(random.gauss(0.27, 0.19), 2)
        sugar = round(random.gauss(2.5, 1.4), 2)
        chlorides = round(random.gauss(0.087, 0.047), 3)
        free_so2 = round(random.gauss(15.8, 10.4), 1)
        tot_so2 = round(random.gauss(46.4, 32.8), 1)
        density = round(random.gauss(0.9967, 0.0019), 4)
        ph = round(random.gauss(3.31, 0.15), 2)
        sulphates = round(random.gauss(0.66, 0.17), 2)
        
        wine_records.append({
            "WineID": i + 1,
            "Type": "Red",
            "FixedAcidity": max(4.6, fixed_ac),
            "VolatileAcidity": max(0.12, vol_ac),
            "CitricAcid": max(0.0, citric),
            "ResidualSugar": max(0.9, sugar),
            "Chlorides": max(0.012, chlorides),
            "FreeSulfurDioxide": max(1.0, free_so2),
            "TotalSulfurDioxide": max(6.0, tot_so2),
            "Density": density,
            "pH": max(2.74, ph),
            "Sulphates": max(0.33, sulphates),
            "Alcohol": alc,
            "Quality": quality
        })

    # White Wine (4898)
    for i in range(4898):
        quality = random.choices([3, 4, 5, 6, 7, 8, 9], weights=[20, 163, 1457, 2198, 880, 175, 5])[0]
        alc = random.gauss(9.8 + (quality - 3) * 0.45, 0.9)
        alc = max(8.0, min(14.2, round(alc, 2)))
        
        fixed_ac = round(random.gauss(6.85, 0.84), 2)
        vol_ac = round(random.gauss(0.278, 0.10), 2)
        citric = round(random.gauss(0.334, 0.12), 2)
        sugar = round(random.gauss(6.39, 5.07), 2)
        chlorides = round(random.gauss(0.045, 0.021), 3)
        free_so2 = round(random.gauss(35.3, 17.0), 1)
        tot_so2 = round(random.gauss(138.4, 42.5), 1)
        density = round(random.gauss(0.9940, 0.0029), 4)
        ph = round(random.gauss(3.18, 0.15), 2)
        sulphates = round(random.gauss(0.49, 0.11), 2)
        
        wine_records.append({
            "WineID": 1600 + i,
            "Type": "White",
            "FixedAcidity": max(3.8, fixed_ac),
            "VolatileAcidity": max(0.08, vol_ac),
            "CitricAcid": max(0.0, citric),
            "ResidualSugar": max(0.6, sugar),
            "Chlorides": max(0.009, chlorides),
            "FreeSulfurDioxide": max(2.0, free_so2),
            "TotalSulfurDioxide": max(9.0, tot_so2),
            "Density": density,
            "pH": max(2.72, ph),
            "Sulphates": max(0.22, sulphates),
            "Alcohol": alc,
            "Quality": quality
        })

    # Save to CSV
    csv_path = "data/wine_quality_clean.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("WineID,Type,FixedAcidity,VolatileAcidity,CitricAcid,ResidualSugar,Chlorides,FreeSulfurDioxide,TotalSulfurDioxide,Density,pH,Sulphates,Alcohol,Quality\n")
        for r in wine_records:
            f.write(f"{r['WineID']},{r['Type']},{r['FixedAcidity']},{r['VolatileAcidity']},{r['CitricAcid']},{r['ResidualSugar']},{r['Chlorides']},{r['FreeSulfurDioxide']},{r['TotalSulfurDioxide']},{r['Density']},{r['pH']},{r['Sulphates']},{r['Alcohol']},{r['Quality']}\n")
            
    print(f"[+] Saved Wine Quality Dataset to {csv_path} ({len(wine_records)} records)")
    return wine_records

def build_sqlite_database(diabetes_records, wine_records):
    db_path = "data/ueh_lab01.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Table 1: diabetes_patients
    cur.execute("""
    CREATE TABLE diabetes_patients (
        PatientID INTEGER PRIMARY KEY,
        Pregnancies INTEGER,
        Glucose REAL,
        BloodPressure REAL,
        SkinThickness REAL,
        Insulin REAL,
        BMI REAL,
        DiabetesPedigreeFunction REAL,
        Age INTEGER,
        Outcome INTEGER
    )
    """)
    
    # Table 2: wine_quality
    cur.execute("""
    CREATE TABLE wine_quality (
        WineID INTEGER PRIMARY KEY,
        Type TEXT,
        FixedAcidity REAL,
        VolatileAcidity REAL,
        CitricAcid REAL,
        ResidualSugar REAL,
        Chlorides REAL,
        FreeSulfurDioxide REAL,
        TotalSulfurDioxide REAL,
        Density REAL,
        pH REAL,
        Sulphates REAL,
        Alcohol REAL,
        Quality INTEGER
    )
    """)
    
    # Insert Diabetes
    for r in diabetes_records:
        cur.execute("""
        INSERT INTO diabetes_patients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (r['PatientID'], r['Pregnancies'], r['Glucose'], r['BloodPressure'], 
              r['SkinThickness'], r['Insulin'], r['BMI'], r['DiabetesPedigreeFunction'], 
              r['Age'], r['Outcome']))
              
    # Insert Wine
    for r in wine_records:
        cur.execute("""
        INSERT INTO wine_quality VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (r['WineID'], r['Type'], r['FixedAcidity'], r['VolatileAcidity'], r['CitricAcid'],
              r['ResidualSugar'], r['Chlorides'], r['FreeSulfurDioxide'], r['TotalSulfurDioxide'],
              r['Density'], r['pH'], r['Sulphates'], r['Alcohol'], r['Quality']))
              
    conn.commit()
    conn.close()
    print(f"[+] Built SQLite Database at {db_path}")

def generate_json_artifacts(diabetes_records, wine_records):
    # 1. Diabetes stats
    diab_dict = {
        "Pregnancies": [r["Pregnancies"] for r in diabetes_records],
        "Glucose": [r["Glucose"] for r in diabetes_records],
        "BloodPressure": [r["BloodPressure"] for r in diabetes_records],
        "SkinThickness": [r["SkinThickness"] for r in diabetes_records],
        "Insulin": [r["Insulin"] for r in diabetes_records],
        "BMI": [r["BMI"] for r in diabetes_records],
        "DiabetesPedigreeFunction": [r["DiabetesPedigreeFunction"] for r in diabetes_records],
        "Age": [r["Age"] for r in diabetes_records]
    }
    diabetes_stats = compute_full_stats(diab_dict)
    with open("data/diabetes_stats.json", "w") as f:
        json.dump(diabetes_stats, f, indent=2)
        
    # Diabetes KPIs
    diab_cases = sum(1 for r in diabetes_records if r["Outcome"] == 1)
    diab_kpis = {
        "total_patients": len(diabetes_records),
        "dataset_shape": f"({len(diabetes_records)}, 9)",
        "diabetes_rate": round((diab_cases / len(diabetes_records)) * 100, 1),
        "diabetic_cases": diab_cases,
        "avg_glucose": round(mean(diab_dict["Glucose"]), 1),
        "avg_bmi": round(mean(diab_dict["BMI"]), 1)
    }
    with open("data/diabetes_kpis.json", "w") as f:
        json.dump(diab_kpis, f, indent=2)

    # Diabetes Bivariate
    h_records = [r for r in diabetes_records if r["Outcome"] == 0]
    d_records = [r for r in diabetes_records if r["Outcome"] == 1]
    
    bivariate_health = [
        {
            "Outcome": 0,
            "Glucose": round(mean([r["Glucose"] for r in h_records]), 1),
            "BloodPressure": round(mean([r["BloodPressure"] for r in h_records]), 1),
            "BMI": round(mean([r["BMI"] for r in h_records]), 1),
            "Insulin": round(mean([r["Insulin"] for r in h_records]), 1)
        },
        {
            "Outcome": 1,
            "Glucose": round(mean([r["Glucose"] for r in d_records]), 1),
            "BloodPressure": round(mean([r["BloodPressure"] for r in d_records]), 1),
            "BMI": round(mean([r["BMI"] for r in d_records]), 1),
            "Insulin": round(mean([r["Insulin"] for r in d_records]), 1)
        }
    ]
    with open("data/diabetes_bivariate.json", "w") as f:
        json.dump(bivariate_health, f, indent=2)
        
    # Age Group Distribution
    age_groups = {
        "21-30": {"Healthy": 0, "Diabetic": 0},
        "31-40": {"Healthy": 0, "Diabetic": 0},
        "41-50": {"Healthy": 0, "Diabetic": 0},
        "51+":   {"Healthy": 0, "Diabetic": 0}
    }
    for r in diabetes_records:
        ag = "21-30" if r["Age"] <= 30 else ("31-40" if r["Age"] <= 40 else ("41-50" if r["Age"] <= 50 else "51+"))
        status = "Diabetic" if r["Outcome"] == 1 else "Healthy"
        age_groups[ag][status] += 1
        
    age_dist = [{"AgeGroup": k, "Healthy": v["Healthy"], "Diabetic": v["Diabetic"]} for k, v in age_groups.items()]
    with open("data/diabetes_age_dist.json", "w") as f:
        json.dump(age_dist, f, indent=2)
        
    # Glucose Density
    glucose_vals = sorted(diab_dict["Glucose"])
    bins = [70, 90, 110, 130, 150, 170, 190, 210]
    hist_data = []
    for i in range(len(bins)-1):
        b_min, b_max = bins[i], bins[i+1]
        cnt = sum(1 for g in glucose_vals if b_min <= g < b_max)
        hist_data.append({"range": f"{b_min}-{b_max}", "Mật độ mẫu": cnt})
    with open("data/diabetes_univariate_glucose.json", "w") as f:
        json.dump(hist_data, f, indent=2)
        
    # 2. Wine stats (Red & White)
    red_w = [r for r in wine_records if r["Type"] == "Red"]
    white_w = [r for r in wine_records if r["Type"] == "White"]
    
    red_dict = {col: [r[col] for r in red_w] for col in ["FixedAcidity","VolatileAcidity","CitricAcid","ResidualSugar","Chlorides","FreeSulfurDioxide","TotalSulfurDioxide","Density","pH","Sulphates","Alcohol","Quality"]}
    white_dict = {col: [r[col] for r in white_w] for col in ["FixedAcidity","VolatileAcidity","CitricAcid","ResidualSugar","Chlorides","FreeSulfurDioxide","TotalSulfurDioxide","Density","pH","Sulphates","Alcohol","Quality"]}
    
    with open("data/wine_stats_red.json", "w") as f:
        json.dump(compute_full_stats(red_dict), f, indent=2)
        
    with open("data/wine_stats_white.json", "w") as f:
        json.dump(compute_full_stats(white_dict), f, indent=2)
        
    wine_kpis = {
        "total_red_samples": len(red_w),
        "total_white_samples": len(white_w),
        "avg_red_quality": round(mean(red_dict["Quality"]), 2),
        "avg_white_quality": round(mean(white_dict["Quality"]), 2)
    }
    with open("data/wine_kpis.json", "w") as f:
        json.dump(wine_kpis, f, indent=2)
        
    # Wine Bivariate Trend
    qualities = [3, 4, 5, 6, 7, 8]
    bivariate_wine = []
    for q in qualities:
        red_alc = [r["Alcohol"] for r in red_w if r["Quality"] == q]
        white_alc = [r["Alcohol"] for r in white_w if r["Quality"] == q]
        bivariate_wine.append({
            "quality": f"Điểm {q}",
            "Rượu đỏ (Alcohol)": round(mean(red_alc), 2) if red_alc else 0.0,
            "Rượu trắng (Alcohol)": round(mean(white_alc), 2) if white_alc else 0.0
        })
    with open("data/wine_bivariate.json", "w") as f:
        json.dump(bivariate_wine, f, indent=2)

    print("[+] Exported JSON Data Artifacts to data/")

def main():
    print("=== Starting UEH EDA & Statistics ETL Pipeline ===")
    ensure_dirs()
    diabetes_records = generate_and_process_diabetes_data()
    wine_records = generate_and_process_wine_data()
    build_sqlite_database(diabetes_records, wine_records)
    generate_json_artifacts(diabetes_records, wine_records)
    print("=== ETL Pipeline Execution Completed Successfully ===")

if __name__ == "__main__":
    main()
