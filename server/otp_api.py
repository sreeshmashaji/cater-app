
from dotenv import dotenv_values
import os
from twilio.rest import Client

env = dict(dotenv_values(".env_admin"))


auth_token = env.get('SENDGRID_AUTH_TOKEN')
account_sid =  env.get('SENDGRID_ACCOUNT_SID')
verify_sid =  env.get('SENDGRID_VERIFY_SID')

# auth_token=''
# account_sid=''



client = Client(account_sid,auth_token)

print("cli",client)



def verify(otp_code,to_mail):
    try:
        verification_check = client.verify.v2.services(verify_sid) \
        .verification_checks \
        .create(to=to_mail, code=otp_code)
        status=verification_check.status
        
        return status
    except Exception as e:
        print("error is ",e)
        return e

    



# def send_otp():
#     verification = client.verify \
#                      .v2 \
#                      .services(verify_sid) \
#                      .verifications \
#                      .create(to=verified_email, channel='email')

#     print(verification.sid)

#     return True

