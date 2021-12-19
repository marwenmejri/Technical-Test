from flask import Flask, request, jsonify
import pandas as pd
import os
from validation_model import validate_data, get_all_sheet_rows
from dotenv import load_dotenv


load_dotenv()
sheet_id = os.getenv('SHEET_ID')

# SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# SERVICE_ACCOUNT_FILE = "keys.json"

app = Flask(__name__)


@app.route('/')
def home():
    data = get_all_sheet_rows(sheet_id=sheet_id)
    print(data, end="\n\n")

    df = pd.read_csv(
        (f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"))
    response = df.to_html(header="true", table_id="table")

    validation = validate_data(data)
    print(validation)

    return response


if __name__ == '__main__':
    app.run()
