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


@pytest.fixture
async def auth_header():
    return await get_auth()

@pytest.mark.asyncio
async def test_create_restaurant():
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
           "name": "Test Restaurant",
            "location": "Mumbai",
            "contactNumber": "1234567890",
            "business_hours": '{"Monday": "09:00-18:00"}',
            "holidays": ["2024-12-25"],
        }
        token=await get_auth()
        print(token)
        token=token["token"]
        test_image_path=r"C:\Users\Sreeshma\Downloads\axo.png"
        with open(test_image_path, 'rb') as image_file:
             image_content = image_file.read()

        
        files = {'restaurant_image': (test_image_path, image_content)}
        
        response = await client.post("caters/restaurants", data=payload,files=files,headers={"Authorization":f"Bearer {token}"})
        if response.status_code==200 :
            print("Response status code:", response.status_code)
            print("Response content:", response.content)
            
        assert response.status_code == 200
        payload = {
           "name": "Test Restaurant",
            "location": "Mumbai",
            "contactNumber": "123456000000000000",
            "business_hours": '{"Monday": "09:00-18:00"}',
            "holidays": ["2024-12-25"],
        }
        response = await client.post("caters/restaurants", data=payload,files=files,headers={"Authorization":f"Bearer {token}"})
        assert response.status_code==400
        assert response.json()["detail"]=="Invalid Phone Number"

        payload = {
           "name": "Test Restaurant",
            "location": "Mumbai",
            "contactNumber": "1234rytr",
            "business_hours": '{"Monday": "09:00-18:00"}',
            "holidays": ["2024-12-25"],
        }
        response = await client.post("caters/restaurants", data=payload,files=files,headers={"Authorization":f"Bearer {token}"})
        assert response.status_code==400
        assert response.json()["detail"]=="Phone number must contain only digits"

    

@pytest.mark.asyncio
async def test_get_restaurants():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data=await get_auth()
        user_id=data["user_id"]
        response = await ac.get(f"/caters/restaurants/{user_id}",  headers={"Authorization": f"Bearer {data["token"]}"})
        if response.status_code!=200 :
            print("Response status code:", response.status_code)
            print("Response content:", response.json())
        if response.status_code==200 :
            print("Response status code:", response.status_code)
            print("Response content:", response.json()) 
        assert response.status_code == 200
        response = await ac.get(f"/caters/restaurants/{"665aa7bf02ed5ff535205aa1"}",  headers={"Authorization": f"Bearer {data["token"]}"})
        assert response.status_code==403
        assert response.json()["detail"]=="Not allowed"



@pytest.mark.asyncio
async def test_update_restaurants():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data=await get_auth()
        user_id=data["user_id"]
        test_image_path=r"C:\Users\Sreeshma\Downloads\pexels-chanwalrus-1059943.jpg"
        with open(test_image_path, 'rb') as image_file:
             image_content = image_file.read()

        
        files = {'restaurant_image': (test_image_path, image_content)}
        form_data={"restaurant_id":"665d555e2902895f8d1e7227","name":"Al-tazaa","contactNumber":"8909877654"}
        response = await ac.put("/caters/restaurants", files=files ,data=form_data,headers={"Authorization": f"Bearer {data["token"]}"})
        if response.status_code!=200:
            print("Response status code:", response.status_code)
            print("Response content:", response.json())
        if response.status_code==200:
            print("Response status code:", response.status_code)
            print("Response content:", response.json())
        assert response.status_code==200
        

@pytest.mark.asyncio
async def test_get_restaurants_by_id():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data=await get_auth()
        user_id=data["user_id"]
        response = await ac.get(f"/caters/restaurants/{user_id}",headers={"Authorization": f"Bearer {data["token"]}"})
        print(response.json())
        assert response.status_code==200
        response = await ac.get(f"/caters/restaurants/{"665d555e2902895f8d1e7227"}",headers={"Authorization": f"Bearer {data["token"]}"})
        assert response.json()["detail"]=="Not allowed"


# @pytest.mark.asyncio
# async def test_delete_multiple():
#     async with AsyncClient(app=app,base_url="http://test") as ac:
#         data=await get_auth()
#         token=data["token"]
#         # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODM4MTg1NSwicm9sZSI6ImFkbWluIn0.M-jH3qSU2m1t7Q6NcX99K7h92uQ1KJ3U_QiqNcbEFhQ"
#          #create,pass that _id
#         payload = {
#            "name": "Test Restaurant",
#             "location": "Mumbai",
#             "contactNumber": "1234567890",
#             "business_hours": '{"Monday": "09:00-18:00"}',
#             "holidays": ["2024-12-25"],
#         }
#         response = await ac.post("caters/restaurants", data=payload,headers={"Authorization":f"Bearer {token}"})
#         _id=response.json()["data"]["_id"]
#         print(f"{_id}")
#         delete_payload={"id": [f"{_id}"]}
#         print(delete_payload)
#         response = await ac.delete("caters/restaurants", params={"id": [_id]},headers={"Authorization":f"Bearer {token}"})
#         print(response.json())
#         assert response.status_code==200
#         assert response.json()["message"]=="Restaurants Deleted"
        


@pytest.mark.asyncio
async def test_get_resto_name():
    async with AsyncClient(app=app,base_url="http://test") as ac:
        data=await get_auth()
        token=data["token"]
        user_id=data["user_id"]
        # user_id="665d54ab2902895f8d1e7226"
        # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODM4MTg1NSwicm9sZSI6ImFkbWluIn0.M-jH3qSU2m1t7Q6NcX99K7h92uQ1KJ3U_QiqNcbEFhQ"
        response = await ac.get(f"caters/restaurants/name/{user_id}",headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==200
        response = await ac.get(f"caters/restaurants/name/665d555e2902895f8d1e7227",headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==403
        assert response.json()["detail"]=="You are not the owner"




@pytest.mark.asyncio
async def test_block_resto():
    async with AsyncClient(app=app,base_url="http://test") as ac:
        data=await get_auth()
        token=data["token"]
        user_id=data["user_id"]
        # user_id="665d54ab2902895f8d1e7226"
        # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODM4MTg1NSwicm9sZSI6ImFkbWluIn0.M-jH3qSU2m1t7Q6NcX99K7h92uQ1KJ3U_QiqNcbEFhQ"
        payload = {
           "name": "Test Restaurant",
            "location": "Mumbai",
            "contactNumber": "1234567890",
            "business_hours": '{"Monday": "09:00-18:00"}',
            "holidays": ["2024-12-25"],
        }
        response = await ac.post("caters/restaurants", data=payload,headers={"Authorization":f"Bearer {token}"})
        _id=response.json()["data"]["_id"]
        block_payload={
            "id": _id,
            "status": True
            }
        response = await ac.put(f"caters/restaurants/change-status",json=block_payload,headers={"Authorization":f"Bearer {token}"})
        assert response.status_code==200
        assert response.json()["message"]=="Restaurant status updated successfully"
        response = await ac.put(f"caters/restaurants/change-status",json=block_payload,headers={"Authorization":f"Bearer {token}"})
        assert response.status_code==400
        assert response.json()["detail"]=="Trying to set the same status"
        block_payload={
            "id": _id,
            "status": False
            }
        response = await ac.put(f"caters/restaurants/change-status",json=block_payload,headers={"Authorization":f"Bearer {token}"})
        assert response.status_code==200
        assert response.json()["message"]=="Restaurant status updated successfully"
        block_payload={
            "id": "66546a9c3e0f649dfafc4179",
            "status": False
            }
        response = await ac.put(f"caters/restaurants/change-status",json=block_payload,headers={"Authorization":f"Bearer {token}"})
        assert response.status_code==403
        assert response.json()["detail"]=="You are  not the restaurant owner"





@pytest.mark.asyncio
async def test_get_one_by_id():
    async with AsyncClient(app=app,base_url="http://test") as ac:
        data=await get_auth()
        token=data["token"]
        user_id=data["user_id"]
        # user_id="665d54ab2902895f8d1e7226"
        # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODM4MTg1NSwicm9sZSI6ImFkbWluIn0.M-jH3qSU2m1t7Q6NcX99K7h92uQ1KJ3U_QiqNcbEFhQ"
        payload = {
           "name": "Test Restaurant",
            "location": "Mumbai",
            "contactNumber": "1234567890",
            "business_hours": '{"Monday": "09:00-18:00"}',
            "holidays": ["2024-12-25"],
        }
        response = await ac.post("caters/restaurants", data=payload,headers={"Authorization":f"Bearer {token}"})
        _id=response.json()["data"]["_id"]
        
        response = await ac.get(f"caters/restaurants/id/{_id}",headers={"Authorization":f"Bearer {token}"})
        assert response.status_code==200

        response = await ac.get(f"caters/restaurants/id/66546a9c3e0f649dfafc4179",headers={"Authorization":f"Bearer {token}"})
        assert response.status_code==403
        assert response.json()["detail"]=="Not allowed"
        
       

        
