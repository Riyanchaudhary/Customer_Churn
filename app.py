from flask import Flask, request
import pandas as pd
import re
import joblib
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 🔥 LOAD EVERYTHING
model = joblib.load("churn_model.pkl")
expected_cols = joblib.load("columns.pkl")
scaler = joblib.load("scaler.pkl")

# 🔹 NORMALIZE FUNCTION
def normalize(col):
    return re.sub(r'[^a-z0-9]', '', col.lower())

# 🔹 COLUMN MAP
EXPECTED_MAP = {
    "tenuremonths": "Tenure Months",
    "monthlycharges": "Monthly Charges",
    "totalcharges": "Total Charges",
    "contract": "Contract"
}

REQUIRED_COLS = [
    "Tenure Months",
    "Monthly Charges",
    "Total Charges",
    "Contract"
]

OPTIONAL_DEFAULTS = {
    "Gender": "Male",
    "Senior Citizen": 0,
    "Partner": "No",
    "Dependents": "No",
    "Phone Service": "Yes",
    "Multiple Lines": "No",
    "Internet Service": "DSL",
    "Online Security": "No",
    "Online Backup": "No",
    "Device Protection": "No",
    "Tech Support": "No",
    "Streaming TV": "No",
    "Streaming Movies": "No",
    "Paperless Billing": "Yes",
    "Payment Method": "Electronic check"
}

# 🔹 FUNCTIONS
def map_columns(df):
    new_cols = {}
    for col in df.columns:
        norm = normalize(col)
        if norm in EXPECTED_MAP:
            new_cols[col] = EXPECTED_MAP[norm]
    return df.rename(columns=new_cols)

def validate_columns(df):
    missing = [col for col in REQUIRED_COLS if col not in df.columns]
    return (False, missing) if missing else (True, None)

def fill_optional(df):
    for col, default in OPTIONAL_DEFAULTS.items():
        if col not in df.columns:
            df[col] = default
    return df

def preprocess(df):
    # Convert numeric
    df["Total Charges"] = pd.to_numeric(df["Total Charges"], errors="coerce")
    df["Total Charges"].fillna(df["Total Charges"].median(), inplace=True)

    # Encode Yes/No
    binary_cols = ["Partner", "Dependents", "Phone Service", "Paperless Billing"]
    for col in binary_cols:
        df[col] = df[col].map({"Yes": 1, "No": 0})

    # Replace "No internet service"
    replace_cols = [
        "Online Security", "Online Backup", "Device Protection",
        "Tech Support", "Streaming TV", "Streaming Movies"
    ]
    for col in replace_cols:
        df[col] = df[col].replace("No internet service", "No")

    # One-hot encoding
    df = pd.get_dummies(df)

    return df

def align_columns(df):
    for col in expected_cols:
        if col not in df.columns:
            df[col] = 0

    df = df[expected_cols]
    return df

def scale_features(df):
    num_cols = ["Tenure Months", "Monthly Charges", "Total Charges"]
    df[num_cols] = scaler.transform(df[num_cols])
    return df

def get_risk(p):
    if p > 0.7:
        return "High Risk"
    elif p > 0.4:
        return "Medium Risk"
    return "Low Risk"

def get_action(risk):
    if risk == "High Risk":
        return "Call Customer"
    elif risk == "Medium Risk":
        return "Send Offer"
    return "No Action"

# 🔹 ROUTES
@app.route('/')
def home():
    return "Server is running"

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = file.filename

    # Read file
    if filename.endswith('.csv'):
        df = pd.read_csv(file)
    elif filename.endswith('.xlsx'):
        df = pd.read_excel(file)
    else:
        return {"error": "Unsupported file format"}

    # 🔥 PIPELINE
    df = map_columns(df)

    valid, missing = validate_columns(df)
    if not valid:
        return {"error": f"Missing columns: {missing}"}

    df = fill_optional(df)
    df = preprocess(df)
    df = align_columns(df)
    df = scale_features(df)

    # 🔥 PREDICTION
    probs = model.predict_proba(df)[:, 1]
    df_out = pd.DataFrame()

    df_out["Churn Probability"] = probs.astype(float)
    df_out["Risk"] = df_out["Churn Probability"].apply(get_risk)
    df_out["Action"] = df_out["Risk"].apply(get_action)

    # ✅ RETURN CLEAN JSON
    return df_out.to_dict(orient="records")

# 🔹 RUN
if __name__ == '__main__':
    app.run(debug=True)