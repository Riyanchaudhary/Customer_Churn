from flask import Flask, request
import pandas as pd
import re
import joblib



app = Flask(__name__)


model = joblib.load("churn_model.pkl")
expected_cols = joblib.load("columns.pkl")

# 🔹 NORMALIZE FUNCTION
def normalize(col):
    col = col.lower()
    col = re.sub(r'[^a-z0-9]', '', col)
    return col


# 🔹 EXPECTED COLUMN MAP
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

def fill_optional(df):
    for col, default in OPTIONAL_DEFAULTS.items():
        if col not in df.columns:
            df[col] = default
    return df

def validate_columns(df):
    missing = [col for col in REQUIRED_COLS if col not in df.columns]

    if missing:
        return False, missing

    return True, None

# 🔹 COLUMN MAPPING FUNCTION
def map_columns(df):
    new_cols = {}

    for col in df.columns:
        norm = normalize(col)

        if norm in EXPECTED_MAP:
            new_cols[col] = EXPECTED_MAP[norm]

    df = df.rename(columns=new_cols)
    return df

# 🔹 HOME ROUTE
@app.route('/')
def home():
    return "Server is running"

# 🔹 UPLOAD ROUTE
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = file.filename

    # Handle CSV + Excel
    if filename.endswith('.csv'):
        df = pd.read_csv(file)
    elif filename.endswith('.xlsx'):
        df = pd.read_excel(file)
    else:
        return "Unsupported file format"

    # 🔥 Apply mapping
    df = map_columns(df)
    valid, missing = validate_columns(df)
    if not valid:
        return {
            "error": f"Missing required columns: {missing}"
        }
    # 🔥 NEW STEP
    df = fill_optional(df)

    # Debug output
    print(df.columns)

    # Return preview
    return df.head().to_json(orient="records")

# 🔹 RUN APP
if __name__ == '__main__':
    app.run(debug=True)