# Technical-Test

Automatic Recruitment Pipeline.

For this test you are asked to make a Flask app with one route that connects to a Google Sheets Spreadsheet on your Gmail account and then, depending on the values of some columns, will do different tasks.

The Spreadsheet should have the following structure: 

ID	Email	Project	Status	Mail sent	Test Score
1	username@mail.com	name_1	Submitted Test	dd/mm/yyyy hh:mm:ss	34/50

Status can be one of the following (Ordered): 
1.	Applied
2.	Online Test Sent
3.	Submitted Test
4.	Reminder Sent
5.	Interview Mail Sent
6.	Refusal Mail Sent

ID, Email, Project and Status are required while Test Score is optional.
Test Score will only appear starting from “Submitted Test” and appears in the following format: “score/total”.
Mail sent takes into account only emails sent from Datagram to the users.
Mail sent will only appear starting from “Online Test Sent”.
For simplicity, suppose there are 3 possible values for Project: name_1, name_2, name_3

You will create a spreadsheet and feed it random rows.

Your flask app will then do the following once the route has been pinged: 
1- Connect to gmail (use your own gmail, be sure to remove your credentials afterwards and not to commit it to github)
2- Open the spreadsheet (again, from your own Drive)
3- Assert that there are no critical errors (from the constraints listed above)
4- For each row, do one of the following: 
-	If Status is Applied
→ Send an email saying “Thank you for applying to [Project].”
→ Change Status to Online Test Sent
→ Change Mail sent to today’s datetime.

-	If Status is Online Test Sent & Mail sent is at least 7 days old & Test Score is empty
→ Send an email saying “You haven’t submitted your test. Everything okay?”
→ Change Status to Reminder Sent
→ Change Mail sent to today’s datetime.



-	If Status is Submitted Test & Test Score is less than half the total 
→ Send an email saying “We are sorry to tell you that you did not pass the test”
→ Change Status to Refusal Mail Sent
→ Change Mail sent to today’s datetime.

-	If Status is Submitted Test & Test Score is more than half the total 
→ Send an email saying “Congratulations for passing the test. You’ll have an interview with _____” **
→ Change Status to Interview Mail Sent
→ Change Mail sent to today’s datetime.

5- Once the above was done, the app should send an error email if anything went wrong and a confirmation message if everything went well. The End.

** Make a dictionary containing a unique name for each unique project. 
