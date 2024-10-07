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
    


async def create_restaurant():
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
        # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODcxNzcxMCwicm9sZSI6ImFkbWluIn0.lXmFbvuLa79cohzQ_iRc22wYMdJEw7Pq5i6VNr519eE"

        response = await client.post("caters/restaurants", data=payload,headers={"Authorization":f"Bearer {token}"})
        id= response.json()["data"]["_id"]
        return{"id":id}
 



@pytest.mark.asyncio
async def test_add_menu():
    async with AsyncClient(app=app,base_url="http://test") as ac:
        data=await get_auth()
        token=data["token"]
        user_id=data["user_id"]
        # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODM5NzE5NCwicm9sZSI6ImFkbWluIn0.VAQWs-i2NT3j2w8CMSk7dBRKlvAvixvqaLTcWkHh67k"
        # user_id="665d54ab2902895f8d1e7226"
       
        data=await create_restaurant()
        id=data["id"]
        form_data = {
            "restaurantId": [id],
            "categoryId": "66546b91decb8588517b3dcd",
            "name": "Test Menu",
            "desc": "Test Description",
            "price": 10.0,
            "minimumServe": 1,
            "type": "Test Type",
        }
        test_image_path=r"C:\Users\Sreeshma\Downloads\axo.png"
        with open(test_image_path, 'rb') as image_file:
             image_content = image_file.read()

        
        files = {'menuImages': (test_image_path, image_content)}
        response = await ac.post("/caters/restaurants/menus", data=form_data,files=files, headers={"Authorization": f"Bearer {token}"})
        print(response.json())
        assert response.status_code==200

        form_data = {
            "restaurantId": [id],
            "categoryId": "667fabe123e85c6b61f42115",
            "name": "Test Menu",
            "desc": "Test Description",
            "price": 10.0,
            "minimumServe": 1,
            "type": "Test Type",
        }
        response = await ac.post("/caters/restaurants/menus", data=form_data, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code==200



        form_data = {
            "restaurantId": [id,id],
            "categoryId": "66546b91decb8588517b3dcd",
            "name": "Test Menu",
            "desc": "Test Description",
            "price": 10.0,
            "minimumServe": 1,
            "type": "Test Type",
        }
        response = await ac.post("/caters/restaurants/menus", data=form_data, headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code==400
        print(response.json())
        assert response.json()["detail"]==f"Duplicate restaurantId values found: ['{id}']"
        form_data = {
            "restaurantId": ["665d54ab2902895f8d1e7226"],
            "categoryId": "66546b91decb8588517b3dcd",
            "name": "Test Menu",
            "desc": "Test Description",
            "price": 10.0,
            "minimumServe": 1,
            "type": "Test Type",
        }
        response = await ac.post("/caters/restaurants/menus", data=form_data, headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code==400
        print(response.json())
        assert response.json()["detail"]==f"Restaurant with ID 665d54ab2902895f8d1e7226 doesn't exist"
        form_data = {
            "restaurantId": ["66546a9c3e0f649dfafc4179"],
            "categoryId": "66546b91decb8588517b3dcd",
            "name": "Test Menu",
            "desc": "Test Description",
            "price": 10.0,
            "minimumServe": 1,
            "type": "Test Type",
        }
        response = await ac.post("/caters/restaurants/menus", data=form_data, headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code==403
        print(response.json())
        assert response.json()["detail"]=="You are not the owner of one or more restaurants"
        form_data = {
            "restaurantId": [id],
            "categoryId": "66546a9c3e0f649dfafc4179",
            "name": "Test Menu",
            "desc": "Test Description",
            "price": 10.0,
            "minimumServe": 1,
            "type": "Test Type",
        }
        response = await ac.post("/caters/restaurants/menus", data=form_data, headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code==400
        print(response.json())
        assert response.json()["detail"]=="Invalid categoryId"

        form_data = {
            "restaurantId": [id],
            "categoryId": "667facf96a89bebd7811565d",
            "name": "Test Menu",
            "desc": "Test Description",
            "price": 10.0,
            "minimumServe": 1,
            "type": "Test Type",
        }
        response = await ac.post("/caters/restaurants/menus", data=form_data, headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code==403
        print(response.json())
        assert response.json()["detail"]=="Category should be added by restaurant owner"
        



# @pytest.mark.asyncio
# async def test_update_menu():
#     async with AsyncClient(app=app,base_url="http://test") as ac:
#         data=await get_auth()
#         token=data["token"]
#         user_id=data["user_id"]
#         # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODQ1OTU5OSwicm9sZSI6ImFkbWluIn0.BLVDK576mVjRgzCT8EfTqn1gSJC1VjAXOM9TuTz_Bx8"
#         # user_id="665d54ab2902895f8d1e7226"
#         data= await create_restaurant()
#         resto_id=data["id"]
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
#         menu_form_data={
#             "menuId":menu_id,
#             "restaurantId":resto_id,
#             "categoryId":"66546b76decb8588517b0b6c",
#             "name": "Test update menu",
#             "desc": "Test  update Description",
#             "price": 100.0,
#             "minimumServe": 4,
#             "type": "Test update Type"

#         }
#         test_image_path=r"C:\Users\Sreeshma\Downloads\pexels-chanwalrus-1059943.jpg"
#         with open(test_image_path, 'rb') as image_file:
#              image_content = image_file.read()

#         files = {'menuImages': (test_image_path, image_content)}
#         update_response=await ac.put("/caters/restaurants/menus", data=menu_form_data,files=files, headers={"Authorization": f"Bearer {token}"})
#         print(update_response.json())
#         assert update_response.status_code==200
#         menu_form_data={
#             "menuId":"66546b76decb8588517b0b6c",
#             "restaurantId":resto_id,
#             "categoryId":"66546b76decb8588517b0b6c",
#             "name": "Test update menu",
            

#         }
#         update_response=await ac.put("/caters/restaurants/menus", data=menu_form_data,headers={"Authorization": f"Bearer {token}"})
#         update_response.status_code==404
#         update_response.json()["detail"]=="Menu doesn't exist"
#         menu_form_data={
#             "menuId":menu_id,
#             "restaurantId":"66546b76decb8588517b0b6c",
#             "categoryId":"66546b76decb8588517b0b6c",
#             "name": "Test update menu",
            

#         }
#         update_response=await ac.put("/caters/restaurants/menus", data=menu_form_data,headers={"Authorization": f"Bearer {token}"})
#         update_response.status_code==403
#         update_response.json()["detail"]=="Invalid restaurant_id"
#         print("here")
#         menu_form_data={
#             "menuId":menu_id,
#             "restaurantId":"66546a9c3e0f649dfafc4179",
#             "categoryId":"66546b76decb8588517b0b6c",
#             "name": "Test update menu",
            

#         }
#         update_response=await ac.put("/caters/restaurants/menus", data=menu_form_data,headers={"Authorization": f"Bearer {token}"})
#         update_response.status_code==403
#         update_response.json()["detail"]=="You are not the owner of the restaurant"


#         menu_form_data={
#             "menuId":menu_id,
#             "restaurantId":resto_id,
#             "categoryId":"666d10e7b239090e19678c90",
#             "name": "Test update menu",

#         }
#         update_response=await ac.put("/caters/restaurants/menus", data=menu_form_data,headers={"Authorization": f"Bearer {token}"})
#         update_response.status_code==403
#         update_response.json()["detail"]=="Invalid categoryId"


        
# @pytest.mark.asyncio
# async def test_update_price_serve():
#     async with AsyncClient(app=app,base_url="http://test") as ac:
#         data=await get_auth()
#         token=data["token"]
#         user_id=data["user_id"]
#         # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODQ1OTU5OSwicm9sZSI6ImFkbWluIn0.BLVDK576mVjRgzCT8EfTqn1gSJC1VjAXOM9TuTz_Bx8"
#         # user_id="665d54ab2902895f8d1e7226"
#         data= await create_restaurant()
#         resto_id=data["id"]
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
#         menu_form_data={
#             "menuId":menu_id,
#             "restaurantId":resto_id,
#             "categoryId":"66546b76decb8588517b0b6c",
#             "name": "Test chicken menu",
#             "desc": "Test  chicken Description",
#             "price": 1000.0,
#             "minimumServe": 5,
#             "type": "Test non Type"

#         }
#         test_image_path=r"C:\Users\Sreeshma\Downloads\pexels-chanwalrus-1059943.jpg"
#         with open(test_image_path, 'rb') as image_file:
#              image_content = image_file.read()

#         files = {'menuImages': (test_image_path, image_content)}
#         update_response=await ac.put("/caters/restaurants/menus/price-serve", data=menu_form_data,files=files, headers={"Authorization": f"Bearer {token}"})
#         print(update_response.json())
#         assert update_response.status_code==200

#         menu_form_data={
#             "menuId":"66546b76decb8588517b0b6c",
#             "restaurantId":resto_id,
#             "categoryId":"66546b76decb8588517b0b6c",
#             "name": "Test chicken menu",
#             "desc": "Test  chicken Description",
            

#         }
#         update_response=await ac.put("/caters/restaurants/menus/price-serve", data=menu_form_data, headers={"Authorization": f"Bearer {token}"})
#         update_response.status_code==403
#         update_response.json()["detail"]=="Invalid menu_id"

#         menu_form_data={
#             "menuId":"66546b76decb8588517b0b6c",
#             "restaurantId":"66546b76decb8588517b0b6c",
#             "categoryId":"66546b76decb8588517b0b6c",
#             "name": "Test chicken menu",
#             "desc": "Test  chicken Description",
            

#         }
#         update_response=await ac.put("/caters/restaurants/menus/price-serve", data=menu_form_data, headers={"Authorization": f"Bearer {token}"})
#         update_response.status_code==404
#         update_response.json()["detail"]=="Restaurant with this menu doesn't exists"



# @pytest.mark.asyncio
# async def test_delete_menu():
#     async with AsyncClient(app=app,base_url="http://test") as ac:
#         data=await get_auth()
#         token=data["token"]
#         user_id=data["user_id"]
#         # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODQ1OTU5OSwicm9sZSI6ImFkbWluIn0.BLVDK576mVjRgzCT8EfTqn1gSJC1VjAXOM9TuTz_Bx8"
#         # user_id="665d54ab2902895f8d1e7226"
#         data= await create_restaurant()
#         resto_id=data["id"]
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
#         response = await ac.delete("/caters/restaurants/menus", params=menu_id, headers={"Authorization": f"Bearer {token}"})
#         response.json()=="MenuItem Removed"

#         response = await ac.delete("/caters/restaurants/menus", params="665d54ab2902895f8d1e7226", headers={"Authorization": f"Bearer {token}"})
#         response.status_code==404
#         response.json()=="Menu Doesn't Exists"
#         response=await ac.delete("/caters/restaurants/menus",params="66546bf63e0f649dfafc417d",headers={"Authorization": f"Bearer {token}"})
#         response.status_code==403
#         response.json()["detail"]=="You are not the owner of restaurant"



# @pytest.mark.asyncio
# async def test_get_by_owner():
#     async with AsyncClient(app=app,base_url="http://test") as ac:
#         data=await get_auth()
#         token=data["token"]
#         user_id=data["user_id"]
#         # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODQ1OTU5OSwicm9sZSI6ImFkbWluIn0.BLVDK576mVjRgzCT8EfTqn1gSJC1VjAXOM9TuTz_Bx8"
#         # user_id="665d54ab2902895f8d1e7226"
#         response=await ac.get(f"/caters/restaurants/menus/{user_id}",headers={"Authorization": f"Bearer {token}"})
#         print(response.json())
#         assert response.status_code==200

#         response=await ac.get(f"/caters/restaurants/menus/666d10e7b239090e19678c90",headers={"Authorization": f"Bearer {token}"})
#         print(response.json())
#         assert response.status_code==403
#         assert response.json()["detail"]=="You are not the owner"

        
    
# @pytest.mark.asyncio
# async def test_find_menu():
#     async with AsyncClient(app=app,base_url="http://test") as ac:
#         data=await get_auth()
#         token=data["token"]
#         user_id=data["user_id"]
#         # user_id="665d54ab2902895f8d1e7226"
#         # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODcxNzcxMCwicm9sZSI6ImFkbWluIn0.lXmFbvuLa79cohzQ_iRc22wYMdJEw7Pq5i6VNr519eE"
#         data= await create_restaurant()
#         resto_id=data["id"]
#         print(resto_id)
#         response=await ac.get(f"/caters/restaurants/menus/find-menus/{resto_id}",headers={"Authorization":f"Bearer {token}"})
#         print(response.json())
#         assert response.status_code==200

#         response=await ac.get(f"/caters/restaurants/menus/find-menus/665d54ab2902895f8d1e7226",headers={"Authorization":f"Bearer {token}"})
#         response.status_code==404
#         response.json()["detail"]=="Restaurant not found"

#         response=await ac.get(f"/caters/restaurants/menus/find-menus/66546a9c3e0f649dfafc4179",headers={"Authorization":f"Bearer {token}"})
#         response.status_code==403
#         response.json()["detail"]=="You are not the owner"

       
# @pytest.mark.asyncio
# async def test_delete_menu():
#     async with AsyncClient(app=app,base_url="http://test") as ac:
#         data=await get_auth()
#         token=data["token"]
#         user_id=data["user_id"]
#         # user_id="665d54ab2902895f8d1e7226"
#         # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtYWlsLWFhYWFtdGoyMzJnZmR3d3JjZWZtc2RrN3hhQGF4b21pdW0uc2xhY2suY29tIiwidXNlcl9pZCI6IjY2NWQ1NGFiMjkwMjg5NWY4ZDFlNzIyNiIsIm5hbWUiOiJBTEFDQVRFUiIsImV4cCI6MTcxODcxNzcxMCwicm9sZSI6ImFkbWluIn0.lXmFbvuLa79cohzQ_iRc22wYMdJEw7Pq5i6VNr519eE"
#         data= await create_restaurant()
#         resto_id=data["id"]
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
#         response = await ac.delete("/caters/restaurants/menus", params={"menuId":menu_id,"restaurantId":resto_id},headers={"Authorization": f"Bearer {token}"})
#         print(response.json())
#         assert response.status_code==200
#         assert response.json()=="MenuItem Removed"

#         response = await ac.delete("/caters/restaurants/menus", params={"menuId":'665d54ab2902895f8d1e7226',"restaurantId":resto_id},headers={"Authorization": f"Bearer {token}"})
#         print(response.json())
#         assert response.status_code==404
#         assert response.json()['detail']=="Menu Doesn't Exists"

#         response = await ac.delete("/caters/restaurants/menus", params={"menuId":'6656f6a918200a8ca46c5f71',"restaurantId":resto_id},headers={"Authorization": f"Bearer {token}"})
#         print(response.json())
#         assert response.status_code==403
#         assert response.json()['detail']=="You are not the owner of restaurant"
        





        



