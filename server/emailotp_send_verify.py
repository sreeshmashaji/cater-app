from fastapi import FastAPI
from dotenv import dotenv_values
import os
from twilio.rest import Client
app=FastAPI()

env = dict(dotenv_values(".env_admin"))

auth_token = env.get('SENDGRID_AUTH_TOKEN')
account_sid =  env.get('SENDGRID_ACCOUNT_SID')
verify_sid =  env.get('SENDGRID_VERIFY_SID')
verified_email = ""
verified_email2=""

print("account",account_sid)
client = Client(account_sid, auth_token)

verification = client.verify.v2.services(verify_sid) \
  .verifications \
  .create(to=verified_email, channel="email")
print(verification.status)

otp_code = input("Please enter the OTP:")

verification_check = client.verify.v2.services(verify_sid) \
  .verification_checks \
  .create(to=verified_email, code=otp_code)
print(verification_check.status)

