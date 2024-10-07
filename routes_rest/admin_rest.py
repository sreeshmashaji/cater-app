
import json
import mimetypes
import time
from typing import Annotated
from bson import ObjectId
from dotenv import dotenv_values
from fastapi import Body, File, Form, HTTPException, UploadFile, status,APIRouter,Depends,BackgroundTasks
from fastapi_limiter.depends import RateLimiter
from config.database import db
from schemas import admin_schema
import utils, oauth2
from services import emailvalidation,verify_password,phone_no_validation
from server import send_mail,otp_api
from config.path import cater_path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import boto3
from geopy.geocoders import Nominatim
import openrouteservice,googlemaps
import strawberry

geolocator = Nominatim(user_agent="my_app")
client = openrouteservice.Client(key='5b3ce3597851110001cf6248849362c01bdb4ee1b0597d2b71832179')

gmaps = googlemaps.Client(key='AIzaSyCD42xKGUAkd-0gWIPzAZzNHtNVZGYCS-4')

auth_scheme = HTTPBearer()



router=APIRouter(prefix=cater_path)


env = dict(dotenv_values(".env_admin"))

AWS_ACCESS_KEY_ID = env.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION_NAME = env.get("AWS_REGION_NAME")
S3_BUCKET_NAME = env.get("S3_BUCKET_NAME")
S3_IMAGE_LINK=env.get("S3_IMAGE_LINK")


s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)





collection = db.register
























#register new one

@router.post('',tags=["Authorization"],summary=" Register a new cater with non-existing email, phonenumber, firstname, lastname, password (role will be admin)")
async def add_user(data:admin_schema.Register,background_task:BackgroundTasks):
    try:
        if not emailvalidation.validate_email(data.email):
            raise HTTPException(status_code=400, detail="Invalid Email Address")

        existing_user = collection.find_one({'email': data.email})
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email Already Exists")
        if len(data.password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")
        
        is_valid, message = verify_password.validate_password(data.password)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
        
        if len(data.firstName) < 3:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please provide a valid name")
        phone_number=data.phoneNumber
        # cleaned_phone_number = phone_no_validation.validate_phone_number(data.phoneNumber)
        if not phone_number.isdigit():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number must contain only digits")
        if   len(phone_number) > 10:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Phone Number")

        data.password=utils.hash(data.password)
        print(data.password)
        update_data=admin_schema.RegisterSave(
        firstName= data.firstName,
        lastName= data.lastName ,
        email=data.email,
        password=data.password,
        phoneNumber=data.phoneNumber 
        

        )
        data= collection.insert_one(update_data.__dict__)
        resultdata= collection.find_one({'_id':data.inserted_id})
        resultdata["_id"]=str(resultdata["_id"])
        if not resultdata:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Sorry Operation Failed")
        
        background_task.add_task(send_mail.sendMail,resultdata["email"],"register" )
        # send_mail.sendMail(resultdata["email"],"register")
        return {"message":"success","data":resultdata}
    except Exception as e:
        raise e






@router.get('/{id}',tags=["Dashboard(Cater)"],summary="  Fetching  registered cater by id")

async def geting(id:str,user=Depends(oauth2.verify_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
        print("inside caters get")
        data = collection.find_one({"_id":ObjectId(id)})
        if user["user_id"]!=id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")

        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
        data["_id"]=str(data["_id"])
        return data
    except Exception as e:
        raise e




# ,dependencies=[Depends(RateLimiter(times=2, seconds=5))]

@router.post('/login' ,tags=["Authorization"],summary="Cater login with registered email , password and role(admin or sub-admin), If login successfull , otp will send to cater's email")
async def login(data: Annotated[
        admin_schema.Login, 
        Body(
            examples=[
                {
                    "role": "admin",
                    "email": "email-aaaamtj232gfdwwrcefmsdk7xa@axomium.slack.com",
                    "password": "Qwerty@1234"
                    
                }
            ],
        ),
    ],background_task:BackgroundTasks):
   
     try:
        if data.role=="admin":
            user=collection.find_one({"email":data.email})
            if not user:
              raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid Credentials")
            user_id=user["_id"]
            name=user["firstName"]
            

        if data.role=="sub-admin":
            user=db.sub_admin.find_one({"email":data.email})
            if not user:
              raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid Credentials")
            user_id=user["ownerId"]
            name=user["name"]
            
        print(user)
         
        if not utils.verify(data.password,user['password']):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid Credentials")
        
        if user["status"]==False:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid login")
             
             

        
        token=oauth2.create_access_token({"email":data.email,"user_id":str(user_id),"name":name},user['role'])
        
        #  send_mail.sendMail(user["email"],"login")
        background_task.add_task(send_mail.sendMail,user["email"],"login" )
            
        return {"token":token,"user_id":str(user_id)}
     except Exception as e:
         raise e



@router.post('/admin-reset-password',tags=["Dashboard(Cater)"],summary="Caters can change their current password into new one ")
def reset(data:admin_schema.Reset,user=Depends(oauth2.verify_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
            existing_user = collection.find_one({'email': user["email"]})
            if not existing_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
            if not utils.verify(data.currentPassword,existing_user['password']):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Incorrect Password")
            if data.newPassword != data.confirmPassword:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password Mismatch")
            hashpass=utils.hash(data.newPassword)
            existing_user["password"]=hashpass
            collection.update_one({"email":user["email"]},{'$set':{"password":hashpass}})
            print(existing_user)
            return "Password Updated"
    except Exception as e:
           raise e



# @router.delete('', tags=["Dashboard(Cater)"], summary="Delete cater by caterId",deprecated=True)
# async def delete_one(id: str):
    
#     resultdata = collection.find_one({'_id': ObjectId(id)})
    
#     if not resultdata:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Doesn't Exists")
        
#     collection.delete_one({"_id": ObjectId(id)})  
#     return "User Removed"




@router.post('/verify-email-otp',tags=["Authorization"],summary="After login a verification otp will be send to the login mail ...we can verify that otp using this api ")
def verify_email(data:admin_schema.VerifyEmailOtp):
        try:
            data=otp_api.verify(data.otp,data.toMail)
            print("success ::",data)
            if data=="pending":
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="OTP Verification Pending")
            elif data=="approved":
                return {"detail":data}
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="OTP Expired")
        except Exception as e:
            raise e
      
@router.post('/forgot-password',tags=["Authorization"],summary="send mail to corresponding email address with reset password link")
def forgot_password(data:admin_schema.ForgotPassword,background_task:BackgroundTasks):
     try:   
            user=collection.find_one({"email":data.email})
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
            token= oauth2.create_reset_token({"email":data.email})
            print(token)
            background_task.add_task(send_mail.sendMail,data.email,"forgot-password",token )
            
            return {"message":"email sent","reset_token":token}
     except Exception as e:
           raise e



@router.post('/reset-password',tags=["Authorization"],summary=" api working with  reset password  link send through forgot password email")
def pasword_reset(data:admin_schema.PasswordRest,email=Depends(oauth2.verify_reset_token),token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
        try:
                if email != data.email:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Email mismatch")
                if data.newPassword ==data.confirmPassword:
                    existing_user=collection.find_one({"email":email})
                    hashpass=utils.hash(data.newPassword)
                    existing_user["password"]=hashpass
                    collection.update_one({"email":email},{'$set':{"password":hashpass}})
                    print(existing_user)
                    black_list=admin_schema.BlackList(resetToken=token.credentials)
                    db.black_list.insert_one(black_list.__dict__)
                    return "Password Updated"
                else:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password mismatch")
        except Exception as e:
             raise e




@router.post('/resend-link',tags=["Authorization"],summary="resend otp when 1st attempt failed")
def resend_otp(data:admin_schema.ForgotPassword,background_task:BackgroundTasks):
     try:
            start_time = time.time()  

            user=collection.find_one({"email":data.email})
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
            token= oauth2.create_reset_token({"email":data.email})
            print(token)
            background_task.add_task(send_mail.sendMail,data.email,"forgot-password",token )
            end_time = time.time()  
            total_time = end_time - start_time  
            print(f"Total time taken: {total_time} seconds")
            return "email sent"
     except Exception as e:
          raise e

# @router.post('/resend-link',tags=["Authorization"],summary="resend otp when 1st attempt failed")
# def resend_otp(data:admin_schema.ForgotPassword):
#     start_time = time.time()  
    
#     user = collection.find_one({"email": data.email})
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
#     token = oauth2.create_reset_token({"email": data.email})
#     print(token)
    
#     send_mail.sendMail(data.email, "forgot-password", token)
    
#     end_time = time.time()  
#     total_time = end_time - start_time  
#     print(f"Total time taken: {total_time} seconds")
    
#     return "email sent"

# @router.post('/block',tags=["Dashboard(Cater)"],summary="Block User  by id  (change status to false)")
# def  block_cater(id:str):
#     try:
#         cater=collection.find_one({"_id":ObjectId(id)})
#         if not cater:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")
#         collection.update_one({"_id":ObjectId(id)},{'$set':{"status":False}})
#         return {"message":"user blocked"}
#     except Exception as e:
#          raise e
    
    
@router.put('',tags=["Dashboard(Cater)"],summary="edit cater")
async def edit_cater(
    id: str = Form(...), 
    firstName: str = Form(None),
    lastName: str = Form(None),
    email: str = Form(None),
    
    phoneNumber: str = Form(None),
    profilePicture: UploadFile = File(None),
    token:HTTPAuthorizationCredentials=Depends(auth_scheme),
    user=Depends(oauth2.verify_access_token)
    
):
    try:
        existing_user = collection.find_one({'_id': ObjectId(id)})
        if not existing_user:
            raise HTTPException(status_code=404, detail="Caterer not found")
        
        if ObjectId(user["user_id"])!=existing_user["_id"]:
            raise HTTPException(status_code=403, detail="only cater can edit")
        update_data = {}

        if firstName is not None:
            update_data['firstName'] = firstName
        if lastName is not None:
            update_data['lastName'] = lastName
        if email is not None:
            update_data['email'] = email
        
        if phoneNumber is not None:
            update_data['phoneNumber'] = phoneNumber

        if profilePicture is not None:
            contents = await profilePicture.read()
            content_type, _ = mimetypes.guess_type(profilePicture.filename)

            s3_client.put_object(
                Bucket=S3_BUCKET_NAME, Key=profilePicture.filename, Body=contents, ContentType=content_type
            )
            image_link = f"{S3_IMAGE_LINK}{profilePicture.filename}"
            update_data["profilePicture"] = image_link

        
               
        print(update_data)
        result = collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})

        if not result:
            raise HTTPException(status_code=400, detail="Failed to update caterer")

        updated_caterer = collection.find_one({'_id': ObjectId(id)})
        updated_caterer["_id"] = str(updated_caterer["_id"])
        return {"message": "Caterer updated successfully", "data": updated_caterer}
    except Exception as e:
         raise e



@router.get("/location/coordinates/{location}",tags=["Dashboard(Cater)"])
def get_coordinates(location:str,):
     try:
        location_data = geolocator.geocode(location)
        latitude = location_data.latitude
        longitude = location_data.longitude
        return {"longitude":longitude,"latitude":latitude}
     except (AttributeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to geocode location")
    
    
@router.get('/cuisine/all')
async def get_categories():
    try:
        data = list(db.cuisine.find().limit(10000))  
        data = [{**doc, '_id': str(doc['_id'])} for doc in data]
       
        return data
    except Exception as e:
        raise e
    


    