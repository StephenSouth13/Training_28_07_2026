# Red Wine Quality Case Study - My Practice File
# Write your Python code here from scratch!

#Step 2: Loading & Filtering Red Wine Data
import csv
import math
import os

#1. Get path to the CSV file 
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "..", "data", "wine_quality_clean.csv")

#2. List to store red wine rows
red_wines = []

#3. Open and read CSV file 
with open(data_path, "r", encoding = "utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Type'] == 'Red':
            red_wines.append(row)

#4. Print how many red wine rows were loaded
print("Total Red Wine bottles loaded:", len(red_wines))

#Step 3: Calculating Mean & Median for Alcohol (%)
#5. Extract all alcohol numbers as floats
alcohol_list = [float(row['Alcohol']) for row in red_wines]

#6. Calculate Mean Alcohol
mean_alcohol = sum(alcohol_list) / len(alcohol_list)

#7. Calculate Median Alcohol
sorted_alcohol = sorted(alcohol_list)
n = len(sorted_alcohol)
mid_index = n // 2
median_alcohol = sorted_alcohol[mid_index]


#8. Print Mean and Median  
print(f"Mean Alcohol: {mean_alcohol:.2f}%")
print(f"Median Alcohol: {median_alcohol:.2f}%")



#STEP 4: Spread & Dispersion (Min, Max,IQR, Std Dev)
#9. Min, Max, and Range
min_alcohol = min(alcohol_list)
max_alcohol = max(alcohol_list)
range_alcohol = max_alcohol - min_alcohol

#10. Q1 (25%), Q3 (75%), and IQR
q1_alcohol = sorted_alcohol[int(0.25 * n)]
q3_alcohol = sorted_alcohol[int(0.75 * n)]
iqr_alcohol = q3_alcohol - q1_alcohol


#11. Standard Deviation
variance = sum((x - mean_alcohol) ** 2 for x in alcohol_list) / (n-1)
std_dev_alcohol = math.sqrt(variance)

#12. Print Dispersion Metrics 
print(f"Min Alcohol: {min_alcohol:.2f}%")
print(f"Max Alcohol: {max_alcohol:.2f}%")
print(f"Range: {range_alcohol:.2f}%")
print(f"Q1 (25%): {q1_alcohol:.2f}%")
print(f"Q3 (75%): {q3_alcohol:.2f}%")
print(f"IQR: {iqr_alcohol:.2f}%")
print(f"Std Deviation: {std_dev_alcohol:.2f}")

#13. Bivariate Analysis: Group by Quality Score
print("\n--- BIVARIATE ANALYSIS: ALCOHOL & VOLATILE ACIDITY BY QUALITY ---")
print(f"{'Quality':<10}{'Bottle Count':<15}{'Avg Alcohol(%)':<20}{'Avg Volatile Acidity':<22}")
print("-" * 67)

for q in [3, 4, 5, 6, 7, 8]:
    #Filter rows matching this quality score
    q_rows = [r for r in red_wines if int(r['Quality']) == q]
    if q_rows:
        count = len(q_rows)
        avg_alc = sum(float(r['Alcohol']) for r in q_rows) / count
        avg_ac = sum(float(r['VolatileAcidity']) for r in q_rows) / count
        print(f"{q:<10}{count:<15}{avg_alc:<20.2f}{avg_ac:<22.2f}")

#14. Print Executive Case Study Summary
print("\n=======================================================================================")
print("RED WINE CASE STUDY: EXECUTIVE SUMMARY REPORT")
print("=========================================================================================")
print("1. Distribution: 82% of red wine are rated average (Score 5 - 6).")
print(" Outstanding wines (Score 8) represent under 1% of samples.")
print("\n2. Alcohol is the #1 Positive Quality Driver:")
print(f" Premium Wines (Score 8) average: 11.94% Alcohol")
print(f" Low Quality Wines (Score 3) average: 9.26% Alcohol")
print(f" Key Advice: Higher natural alcohol correlates strongly with better ratings")
print("\n3. Overall Quality Range & Spread:")
print(f" Mean Alcohol: {mean_alcohol:.2f}% | Median: {median_alcohol:.2f}%")
print(f" Alcohol IQR (Middle 50%): {iqr_alcohol:.2f}%")
print("==========================================================================================")

#15. Export Summary Result to CSV for Tableuau Dashboard
output_csv = os.path.join(script_dir, "my_red_wine_summary.csv")

with open(output_csv, "w", newline= "", encoding = "utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["QualityScore", "BottleCount", "AvgAlcohol", "AvgVolatileAcidity"])

    for q in [3, 4, 5, 6, 7, 8]:
        q_rows = [r for r in red_wines if int(r['Quality']) == q]
        if q_rows:
            count = len(q_rows)
            avg_alc = round(sum(float(r['Alcohol']) for r in q_rows) / count, 2)
            avg_ac = round(sum(float(r['VolatileAcidity']) for r in q_rows) / count, 2)
            writer.writerow([q, count, avg_alc, avg_ac])

print(f"\n Success! Exported file for Tableau to: my_practice/my_red_wine_summary.csv")