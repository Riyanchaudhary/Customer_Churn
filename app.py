from flask import Flask, request
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is running"

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

    # Return preview (first 5 rows)
    return df.head().to_json(orient="records")

if __name__ == '__main__':
    app.run(debug=True)