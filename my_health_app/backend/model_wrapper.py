import os
import joblib
import pandas as pd
import numpy as np

# Feature sets directly from the original model to prevent importing model_code 
# and triggering training loop on startup.
ORIGINAL_SYMPTOMS = [
    "fever", "headache", "nausea", "vomiting", "fatigue",
    "joint_pain", "skin_rash", "cough", "weight_loss", "yellow_eyes",
]
TARGETED_INDICATORS = [
    "chills_cyclical", "night_sweats", "dark_urine", 
    "positional_dizziness", "sudden_weakness", "neck_stiffness",
    "frequent_urination", "shortness_of_breath", "retro_orbital_pain"
]
VITALS = [
    "Respiratory_Rate", "Oxygen_Saturation", "O2_Scale",
    "Systolic_BP", "Heart_Rate", "Temperature",
    "On_Oxygen", "Consciousness_enc",
]
LAB_TESTS = [
    "ALT_UL", "ALT_log",
    "WBC_K_uL", "WBC_high", "WBC_low",
    "TSH_mIUL", "TSH_flag",
]
ENGINEERED = [
    "Shock_Index", "SpO2_HR_ratio", "Temp_deviation",
    "Hypoxia_flag", "Tachycardia_flag", "Fever_flag", "Hypotensive_flag",
    "Severity_Score", "Symptom_Count",
]

ALL_FEATURES = ORIGINAL_SYMPTOMS + TARGETED_INDICATORS + VITALS + LAB_TESTS + ENGINEERED
CONSCIOUSNESS_MAP = {"A": 0, "C": 1, "V": 2, "P": 3, "U": 4}

class HealthModelWrapper:
    def __init__(self, models_dir="models"):
        self.models_dir = models_dir
        self.disease_model = None
        self.risk_model = None
        self.scaler = None
        self.le_disease = None
        self.le_risk = None
        self.config = None
        self.is_loaded = False

    def load_models(self):
        """Loads the pre-trained joblib files."""
        if self.is_loaded:
            return True
            
        try:
            self.disease_model = joblib.load(os.path.join(self.models_dir, "disease_model.pkl"))
            self.risk_model    = joblib.load(os.path.join(self.models_dir, "risk_model.pkl"))
            self.scaler        = joblib.load(os.path.join(self.models_dir, "scaler.pkl"))
            self.le_disease    = joblib.load(os.path.join(self.models_dir, "le_disease.pkl"))
            self.le_risk       = joblib.load(os.path.join(self.models_dir, "le_risk.pkl"))
            self.config        = joblib.load(os.path.join(self.models_dir, "config.pkl"))
            self.is_loaded = True
            return True
        except FileNotFoundError:
            print("[ERROR] Model files not found. Did you run init_model.py first?")
            return False

    def predict(self, symptoms: dict, vitals: dict, labs: dict = None) -> dict:
        """
        Replicates the predict function from model_code.py.
        """
        if not self.is_loaded:
            if not self.load_models():
                raise RuntimeError("Models are not loaded and could not be found.")

        vitals_provided = any(k in vitals for k in ["Heart_Rate", "Systolic_BP", "Respiratory_Rate", "Oxygen_Saturation", "Temperature"])

        SYMPTOM_COLS = ORIGINAL_SYMPTOMS + TARGETED_INDICATORS
        row = {s: symptoms.get(s, 0) for s in SYMPTOM_COLS}

        row["Respiratory_Rate"]  = vitals.get("Respiratory_Rate", 18)
        row["Oxygen_Saturation"] = vitals.get("Oxygen_Saturation", 96)
        row["O2_Scale"]          = vitals.get("O2_Scale", 1.0)
        row["Systolic_BP"]       = vitals.get("Systolic_BP", 120)
        row["Heart_Rate"]        = vitals.get("Heart_Rate", 80)
        row["Temperature"]       = vitals.get("Temperature", 37.0)
        row["On_Oxygen"]         = vitals.get("On_Oxygen", 0)
        row["Consciousness_enc"] = CONSCIOUSNESS_MAP.get(vitals.get("Consciousness", "A"), 0)

        l = labs or {}
        row["ALT_UL"]   = l.get("ALT_UL", 25.0)
        row["WBC_K_uL"] = l.get("WBC_K_uL", 8.0)
        row["TSH_mIUL"] = l.get("TSH_mIUL", 2.1)

        # Derived features
        row["ALT_log"]         = np.log1p(row["ALT_UL"])
        row["TSH_flag"]        = int(row["TSH_mIUL"] < 0.3)
        row["WBC_high"]        = int(row["WBC_K_uL"] > 11.0)
        row["WBC_low"]         = int(row["WBC_K_uL"] < 4.5)
        row["Shock_Index"]     = row["Heart_Rate"] / (row["Systolic_BP"] + 1e-6)
        row["SpO2_HR_ratio"]   = row["Oxygen_Saturation"] / (row["Heart_Rate"] + 1e-6)
        row["Temp_deviation"]  = row["Temperature"] - 37.0
        row["Hypoxia_flag"]    = int(row["Oxygen_Saturation"] < 90)
        row["Tachycardia_flag"]= int(row["Heart_Rate"] > 100)
        row["Fever_flag"]      = int(row["Temperature"] > 38.0)
        row["Hypotensive_flag"]= int(row["Systolic_BP"] < 90)
        row["Severity_Score"]  = (row["Hypoxia_flag"]*3 + row["Tachycardia_flag"]*2 +
                                   row["Fever_flag"] + row["Hypotensive_flag"]*3 +
                                   row["Consciousness_enc"]*2)
        row["Symptom_Count"]   = sum(symptoms.get(s, 0) for s in ORIGINAL_SYMPTOMS)

        p  = pd.DataFrame([row])[ALL_FEATURES]
        
        # Apply scaling based on config
        Xp  = p if not self.config["disease_scaled"] else self.scaler.transform(p)
        Xrp = p if not self.config["risk_scaled"] else self.scaler.transform(p)

        pred_d = self.le_disease.inverse_transform(self.disease_model.predict(Xp))[0]

        if vitals_provided:
            pred_r = self.le_risk.inverse_transform(self.risk_model.predict(Xrp))[0]

            # Refine contradictory predictions
            if pred_d == "Healthy":
                if pred_r in ["High", "Critical"] or row["Severity_Score"] >= 2:
                    pred_d = "Atypical/Unknown Illness"
                else:
                    pred_d = "Generally Healthy"

            try:
                conf_d = float(self.disease_model.predict_proba(Xp).max())
                conf_r = float(self.risk_model.predict_proba(Xrp).max())
            except Exception:
                conf_d = None
                conf_r = None

            recommendation = "Monitor symptoms. Visit a doctor if condition worsens."
            if pred_r == "Critical":
                recommendation = "IMMEDIATE Emergency Room (ER) visit required."
            elif pred_r == "High":
                recommendation = "Please visit a doctor within 24 hours."
            elif pred_r == "Moderate":
                recommendation = "Schedule a doctor's appointment within 3-5 days."
            elif pred_r == "Low":
                recommendation = "Monitor symptoms. Visit a doctor if condition worsens over the next week."

            return {
                "disease"            : pred_d,
                "disease_confidence" : conf_d,
                "risk_level"         : pred_r,
                "risk_confidence"    : conf_r,
                "severity_score"     : row["Severity_Score"],
                "recommendation"     : recommendation
            }
        else:
            if pred_d == "Healthy":
                pred_d = "Generally Healthy"
                
            try:
                conf_d = float(self.disease_model.predict_proba(Xp).max())
            except Exception:
                conf_d = None
                
            return {
                "disease"            : pred_d,
                "disease_confidence" : conf_d,
                "risk_level"         : "N/A",
                "risk_confidence"    : None,
                "severity_score"     : "N/A",
                "recommendation"     : "Vitals not provided. Risk level and severity cannot be assessed."
            }
