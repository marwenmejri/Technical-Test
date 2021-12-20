import re
import os
import pandas as pd
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ValidationError, validator, Field, EmailStr
from dotenv import load_dotenv
from read_wright_gs import get_spreadsheet_data

load_dotenv()
sheet_id = os.getenv('SHEET_ID')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = "keys.json"


class UserModel(BaseModel):
    id: int = Field(required=True, unique=True)
    email: EmailStr = Field(required=True)
    project: str = Field(required=True)
    status: str = Field(required=True)
    mail_sent: str = None
    test_score: Optional[str] = None

    @validator('project')
    def validate_project_name(cls, v):
        if v not in ['name_1', 'name_2', 'name_3']:
            raise ValueError('Project Name does not Exist')
        return v.title()

    @validator('status')
    def validate_status_value(cls, v):
        if v not in ['Submitted Test', 'Online Test Sent', 'Interview Mail Sent',
                     'Applied', 'Refusal Mail Sent', 'Reminder Sent']:
            raise ValueError('Invalid Status')
        return v.title()

    @validator('test_score')
    def validate_testscore(cls, v, values, **kwargs):
        if 'status' in values and values["status"] not in ['Submitted Test', 'Interview Mail Sent', 'Refusal Mail Sent']:
            if v != None:
                # print(v, type(v))
                raise ValueError('Unsubmitted Test should not have a score')
        else:
            if v == None:
                raise ValueError('Submitted Test should  have a score')

        if v != None:
            pattern = '^[0-4][0-9]/50'
            if len(re.findall(pattern, v)) == 0:
                raise ValueError(
                    'Test Score have a invalid pattern, it should be : xx/50')
        return v

    @validator('mail_sent')
    def validate_mail_sent(cls, v, values, **kwargs):
        bool = False
        if 'status' in values and values["status"] != 'Applied':
            if v == None:
                raise ValueError('Mail shoul already been sent')
        else:
            if v != None:
                raise ValueError('Mail shoul not been sent')

        if v != None:
            try:
                datetime.strptime(v, '%Y/%m/%d %H:%M:%S')
                bool = True
            except Exception:
                pass
            if not bool:
                raise ValueError(
                    "Try to enter a Valid date format : yyyy/mm/dd hh:mm:ss")

        return v


def get_all_sheet_rows(sheet_id):

    data, df = get_spreadsheet_data(sheet_id=sheet_id, SERVICE_ACCOUNT_FILE=SERVICE_ACCOUNT_FILE,
                                    range="Feuille1!A1:F8", scopes=SCOPES)
    all_rows = {}
    for key, value in df.iterrows():
        all_rows[key] = list(value)
    return all_rows


def validate_data(data):
    check = True
    for key, value in data.items():
        key += 1
        try:
            UserModel(
                id=value[0],
                email=value[1],
                project=value[2],
                status=value[3],
                mail_sent=value[4],
                test_score=value[5]
            )
        except ValidationError as e:
            print(f"Validation Error in Row n°{key}", e.json())
            check = False

    if check:
        print('No ValidationError caught.')
    return check


if __name__ == '__main__':

    data = get_all_sheet_rows(sheet_id=sheet_id)
    print(data)
    print(validate_data(data))
    # print(UserModel.schema())
