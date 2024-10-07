from httpx import AsyncClient
import pytest,sys,os
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from main import app

client = TestClient(app)

mock_user={"email":"damon@gmail.com"}
order_id="667a4b68ac0e11d2c095db6c"#pending id (not cancelled)
pending_order="6676affd7af1962f495f7acd"

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
async def test_checkout_session():
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
        print(str(cart_id))
        payload={
            "cart_item_ids": [
                f"{cart_id}"
            ],
            "delivery_time": "8.50",
            "delivery_date": "12-12-2024",
            "delivery_address_id": "6662d565effb1ca7d11a1039"
            }
        print(payload)
        
        response=await ac.post("/orders/create-checkout-session",json=payload,headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==200




@pytest.mark.asyncio
async def test_get_customer_by_id():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data=await get_auth()
        token=data["token"]
        customer_id=data["customer_id"]
        data=await get_auth2()
        token=data["token"]
        user_id=data["user_id"]
        response=await ac.get(f"/orders/customer/{customer_id}",headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==200
        response=await ac.get(f"/orders/customer/{user_id}",headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==404
        assert response.json()["detail"]=="User not found"


@pytest.mark.asyncio
async def test_get_orders():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data=await get_auth()
        token=data["token"]
        customer_id=data["customer_id"]
        response=await ac.get(f"/orders/customer-orders/{customer_id}",headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==200
        # 6667c55028b6a5a2b6564687
        response=await ac.get(f"/orders/customer-orders/6667c55028b6a5a2b6564687",headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==404
        assert response.json()["detail"]=="No orders found"
        # 6656c8dc18200a8ca46c5f6e
        response=await ac.get(f"/orders/customer-orders/6656c8dc18200a8ca46c5f6e",headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==403
        assert response.json()["detail"]=="Not allowed"


@pytest.mark.asyncio
async def test_get_orders_by_cater():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data=await get_auth2()
        token=data["token"]
        user_id=data["user_id"]
        response=await ac.get(f"/orders/{user_id}",headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==200

        response=await ac.get(f"/orders/667a4b68ac0e11d2c095db6c",headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==403
        assert response.json()["detail"]=="Not allowed"




@pytest.mark.asyncio
async def test_cancel_order():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data=await get_auth()
        token=data["token"]
        user_id=data["customer_id"]
        response=await ac.put(f'/orders/cancel-order/{order_id}',headers={"Authorization":f"Bearer {token}"})
        assert response.status_code==200
        assert response.json()=="Order cancelled"

        response=await ac.put(f'/orders/cancel-order/"6676792ead23f87521580998',headers={"Authorization":f"Bearer {token}"})
        assert response.status_code==403
        assert response.json()["detail"]=="Not allowed to cancel the order"



# @pytest.mark.asyncio
# async def test_set_order_status():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         data=await get_auth()
#         token=data["token"]
#         user_id=data["customer_id"] 
#         payload={"status": "Accept"}
#         response=await ac.put(f"/orders/{order_id}",json=payload,headers={"Auhtorization":f"Bearer {token}"})

