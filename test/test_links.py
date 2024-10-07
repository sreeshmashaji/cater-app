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
    
async def get_auth2():
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "role": "admin",
            "email": "sreeshma3023@gmail.com",
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
async def test_add_link():
    async with AsyncClient(app=app,base_url="http://test") as ac:
            auth = await get_auth()
            token=auth["token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            payload = {
                        "facebook": "https://facebook.com/user",
                        "instagram": "https://instagram.com/user",
                        "linkedin": "https://linkedin.com/user",
                        "twitter": "https://twitter.com/user"
                        }

            response = await ac.post("/caters/socialmedia/link", json=payload, headers=headers)
            assert response.status_code == 200
            assert response.json()["message"] == "success"
            response = await ac.post("/caters/socialmedia/link", json=payload, headers=headers)
            response.status_code==400
            response.json()["detail"]=="Already added links"



@pytest.mark.asyncio
async def test_get_link():
    async with AsyncClient(app=app,base_url="http://test") as ac:
   
        auth = await get_auth()
        token=auth["token"]
        # token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODgwODA0Niwicm9sZSI6ImFkbWluIn0.ixKmQOmdPGS3KSCZuTXrvN6T6WY5RUM-yWiRZZJn3iQ'
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await ac.get("/caters/socialmedia/link", headers=headers)
        print(response.json())
        assert response.status_code == 200
        auth = await get_auth2()
        token=auth["token"]
        response = await ac.get("/caters/socialmedia/link", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code==404
        response.json()["detail"]=="Data not found"

    

@pytest.mark.asyncio
async def test_update_link():
    async with AsyncClient(app=app,base_url="http://test") as ac:

        auth = await get_auth()
        token=auth["token"]
        user_id=auth["user_id"]
        # token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODgwODA0Niwicm9sZSI6ImFkbWluIn0.ixKmQOmdPGS3KSCZuTXrvN6T6WY5RUM-yWiRZZJn3iQ'
        # user_id="665d54ab2902895f8d1e7226"
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/caters/socialmedia/link", headers=headers)
        print(response.json())
        link_id=response.json()["_id"]
        print(link_id)
        
        payload = {
                        "facebook": "https://facebook_update.com/user",
                        "instagram": "https://instagram.com/user",
                        "linkedin": "https://linkedin.com/user",
                        "twitter": "https://twitter.com/user"
                        }

        response = await ac.put(f"/caters/socialmedia/link/{link_id}",json=payload, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code==200
        assert response.json()["message"]=="success"

        response = await ac.put(f"/caters/socialmedia/link/665d54ab2902895f8d1e7226",json=payload, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code==404
        assert response.json()["detail"]=="Link not found"

        response = await ac.put(f"/caters/socialmedia/link/{link_id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code==400
        assert response.json()["detail"]=="No fields to update"


        auth = await get_auth2()
        token=auth["token"]
        response = await ac.put(f"/caters/socialmedia/link/{link_id}",json=payload, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code==403
        assert response.json()["detail"]=="You are not the owner"





        


        


    