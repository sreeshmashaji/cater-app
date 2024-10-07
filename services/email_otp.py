from fastapi import FastAPI



import os
from twilio.rest import Client
app=FastAPI()



# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

auth_token = ''
account_sid = ""
verify_sid = ""
verified_email = ""
verified_email2=""

client = Client(account_sid, auth_token)

verification = client.verify.v2.services(verify_sid) \
  .verifications \
  .create(to=verified_email2, channel="email")
print(verification.status)

otp_code = input("Please enter the OTP:")

verification_check = client.verify.v2.services(verify_sid) \
  .verification_checks \
  .create(to=verified_email2, code=otp_code)
print(verification_check.status)

