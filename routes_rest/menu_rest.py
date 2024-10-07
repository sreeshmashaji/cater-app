from datetime import datetime
import json
import mimetypes
import utils
import pytz
from config.path import menu_path
from typing import Counter, Dict, List, Optional
from bson import ObjectId
from fastapi import Body, Depends, File, Form, HTTPException, Query, Response, UploadFile, status,APIRouter
from config.database import db
from schemas import menu_schema
from dotenv import dotenv_values
import boto3
import oauth2
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
auth_scheme = HTTPBearer()


collection=db.menus


router=APIRouter(prefix=menu_path,tags=["Menu"])

env = dict(dotenv_values(".env_admin"))

AWS_ACCESS_KEY_ID = env.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION_NAME = env.get("AWS_REGION_NAME")
S3_BUCKET_NAME = env.get("S3_BUCKET_NAME")
S3_IMAGE_LINK=env.get("S3_IMAGE_LINK")


s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)







@router.post('', summary="Add menus to registered restaurant. Only restaurant owner can add menu with name, description, price, category id, etc. Category id must be valid.")
async def add_menu(
    restaurantId: list[str] = Form(),
    categoryId: str = Form(...),
    name: str = Form(...),
    desc: str = Form(...),
    price: float = Form(...),
    minimumServe: int = Form(...),
    type: str = Form(...),
    menuImages: List[UploadFile] = File(None),
    user=Depends(oauth2.verify_access_token),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    try:
            print(restaurantId)
            ownerId = user["user_id"]

            
            duplicate_restaurant_ids = [item for item, count in Counter(restaurantId).items() if count > 1]
            if duplicate_restaurant_ids:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Duplicate restaurantId values found: {duplicate_restaurant_ids}")

            for r_id in restaurantId:
                print(r_id)
                existing_restaurant = db.restaurants.find_one({'_id': ObjectId(r_id)})
                if not existing_restaurant:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Restaurant with ID {r_id} doesn't exist")
                if existing_restaurant["ownerId"] != ObjectId(ownerId):
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of one or more restaurants")

            existing_default_category = db.default_category.find_one({'_id': ObjectId(categoryId)})
            if not existing_default_category:
                  existing_custome_category=db.category.find_one({"_id":ObjectId(categoryId)})
                  if not existing_custome_category:
                      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid categoryId")
                  elif existing_custome_category["ownerId"] != ObjectId(ownerId):
                     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Category should be added by restaurant owner")

            image_links = []
            if menuImages:
                for menu_image in menuImages:
                    contents = await menu_image.read()
                    content_type, _ = mimetypes.guess_type(menu_image.filename)
                    s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=menu_image.filename, Body=contents, ContentType=content_type)
                    image_link = f"{S3_IMAGE_LINK}{menu_image.filename}"
                    image_links.append(image_link)

            data = menu_schema.MenuItem(
                ownerId=ObjectId(ownerId),
                restaurantId=[ObjectId(r_id) for r_id in restaurantId],
                name=name,
                desc=desc,
                price=price,
                minimumServe=minimumServe,
                type=type,
                categoryId=ObjectId(categoryId),
                image=image_links,
                dateAdded=datetime.now(pytz.utc)
            )

            inserted_data = collection.insert_one(data.__dict__)
            
            result_data = collection.find_one({'_id': inserted_data.inserted_id})
            result_data["_id"] = str(result_data["_id"])
            result_data["categoryId"] = str(result_data["categoryId"])
            result_data["ownerId"] = str(result_data["ownerId"])
            result_data["restaurantId"] = [str(rid) for rid in result_data["restaurantId"]]
            for i in restaurantId:
                resto=db.restaurants.find_one({"_id":ObjectId(i)})
                location=resto["location"]
                datas={"restaurantId":i,"menuId":str(inserted_data.inserted_id),"price":price, "minimumServe":minimumServe,"categoryId":ObjectId(categoryId),"averageStarCount":0,"name":name,"desc":desc,"type":type,"image":image_links,"location":location}
                
                db.restaurant_menu.insert_one(datas)

            if not result_data:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation Failed")
            await utils.invalidate_all_cache()
            
            return {"message": "success", "data": result_data}
    except Exception as e:
         raise e 






@router.put('',summary="update menu of corresponding restaurant, only restaurant owner can update the menu")
async def update_menu(
    menuId: str=Form(...),
    
    restaurantId: list[str] = Form(None),
    categoryId: str = Form(None),
    name: str = Form(None),
    desc: str = Form(None),
    price: float = Form(None),
    minimumServe: int = Form(None),
    type: str = Form(None),
    menuImages: List[UploadFile] = File(None),
    user=Depends(oauth2.verify_access_token),
    token:HTTPAuthorizationCredentials=Depends(auth_scheme)
):  
    try:
            ownerId = user["user_id"]
            
            existing_menu = collection.find_one({'_id': ObjectId(menuId)})
            if not existing_menu:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu doesn't exist")
            if restaurantId:
                for i in restaurantId:
                    existing_restaurant = db.restaurants.find_one({'_id': ObjectId(i)})
                    if not existing_restaurant:
                        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid restaurant_id")
                    if ObjectId(ownerId) != existing_restaurant["ownerId"]:
                      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of the restaurant")
                
            if categoryId:
                existing_default_category = db.default_category.find_one({'_id': ObjectId(categoryId)})
                if not existing_default_category:
                  existing_custome_category=db.category.find_one({"_id":ObjectId(categoryId)})
                  if not existing_custome_category:
                      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid categoryId")
                  elif existing_custome_category["ownerId"] != ObjectId(ownerId):
                     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Category should be added by restaurant owner")

            image_links = existing_menu['image']
            if menuImages:
                
                num_new_images = len(menuImages)
                
                
                max_images_allowed = 3
                
                
                num_images_to_remove = max(0, len(existing_menu['image']) + num_new_images - max_images_allowed)
                
            
                image_links = existing_menu['image'][:-num_images_to_remove] if num_images_to_remove > 0 else existing_menu['image']
                
                
                for menu_image in menuImages:
                    contents = await menu_image.read()
                    content_type, _ = mimetypes.guess_type(menu_image.filename)
                    s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=menu_image.filename, Body=contents, ContentType=content_type)
                    image_link = f"{S3_IMAGE_LINK}{menu_image.filename}"
                    image_links.append(image_link)
                    
            update_data = {}
            if restaurantId:
                update_data["restaurantId"] = [ObjectId(r_id) for r_id in restaurantId]
            if name:
                update_data["name"] = name
            if desc:
                update_data["desc"] = desc
            if price:
                update_data["price"] = price
            if minimumServe:
                update_data["minimumServe"] = minimumServe
            if type:
                update_data["type"] = type
            if categoryId:
                update_data["categoryId"] = ObjectId(categoryId)
            if menuImages:
              update_data["image"]=image_links

            
            updated_menu = collection.update_one({'_id': ObjectId(menuId)}, {"$set": update_data})
            updated_menu=collection.find_one({"_id":ObjectId(menuId)})

            if not updated_menu:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sorry, operation failed")
            if restaurantId:
                db.restaurant_menu.delete_many({'menuId':menuId})
                
                for i in restaurantId:
                    resto=db.restaurants.find_one({"_id":ObjectId(i)})
                    location=resto["location"]
                    datas={"restaurantId":i,"menuId":menuId,"price":updated_menu["price"], "minimumServe":updated_menu["minimumServe"],"categoryId":ObjectId(updated_menu["categoryId"]),"averageStarCount":0,"name":updated_menu["name"],"desc":updated_menu["desc"],"type":updated_menu["type"],"image":updated_menu["image"],"location":location}
                    
                    # datas={"restaurantId":i,"menuId":menuId,"price":price, "minimumServe":minimumServe,"categoryId":categoryId}
                    
                    db.restaurant_menu.insert_one(datas)
            await utils.invalidate_all_cache()
            
            return {"message": "Success"}
    except Exception as e:
        raise e



@router.put('/price-serve')
async def update_price_serve(
     restaurantId: str = Form(...),
    menuId: str = Form(...),
    price: float = Form(None),
    minimumServe: int = Form(None),
    categoryId: str = Form(None),
    name: str = Form(None),
    desc: str = Form(None),
    type: str = Form(None),
    menuImages: List[UploadFile] = File(None),
    user=Depends(oauth2.verify_access_token),
    token:HTTPAuthorizationCredentials=Depends(auth_scheme)
): 
    try:  
        ownerId=user["user_id"]
        existing_menu = db.menus.find_one({'_id': ObjectId(menuId)})
        if not existing_menu:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid menu_id")
        if ObjectId(ownerId) != existing_menu["ownerId"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner ")
    
        if categoryId:

            existing_default_category = db.default_category.find_one({'_id': ObjectId(categoryId)})
            if not existing_default_category:
                  existing_custome_category=db.category.find_one({"_id":ObjectId(categoryId)})
                  if not existing_custome_category:
                      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid categoryId")
                  elif existing_custome_category["ownerId"] != ObjectId(ownerId):
                     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Category should be added by restaurant owner")
                  


        details=db.restaurant_menu.find_one({"menuId":menuId,"restaurantId":restaurantId})
        if details is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant with this menu doesn't exists")
        update_data={} 
        if price:
           update_data["price"] = price
        if minimumServe:
          update_data["minimumServe"] = minimumServe
        if categoryId:
          update_data["categoryId"] = ObjectId(categoryId)
        if name:
          update_data["name"] = name
        if type:
          update_data["type"] = type

        if desc:
          update_data["desc"] = desc
        image_links = []
        if menuImages:
            for menu_image in menuImages:
                contents = await menu_image.read()
                content_type, _ = mimetypes.guess_type(menu_image.filename)
                s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=menu_image.filename, Body=contents, ContentType=content_type)
                image_link = f"{S3_IMAGE_LINK}{menu_image.filename}"
                image_links.append(image_link)
            update_data["image"]=image_links

        updated_menu = db.restaurant_menu.update_one({'_id':ObjectId(details["_id"])}, {"$set": update_data})
        print(updated_menu)
        if not updated_menu:
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sorry, operation failed") 
        await utils.invalidate_all_cache()
        
        return "success"
    except Exception as e:
        raise e
    



@router.delete('',summary="Delete menuitem by id..only corresponding resataurant owner can delete menu item")
async def delete_menu(menuId:str,user=Depends(oauth2.verify_access_token),
    token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:

        ownerId=user["user_id"]
        resultdata = collection.find_one({'_id':ObjectId(menuId)}) 
        if not resultdata:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu Doesn't Exists")
        # existing_restaurant_db= db.restaurants.find_one({'_id': ObjectId(restaurantId)})

        if ObjectId(ownerId)!=resultdata["ownerId"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not the owner of restaurant")
        
        collection.delete_one({"_id":ObjectId(menuId)})
        db.restaurant_menu.delete_many({'menuId':menuId})
        await utils.invalidate_all_cache()
        
        return "MenuItem Removed"
    except Exception as e:
        raise e
        

@router.get('/{owner_id}')
def get_menus(owner_id: str, user=Depends(oauth2.verify_access_token),
              token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    try:
        print("inside get menu")
        if owner_id != user['user_id']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not the owner")
        data = collection.find({"ownerId": ObjectId(owner_id)})
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No menus found")
        
        resultdata = []
        for items in data:
            resto_ids = items["restaurantId"]
            resto_details=[]
            
            for id in resto_ids:
                
                name_doc = db.restaurants.find_one({"_id": ObjectId(id)})
                if name_doc:
                    name = name_doc["name"]
                    obj = {"_id": str(id), "name": name}
                    resto_details.append(obj)
                    items["restaurantId"]=resto_details

            unique_list = []
            for item in resto_details:
             if item not in unique_list:
                unique_list.append(item)  
            category=db.default_category.find_one({"_id":ObjectId(items["categoryId"])})
            if not category:
                category=db.category.find_one({"_id":ObjectId(items["categoryId"])})
            category_details={'_id':str(items["categoryId"]),'name':category["name"]}

            
            
            formatted_doc = {
                **items,
                
                '_id': str(items['_id']),
                'restaurantId': unique_list,
                
                'categoryId': category_details,
                
                'ownerId': str(items['ownerId'])
            }
            resultdata.append(formatted_doc)
        
        
        return resultdata
    except Exception as e:
        raise e



@router.get('/find-menus/{restaurant_id}')
def finding(restaurant_id: str, token: HTTPAuthorizationCredentials = Depends(auth_scheme), user=Depends(oauth2.verify_access_token)):
    try:
    # print("menuss ")
            resto_data = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
            if resto_data is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
            
            
            restaurant_name = resto_data.get("name")
            

            if ObjectId(user["user_id"]) != resto_data.get("ownerId"):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner")

            datas = list(db.restaurant_menu.find({"restaurantId": restaurant_id}))
            
            data = [{'menuId': resultdata['menuId']} for resultdata in datas]
            
            menu_details = []
            for menus in data:
                print(menus)
                menu_data = collection.find_one({"_id": ObjectId(menus['menuId'])})
                resto_menu = db.restaurant_menu.find_one({"restaurantId": restaurant_id,"menuId":menus["menuId"]})
                print(resto_menu)
                if  "price" in resto_menu:
                    menu_data["price"]=resto_menu["price"]
                if  "minimumServe" in resto_menu:
                    menu_data["minimumServe"]=resto_menu["minimumServe"]
                if  "categoryId" in resto_menu:
                   menu_data["categoryId"]=resto_menu["categoryId"]
                if "name" in resto_menu:
                        menu_data["name"] = resto_menu["name"]
                if "desc" in resto_menu:
                        menu_data["desc"] = resto_menu["desc"]
                if "type" in resto_menu:
                        menu_data["type"] = resto_menu["type"]
                if "image" in resto_menu:
                        menu_data["image"] = resto_menu["image"]
                


                menu_details.append(menu_data)
                

            
            categories=[]
            
            for doc in menu_details:
                doc.pop('restaurantId', None)
                category_id = doc.get("categoryId")
                if category_id:
                    category = db.default_category.find_one({"_id": ObjectId(category_id)})
                    if not category:
                      category = db.category.find_one({"_id": ObjectId(category_id)})


                    if category:
                        doc['categoryId'] = {'_id': str(category_id), 'name': category.get("name")}
                    else:
                        doc['categoryId'] = None
            
            return_data = [{**doc, '_id': str(doc['_id']), "ownerId": str(doc.get('ownerId'))} for doc in menu_details]
            return return_data
    except Exception as e:
        raise e   


@router.delete('/delete-one',summary="Delete menuitem by id..only corresponding resataurant owner can delete menu item,menu item will be removed from restauramnt's menu list")
async def delete_One_menu(menuId:str,restaurantId:str,user=Depends(oauth2.verify_access_token),
    token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    
    try:
        ownerId=user["user_id"]
        resultdata = collection.find_one({'_id':ObjectId(menuId)}) 
        if not resultdata:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu Doesn't Exists")
        resultdata["restaurantId"].remove(ObjectId(restaurantId))
        collection.update_one({"_id": ObjectId(menuId)}, {"$set": {"restaurantId": resultdata["restaurantId"]}})

        if ObjectId(ownerId)!=resultdata["ownerId"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not the owner of restaurant")
        
        
        db.restaurant_menu.delete_many({'menuId':menuId,'restaurantId':restaurantId})
        await utils.invalidate_all_cache()
           
        return "MenuItem Removed"
    except Exception as e:
        raise e
   

















































# @router.delete('delete')






# @router.put('/menu-item')
# async def update_menu_item(
#     owner_id:str=Form(...),
#     restaurant_id: str = Form(...),
#     category: str = Form(...),
#     field: str = Form(...),
#     new_value: str|float|int|UploadFile= Form(...),
#     item_index: int = Form(...)
# ):
#     existing_restaurant = collection.find_one({'restaurantId': restaurant_id})
#     if not existing_restaurant:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    
#     existing_restaurant_db= db.restaurants.find_one({'_id': ObjectId(restaurant_id)})
#     if owner_id!=existing_restaurant_db["owner_id"]:
#          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="you are not the owner of restaurant")

#     if category not in existing_restaurant['menu'] or field not in {"name", "price", "desc", "minimumServe", "type","image"}:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid category or field")

#     menu_items = existing_restaurant["menu"].get(category, [])
#     print(menu_items)
#     if  item_index < len(menu_items):
#         if field == "image":
#             # Handle image upload
#             image = await new_value.read()
#             content_type, _ = mimetypes.guess_type(new_value.filename)
#             # Upload image to S3 or other storage
#             s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=new_value.filename, Body=image, ContentType=content_type)
#             new_value = f"{S3_IMAGE_LINK}{new_value.filename}"
        
#         update_result = collection.update_one(
#             {"restaurantId": restaurant_id},
#             {"$set": {f"menu.{category}.{item_index}.{field}": new_value}}
#         )
#         if update_result.matched_count == 1:
#             return "success"
#         else:
#             return {"error": "Menu item not found in the database"}
#     else:
#         return {"error": "Menu item index out of range"}
    





# @router.delete('/menu-item')
# async def delete_menu_item(
#     owner_id:str=Form(...),
#     restaurant_id: str = Form(...),
#     category: str = Form(...),
#     item_index: int = Form(...)
# ):
#     existing_restaurant = collection.find_one({'restaurantId': restaurant_id})
#     if not existing_restaurant:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    
#     existing_restaurant_db= db.restaurants.find_one({'_id': ObjectId(restaurant_id)})
#     if owner_id!=existing_restaurant_db["owner_id"]:
#          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="you are not the owner of restaurant")

#     if category not in existing_restaurant['menu'] :
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid category ")

#     menu_items = existing_restaurant["menu"].get(category, [])
#     if item_index < len(menu_items) :
#         deleted_item=menu_items.pop(item_index)
#         delete_result = collection.update_one(
#             {"restaurantId": restaurant_id},
#             {"$set": {f"menu.{category}":menu_items}}
#         )
#         if delete_result.modified_count == 1:
#             return f"Deleted menu item at index {item_index}: {deleted_item}"
#         else:
#             return {"error": "Menu item not found in the database"}
#     else:
#         return {"error": "Menu item index out of range"}

    