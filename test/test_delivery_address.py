from dotenv import load_dotenv
from httpx import AsyncClient
import pytest,sys,os

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

client = TestClient(app)


# @pytest.fixture
# def load_env():
#     load_dotenv(".env_admin")  # Load variables from .env_admin
#     yield 

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
    

@pytest.mark.asyncio
async def test_add_delivery_address():
    async with AsyncClient(app=app, base_url="http://test") as ac:


        data= await get_auth()
        token=data["token"]
        payload={
                "Name": "Eva",
                "Address": "Little house",
                "city": "calicut",
                "state": "kozhikode",
                "zipCode": "673005",
                "phoneNumber": "907865543",
                "status": False
                }
        
        response=await ac.post("/customers/delivery-address",json=payload,headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==200

        payload={
                "Name": "Eva",
                "Address": "Little house",
                "city": "calicut",
                "state": "kozhikode",
                "zipCode": "673005",
                "phoneNumber": "90ff6543",
                "status": False
                }
        
        response=await ac.post("/customers/delivery-address",json=payload,headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==400
        assert response.json()["detail"]=="Phone number must contain only digits"

        payload={
                "Name": "Eva",
                "Address": "Little house",
                "city": "calicut",
                "state": "kozhikode",
                "zipCode": "673005",
                "phoneNumber": "909999999999543",
                "status": False
                }
        
        response=await ac.post("/customers/delivery-address",json=payload,headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==400
        assert response.json()["detail"]=="Invalid Phone Number"


@pytest.mark.asyncio
async def test_get_delivery_address():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data= await get_auth()
        token=data["token"]
        response=await ac.get("/customers/delivery-address/all",headers={"Authorization":f"Bearer {token}"})
        print(response.json())
        assert response.status_code==200


@pytest.mark.asyncio
async def test_delete_delivery_address():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data= await get_auth()
        token=data["token"]
        payload={
                "Name": "Eva",
                "Address": "Little house",
                "city": "calicut",
                "state": "kozhikode",
                "zipCode": "673005",
                "phoneNumber": "907865543",
                "status": False
                }
        
        response=await ac.post("/customers/delivery-address",json=payload,headers={"Authorization":f"Bearer {token}"})
        address_id=response.json()["data"]["_id"]
        print(address_id)

        response=await ac.delete(f"/customers/delivery-address/{address_id}",headers={"Authorization":f"Bearer {token}"})

































# 667658bfe48e5f53920be007