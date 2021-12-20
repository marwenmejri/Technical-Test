from flask import Flask, request, jsonify
import pandas as pd
import os
import sys
from validation_model import get_all_sheet_rows
from dotenv import load_dotenv
from todo_tasks import update_sheet, send_email

load_dotenv()
sheet_id = os.getenv('SHEET_ID')
gmail_user = os.getenv('gmail_user')
gmail_password = os.getenv('gmail_password')


app = Flask(__name__)


@app.route('/')
def home():
    data = get_all_sheet_rows(sheet_id=sheet_id)
    print(data, end="\n\n")

    df = pd.read_csv(
        (f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"))
    response = df.to_html(header="true", table_id="table")

    # File For capturing all print logs
    sys.stdout = open('out.txt', 'w')

    # Applying all Logic to the sheet file
    result = update_sheet(sheet_id, gmail_user=gmail_user,
                          gmail_password=gmail_password)

    # Send an email containing logg file to the adminstrator of the Apps
    body = "Could you find a loggs file containing all application run details "
    subject = 'Application Loggs'
    send_email(email='mejri.marwen00@gmail.com', gmail_user=gmail_user,
               gmail_password=gmail_password, body=body, subject=subject, filename_="out.txt")

    sys.stdout.close()

    return response


if __name__ == '__main__':
    app.run()
