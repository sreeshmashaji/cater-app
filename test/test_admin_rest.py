import typing
from dotenv import dotenv_values
from fastapi import status
from fastapi_limiter import FastAPILimiter
import pytest
from unittest.mock import patch
from httpx import ASGITransport, AsyncClient
import sys,os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from main import app
from bson import ObjectId
from config.database import db
import utils
from twilio.rest import Client
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from server import otp_api
import redis.asyncio as redis
client=TestClient(app)



mock_user = {
    
    "email": "evii@gmail.com",
    
    
}


      


@pytest.mark.asyncio
async def test_add_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/caters",
            json={
                "firstName": "Test",
                "lastName": "User",
                "email": mock_user["email"],
                "password": "Qwerty@1234",
                "phoneNumber": "1234567890"
            }
        )
        if response.status_code != 200:
            print("Response status code:", response.status_code)
            print("Response content:", response.json())
        assert response.status_code == 200
        
        response = await ac.post(
                "/caters",
                json={
                    "firstName": "Test",
                    "lastName": "User",
                    "email":" g.gmail.com",
                    "password": "Qwerty@1234",
                    "phoneNumber": "1234567890"
                }
            )

        assert response.status_code == 400
        assert response.json()["detail"]=="Invalid Email Address"






@pytest.mark.asyncio
async def test_login_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "role": "admin",
            "email": "sreeshma3023@gmail.com",
            "password": "Qwerty@1234"
        }
        
        response = await client.post("caters/login", json=payload)
        
        print("Response status code:", response.status_code)
        print("Response content:", response.content)
        
        assert response.status_code == 200
        assert "token" in response.json()

        payload = {
            "role": "admin",
            "email": "sreeshma3023@gmail.com",
            "password": "Qwerty1234"
        }
        
        response = await client.post("caters/login", json=payload)
        assert response.status_code==400
        assert response.json()["detail"]=="Invalid Credentials"


        payload = {
            "role": "admin",
            "email": "sreeshma303@gmail.com",
            "password": "Qwerty@1234"
        }
        
        response = await client.post("caters/login", json=payload)
        assert response.status_code==400
        assert response.json()["detail"]=="Invalid Credentials"



@pytest.mark.asyncio
async def test_rest_password():
    async with AsyncClient(app=app,base_url='http://test')as ac:
        login_response=await ac.post("/caters/login",json={
            "role": "admin",
            "email": "sreeshma3023@gmail.com",
            "password": "Qwerty@1234"
        })
        token=login_response.json()["token"]
        reset_response=await ac.post("/caters/admin-reset-password",json={
            
                    "currentPassword": "Qwerty@1234",
                    "newPassword": "Qwerty@1234",
                    "confirmPassword": "Qwerty@1234"

        },headers={"Authorization":f"Bearer {token}"})
        if reset_response.status_code != 200:
            print("Response status code:", reset_response.status_code)
            print("Response content:", reset_response.json())
        assert reset_response.status_code == 200

        reset_response=await ac.post("/caters/admin-reset-password",json={
            
                    "currentPassword": "Qwert@1234",
                    "newPassword": "Qwerty@1234",
                    "confirmPassword": "Qwerty@1234"

        },headers={"Authorization":f"Bearer {token}"})
        assert reset_response.status_code==400
        assert reset_response.json()["detail"]=="Incorrect Password"

        reset_response=await ac.post("/caters/admin-reset-password",json={
            
                    "currentPassword": "Qwerty@1234",
                    "newPassword": "Qwert@1234",
                    "confirmPassword": "Qwerty@1234"

        },headers={"Authorization":f"Bearer {token}"})
        assert reset_response.status_code==400
        assert reset_response.json()["detail"]=="Password Mismatch"

# @pytest.mark.asyncio
# async def test_verify_email_otp():
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
#         otp_data = {"otp": "654321", "toMail": "sreeshma3023@gmail.com"}
#         response = await ac.post("/caters/verify-email-otp", json=otp_data)
#         assert response.status_code == 404
#         assert response.json()["detail"] == "OTP Verification Pending"
        
#         otp_data = {"otp": "798161", "toMail":"sreeshma3023@gmail.com"}
#         response = await ac.post("/caters/verify-email-otp", json=otp_data)
#         assert response.status_code == 200
#         assert response.json()["detail"] == "approved"

#         otp_data = {"otp": "000000", "toMail":"sreeshma3023@gmail.com"}
#         response = await ac.post("/caters/verify-email-otp", json=otp_data)
#         assert response.status_code == 404
#         assert response.json()["detail"] == "OTP Expired"



@pytest.mark.asyncio
async def test_forgot_and_reset_password():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        forgot_response=await ac.post("/caters/forgot-password", json={"email":"sreeshma3023@gmail.com"})
        if forgot_response.status_code != 200:
            print("Response status code:", forgot_response.status_code)
            print("Response content:", forgot_response.json())
        assert forgot_response.status_code == 200
        reset_token=forgot_response.json()["reset_token"]
        forgot_response=await ac.post("/caters/forgot-password", json={"email":"non-exist@gmail.com"})
        assert forgot_response.status_code == 404
        assert forgot_response.json()["detail"]=="User not found"
        payload={"email": "non@gmail.com","newPassword": "Qwerty@12", "confirmPassword": "Qwerty@12"}

        reset_response=await ac.post("/caters/reset-password", json=payload,headers={"Authorization":f"Bearer {reset_token}"})
        assert reset_response.status_code==401
        assert reset_response.json()["detail"]=="Email mismatch"
        payload={"email": "sreeshma3023@gmail.com","newPassword": "Qwert@12", "confirmPassword": "Qwerty@12"}

        reset_response=await ac.post("/caters/reset-password", json=payload,headers={"Authorization":f"Bearer {reset_token}"})
        assert reset_response.status_code==400
        assert reset_response.json()["detail"]=="Password mismatch"
        payload={"email": "sreeshma3023@gmail.com","newPassword": "Qwerty@1234", "confirmPassword": "Qwerty@1234"}
        reset_response=await ac.post("/caters/reset-password", json=payload,headers={"Authorization":f"Bearer {reset_token}"})
        if reset_response.status_code != 200:
            print("Response status code:", reset_response.status_code)
            print("Response content:", reset_response.json())
        assert reset_response.status_code==200
        assert reset_response.json()=="Password Updated"
        

@pytest.mark.asyncio
async def test_block_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        
        login_response = await ac.post("/caters/login", json={
            "role": "admin",
            "email": "sreeshma3023@gmail.com",
            "password": "Qwerty@1234"
        })
        token = login_response.json()["token"]
        user_id = login_response.json()["user_id"]
        print("userId",user_id)
       
        response = await ac.post("/caters/block", params={"id": user_id}, headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200:
            print("Response status code:", response.status_code)
            print("Response content:", response.json())
        assert response.status_code == 200
        assert response.json()["message"] == "user blocked"
        response = await ac.post("/caters/block", params={"id": "666029fcf99332ffe3ed43eb"}, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code==404
        assert response.json()["detail"] == "user not found"


      
@pytest.mark.asyncio
async def test_edit_cater():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        
        login_response = await ac.post("/caters/login", json={
             "role": "admin",
            "email": "email-aaaamtj232gfdwwrcefmsdk7xa@axomium.slack.com",
            "password": "Qwerty@1234"
        })
        token = login_response.json()["token"]
        user_id = login_response.json()["user_id"]
        # user_id="665d54ab2902895f8d1e7226"
        # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBbGFjYXRlciIsImV4cCI6MTcxNzY4Mzg3NCwicm9sZSI6ImFkbWluIn0.NDKvxaK_QQONsCobyn23xdUSJ5RbhT0Uo7VTgG7qGMw"
        print("userId",user_id,token)
        test_image_path=r"C:\Users\Sreeshma\Downloads\axo.png"
        with open(test_image_path, 'rb') as image_file:
             image_content = image_file.read()

        form_data={"id":user_id}
        files = {'profilePicture': (test_image_path, image_content)}
        edit_response = await ac.put("/caters", data=form_data, files=files,headers={"Authorization":f"Bearer {token}"})
        if edit_response.status_code != 200:
            print("Response status code:", edit_response.status_code)
            print("Response content:", edit_response.json())
        if edit_response.status_code == 200:
            print("Response status code:", edit_response.status_code)
            print("Response content:", edit_response.json())
        assert edit_response.status_code == 200
        assert edit_response.json()["message"]=="Caterer updated successfully"
        assert "profilePicture" in edit_response.json()["data"]
        

        form_data={"id":user_id,"firstName":"ALACATER","lastName":"CATERING","phoneNumber":"908765543"}
        edit_response = await ac.put("/caters", data=form_data,headers={"Authorization":f"Bearer {token}"})
        if edit_response.status_code != 200:
            print("Response status code:", edit_response.status_code)
            print("Response content:", edit_response.json())
        if edit_response.status_code == 200:
            print("Response status code:", edit_response.status_code)
            print("Response content:", edit_response.json())
        assert  edit_response.json()["data"]["firstName"]==form_data["firstName"]
        assert  edit_response.json()["data"]["lastName"]==form_data["lastName"]

        assert  edit_response.json()["data"]["phoneNumber"]==form_data["phoneNumber"]



        form_data={"id":"665d54ab2902895f8d1b7226","firstName":"ALACATER","lastName":"CATERING","phoneNumber":"908765543"}
        edit_response = await ac.put("/caters", data=form_data,headers={"Authorization":f"Bearer {token}"})
        assert edit_response.status_code==404
        assert edit_response.json()["detail"]=="Caterer not found"

        form_data={"id":"665d54ab2902895f8d1b7226","firstName":"ALACATER","lastName":"CATERING","phoneNumber":"908765543"}
        edit_response = await ac.put("/caters", data=form_data,headers={"Authorization":f"Bearer {token}"})
        assert edit_response.status_code==404
        assert edit_response.json()["detail"]=="Caterer not found"






       