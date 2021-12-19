import os
from google.auth.transport import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from dotenv import load_dotenv


load_dotenv()
sheet_id = os.getenv('SHEET_ID')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = "keys.json"


def get_spreadsheet_data(sheet_id, SERVICE_ACCOUNT_FILE, range, scopes=SCOPES):
    creds = None
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    request = sheet.values().get(spreadsheetId=sheet_id,
                                 range=range)
    response = request.execute()

    data = response.get('values', [])
    # print(values)

    # Transforming data in a pandas DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])
    # print(df.head(10))

    return data, df


aoa = [['ID', 'Email', 'Project', 'Status', 'Mail sent', 'Test Score'],
       ['1', 'username@mail.com', 'name_1', 'Interview Mail Sent', '2021/12/18 18:48:53',
        '34/50'],
       ['2', 'username@mail.com', 'name_1', 'Submitted Test', '2021/12/18 18:48:53', '34/50']]


def update_spreadsheet_data(sheet_id, data, SERVICE_ACCOUNT_FILE, range, scopes=SCOPES):
    creds = None
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    request = sheet.values().update(spreadsheetId=sheet_id, range=range, valueInputOption="USER_ENTERED",
                                    body={"values": data})
    response = request.execute()

    return response


if __name__ == '__main__':
    data, df = get_spreadsheet_data(sheet_id=sheet_id, SERVICE_ACCOUNT_FILE=SERVICE_ACCOUNT_FILE,
                                    range="Feuille1!A1:F8", scopes=SCOPES)
    print(data, df, sep="\n\n")

    # response = update_spreadsheet_data(sheet_id=sheet_id, data=aoa,
    #                                    SERVICE_ACCOUNT_FILE=SERVICE_ACCOUNT_FILE,
    #                                    range="Feuille2!A4", scopes=SCOPES)
    # print(response)
