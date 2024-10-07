import re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail,Content
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import dotenv_values
from twilio.rest import Client


env = dict(dotenv_values(".env_admin"))


FROM_EMAIL = env.get('SENDGRID_FROM_EMAIL')
SENDGRID_API_KEY=env.get('SENDGRID_API_KEY')

auth_token = env.get('SENDGRID_AUTH_TOKEN')
account_sid =  env.get('SENDGRID_ACCOUNT_SID')
verify_sid =  env.get('SENDGRID_VERIFY_SID')
cater_redirect_uri=env.get("CATER_RESET_PASSWORD_REDIRECT_URI")
customer_redirect_uri=env.get("CUSTOMER_RESET_PASSWORD_REDIRECT_URI")

            
    
# file_path='../sendgrid_template/reset.html'




def sendMail(to_email:str,type:str,token:str|None=None):
    pass
    # if type =="register":
    #     TEMPLATE_ID = env.get('SENDGRID_WELCOME_TEMPLATE_ID')

    #     message = Mail(
    #         from_email=FROM_EMAIL,
    #         to_emails=to_email,)
    #     message.dynamic_template_data={"twilio_message":"Register Successfully"}
    #     message.template_id=TEMPLATE_ID
    #     try:
    #         sg = SendGridAPIClient(env.get("SENDGRID_API_KEY"))
    #         print("api",env.get("SENDGRID_API_KEY"))
    #         response = sg.send(message)
    #         print(response.status_code)
    #         print(response.body)
    #         print(response.headers)
    #     except Exception as e:
    #         print(e)


    # if type=="login":
    #     try:
    #         client = Client(account_sid, auth_token)
    #         verification = client.verify.v2.services(verify_sid) \
    #         .verifications \
    #         .create(to=to_email, channel="email")
    #         print(verification.status)
    #         return True
    #     except Exception as e:
    #         print(e)

    # if type=="forgot-password":
    #     file_path = os.path.abspath(os.getcwd())+"/sendgrid_template/reset.html"
    #     with open(file_path, "r") as f:
    #         html_contents = f.read()

    #     # Use regular expressions to find and replace all occurrences of the search string.
    #     pattern = re.compile("{{reset_link}}")
    #     html_contents = pattern.sub(f"{cater_redirect_uri}email={to_email}&reset_token={token}", html_contents)
    #     message = Mail(
    #         from_email=FROM_EMAIL,
    #         to_emails=to_email,
    #         subject='Alacater Reset Password',
    #         html_content=Content("text/html",html_contents))
    #     try:
    #         sg = SendGridAPIClient(SENDGRID_API_KEY)
    #         response = sg.send(message)
    #         print(response.status_code)
    #         print(response.body)
    #         print(response.headers)
    #     except Exception as e:
    #         print(e)
    # if type=="customer-forgot-password":
    #     file_path = os.path.abspath(os.getcwd())+"/sendgrid_template/reset.html"
    #     with open(file_path, "r") as f:
    #         html_contents = f.read()

    #     # Use regular expressions to find and replace all occurrences of the search string.
    #     pattern = re.compile("{{reset_link}}")
    #     html_contents = pattern.sub(f"{customer_redirect_uri}email={to_email}&reset_token={token}", html_contents)
    #     message = Mail(
    #         from_email=FROM_EMAIL,
    #         to_emails=to_email,
    #         subject='Alacater Reset Password',
    #         html_content=Content("text/html",html_contents))
    #     try:
    #         sg = SendGridAPIClient(SENDGRID_API_KEY)
    #         response = sg.send(message)
    #         print(response.status_code)
    #         print(response.body)
    #         print(response.headers)
    #     except Exception as e:
    #         print(e)
























