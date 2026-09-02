<img width="702" height="547" alt="ROC_Curve" src="https://github.com/user-attachments/assets/ea08967c-3527-47b4-9d17-46a7d0b308f9" />
# Credit Risk & Lending ML (`/credit_risk_lending_ml`)

This folder contains the credit risk model, risk-based pricing system, and anomaly detection pipeline for Paytm Postpaid.

---

## 1. Data Summary
* **Total Applicants:** 400 (`credit_applicants.csv`)
* **Default Rate:** **20.25%** (81 defaults / 400 applicants)
* **Thin-File Applicants:** 80 applicants (20.0%) have missing credit bureau scores.
* **Transactions:** 265 total rows (`txn_behaviour.csv`), including 15 seeded fraud anomalies (`BTXNA0` to `BTXNA14`).

---

## 2. Preprocessing & Leakage Prevention
* **No Dropped Rows:** Kept all 80 thin-file applicants and flagged them with `is_thin_file = 1`.
* **75/25 Stratified Split:** Split using `random_state=42` stratified on default to maintain the 20.25% default rate in both train (300) and test (100) sets.
* **No Data Leakage:** Imputed missing bureau scores using the **training median (612.0)** only. Scaled numeric features using `StandardScaler` fitted strictly on training data.

---

## 3. Model Comparison (Test Set)

| Metric | Logistic Regression | Decision Tree |
| :--- | :---: | :---: |
| **Accuracy** | **76.00%** | 65.00% |
| **Precision** | **38.89%** | 22.22% |
| **Recall** | **35.00%** | 30.00% |
| **F1-Score** | **0.3684** | 0.2553 |
| **ROC-AUC** | **0.7188** | 0.5188 |

---

## 4. Risk-Based Pricing Table

Applicants are grouped into 4 risk tiers based on Logistic Regression predicted default probabilities. The observed default rate increases smoothly across tiers:

| Risk Tier | Default Probability | Total Count | Defaults | Actual Default Rate | Suggested APR |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Tier 1 (Low Risk)** | 0.31% – 3.78% | 100 | 3 | **3.0%** | 12% – 14% |
| **Tier 2 (Moderate Risk)** | 3.79% – 11.59% | 100 | 8 | **8.0%** | 15% – 18% |
| **Tier 3 (High Risk)** | 11.62% – 32.55% | 100 | 18 | **18.0%** | 20% – 24% |
| **Tier 4 (Very High Risk)** | 32.61% – 94.63% | 100 | 52 | **52.0%** | 26% – 32% (or Decline) |

---

## 5. Anomaly Detection (`IsolationForest`)
* **Features Used:** `txn_hour`, `is_new_device`, `txn_amount_inr`
* **Contamination:** Set to 5.66% ($15 / 265$)
* **Results:** Successfully caught **11 out of the 15 seeded anomalies** (**73.33% recall**).

---

## 6. Bias-Awareness & Governance
* **Proxy Risk:** Income, bureau scores, and gig employment can unintentionally act as proxies for age or geography, unfairly penalizing younger or non-metro applicants.
* **Governance Step:** Implement a **maker-checker review** where thin-file rejects (`is_thin_file = 1`) are reviewed manually using alternative data (like UPI inflow regularity) before an automated decline is finalized.

---

## 7. Final Recommendation
**Deploy Logistic Regression.** It outperforms the Decision Tree across all metrics (ROC-AUC of **0.7188** vs **0.5188** and accuracy of **76%** vs **65%**). The Decision Tree overfits heavily, while Logistic Regression outputs smooth, reliable probabilities that work seamlessly for risk pricing.
