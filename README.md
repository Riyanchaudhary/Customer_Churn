# 🚀 Churn Analytics Dashboard

A full-stack machine learning application that predicts customer churn from raw user-uploaded datasets and presents actionable insights through an interactive dashboard.

---
link - https://customer-churn-638v.vercel.app/
# 📌 Project Objective

The goal of this project is to simulate a **real-world business scenario** where companies want to identify customers likely to churn and take proactive actions to retain them.

This system allows users to:

* Upload raw customer data (CSV/Excel)
* Automatically preprocess and standardize the dataset
* Generate churn predictions using a trained ML model
* Visualize insights through a modern dashboard

---

# ⚙️ End-to-End Pipeline (What I Built)

## 1️⃣ File Upload & Data Ingestion

* Built a Flask API endpoint (`/upload`) to accept CSV and Excel files
* Used `pandas` to dynamically read input files
* Designed the system to handle **user-provided datasets with inconsistent formats**

---

## 2️⃣ Column Normalization (Key Innovation)

Real-world datasets often have inconsistent column names like:

* `tenure_months`
* `Tenure-Months`
* `TENURE MONTHS`

### 🔧 Solution:

I implemented a **custom normalization function**:

* Converted column names to lowercase
* Removed spaces, hyphens, and special characters using regex
* Mapped normalized names to expected schema

```python
def normalize(col):
    return re.sub(r'[^a-z0-9]', '', col.lower())
```

### 📌 Example:

| Raw Column      | Normalized     | Mapped To       |
| --------------- | -------------- | --------------- |
| Tenure-Months   | tenuremonths   | Tenure Months   |
| monthly_charges | monthlycharges | Monthly Charges |

👉 This makes the system **robust to real-world messy data**

---

## 3️⃣ Column Mapping & Validation

* Created a mapping dictionary (`EXPECTED_MAP`) to standardize column names
* Verified presence of required columns:

  * Tenure Months
  * Monthly Charges
  * Total Charges
  * Contract

### ✅ Validation Step:

If required columns are missing → API returns error

---

## 4️⃣ Handling Missing & Optional Features

To support incomplete datasets:

* Defined `OPTIONAL_DEFAULTS`
* Automatically filled missing columns with realistic defaults

Example:

```text
Gender → Male  
Partner → No  
Internet Service → DSL  
```

👉 This ensures **model compatibility even with partial data**

---

## 5️⃣ Data Preprocessing Pipeline

### 🔹 Numeric Handling

* Converted `Total Charges` to numeric
* Replaced invalid values with median

```python
df["Total Charges"] = pd.to_numeric(df["Total Charges"], errors="coerce")
df["Total Charges"].fillna(df["Total Charges"].median(), inplace=True)
```

---

### 🔹 Binary Encoding

Converted categorical values:

```text
Yes → 1  
No → 0  
```

Applied to:

* Partner
* Dependents
* Phone Service
* Paperless Billing

---

### 🔹 Category Cleaning

Replaced:

```text
"No internet service" → "No"
```

👉 Prevents unnecessary category explosion

---

### 🔹 One-Hot Encoding

Used `pd.get_dummies()` to convert categorical variables into numerical format

---

## 6️⃣ Feature Alignment

* Ensured incoming data matches training schema using `columns.pkl`
* Missing columns are added with 0 values

```python
df = df[expected_cols]
```

👉 Guarantees model compatibility

---

## 7️⃣ Feature Scaling

* Loaded pre-trained scaler (`scaler.pkl`)
* Applied scaling to numerical features:

```text
Tenure Months  
Monthly Charges  
Total Charges  
```

---

## 8️⃣ Model Prediction

* Used trained **XGBoost classifier**
* Generated churn probabilities:

```python
probs = model.predict_proba(df)[:, 1]
```

---

## 9️⃣ Business Logic Layer

Converted predictions into actionable insights:

### 🔹 Risk Classification

| Probability | Risk        |
| ----------- | ----------- |
| > 0.7       | High Risk   |
| 0.4–0.7     | Medium Risk |
| < 0.4       | Low Risk    |

---

### 🔹 Recommended Actions

| Risk   | Action        |
| ------ | ------------- |
| High   | Call Customer |
| Medium | Send Offer    |
| Low    | No Action     |

---

## 🔟 API Response

Backend returns structured JSON:

```json
{
  "Churn Probability": 0.82,
  "Risk": "High Risk",
  "Action": "Call Customer"
}
```

---

# 🎨 Frontend (React Dashboard)

Built using React + Vite

### Key Features:

* 📤 File upload interface
* 📊 Doughnut chart for risk distribution
* 📈 KPI cards:

  * High / Medium / Low risk counts
  * Average churn probability
* 🔍 Search and filtering
* 📉 Progress bars for churn %
* 📥 Download results as CSV
* 🧠 Explainability (basic reasoning)

---

# 🛠️ Tech Stack

### Backend:

* Flask
* Pandas, NumPy
* Scikit-learn
* XGBoost

### Frontend:

* React (Vite)
* Chart.js
* Custom CSS

---

# 📊 Model Performance

* Accuracy: ~77%
* Precision: ~0.57
* Recall: ~0.77
* F1 Score: ~0.66
* ROC-AUC: ~0.85

---

# 🚀 Key Highlights

* Handles messy real-world data through normalization
* Fully automated preprocessing pipeline
* End-to-end ML system (not just model training)
* Business-oriented output (risk + action)
* Interactive dashboard for decision-making

---

# 🔮 Future Improvements

* SHAP-based explainability
* Authentication system
* API-based real-time predictions
* Advanced analytics dashboard

---

# 👤 Author

Riyan Chaudhary
