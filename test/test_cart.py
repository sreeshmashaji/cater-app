from httpx import AsyncClient
import pytest,sys,os
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from main import app

client = TestClient(app)



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
    


@pytest.mark.asyncio
async def test_add_cart():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data=await get_auth2()
        token=data["token"]
        user_id=data["user_id"]
        payload = {
           "name": "Test Restaurant",
            "location": "Mumbai",
            "contactNumber": "1234567890",
            "business_hours": '{"Monday": "09:00-18:00"}',
            "holidays": ["2024-12-25"],
        }
        response = await ac.post("caters/restaurants", data=payload,headers={"Authorization":f"Bearer {token}"})
        resto_id=response.json()["data"]["_id"]
        form_data = {
            "restaurantId": [resto_id],
            "categoryId": "66546b91decb8588517b3dcd",
            "name": "Test Menu",
            "desc": "Test Description",
            "price": 10.0,
            "minimumServe": 1,
            "type": "Test Type",
        }
        response = await ac.post("/caters/restaurants/menus", data=form_data, headers={"Authorization": f"Bearer {token}"})
        print(response.json())
        menu_id=response.json()["data"]["_id"]


        data=await get_auth()
        token=data["token"]
       


        payload={
            "restaurantId": resto_id,
            "menuId": menu_id,
            "quantity": 1
        }

        response=await ac.post("/cart",json=payload,headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==200

        payload={
            "restaurantId": resto_id,
            "menuId":"66546b91decb8588517b3dcd",
            "quantity": 1
        }

        response=await ac.post("/cart",json=payload,headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==404
        assert response.json()["detail"]=="Menu item not found"




@pytest.mark.asyncio
async def test_get_cart():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data=await get_auth()
        token=data["token"]
        customer_id=data["customer_id"]
        response=await ac.get(f"/cart/{customer_id}",headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==200

        response=await ac.get(f"/cart/66546b91decb8588517b3dcd",headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==403
        assert response.json()["detail"]=="You do not have permission to access this resource"




@pytest.mark.asyncio
async def test_delete_cart():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data=await get_auth2()
        token=data["token"]
        user_id=data["user_id"]
        payload = {
           "name": "Test Restaurant",
            "location": "Mumbai",
            "contactNumber": "1234567890",
            "business_hours": '{"Monday": "09:00-18:00"}',
            "holidays": ["2024-12-25"],
        }
        response = await ac.post("caters/restaurants", data=payload,headers={"Authorization":f"Bearer {token}"})
        resto_id=response.json()["data"]["_id"]
        form_data = {
            "restaurantId": [resto_id],
            "categoryId": "66546b91decb8588517b3dcd",
            "name": "Test Menu",
            "desc": "Test Description",
            "price": 10.0,
            "minimumServe": 1,
            "type": "Test Type",
        }
        response = await ac.post("/caters/restaurants/menus", data=form_data, headers={"Authorization": f"Bearer {token}"})
        print(response.json())
        menu_id=response.json()["data"]["_id"]


        data=await get_auth()
        token=data["token"]
    
        payload={
            "restaurantId": resto_id,
            "menuId": menu_id,
            "quantity": 1
        }

        response=await ac.post("/cart",json=payload,headers={"Authorization":f"Bearer {token}"})
        cart_id=response.json()["data"]["_id"]

        response=await ac.delete(f"/cart/{cart_id}",headers={"Authorization":f"Bearer {token}"})
        print(response.json())