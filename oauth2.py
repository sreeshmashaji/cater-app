from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import Depends, HTTPException,status
from jose import JWTError,jwt
import pytz
from schemas import admin_schema
from fastapi.security.oauth2 import OAuth2PasswordBearer
from pytz import timezone
from dotenv import dotenv_values
from config.database import db

env = dict(dotenv_values(".env_admin"))

collection=db.black_list


oauth2_schema=OAuth2PasswordBearer(tokenUrl='login')
oauth2_schema_reset=OAuth2PasswordBearer(tokenUrl='confirm-password')
outh2_customer_scheme=OAuth2PasswordBearer(tokenUrl='customer-login')
IST = timezone('Asia/Kolkata')

SECRET_KEY =env.get("JWT_SECRET_KEY")
ALGORITHM =env.get("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES :int=env.get("JWT_EXPIRE_TIME")



def create_access_token(data:dict,role:str):
    to_encode=data.copy()
    expire=datetime.now(pytz.utc)+timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire})
    to_encode.update({"role":role})
    print(to_encode)
    print(expire)
    encode_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    print(encode_jwt)
    return encode_jwt





def create_reset_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(pytz.utc)+timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire})

    print(to_encode)
    print(expire)
    encode_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    print(encode_jwt)
    return encode_jwt



def verify_admin(token: str = Depends(oauth2_schema)):
    try:
        print("Verifying token:", token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Token payload:", payload)
        if payload['role'] == "admin":
            return True
        else:
            return False
    except JWTError as e:
        print("JWT Error:", e)
        return False




def verify_access_token(token: str=Depends(oauth2_schema)):

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        print("id",id)
        if id is None:
            raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
        
        # user=db.register.find_one({"_id":ObjectId(id)})
        # user["_id"]=str(user["_id"])
        print(type(payload))
    except JWTError:
        raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    return payload




def verify_reset_token(token: str=Depends(oauth2_schema_reset)):

    try:

        reset_token=collection.find_one({"resetToken":token})
        if reset_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Reset password link expired")


        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        print(payload.get("exp"))
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
        # black_list=admin_schema.BlackList(resetToken=token)
        # collection.insert_one(black_list.__dict__)
        return email

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    



def create_customer_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(pytz.utc)+timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire})
    
    print(to_encode)
    print(expire)
    encode_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    print(encode_jwt)
    return encode_jwt











def verify_customer_access_token(token: str=Depends(outh2_customer_scheme)):

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("customer_id")
        print(id)
        
        if id is None:
            raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
        
        # user=db.register.find_one({"_id":ObjectId(id)})
        # user["_id"]=str(user["_id"])
        print(type(payload))
    except JWTError:
        raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    return payload









def create_super_admin_access_token(data:dict,role:str):
    to_encode=data.copy()
    expire=datetime.now(pytz.utc)+timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire})
    to_encode.update({"role":role})
    print(to_encode)
    print(expire)
    encode_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    print(encode_jwt)
    return encode_jwt




def verify_super_access_token(token: str=Depends(oauth2_schema)):

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("super_admin_id")
        
        if id is None:
            raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
        
        # user=db.register.find_one({"_id":ObjectId(id)})
        # user["_id"]=str(user["_id"])
        print(type(payload))
    except JWTError:
        raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    return payload


