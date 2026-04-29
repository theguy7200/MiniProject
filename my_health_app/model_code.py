# =============================================================================
#  Health Risk & Disease Prediction - Clean ML Pipeline
#  Dataset : 16,000 patients (1,000 real + 15,000 synthetic)
#  Features: 40 (symptoms + targeted indicators + vitals + 3 lab tests + engineered)
#  Models  : Random Forest  |  Logistic Regression  |  Gradient Boosting
#  Results : Disease ~87%   |  Risk Level ~92%
# =============================================================================

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import time

from sklearn.model_selection  import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing    import LabelEncoder, StandardScaler, label_binarize
from sklearn.ensemble         import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model     import LogisticRegression
from sklearn.metrics          import (accuracy_score, f1_score, cohen_kappa_score,
                                      roc_auc_score, classification_report,
                                      confusion_matrix, ConfusionMatrixDisplay)

np.random.seed(42)

# -----------------------------------------------------------------------------
# 1.  LOAD DATASET
# -----------------------------------------------------------------------------
import os
_current_dir = os.path.dirname(os.path.abspath(__file__))
_csv_path = os.path.join(_current_dir, "professional_dataset_16k.csv")
df = pd.read_csv(_csv_path)

print("=" * 60)
print("  Health Risk & Disease Prediction - ML Pipeline")
print("=" * 60)
print(f"\nDataset         : {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"Diseases        : {df['disease'].nunique()} classes")
print(f"Risk levels     : {sorted(df['Risk_Level'].unique())}")
print(f"Missing values  : {df.isnull().sum().sum()}")

# -----------------------------------------------------------------------------
# 2.  FEATURE ENGINEERING
# -----------------------------------------------------------------------------
CONSCIOUSNESS_MAP = {"A": 0, "C": 1, "V": 2, "P": 3, "U": 4}
df["Consciousness_enc"] = df["Consciousness"].map(CONSCIOUSNESS_MAP)

# Clinical ratio features
df["Shock_Index"]    = df["Heart_Rate"] / (df["Systolic_BP"] + 1e-6)
df["SpO2_HR_ratio"]  = df["Oxygen_Saturation"] / (df["Heart_Rate"] + 1e-6)
df["Temp_deviation"] = df["Temperature"] - 37.0          # deviation from normal

# Binary clinical flags
df["Hypoxia_flag"]     = (df["Oxygen_Saturation"] < 90).astype(int)
df["Tachycardia_flag"] = (df["Heart_Rate"] > 100).astype(int)
df["Fever_flag"]       = (df["Temperature"] > 38.0).astype(int)
df["Hypotensive_flag"] = (df["Systolic_BP"] < 90).astype(int)

# Composite severity score (NEWS2-inspired)
df["Severity_Score"] = (
    df["Hypoxia_flag"]     * 3 +
    df["Tachycardia_flag"] * 2 +
    df["Fever_flag"]       * 1 +
    df["Hypotensive_flag"] * 3 +
    df["Consciousness_enc"]* 2
)

# Symptom count
BASE_SYMPTOMS = ["fever","headache","nausea","vomiting","fatigue",
                 "joint_pain","skin_rash","cough","weight_loss","yellow_eyes"]
df["Symptom_Count"] = df[BASE_SYMPTOMS].sum(axis=1)

# Lab-derived flags
df["ALT_log"]   = np.log1p(df["ALT_UL"])          # log-transform skewed ALT
df["TSH_flag"]  = (df["TSH_mIUL"] < 0.3).astype(int)   # suppressed = hyperthyroidism
df["WBC_high"]  = (df["WBC_K_uL"] > 11.0).astype(int)  # leukocytosis = infection
df["WBC_low"]   = (df["WBC_K_uL"] < 4.5).astype(int)   # leukopenia = Typhoid

# -----------------------------------------------------------------------------
# 3.  DEFINE FEATURE SETS
# -----------------------------------------------------------------------------
ORIGINAL_SYMPTOMS = [
    "fever", "headache", "nausea", "vomiting", "fatigue",
    "joint_pain", "skin_rash", "cough", "weight_loss", "yellow_eyes",
]
TARGETED_INDICATORS = [
    "chills_cyclical",      # Malaria - high specificity
    "night_sweats",         # Tuberculosis
    "dark_urine",           # Hepatitis B/C, Chronic cholestasis
    "positional_dizziness", # Vertigo (BPPV)
    "sudden_weakness",      # Paralysis / brain hemorrhage
    "neck_stiffness",       # Cervical spondylosis
    "frequent_urination",   # Diabetes
    "shortness_of_breath",  # Pneumonia
    "retro_orbital_pain",   # Dengue
]
VITALS = [
    "Respiratory_Rate", "Oxygen_Saturation", "O2_Scale",
    "Systolic_BP", "Heart_Rate", "Temperature",
    "On_Oxygen", "Consciousness_enc",
]
LAB_TESTS = [
    "ALT_UL", "ALT_log",           # Liver enzymes
    "WBC_K_uL", "WBC_high", "WBC_low",  # White blood cells
    "TSH_mIUL", "TSH_flag",        # Thyroid function
]
ENGINEERED = [
    "Shock_Index", "SpO2_HR_ratio", "Temp_deviation",
    "Hypoxia_flag", "Tachycardia_flag", "Fever_flag", "Hypotensive_flag",
    "Severity_Score", "Symptom_Count",
]

ALL_FEATURES = ORIGINAL_SYMPTOMS + TARGETED_INDICATORS + VITALS + LAB_TESTS + ENGINEERED

print(f"\nFeature breakdown:")
print(f"  Original symptoms    : {len(ORIGINAL_SYMPTOMS)}")
print(f"  Targeted indicators  : {len(TARGETED_INDICATORS)}")
print(f"  Vital signs          : {len(VITALS)}")
print(f"  Lab tests            : {len(LAB_TESTS)}")
print(f"  Engineered features  : {len(ENGINEERED)}")
print(f"  ---------------------------------")
print(f"  Total                : {len(ALL_FEATURES)}")

# -----------------------------------------------------------------------------
# 4.  ENCODE TARGETS
# -----------------------------------------------------------------------------
le_disease = LabelEncoder()
le_risk    = LabelEncoder()

y_disease = le_disease.fit_transform(df["disease"])
y_risk    = le_risk.fit_transform(df["Risk_Level"])

DISEASE_NAMES = list(le_disease.classes_)
RISK_NAMES    = list(le_risk.classes_)

print(f"\nDisease classes ({len(DISEASE_NAMES)}): {DISEASE_NAMES[:4]} ...")
print(f"Risk classes    ({len(RISK_NAMES)}): {RISK_NAMES}")

# -----------------------------------------------------------------------------
# 5.  TRAIN / TEST SPLIT  (80 / 20, stratified)
# -----------------------------------------------------------------------------
X = df[ALL_FEATURES]

train_idx, test_idx = train_test_split(
    np.arange(len(df)), test_size=0.20, random_state=42, stratify=y_disease
)

X_train = X.iloc[train_idx]
X_test  = X.iloc[test_idx]

yd_train, yd_test = y_disease[train_idx], y_disease[test_idx]
yr_train, yr_test = y_risk[train_idx], y_risk[test_idx]

# Scale for Logistic Regression
scaler  = StandardScaler()
X_tr_sc = scaler.fit_transform(X_train)
X_te_sc = scaler.transform(X_test)

print(f"\nTrain samples : {X_train.shape[0]:,}")
print(f"Test  samples : {X_test.shape[0]:,}")

# -----------------------------------------------------------------------------
# 6.  MODEL DEFINITIONS
# -----------------------------------------------------------------------------
MODELS = {
    "Random Forest": {
        "model":  RandomForestClassifier(
            n_estimators    = 200,
            max_features    = "sqrt",
            min_samples_leaf= 2,
            n_jobs          = -1,
            random_state    = 42,
        ),
        "scaled": False,
    },
    "Gradient Boosting": {
        "model":  GradientBoostingClassifier(
            n_estimators  = 150,
            learning_rate = 0.08,
            max_depth     = 5,
            subsample     = 0.8,
            random_state  = 42,
        ),
        "scaled": False,
    },
    "Logistic Regression": {
        "model":  LogisticRegression(
            max_iter     = 500,
            C            = 1.0,
            solver       = "lbfgs",
            random_state = 42,
        ),
        "scaled": True,
    },
}

# -----------------------------------------------------------------------------
# 7.  EVALUATION HELPER
# -----------------------------------------------------------------------------
def evaluate(name, model, Xtr, ytr, Xte, yte, label_names):
    t0  = time.time()
    model.fit(Xtr, ytr)
    yp  = model.predict(Xte)
    acc = accuracy_score(yte, yp)
    f1  = f1_score(yte, yp, average="macro", zero_division=0)
    kap = cohen_kappa_score(yte, yp)
    try:
        proba = model.predict_proba(Xte)
        auc   = roc_auc_score(
            label_binarize(yte, classes=range(len(label_names))),
            proba, average="macro", multi_class="ovr"
        )
    except Exception:
        auc = float("nan")

    print(f"\n  {'-'*50}")
    print(f"  {name}")
    print(f"  {'-'*50}")
    print(f"  Accuracy   : {acc:.4f}")
    print(f"  Macro F1   : {f1:.4f}")
    print(f"  Cohen Kappa: {kap:.4f}")
    print(f"  AUC-ROC    : {auc:.4f}")
    print(f"  Time       : {time.time()-t0:.0f}s")
    print()
    print(classification_report(yte, yp, target_names=label_names, zero_division=0))
    return model, {"acc": acc, "f1": f1, "kappa": kap, "auc": auc}, yp


# -----------------------------------------------------------------------------
# 8A.  TASK 1 - DISEASE PREDICTION
# -----------------------------------------------------------------------------
print("\n" + "=" * 60)
print("  TASK 1 - DISEASE PREDICTION  (14 classes)")
print("=" * 60)

d_results, d_preds, d_models = {}, {}, {}

for name, cfg in MODELS.items():
    Xtr_ = X_tr_sc if cfg["scaled"] else X_train
    Xte_ = X_te_sc if cfg["scaled"] else X_test
    m, metrics, yp = evaluate(name, cfg["model"], Xtr_, yd_train,
                               Xte_, yd_test, DISEASE_NAMES)
    d_results[name] = metrics
    d_preds[name]   = yp
    d_models[name]  = m

best_d = max(d_results, key=lambda k: d_results[k]["f1"])
print(f"\n*  Best Disease Model : {best_d}")
print(f"   Accuracy={d_results[best_d]['acc']:.4f}  "
      f"F1={d_results[best_d]['f1']:.4f}  "
      f"AUC={d_results[best_d]['auc']:.4f}")

# -----------------------------------------------------------------------------
# 8B.  TASK 2 - RISK LEVEL PREDICTION
# -----------------------------------------------------------------------------
print("\n" + "=" * 60)
print("  TASK 2 - RISK LEVEL PREDICTION  (4 classes)")
print("=" * 60)

r_results, r_preds, r_models = {}, {}, {}

for name, cfg in MODELS.items():
    Xtr_ = X_tr_sc if cfg["scaled"] else X_train
    Xte_ = X_te_sc if cfg["scaled"] else X_test
    # Re-instantiate so we don't reuse fitted disease model
    fresh_model = cfg["model"].__class__(**cfg["model"].get_params())
    m, metrics, yp = evaluate(name, fresh_model, Xtr_, yr_train,
                               Xte_, yr_test, RISK_NAMES)
    r_results[name] = metrics
    r_preds[name]   = yp
    r_models[name]  = m

best_r = max(r_results, key=lambda k: r_results[k]["f1"])
print(f"\n*  Best Risk Model    : {best_r}")
print(f"   Accuracy={r_results[best_r]['acc']:.4f}  "
      f"F1={r_results[best_r]['f1']:.4f}  "
      f"AUC={r_results[best_r]['auc']:.4f}")

# -----------------------------------------------------------------------------
# 9.  5-FOLD CROSS VALIDATION ON BEST MODELS
# -----------------------------------------------------------------------------
print("\n" + "=" * 60)
print("  CROSS VALIDATION (5-fold, best models)")
print("=" * 60)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

best_d_model = d_models[best_d]
best_r_model = r_models[best_r]

d_use_scaled = MODELS[best_d]["scaled"]
r_use_scaled = MODELS[best_r]["scaled"]

cv_Xd = X_te_sc if d_use_scaled else X_test
cv_Xr = X_te_sc if r_use_scaled else X_test

cv_d = cross_val_score(best_d_model, cv_Xd, yd_test, cv=skf,
                        scoring="f1_macro", n_jobs=-1)
cv_r = cross_val_score(best_r_model, cv_Xr, yr_test, cv=skf,
                        scoring="f1_macro", n_jobs=-1)

print(f"\n  Disease ({best_d}):")
print(f"    CV Macro F1 = {cv_d.mean():.4f} ± {cv_d.std():.4f}")
print(f"\n  Risk ({best_r}):")
print(f"    CV Macro F1 = {cv_r.mean():.4f} ± {cv_r.std():.4f}")

# -----------------------------------------------------------------------------
# 10.  VISUALISATIONS
# -----------------------------------------------------------------------------
print("\n[...] Generating charts ...")

fig, axes = plt.subplots(2, 2, figsize=(18, 14))
fig.patch.set_facecolor("#f8f9fa")
fig.suptitle("Health Risk & Disease Prediction - Results\n"
             "16,000 Patients | 40 Features | 3 Models",
             fontsize=15, fontweight="bold", y=1.01)

BLUE   = "#2E75B6"
ORANGE = "#E8622A"
GREEN  = "#2E7D32"

# -- 10.1  Model comparison - Disease ------------------------------------------
ax = axes[0, 0]
names  = list(d_results.keys())
accs   = [d_results[n]["acc"] for n in names]
f1s    = [d_results[n]["f1"]  for n in names]
x      = np.arange(len(names))
b1 = ax.bar(x - 0.2, accs, 0.35, label="Accuracy", color=BLUE,   alpha=0.85)
b2 = ax.bar(x + 0.2, f1s,  0.35, label="Macro F1", color=ORANGE, alpha=0.85)
ax.set_xticks(x); ax.set_xticklabels(names, fontsize=10)
ax.set_ylim(0.80, 0.95)
ax.set_ylabel("Score"); ax.set_title("Disease Prediction - Model Comparison", fontweight="bold")
ax.legend(); ax.grid(axis="y", alpha=0.3)
for bar in list(b1) + list(b2):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
            f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=8.5)

# -- 10.2  Model comparison - Risk ---------------------------------------------
ax = axes[0, 1]
accs_r = [r_results[n]["acc"] for n in names]
f1s_r  = [r_results[n]["f1"]  for n in names]
b3 = ax.bar(x - 0.2, accs_r, 0.35, label="Accuracy", color=BLUE,   alpha=0.85)
b4 = ax.bar(x + 0.2, f1s_r,  0.35, label="Macro F1", color=GREEN,  alpha=0.85)
ax.set_xticks(x); ax.set_xticklabels(names, fontsize=10)
ax.set_ylim(0.80, 1.00)
ax.set_ylabel("Score"); ax.set_title("Risk Level Prediction - Model Comparison", fontweight="bold")
ax.legend(); ax.grid(axis="y", alpha=0.3)
for bar in list(b3) + list(b4):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
            f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=8.5)

# -- 10.3  Confusion matrix - Disease (best model) -----------------------------
ax = axes[1, 0]
cm = confusion_matrix(yd_test, d_preds[best_d])
cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
short = [n[:20] for n in DISEASE_NAMES]
sns.heatmap(cm_norm, annot=True, fmt=".2f", cmap="Blues",
            xticklabels=short, yticklabels=short, ax=ax,
            cbar=True, linewidths=0.4)
ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
ax.set_title(f"Disease Confusion Matrix - {best_d}", fontweight="bold")
ax.tick_params(axis="x", rotation=45, labelsize=7)
ax.tick_params(axis="y", rotation=0,  labelsize=7)

# -- 10.4  Feature importance (Random Forest) ----------------------------------
ax = axes[1, 1]
rf_fi = d_models.get("Random Forest")
if rf_fi is None:
    rf_fi = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
    rf_fi.fit(X_train, yd_train)
fi = pd.Series(rf_fi.feature_importances_, index=ALL_FEATURES)\
       .sort_values(ascending=True).tail(18)
colors_fi = plt.cm.Blues(np.linspace(0.35, 0.9, len(fi)))
ax.barh(fi.index, fi.values, color=colors_fi)
ax.set_xlabel("Importance")
ax.set_title("Top 18 Features - Disease Model (RF)", fontweight="bold")
ax.tick_params(labelsize=8)

plt.tight_layout()
plt.savefig("results.png", dpi=150, bbox_inches="tight")
print("[OK] Saved -> results.png")

# -----------------------------------------------------------------------------
# 11.  SUMMARY TABLE
# -----------------------------------------------------------------------------
print("\n" + "=" * 60)
print("  FINAL SUMMARY")
print("=" * 60)

rows = []
for name in MODELS:
    rows.append({
        "Model"        : name,
        "Disease Acc"  : round(d_results[name]["acc"], 4),
        "Disease F1"   : round(d_results[name]["f1"],  4),
        "Disease AUC"  : round(d_results[name]["auc"], 4),
        "Risk Acc"     : round(r_results[name]["acc"], 4),
        "Risk F1"      : round(r_results[name]["f1"],  4),
        "Risk AUC"     : round(r_results[name]["auc"], 4),
    })
summary = pd.DataFrame(rows).sort_values("Disease F1", ascending=False).reset_index(drop=True)
print(summary.to_string(index=False))
summary.to_csv("model_summary.csv", index=False)
print("\n[OK] Saved -> model_summary.csv")

# -----------------------------------------------------------------------------
# 12.  PREDICTION FUNCTION
# -----------------------------------------------------------------------------
def predict(symptoms: dict, vitals: dict, labs: dict = None) -> dict:
    """
    Predict disease and risk level for a new patient.

    symptoms : dict  e.g. {"fever": 1, "cough": 1, "chills_cyclical": 1, ...}
    vitals   : dict  e.g. {"Oxygen_Saturation": 93, "Heart_Rate": 110, ...}
    labs     : dict  e.g. {"ALT_UL": 250, "WBC_K_uL": 3.4, "TSH_mIUL": 1.8}
    """
    SYMPTOM_COLS = ORIGINAL_SYMPTOMS + TARGETED_INDICATORS
    row = {s: symptoms.get(s, 0) for s in SYMPTOM_COLS}

    row["Respiratory_Rate"]  = vitals.get("Respiratory_Rate", 18)
    row["Oxygen_Saturation"] = vitals.get("Oxygen_Saturation", 96)
    row["O2_Scale"]          = vitals.get("O2_Scale", 1.0)
    row["Systolic_BP"]       = vitals.get("Systolic_BP", 120)
    row["Heart_Rate"]        = vitals.get("Heart_Rate", 80)
    row["Temperature"]       = vitals.get("Temperature", 37.0)
    row["On_Oxygen"]         = vitals.get("On_Oxygen", 0)
    row["Consciousness_enc"] = CONSCIOUSNESS_MAP.get(vitals.get("Consciousness","A"), 0)

    l = labs or {}
    row["ALT_UL"]   = l.get("ALT_UL",  25.0)
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

    p   = pd.DataFrame([row])[ALL_FEATURES]
    Xp  = p if not MODELS[best_d]["scaled"] else scaler.transform(p)
    Xrp = p if not MODELS[best_r]["scaled"] else scaler.transform(p)

    pred_d = le_disease.inverse_transform(d_models[best_d].predict(Xp))[0]
    pred_r = le_risk.inverse_transform(r_models[best_r].predict(Xrp))[0]

    try:
        conf_d = f"{d_models[best_d].predict_proba(Xp).max()*100:.1f}%"
        conf_r = f"{r_models[best_r].predict_proba(Xrp).max()*100:.1f}%"
    except Exception:
        conf_d = conf_r = "N/A"

    return {
        "disease"            : pred_d,
        "disease_confidence" : conf_d,
        "risk_level"         : pred_r,
        "risk_confidence"    : conf_r,
        "severity_score"     : row["Severity_Score"],
    }


# -----------------------------------------------------------------------------
# 13.  SAVE MODELS FOR DEPLOYMENT
# -----------------------------------------------------------------------------
import joblib
import os

def save_models(models_dir="backend/models"):
    os.makedirs(models_dir, exist_ok=True)
    print(f"\n[INFO] Saving models to {models_dir}/...")
    # Using the best models discovered during training
    joblib.dump(d_models[best_d], os.path.join(models_dir, "disease_model.pkl"))
    joblib.dump(r_models[best_r], os.path.join(models_dir, "risk_model.pkl"))
    joblib.dump(scaler, os.path.join(models_dir, "scaler.pkl"))
    joblib.dump(le_disease, os.path.join(models_dir, "le_disease.pkl"))
    joblib.dump(le_risk, os.path.join(models_dir, "le_risk.pkl"))
    
    # Save config mapping if models needed scaling
    config = {
        "disease_scaled": MODELS[best_d]["scaled"],
        "risk_scaled": MODELS[best_r]["scaled"],
        "best_disease_model": best_d,
        "best_risk_model": best_r
    }
    joblib.dump(config, os.path.join(models_dir, "config.pkl"))
    print("[OK] Models and config saved successfully.")

if __name__ == "__main__":
    # -- Demo predictions ----------------------------------------------------------
    print("\n" + "=" * 60)
    print("  DEMO PREDICTIONS")
    print("=" * 60)
    
    PATIENTS = [
        {
            "label"   : "Patient A - Malaria Profile",
            "symptoms": {"fever":1,"headache":1,"joint_pain":1,"yellow_eyes":1,
                         "chills_cyclical":1,"fatigue":1},
            "vitals"  : {"Oxygen_Saturation":93,"Heart_Rate":108,"Systolic_BP":100,
                         "Temperature":39.4,"Respiratory_Rate":22,"Consciousness":"A"},
            "labs"    : {"ALT_UL":55,"WBC_K_uL":3.2,"TSH_mIUL":1.9},
        },
        {
            "label"   : "Patient B - High Risk Respiratory",
            "symptoms": {"fever":1,"cough":1,"weight_loss":1,"fatigue":1,"night_sweats":1},
            "vitals"  : {"Oxygen_Saturation":85,"Heart_Rate":130,"Systolic_BP":82,
                         "Temperature":39.9,"Respiratory_Rate":31,"Consciousness":"V",
                         "On_Oxygen":1},
            "labs"    : {"ALT_UL":40,"WBC_K_uL":14.5,"TSH_mIUL":2.0},
        },
        {
            "label"   : "Patient C - Normal/Low Risk",
            "symptoms": {"nausea":1,"vomiting":1,"headache":1},
            "vitals"  : {"Oxygen_Saturation":98,"Heart_Rate":72,"Systolic_BP":118,
                         "Temperature":37.1,"Respiratory_Rate":16,"Consciousness":"A"},
            "labs"    : {"ALT_UL":22,"WBC_K_uL":7.5,"TSH_mIUL":2.3},
        },
    ]
    
    for pat in PATIENTS:
        result = predict(pat["symptoms"], pat["vitals"], pat.get("labs"))
        print(f"\n  {pat['label']}")
        print(f"  Disease    : {result['disease']}  ({result['disease_confidence']})")
        print(f"  Risk Level : {result['risk_level']}  ({result['risk_confidence']})")
        print(f"  Severity   : {result['severity_score']}/20")
    
    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print(f"  Disease  -> Best: {best_d}  Acc={d_results[best_d]['acc']:.4f}  F1={d_results[best_d]['f1']:.4f}")
    print(f"  Risk     -> Best: {best_r}  Acc={r_results[best_r]['acc']:.4f}  F1={r_results[best_r]['f1']:.4f}")
    print("=" * 60)
    
    # Save the models
    save_models()
