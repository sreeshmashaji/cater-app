from httpx import AsyncClient
import pytest,sys,os
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from main import app

client = TestClient(app)

mock_user={"email":"bonny@gmail.com"}

async def get_auth():
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            
            "email": "eva@gmail.com",
            "password": "Qwerty@1234"
        }
        
        response = await client.post("/customers/customer-login", json=payload)
        if response!=200:
            print(response.json())
        assert response.status_code == 200
        token = response.json().get("token")
        assert token is not None
        
        return {"token":response.json()["token"],"customer_id":response.json()["customer_id"]}
    
async def get_auth2():
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "role": "admin",
            "email": "email-aaaamtj232gfdwwrcefmsdk7xa@axomium.slack.com",
            "password": "Qwerty@1234"
        }
        
        response = await client.post("/caters/login", json=payload)
        if response!=200:
            print(response.json())
        assert response.status_code == 200
        token = response.json().get("token")
        assert token is not None
        
        return {"token":response.json()["token"],"user_id":response.json()["user_id"]}





# @pytest.mark.asyncio
# async def test_add_customer():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         payload={
#             "email": mock_user["email"],
#             "firstName": "Athul",
#             "lastName": "Ajith",
#             "password": "Qwerty@1234",
#             "phoneNumber": "908976654",
#             "avatarId": "QWErt3g5t"
#             }
#         response=await ac.post("/customers",json=payload)
#         print(response.json())
#         assert response.status_code==200

#         payload={
#             "email": mock_user["email"],
#             "firstName": "Athul",
#             "lastName": "Ajith",
#             "password": "Qwerty@1234",
#             "phoneNumber": "908976654",
#             "avatarId": "QWErt3g5t"
#             }
#         response=await ac.post("/customers",json=payload)
#         print(response.json())
#         assert response.status_code==400
#         assert response.json()["detail"]=="Email Already Exists"

#         payload={
#             "email": "agmail.com",
#             "firstName": "Athul",
#             "lastName": "Ajith",
#             "password": "Qwerty@1234",
#             "phoneNumber": "908976654",
#             "avatarId": "QWErt3g5t"
#             }
#         response=await ac.post("/customers",json=payload)
#         print(response.json())
#         assert response.status_code==400
#         assert response.json()["detail"]=="Invalid Email Address"


#         payload={
#             "email": "a2@gmail.com",
#             "firstName": "Athul",
#             "lastName": "Ajith",
#             "password": "@1234",
#             "phoneNumber": "908976654",
#             "avatarId": "QWErt3g5t"
#             }
#         response=await ac.post("/customers",json=payload)
#         print(response.json())
#         assert response.status_code==400
#         assert response.json()["detail"]=="Password must be at least 8 characters long"


#         payload={
#             "email": "a2@gmail.com",
#             "firstName": "Athul",
#             "lastName": "Ajith",
#             "password": "Qwerty@1234",
#             "phoneNumber": "908978888888888",
#             "avatarId": "QWErt3g5t"
#             }
#         response=await ac.post("/customers",json=payload)
#         print(response.json())
#         assert response.status_code==400
#         assert response.json()["detail"]=="Invalid Phone Number"

#         payload={
#             "email": "a2@gmail.com",
#             "firstName": "Athul",
#             "lastName": "Ajith",
#             "password": "Qwerty@1234",
#             "phoneNumber": "90898hjg8",
#             "avatarId": "QWErt3g5t"
#             }
#         response=await ac.post("/customers",json=payload)
#         print(response.json())
#         assert response.status_code==400
#         assert response.json()["detail"]=="Phone number must contain only digits"




# @pytest.mark.asyncio
# async def test_login_user():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         payload={
#             "email":mock_user["email"],
#             "password":"Qwerty@1234"
#         }

#         response=await ac.post("customers/customer-login",json=payload)
#         print(response.json())
#         assert response.status_code==200
#         assert "token" in response.json()

#         payload={
#             "email":"ath@gmail.com",
#             "password":"Qwerty@1234"
#         }

#         response=await ac.post("customers/customer-login",json=payload)
#         print(response.json())
#         assert response.status_code==403
#         assert response.json()["detail"]=="Invalid credentials"

#         payload={
#             "email":mock_user["email"],
#             "password":"Qwty@1234"
#         }

#         response=await ac.post("customers/customer-login",json=payload)
#         print(response.json())
#         assert response.status_code==403
#         assert response.json()["detail"]=="Invalid credentials"


# @pytest.mark.asyncio
# async def test_get_customer():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         data=await get_auth()
#         token=data["token"]
#         customer_id=data["customer_id"]

#         response=await ac.get(f'/customers/{customer_id}',headers={"Authorization":f"Bearer {token}"})
#         print(response.json())
#         assert response.status_code==200

#         response=await ac.get(f'/customers/665d54ab2902895f8d1e7226',headers={"Authorization":f"Bearer {token}"})
#         print(response.json())
#         assert response.status_code==403
#         assert response.json()["detail"]=="Not allowed"


    
# @pytest.mark.asyncio
# async def test_delete_customer():
#     async with AsyncClient(app=app, base_url="http://test") as ac:

#         payload={
#             "email": "n@gmail.com",
#             "firstName": "Athul",
#             "lastName": "Ajith",
#             "password": "Qwerty@1234",
#             "phoneNumber": "908976654",
#             "avatarId": "QWErt3g5t"
#             }
#         response=await ac.post("/customers",json=payload)
#         payload={
#             "email": "n@gmail.com",
#             "password": "Qwerty@1234",
#         }

#         response=await ac.post("customers/customer-login",json=payload)
#         token=response.json()["token"]
#         customer_id=response.json()["customer_id"]
#         response=await ac.delete(f"/customers/{customer_id}",headers={"Authorization":f"Bearer {token}"})
#         assert response.status_code==200


        
     
# @pytest.mark.asyncio
# async def test_rest_password():
#     async with AsyncClient(app=app,base_url='http://test')as ac:
#         data=await get_auth()
#         token=data["token"]
#         reset_response=await ac.post("/customers/customer-reset-password",json={
            
#                     "currentPassword": "Qwerty@1234",
#                     "newPassword": "Qwerty@1234",
#                     "confirmPassword": "Qwerty@1234"

#         },headers={"Authorization":f"Bearer {token}"})
#         if reset_response.status_code != 200:
#             print("Response status code:", reset_response.status_code)
#             print("Response content:", reset_response.json())
#         assert reset_response.status_code == 200

#         response=await ac.post("/customers/customer-reset-password",json={
            
#                     "currentPassword": "Qwert@1234",
#                     "newPassword": "Qwerty@1234",
#                     "confirmPassword": "Qwerty@1234"

#         },headers={"Authorization":f"Bearer {token}"})
#         assert response.status_code==400
#         assert response.json()["detail"]=="Incorrect Password"

#         response=await ac.post("/customers/customer-reset-password",json={
            
#                     "currentPassword": "Qwerty@1234",
#                     "newPassword": "Qwert@1234",
#                     "confirmPassword": "Qwerty@1234"

#         },headers={"Authorization":f"Bearer {token}"})
#         assert response.status_code==400
#         assert response.json()["detail"]=="Password Mismatch"


# # @pytest.mark.asyncio
# # async def test_verify_email_otp():
# #     async with AsyncClient(app=app, base_url="http://test") as ac:
# #         otp_data = {"otp": "654321", "toMail": "sreeshma3023@gmail.com"}
# #         response = await ac.post("/caters/verify-email-otp", json=otp_data)
# #         assert response.status_code == 404
# #         assert response.json()["detail"] == "OTP Verification Pending"
        
# #         otp_data = {"otp": "798161", "toMail":"sreeshma3023@gmail.com"}
# #         response = await ac.post("/caters/verify-email-otp", json=otp_data)
# #         assert response.status_code == 200
# #         assert response.json()["detail"] == "approved"

# #         otp_data = {"otp": "000000", "toMail":"sreeshma3023@gmail.com"}
# #         response = await ac.post("/caters/verify-email-otp", json=otp_data)
# #         assert response.status_code == 404
# #         assert response.json()["detail"] == "OTP Expired"
        


# @pytest.mark.asyncio
# async def test_forgot_and_reset_password():
#     async with AsyncClient(app=app, base_url="http://test") as ac:


#         forgot_response=await ac.post("/customers/forgot-password", json={"email":mock_user["email"]})
#         if forgot_response.status_code != 200:
#             print("Response status code:", forgot_response.status_code)
#             print("Response content:", forgot_response.json())
#         assert forgot_response.status_code == 200
#         reset_token=forgot_response.json()["reset_token"]
#         forgot_response=await ac.post("/customers/forgot-password", json={"email":"non-exist@gmail.com"})
#         assert forgot_response.status_code == 404
#         assert forgot_response.json()["detail"]=="User not found"
#         payload={"email": "non@gmail.com","newPassword": "Qwerty@12", "confirmPassword": "Qwerty@12"}

#         reset_response=await ac.post("/customers/reset-password", json=payload,headers={"Authorization":f"Bearer {reset_token}"})
#         assert reset_response.status_code==401
#         assert reset_response.json()["detail"]=="Email mismatch"

#         payload={"email": mock_user["email"],"newPassword": "Qwert@12", "confirmPassword": "Qwerty@12"}

#         reset_response=await ac.post("/customers/reset-password", json=payload,headers={"Authorization":f"Bearer {reset_token}"})
#         assert reset_response.status_code==400
#         assert reset_response.json()["detail"]=="Password mismatch"
        
#         payload={"email": mock_user["email"],"newPassword": "Qwerty@1234", "confirmPassword": "Qwerty@1234"}
#         reset_response=await ac.post("/customers/reset-password", json=payload,headers={"Authorization":f"Bearer {reset_token}"})
#         if reset_response.status_code != 200:
#             print("Response status code:", reset_response.status_code)
#             print("Response content:", reset_response.json())
#         assert reset_response.status_code==200
#         assert reset_response.json()=="Password Updated"



# @pytest.mark.asyncio
# async def test_resend_link():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response=await ac.post("/customers/resend-link", json={"email":mock_user["email"]})
#         print(response.json())
#         assert response.status_code==200
#         assert response.json()=="email sent"

#         response=await ac.post("/customers/resend-link", json={"email":"ak@gmail.com"})
#         print(response.json())
#         assert response.status_code==404
#         assert response.json()["detail"]=="User not found"



@pytest.mark.asyncio
async def test_search_location():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response=await ac.get("/customers/restaurants/Al Barsha First", params={"offset":0,"limit":30})
        print(response.json())
        assert response.status_code==200
        response=await ac.get("/customers/restaurants/Alhhh ", params={"offset":0,"limit":30})
        print(response.json())
        assert response.status_code==400
        assert response.json()["detail"]=="Failed to geocode location"




# @pytest.mark.asyncio
# async def test_search_restaurant():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         data=await get_auth2()
#         token=data["token"]
#         user_id=data["user_id"]
#         payload = {
#            "name": "Test Restaurant",
#             "location": "Mumbai",
#             "contactNumber": "1234567890",
#             "business_hours": '{"Monday": "09:00-18:00"}',
#             "holidays": ["2024-12-25"],
#         }
#         response = await ac.post("caters/restaurants", data=payload,headers={"Authorization":f"Bearer {token}"})
#         resto_id=response.json()["data"]["_id"]
#         form_data = {
#             "restaurantId": [resto_id],
#             "categoryId": "66546b91decb8588517b3dcd",
#             "name": "Test Menu",
#             "desc": "Test Description",
#             "price": 10.0,
#             "minimumServe": 1,
#             "type": "Test Type",
#         }
#         response = await ac.post("/caters/restaurants/menus", data=form_data, headers={"Authorization": f"Bearer {token}"})
#         print(response.json())
#         menu_id=response.json()["data"]["_id"]
#         response = await ac.get(f"customers/restaurant-details/{resto_id}")
#         print(response.json())
#         assert  response.status_code==200
#         response = await ac.get(f"customers/restaurant-details/66546b91decb8588517b3dcd")
#         assert  response.status_code==404
#         assert response.json()["detail"]=="Restaurant not found"




# @pytest.mark.asyncio
# async def test_search_menu():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         data=await get_auth2()
#         token=data["token"]
#         user_id=data["user_id"]
#         payload = {
#            "name": "Test Restaurant",
#             "location": "Mumbai",
#             "contactNumber": "1234567890",
#             "business_hours": '{"Monday": "09:00-18:00"}',
#             "holidays": ["2024-12-25"],
#         }
#         response = await ac.post("caters/restaurants", data=payload,headers={"Authorization":f"Bearer {token}"})
#         resto_id=response.json()["data"]["_id"]
#         form_data = {
#             "restaurantId": [resto_id],
#             "categoryId": "66546b91decb8588517b3dcd",
#             "name": "Test Menu",
#             "desc": "Test Description",
#             "price": 10.0,
#             "minimumServe": 1,
#             "type": "Test Type",
#         }
#         response = await ac.post("/caters/restaurants/menus", data=form_data, headers={"Authorization": f"Bearer {token}"})
#         print(response.json())
#         menu_id=response.json()["data"]["_id"]
#         response=await ac.get(f"/customers/menu-details/{menu_id}",params={"restaurantId":resto_id})
#         print(response.json())
#         assert response.status_code==200
#         response=await ac.get(f"/customers/menu-details/66546b91decb8588517b3dcd",params={"restaurantId":resto_id})
#         assert response.status_code==404
#         assert response.json()["detail"]=="No menus found"


