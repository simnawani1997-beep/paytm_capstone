# ==============================================================================
# PART 2 — CREDIT RISK & LENDING ML (/credit_risk_lending_ml)
# ==============================================================================

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, roc_curve
)
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt

# ------------------------------------------------------------------------------
# Task 1: Load Data & Pre-imputation Thin-File Feature Engineering
# ------------------------------------------------------------------------------
df = pd.read_csv("credit_applicants.csv")
print("=== TASK 1: DATA PROFILE & THIN-FILE AUDIT ===")
measured_default_rate = df["default"].mean()
missing_bureau_count = df["credit_bureau_score"].isna().sum()
missing_bureau_pct = df["credit_bureau_score"].isna().mean()

print(f"Total Applicants: {len(df)}")
print(f"Measured Default Rate: {measured_default_rate:.2%} ({df['default'].sum()} defaults)")
print(f"Missing Bureau Score Count: {missing_bureau_count} ({missing_bureau_pct:.2%})")

# Engineer thin-file indicator flag directly from raw data BEFORE imputation
# (Ensures zero data leakage and preserves the alternate-data applicant segment)
df["is_thin_file"] = df["credit_bureau_score"].isna().astype(int)

X = df.drop(columns=["applicant_id", "default"])
y = df["default"]

# ------------------------------------------------------------------------------
# Task 2: 75/25 Stratified Train/Test Split & Leakage-Free Preprocessing
# ------------------------------------------------------------------------------
print("\n=== TASK 2: STRATIFIED SPLIT & TRAINING-DERIVED PREPROCESSING ===")
# Exactly 75/25 split stratified on default with random_state=42 (yields exactly 100 test rows)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)

print(f"Training Set Size: {len(X_train)} rows | Defaults: {y_train.sum()} ({y_train.mean():.2%})")
print(f"Test Set Size:     {len(X_test)} rows  | Defaults: {y_test.sum()} ({y_test.mean():.2%})")

# Step 2a: Compute median ONLY on training non-missing bureau scores
train_median_bureau = X_train["credit_bureau_score"].median()
print(f"Training Bureau Score Median: {train_median_bureau}")

X_train = X_train.copy()
X_test = X_test.copy()

# Apply the exact training-derived median to both splits
X_train["credit_bureau_score"] = X_train["credit_bureau_score"].fillna(train_median_bureau)
X_test["credit_bureau_score"] = X_test["credit_bureau_score"].fillna(train_median_bureau)

# Step 2b: One-Hot Encode employment_type (aligning columns across splits)
X_train = pd.get_dummies(X_train, columns=["employment_type"], drop_first=True, dtype=int)
X_test = pd.get_dummies(X_test, columns=["employment_type"], drop_first=True, dtype=int)

# Step 2c: Fit StandardScaler ONLY on training split
num_cols = [
    "age", "monthly_income_inr", "existing_loans_count", "credit_utilization_ratio",
    "upi_monthly_inflow_inr", "bounced_payments_count", "credit_bureau_score"
]
scaler = StandardScaler()
X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
X_test[num_cols] = scaler.transform(X_test[num_cols])

# ------------------------------------------------------------------------------
# Task 3 & 4: Model Training, Evaluation, and Comparison
# ------------------------------------------------------------------------------
print("\n=== TASK 3 & 4: MODEL TRAINING & TEST EVALUATION (100 SAMPLES) ===")

# Model 1: Logistic Regression
lr_model = LogisticRegression(random_state=42)
lr_model.fit(X_train, y_train)
y_pred_lr = lr_model.predict(X_test)
y_prob_lr = lr_model.predict_proba(X_test)[:, 1]

# Model 2: Decision Tree Classifier
dt_model = DecisionTreeClassifier(random_state=42)
dt_model.fit(X_train, y_train)
y_pred_dt = dt_model.predict(X_test)
y_prob_dt = dt_model.predict_proba(X_test)[:, 1]

def print_model_report(name, y_true, y_pred, y_prob):
    cm = confusion_matrix(y_true, y_pred)
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    auc = roc_auc_score(y_true, y_prob)
    
    print(f"--- {name} ---")
    print("Confusion Matrix [[TN, FP], [FN, TP]]:")
    print(cm)
    print(f"Accuracy:  {acc:.4f} ({acc:.2%})")
    print(f"Precision: {prec:.4f} ({prec:.2%})")
    print(f"Recall:    {rec:.4f} ({rec:.2%})")
    print(f"F1-Score:  {f1:.4f}")
    print(f"ROC-AUC:   {auc:.4f}\n")
    print("Full Classification Report:")
    print(classification_report(y_true, y_pred, digits=4))
    return {"Accuracy": acc, "Precision": prec, "Recall": rec, "F1": f1, "ROC_AUC": auc, "CM": cm}

results_lr = print_model_report("MODEL A: LOGISTIC REGRESSION", y_test, y_pred_lr, y_prob_lr)
results_dt = print_model_report("MODEL B: DECISION TREE CLASSIFIER", y_test, y_pred_dt, y_prob_dt)

# ------------------------------------------------------------------------------
# Task 5: Risk-Based Pricing Table (Quartiles of Predicted Probability)
# ------------------------------------------------------------------------------
print("\n=== TASK 5: RISK-BASED PRICING TABLE (FULL POPULATION MONOTONICITY) ===")

# Predict default probabilities for all applicants using the trained logistic regression model
X_all = pd.concat([X_train, X_test])
y_all = pd.concat([y_train, y_test])
all_pred_probs = lr_model.predict_proba(X_all)[:, 1]

pricing_df = pd.DataFrame({"actual_default": y_all, "pred_prob": all_pred_probs})
pricing_df["risk_tier"] = pd.qcut(
    pricing_df["pred_prob"],
    q=4,
    labels=["Tier 1 (Low Risk)", "Tier 2 (Moderate Risk)", "Tier 3 (High Risk)", "Tier 4 (Very High Risk)"]
)

apr_mapping = {
    "Tier 1 (Low Risk)": "12.0% - 14.0%",
    "Tier 2 (Moderate Risk)": "15.0% - 18.0%",
    "Tier 3 (High Risk)": "20.0% - 24.0%",
    "Tier 4 (Very High Risk)": "26.0% - 32.0% (or Decline)"
}

pricing_summary = pricing_df.groupby("risk_tier", observed=False).agg(
    total_applicants=("actual_default", "count"),
    observed_defaults=("actual_default", "sum"),
    actual_default_rate=("actual_default", "mean"),
    min_prob=("pred_prob", "min"),
    max_prob=("pred_prob", "max")
).reset_index()

pricing_summary["assigned_apr"] = pricing_summary["risk_tier"].map(apr_mapping)
pricing_summary["actual_default_rate_pct"] = pricing_summary["actual_default_rate"].map(lambda x: f"{x:.2%}")
pricing_summary["prob_range"] = pricing_summary.apply(lambda r: f"{r['min_prob']:.2%} - {r['max_prob']:.2%}", axis=1)

print(pricing_summary[["risk_tier", "prob_range", "total_applicants", "observed_defaults", "actual_default_rate_pct", "assigned_apr"]])

# ------------------------------------------------------------------------------
# Task 6: Anomaly Detection on Transaction Stream (IsolationForest)
# ------------------------------------------------------------------------------
print("\n=== TASK 6: ISOLATION FOREST ANOMALY DETECTION (txn_behaviour.csv) ===")
behaviour = pd.read_csv("txn_behaviour.csv")

# Standardize numeric features: txn_hour, is_new_device, txn_amount_inr
iso_features = ["txn_hour", "is_new_device", "txn_amount_inr"]
scaler_iso = StandardScaler()
X_iso_scaled = scaler_iso.fit_transform(behaviour[iso_features])

# Contamination matches the proportion of seeded anomalies (15 / 265 ≈ 5.66%)
contamination_rate = 15.0 / len(behaviour)
iso_forest = IsolationForest(contamination=contamination_rate, random_state=42)

# -1 represents an anomaly, 1 represents normal
behaviour["pred_anomaly"] = (iso_forest.fit_predict(X_iso_scaled) == -1).astype(int)
behaviour["is_seeded_anomaly"] = behaviour["txn_id"].str.startswith("BTXNA").astype(int)

flagged_total = behaviour["pred_anomaly"].sum()
seeded_detected = behaviour[(behaviour["is_seeded_anomaly"] == 1) & (behaviour["pred_anomaly"] == 1)]
recall_iso = len(seeded_detected) / 15.0

print(f"Total Transactions: {len(behaviour)}")
print(f"Total Transactions Flagged as Anomalies: {flagged_total}")
print(f"Seeded Anomalies (BTXNA*) Detected: {len(seeded_detected)} / 15")
print(f"Isolation Forest Empirical Recall: {recall_iso:.2%}")
