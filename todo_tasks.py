from datetime import datetime, timedelta
import os
from validation_model import validate_data, get_all_sheet_rows
from dotenv import load_dotenv
from read_wright_gs import update_spreadsheet_data
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sys


load_dotenv()
sheet_id = os.getenv('SHEET_ID')
gmail_user = os.getenv('gmail_user')
gmail_password = os.getenv('gmail_password')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = "keys.json"


# Function to know if we have to sent Reminder Mail
def compare_date_mailsent(date):

    today = datetime.strptime(datetime.now().strftime(
        '%Y/%m/%d %H:%M:%S'), '%Y/%m/%d %H:%M:%S')
    last_week = today - timedelta(days=7)
    mail_sent_date = datetime.strptime(date, '%Y/%m/%d %H:%M:%S')

    if last_week > mail_sent_date:
        return True
    else:
        return False

# Function to calculate test result


def test_result(test_score):
    result = float(test_score[:2])
    total_marks = float(test_score[3:])
    if result >= (total_marks // 2):
        return True
    else:
        return False


def send_email(email, gmail_user, gmail_password, body, subject, filename_=None):

    try:
        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = gmail_user
        message['To'] = email
        message['Subject'] = subject
        # The subject line
        # The body and the attachments for the mail
        message.attach(MIMEText(body, 'plain'))

        if filename_:
            attach_file_name = filename_
            # Open the file as binary mode
            attach_file = open(attach_file_name, 'rb')
            payload = MIMEBase('application', 'octate-stream')
            payload.set_payload((attach_file).read())
            encoders.encode_base64(payload)  # encode the attachment
            # add payload header with filename
            payload.add_header('Content-Decomposition', 'attachment',
                               filename=attach_file_name)
            message.attach(payload)
        # Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
        session.starttls()  # enable security
        # login with mail_id and password
        session.login(gmail_user, gmail_password)
        text = message.as_string()
        session.sendmail(gmail_user, email, text)
        session.quit()
        print(
            f"Email about {subject} sent to {email} on {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
    except Exception as e:
        print(e)
        print('Something went wrong...')


def update_sheet(sheet_id, gmail_user, gmail_password):
    data = get_all_sheet_rows(sheet_id=sheet_id)
    print("data : \n", data, end="\n\n")
    validation = validate_data(data)
    print("validation : \n", validation, end="\n**********\n")

    # Updating Data
    if validation:
        data_for_update = []
        for key, value in data.items():

            # for Logic 1 : Status is Applied
            if value[3] == 'Applied':
                value[3] = "Online Test Sent"
                value[4] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                email_adress = value[1]

                # Send Online Test Sent Email
                body = 'Thank you for applying to Project :'
                subject = 'Application Received'
                send_email(email=email_adress, gmail_user=gmail_user,
                           gmail_password=gmail_password, body=body, subject=subject)

            # For Logic 2 : Online Test Sent & Mail sent is at least 7 days old & Test Score is empty
            if value[3] == "Online Test Sent":
                check_date = compare_date_mailsent(value[4])
                if check_date and value[5] == None:

                    # Change value of Status and mail Sent
                    value[3] = "Reminder Sent"
                    value[4] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                    email_adress = value[1]

                    # Sent Reminder Mail
                    body1 = 'You haven\'t submitted your test. Everything okay?'
                    subject1 = 'Reminder Mail'
                    send_email(email=email_adress, gmail_user=gmail_user,
                               gmail_password=gmail_password, body=body1, subject=subject1)

            # For Logic 3 : Status is Submitted Test & Test Score is less than half the total => Refusal Mail Sent
            if value[3] == "Submitted Test":
                if not test_result(value[-1]):
                    value[3] = "Refusal Mail Sent"
                    value[4] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                    email_adress = value[1]

                    # Sent Reminder Mail
                    body2 = 'We are sorry to tell you that you did not pass the test'
                    subject2 = 'Result Test Mail'
                    send_email(email=email_adress, gmail_user=gmail_user,
                               gmail_password=gmail_password, body=body2, subject=subject2)

                # For Logic 4 : Status is Submitted Test & Test Score is more than half the total => Interview Mail Sent
                else:
                    value[3] = "Interview Mail Sent"
                    value[4] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                    email_adress = value[1]

                    # Sent Interview Mail : Congrats
                    body2 = 'Congratulations for passing the test. You’ll have an interview with _____'
                    subject2 = 'Result Test Mail : Congratulations'
                    send_email(email=email_adress, gmail_user=gmail_user,
                               gmail_password=gmail_password, body=body2, subject=subject2)

            data_for_update.append(value)
        print('data_after_update : \n', data_for_update, end="\n\n")

        response = update_spreadsheet_data(sheet_id=sheet_id, data=data_for_update,
                                           SERVICE_ACCOUNT_FILE=SERVICE_ACCOUNT_FILE,
                                           range="Feuille1!A2", scopes=SCOPES)
        print("Update Respnse : \n", response, end="\n\n")

        # Validating Data After Updating
        data_updated = get_all_sheet_rows(sheet_id=sheet_id)
        validation_after_update = validate_data(data_updated)
        if validation_after_update:
            return "Data Updated & Validated"
    else:
        return '''You Need to Validate your google sheet Data Before Updating the file !!
        Assert that there are no critical errors (from the constraints listed above)'''


if __name__ == '__main__':

    sys.stdout = open('out.txt', 'w')
    result = update_sheet(sheet_id, gmail_user=gmail_user,
                          gmail_password=gmail_password)

    body = "Here you can find the loggs file containing all application run details "
    subject = 'Application Loggs'
    send_email(email='mejri.marwen00@gmail.com', gmail_user=gmail_user,
               gmail_password=gmail_password, body=body, subject=subject, filename_="out.txt")

    sys.stdout.close()
