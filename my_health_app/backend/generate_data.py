import pandas as pd
import numpy as np
import os

np.random.seed(42)

NUM_PATIENTS = 16000

# Base Symptoms
BASE_SYMPTOMS = ["fever", "headache", "nausea", "vomiting", "fatigue",
                 "joint_pain", "skin_rash", "cough", "weight_loss", "yellow_eyes"]

# Targeted Indicators
TARGETED_INDICATORS = [
    "chills_cyclical", "night_sweats", "dark_urine", "positional_dizziness",
    "sudden_weakness", "neck_stiffness", "frequent_urination", "shortness_of_breath", "retro_orbital_pain"
]

DISEASES = [
    "Healthy", "Viral Fever", "Dengue", "Typhoid", "Malaria", 
    "Pneumonia", "Diabetes Type 2", "Tuberculosis", "Hepatitis", 
    "Stroke", "Meningitis"
]

def generate_patient(disease):
    # Default everything to 0 or normal
    row = {s: 0 for s in BASE_SYMPTOMS + TARGETED_INDICATORS}
    
    # Normal vitals
    row["Respiratory_Rate"] = int(np.random.normal(16, 2))
    row["Oxygen_Saturation"] = int(np.random.normal(98, 1))
    row["Systolic_BP"] = int(np.random.normal(120, 10))
    row["Heart_Rate"] = int(np.random.normal(75, 10))
    row["Temperature"] = round(np.random.normal(36.8, 0.3), 1)
    row["O2_Scale"] = 1.0
    row["On_Oxygen"] = 0
    row["Consciousness"] = "A"
    
    # Normal labs
    row["ALT_UL"] = round(np.random.normal(25, 5), 1)
    row["WBC_K_uL"] = round(np.random.normal(7.5, 1.5), 1)
    row["TSH_mIUL"] = round(np.random.normal(2.0, 0.5), 1)
    
    risk_level = "Low"

    # Profile logic
    if disease == "Viral Fever":
        row["fever"] = 1
        row["fatigue"] = 1
        row["headache"] = np.random.choice([0, 1], p=[0.3, 0.7])
        row["Temperature"] = round(np.random.uniform(37.5, 38.5), 1)
        row["Heart_Rate"] = int(np.random.normal(90, 5))
        risk_level = "Low"
        
    elif disease == "Dengue":
        row["fever"] = 1
        row["joint_pain"] = 1
        row["headache"] = 1
        row["retro_orbital_pain"] = 1
        row["skin_rash"] = np.random.choice([0, 1], p=[0.4, 0.6])
        row["Temperature"] = round(np.random.uniform(38.5, 40.0), 1)
        row["WBC_K_uL"] = round(np.random.uniform(2.0, 4.0), 1) # Leukopenia
        risk_level = "High"
        
    elif disease == "Typhoid":
        row["fever"] = 1
        row["nausea"] = 1
        row["fatigue"] = 1
        row["headache"] = 1
        row["Temperature"] = round(np.random.uniform(38.0, 39.5), 1)
        row["WBC_K_uL"] = round(np.random.uniform(3.0, 5.0), 1) # Mild leukopenia
        risk_level = "Moderate"

    elif disease == "Malaria":
        row["fever"] = 1
        row["chills_cyclical"] = 1
        row["fatigue"] = 1
        row["vomiting"] = np.random.choice([0, 1], p=[0.5, 0.5])
        row["Temperature"] = round(np.random.uniform(38.5, 40.5), 1)
        row["Heart_Rate"] = int(np.random.normal(105, 10))
        risk_level = "Moderate"

    elif disease == "Pneumonia":
        row["fever"] = 1
        row["cough"] = 1
        row["shortness_of_breath"] = 1
        row["fatigue"] = 1
        row["Respiratory_Rate"] = int(np.random.normal(28, 4))
        row["Oxygen_Saturation"] = int(np.random.normal(88, 4))
        row["Temperature"] = round(np.random.uniform(38.0, 39.5), 1)
        row["WBC_K_uL"] = round(np.random.uniform(12.0, 18.0), 1) # Leukocytosis
        if row["Oxygen_Saturation"] < 90:
            row["On_Oxygen"] = 1
        risk_level = "High"

    elif disease == "Diabetes Type 2":
        row["frequent_urination"] = 1
        row["fatigue"] = 1
        row["weight_loss"] = np.random.choice([0, 1], p=[0.4, 0.6])
        row["Systolic_BP"] = int(np.random.normal(135, 15))
        risk_level = "Moderate"

    elif disease == "Tuberculosis":
        row["cough"] = 1
        row["night_sweats"] = 1
        row["weight_loss"] = 1
        row["fatigue"] = 1
        row["fever"] = np.random.choice([0, 1], p=[0.2, 0.8])
        row["Respiratory_Rate"] = int(np.random.normal(22, 3))
        risk_level = "High"

    elif disease == "Hepatitis":
        row["yellow_eyes"] = 1
        row["dark_urine"] = 1
        row["nausea"] = 1
        row["fatigue"] = 1
        row["fever"] = np.random.choice([0, 1], p=[0.5, 0.5])
        row["ALT_UL"] = round(np.random.uniform(100.0, 500.0), 1) # Highly elevated ALT
        risk_level = "Moderate"

    elif disease == "Stroke":
        row["sudden_weakness"] = 1
        row["headache"] = np.random.choice([0, 1], p=[0.6, 0.4])
        row["positional_dizziness"] = 1
        row["Systolic_BP"] = int(np.random.uniform(160, 220))
        row["Consciousness"] = np.random.choice(["A", "C", "V", "U"], p=[0.2, 0.4, 0.3, 0.1])
        risk_level = "Critical"

    elif disease == "Meningitis":
        row["fever"] = 1
        row["headache"] = 1
        row["neck_stiffness"] = 1
        row["nausea"] = 1
        row["vomiting"] = 1
        row["Temperature"] = round(np.random.uniform(39.0, 40.5), 1)
        row["WBC_K_uL"] = round(np.random.uniform(15.0, 25.0), 1)
        row["Consciousness"] = np.random.choice(["C", "V", "P"], p=[0.5, 0.3, 0.2])
        risk_level = "Critical"
        
    row["disease"] = disease
    row["Risk_Level"] = risk_level
    
    # Clip constraints
    row["Oxygen_Saturation"] = min(100, max(60, row["Oxygen_Saturation"]))
    row["Respiratory_Rate"] = min(50, max(8, row["Respiratory_Rate"]))
    row["Heart_Rate"] = min(200, max(40, row["Heart_Rate"]))
    
    return row

print(f"Generating {NUM_PATIENTS} highly authentic patient records...")

data = []
# Create a roughly even distribution, maybe slightly more healthy/viral fever
probabilities = [0.15, 0.15, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05]
sampled_diseases = np.random.choice(DISEASES, size=NUM_PATIENTS, p=probabilities)

for d in sampled_diseases:
    data.append(generate_patient(d))

df = pd.DataFrame(data)

# Save to the root directory where init_model.py expects it initially,
# Wait, model_code uses absolute path to its own directory, which is my_health_app.
output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "professional_dataset_16k.csv")
df.to_csv(output_path, index=False)
print(f"Dataset successfully saved to: {output_path}")
