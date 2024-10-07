from httpx import AsyncClient
import pytest,sys,os
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from main import app

client = TestClient(app)



async def get_auth():
    
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
    
async def get_sub_auth():
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "role": "sub-admin",
            "email": "sreesh@gmail.com",
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
# async def test_add_sub_admin():
#     async with AsyncClient(app=app,base_url="http://test") as ac:
#         # data=await get_auth()
#         # token=data["token"]
#         # user_id=data["user_id"]
#         token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODcxNzcxMCwicm9sZSI6ImFkbWluIn0.lXmFbvuLa79cohzQ_iRc22wYMdJEw7Pq5i6VNr519eE"
        
#         user_id="665d54ab2902895f8d1e7226"
#         payload={
#             "email": "sreesh@gmail.com",
#             "name": "sreeshma",
#             "password": "Qwerty@1234"
#         }
#         response=await ac.post("/sub-admin",json=payload,headers={"Authorization":f"Bearer {token}"})
#         print(response.json())
#         assert response.status_code==200

#         payload={
#             "email": "sreeshmagmail.com",
#             "name": "sreeshma",
#             "password": "Qwerty@1234"
#         }
#         response=await ac.post("/sub-admin",json=payload,headers={"Authorization":f"Bearer {token}"})
#         print(response.json())
#         assert response.status_code==400
#         assert response.json()["detail"]=="Invalid Email Address"

#         payload={
#             "email": "email-aaaamtj232gfdwwrcefmsdk7xa@axomium.slack.com",
#             "name": "sreeshma",
#             "password": "Qwerty@1234"
#         }
#         response=await ac.post("/sub-admin",json=payload,headers={"Authorization":f"Bearer {token}"})
#         print(response.json())
#         assert response.status_code==400
#         assert response.json()["detail"]=="Email is registered as cater"

#         payload={
#             "email": "sreeshma@gmail.com",
#             "name": "sreeshma",
#             "password": "Qwerty@1234"
#         }
#         response=await ac.post("/sub-admin",json=payload,headers={"Authorization":f"Bearer {token}"})
#         print(response.json())
#         assert response.status_code==400
#         assert response.json()["detail"]=="Email Already Exists"

#         data= await get_sub_auth()
#         token=data["token"]

#         payload={
#             "email": "sreeshma@gmail.com",
#             "name": "sreeshma",
#             "password": "Qwerty@1234"
#         }
#         response=await ac.post("/sub-admin",json=payload,headers={"Authorization":f"Bearer {token}"})
#         print(response.json())
#         assert response.status_code==403
#         assert response.json()["detail"]=="Please make sure you are an admin"



# @pytest.mark.asyncio
# async def test_get_sub_admin():
#     async with AsyncClient(app=app,base_url="http://test") as ac:
#         # data=await get_auth()
#         # token=data["token"]
#         # user_id=data["user_id"]
#         token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODcxNzcxMCwicm9sZSI6ImFkbWluIn0.lXmFbvuLa79cohzQ_iRc22wYMdJEw7Pq5i6VNr519eE"
        
#         user_id="665d54ab2902895f8d1e7226"
#         response=await ac.get(f"/sub-admin/{user_id}",headers={"Authorization":f"Bearer {token}"})
#         print(response.json())
#         assert response.status_code==200


# @pytest.mark.asyncio
# async def test_delete_sub_admin():
#     async with AsyncClient(app=app,base_url="http://test") as ac:
#         token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODcxNzcxMCwicm9sZSI6ImFkbWluIn0.lXmFbvuLa79cohzQ_iRc22wYMdJEw7Pq5i6VNr519eE"
        
#         user_id="665d54ab2902895f8d1e7226"
#         list=[
#              "667114f8beac9a3abc2a8d4b","667118d4b5c06f187552d506"]
#         response=await ac.delete("/sub-admin",list,headers={"Authorization":f"Bearer {token}"})

        
    
        
#delete =body 




