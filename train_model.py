import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import xgboost as xgb

# =========================
# LOAD DATA
# =========================
df = pd.read_excel("Telco_customer_churn.xlsx")

# =========================
# CLEANING
# =========================
df.drop([
    "CustomerID", "Count", "Country", "State", "City", "Zip Code",
    "Lat Long", "Latitude", "Longitude",
    "Churn Score", "Churn Label", "Churn Reason", "CLTV"
], axis=1, inplace=True)

df.rename(columns={"Churn Value": "Churn"}, inplace=True)

# Fix Total Charges
df["Total Charges"] = pd.to_numeric(df["Total Charges"], errors="coerce")
df["Total Charges"].fillna(df["Total Charges"].median(), inplace=True)

# =========================
# ENCODING
# =========================

# Binary columns
binary_cols = ["Partner", "Dependents", "Phone Service", "Paperless Billing"]

for col in binary_cols:
    df[col] = df[col].map({"Yes": 1, "No": 0})

# Replace "No internet service"
cols_replace = [
    "Online Security", "Online Backup", "Device Protection",
    "Tech Support", "Streaming TV", "Streaming Movies"
]

for col in cols_replace:
    df[col] = df[col].replace("No internet service", "No")

# One-hot encoding
df = pd.get_dummies(df, drop_first=True)

# =========================
# SPLIT
# =========================
X = df.drop("Churn", axis=1)
y = df["Churn"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# SCALING (OPTIONAL but good)
# =========================
scaler = StandardScaler()

num_cols = ["Tenure Months", "Monthly Charges", "Total Charges"]
X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
X_test[num_cols] = scaler.transform(X_test[num_cols])

# =========================
# MODEL
# =========================
model = xgb.XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)

model.fit(X_train, y_train)

# =========================
# EVALUATION
# =========================
y_prob = model.predict_proba(X_test)[:,1]
y_pred = (y_prob > 0.3).astype(int)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall:", recall_score(y_test, y_pred))
print("F1 Score:", f1_score(y_test, y_pred))
print("ROC-AUC:", roc_auc_score(y_test, y_prob))

# =========================
# SAVE MODEL + COLUMNS + SCALER
# =========================
joblib.dump(model, "churn_model.pkl")
joblib.dump(X.columns.tolist(), "columns.pkl")
joblib.dump(scaler, "scaler.pkl")

print("✅ Model, columns, and scaler saved successfully")