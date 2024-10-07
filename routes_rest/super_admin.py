import json

import re
import time
from typing import Annotated
from bson import ObjectId
from dotenv import dotenv_values
from fastapi import Body, File, Form, HTTPException, UploadFile, status,APIRouter,Depends,BackgroundTasks
from config.database import db
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from schemas import super_admin_schema
import utils,oauth2


auth_scheme = HTTPBearer()



router=APIRouter(prefix="/super-admin",tags=["super-admin"])

collection=db.super_admin

# cred={
#     "email":"alacater@gmail.com",
#     "password":"Qwerty@1234",
#     "firstName":"Alacater",
#     "lastName":"Catering",
#     "role":"super-admin"
# }




@router.post('/login' )
async def login(data: Annotated[
        super_admin_schema.Login, 
        Body(
            examples=[
                {
                    "role": "super-admin",
                    "email": "sachin@axomium.com",
                    "password": "Qwerty@1234"
                    
                }
            ],
        ),
    ] ):
   
     
        user=collection.find_one({"email":data.email})
        if not user:
              raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid Credentials")
        if not utils.verify(data.password,user['password']):
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid Credentials")
        user_id=user["_id"]
        name=user["firstName"]
        if data.role!=user["role"]:
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Role mismatch")

        
        token=oauth2.create_super_admin_access_token({"email":data.email,"super_admin_id":str(user_id),"name":name},user['role'])
          
        return {"token":token,"user_id":str(user_id)}



@router.get("/caters")
def get_all_caters(user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
       if user["role"]!="super-admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
              
       caters=list(db.register.find())
       print(caters)
#        
       for one in caters:
            
            one["_id"]=str(one["_id"])
            
       
       return caters



# @router.get("/caters/{id}")
# def get_cater(id:str,user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
#        if user["role"]!="super-admin":
#          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
       
#        caters=db.register.find_one({"_id":ObjectId(id)})
#        print(caters)
#        caters["_id"]=str(caters["_id"])
#        return caters


@router.get("/restaurants")
def get_all_restaurants(ownerid:str,user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
       if user["role"]!="super-admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
              
       resto=list(db.restaurants.find({"ownerId":ObjectId(ownerid)}))
       print(resto)
#        
       data = [{**resultdata, '_id': str(resultdata['_id']),'ownerId': str(resultdata['ownerId'])} for resultdata in resto]
       
       return data


@router.get("/restaurants/{restaurant_id}")
def get_restaurant(restaurant_id:str,user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
       if user["role"]!="super-admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
       
       restaurant_details = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
       if not restaurant_details:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        
       menu_details = []
        
    
       datas = list(db.restaurant_menu.find({"restaurantId": restaurant_id}))
       print(datas)
        
       for data in datas:
            
            menu_data = {
                
                "_id": str(data["menuId"]),
                "name": data.get("name"),
                "desc": data.get("desc"),
                "price": data.get("price"),
                "minimumServe": data.get("minimumServe"),
                "type": data.get("type"),
                "image": data.get("image"),
                "categoryId": data.get("categoryId"),
                "averageStarCount":data.get("averageStarCount")
            }

            
            if data.get("categoryId"):
                category = db.default_category.find_one({"_id": ObjectId(data["categoryId"])})
                if not category:
                   category = db.category.find_one({"_id": ObjectId(data["categoryId"])})
                       
                if category:
                    category_details = {'_id': str(category.get("_id")), 'name': category.get("name")}
                    menu_data['categoryId'] = category_details

            menu_details.append(menu_data)


        
       restaurant_details["_id"] = str(restaurant_details["_id"])
       restaurant_details["ownerId"] = str(restaurant_details["ownerId"])
       ratingCount=db.reviews.count_documents({"restaurantId":ObjectId(restaurant_id)})
       restaurant_details["ratingCount"]=ratingCount 
       full_details = {
            'restaurant_details': restaurant_details,
            'menu_details': menu_details
        }
        
       return full_details



# @router.get("/menus")
# def get_all_menus(user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
#        if user["role"]!="super-admin":
#          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
              
#        menus=list(db.menus.find())
#        print(menus)
#        for items in menus:
#         resto_ids = items["restaurantId"]
#         resto_details=[]
        
#         for id in resto_ids:
            
#             name_one_resto = db.restaurants.find_one({"_id": ObjectId(id)})
#             if name_one_resto:
#                 name = name_one_resto["name"]
#                 obj = {"_id": str(id), "name": name}
#                 resto_details.append(obj)
#                 items["restaurantId"]=resto_details

# #        
#        data = [{**resultdata, '_id': str(resultdata['_id']),'ownerId': str(resultdata['ownerId']),'categoryId': str(resultdata['categoryId'])} for resultdata in menus]
       
#        return data



# @router.get("/menus/{id}")
# def get_menu(id:str,user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
#        if user["role"]!="super-admin":
#          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
       
#        menu=db.menus.find_one({"_id":ObjectId(id)})
#        print(menu)
#        menu["_id"]=str(menu["_id"])
#        menu["ownerId"]=str(menu["ownerId"])
#        menu["categoryId"]=str(menu["categoryId"])
#        menu["restaurantId"]=[str(id) for id in menu["restaurantId"]]

#        return menu
       


@router.get("/menu-detail")
def menu_detail(restaurantId:str,menuId:str,user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    if user["role"]!="super-admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
    data = db.restaurant_menu.find_one({"restaurantId":restaurantId,"menuId":menuId})
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No menus found")
    
        
    category=db.default_category.find_one({"_id":ObjectId(data["categoryId"])})
    if not category:
       category=db.category.find_one({"_id":ObjectId(data["categoryId"])})

    if category:
       category_details={'_id':str(data["categoryId"]),'name':category["name"]}

        
        
    formatted_one_resto = {
            **data,
            
            '_id': str(data['_id']),
            
            
            'categoryId': category_details,
            
            
        }
    # resultdata.append(formatted_one_resto)
    
    
    return formatted_one_resto

     
       
       
       
@router.put("/reset-password")
def reset_password(data:super_admin_schema.Reset,user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
      super_admin_id=user["super_admin_id"]      
      super_admin=collection.find_one({"_id":ObjectId(super_admin_id)})
      if not super_admin:
           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Super admin not found")
      if not utils.verify(data.currentPassword,super_admin['password']):
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Incorrect Password")
      if data.confirmPassword!=data.newPassword:
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password mismatch")
      password=utils.hash(data.newPassword)
      try:
        update_result=collection.update_one({"_id":ObjectId(super_admin_id)},{"$set":{"password":password}})
      except Exception as e:
           raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Updation failed")

    
      return "success"
           
        
       
    
       
       
       
       
@router.post("/black-list/{cater_id}")
def add_black_list(cater_id:str,Status:bool=False,user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
     if user["role"]!="super-admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
     try:
        cater=db.register.find_one({"_id":ObjectId(cater_id)})
        if not cater:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Cater not found")
        if cater['status']==Status:
                print("heere")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Trying to set the same status")
        db.register.update_one({"_id":ObjectId(cater_id)},{'$set':{"status":Status}})
        if Status==False:
             message="Blocked"
        else:
             message="Unblocked"
        return {"message":f"Cater status changed to {message}"} 
     except Exception as e:
         raise e
          


@router.get("/black-list")
def get_black_list(user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
         if user["role"]!="super-admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed") 
         blocked_caters=list(db.register.find({"status":False}))
         print(blocked_caters)
         for one in blocked_caters:
              one["_id"]=str(one["_id"])
              one.pop("profilePicture")
              one.pop("password")
         return blocked_caters
          
    
       
       
@router.get("/restaurants/location/{location}")
def restaurants_by_location(location:str,user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
       if user["role"]!="super-admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
       regex = re.compile(location, re.IGNORECASE)
       data = list(db.restaurants.find({"location": {"$regex": regex}}))
       
       for resto in data:
       #      print(resto)
            resto["_id"]=str(resto["_id"])
            resto.pop('latitude', None)
            resto.pop('longitude', None)
            resto.pop('contactNumber',None)
            resto.pop('business_hours',None)
            resto.pop('holidays',None)
            resto.pop('ownerId',None)
            resto.pop('image',None)
            resto.pop('status',None)
            resto.pop('location',None)
            resto.pop('averageStarCount',None)

            
            resto.pop('dateAdded',None)

       
       return data


         
       
# @router.post("/restaurant-category")  
# def restaurant_category(data:super_admin_schema.Category,user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
#      if user["role"]!="super-admin":
#          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
     
#      category=db.restaurant_category.find_one({"categoryName":data.categoryName,"location":data.location})
#      if category:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Category already exist")
#      restaurants=data.restaurants
     
#      for resto in restaurants:
#           database=db.restaurants.find_one({"_id":ObjectId(resto)})
#           if database["location"]!=data.location:
#                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Restaurant location mismatch")
#      datas={"location":data.location,"categoryName":data.categoryName,"restaurants":restaurants}
#      data_result=db.restaurant_category.insert_one(datas)
    
#      result= collection.find_one({'_id':data_result.inserted_id})
#      if result:
#         result["_id"]=str(result["_id"])
#      return {"message":"Category Added","data":result}
     


@router.post("/restaurant-category")
async def restaurant_category(data: super_admin_schema.Category,user=Depends(oauth2.verify_super_access_token), token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if user["role"] != "super-admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    length=db.restaurant_category.count_documents({"location":data.location})
    print(length)
    if length<5:

          category = db.restaurant_category.find_one({"categoryName": {"$regex": f"^{data.categoryName}$", "$options": "i"}, "location": data.location})
          if category:
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")

          restaurants = data.restaurants

          for resto in restaurants:
               database = db.restaurants.find_one({"_id": ObjectId(resto)})
               if not database or database["location"] != data.location:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Restaurant location mismatch")

          data_to_insert = {"location": data.location, "categoryName": data.categoryName,"description":data.description, "restaurants": restaurants}
          insert_result = db.restaurant_category.insert_one(data_to_insert)

          if not insert_result.acknowledged:
               raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to insert category")

          result = db.restaurant_category.find_one({'_id': insert_result.inserted_id})
          if not result:
               raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve inserted category")

          result["_id"] = str(result["_id"])
          await utils.invalidate_all_cache()

          return {"message": "Category Added", "data": result}
    else:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Category limit reached")


@router.get("/restaurant-category")
def get_all_category(user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    if user["role"]!="super-admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
    
    categories=list(db.restaurant_category.find())
    print(categories)
    for one in categories:
        one["_id"]=str(one["_id"])
        resto_details=[]
        restos=one["restaurants"]
        for i in restos:
               one_resto=db.restaurants.find_one({"_id":ObjectId(i)})
               
              
               if one_resto :     
                         print(one_resto)
                         one_resto["_id"]=str(one_resto["_id"])
                         one_resto['ownerId'] = str(one_resto['ownerId'])
                         one_resto.pop('latitude', None)
                         one_resto.pop('longitude', None)
                         one_resto.pop('contactNumber',None)
                         one_resto.pop('business_hours',None)
                         one_resto.pop('holidays',None)
                         
                         one_resto.pop('dateAdded',None)
                         resto_details.append(one_resto)

               
        one["restaurants"]=resto_details

    return categories

         
         



@router.put("/restaurant-category/{category_id}")  
async def restaurant_category(category_id:str,data:super_admin_schema.UpdateCategory,user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
     if user["role"]!="super-admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
     category=db.restaurant_category.find_one({"_id":ObjectId(category_id)})
     if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found")
     restaurants=data.restaurants
     for resto in restaurants:
          database=db.restaurants.find_one({"_id":ObjectId(resto)})
          if database["location"]!=category["location"]:
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Restaurant location mismatch")
     try:
          db.restaurant_category.update_one({"_id":ObjectId(category_id)},{"$set":{"restaurants":restaurants,"categoryName":data.categoryName,"description":data.description}})

     except Exception as e:
          print(e)
          raise HTTPException(status_code=500,detail="Error occured during updation")
     await utils.invalidate_all_cache()
     
     return "Category updated"
 




@router.delete("/restaurant-category/{category_id}")  
async def restaurant_category(category_id:str,user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
     if user["role"]!="super-admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
     category=db.restaurant_category.find_one({"_id":ObjectId(category_id)})
     if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found")
     try:
          db.restaurant_category.delete_one({"_id":ObjectId(category_id)})
     except Exception as e:
          raise HTTPException(status_code=500,detail="Error occured during deletion")
     await utils.invalidate_all_cache()
     
     return "Category deleted"
          




  
@router.get("/restaurant-category/{location}")  
def restaurant_category(
    location: str,
    user=Depends(oauth2.verify_super_access_token),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    if user["role"] != "super-admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed"
        )

    # Fetch categories based on location
    categories = list(db.restaurant_category.find({"location": location}))
    print(categories)
    
    for category in categories:
        category["_id"] = str(category["_id"])
        restos = category["restaurants"]
        
        if len(restos)==0:
            db.restaurant_category.delete_one({"_id":ObjectId(category["_id"])})
           

    categories = list(db.restaurant_category.find({"location": location}))
    for category in categories:
        resto_details = []

        category["_id"] = str(category["_id"])
        restos = category["restaurants"]        
        for resto_id in restos:
                
                one_resto = db.restaurants.find_one({"_id": ObjectId(resto_id)})
                if one_resto:
                    one_resto["_id"] = str(one_resto["_id"])
                    one_resto['ownerId'] = str(one_resto['ownerId'])
                    
                    
                    fields_to_remove = [
                        'latitude', 'longitude', 'contactNumber', 'business_hours', 
                        'holidays', 'dateAdded'
                    ]
                    for field in fields_to_remove:
                        one_resto.pop(field, None)
                    
                    resto_details.append(one_resto)
        
        category["restaurants"] = resto_details
    
    # Filter categories by active owners
    for category in categories:
        category["restaurants"] = [
            one for one in category["restaurants"]
            if db.register.find_one({"_id": ObjectId(one["ownerId"]), "status": True})
        ]
    
    
#     filtered_categories = [category for category in categories if category["restaurants"]]

    return categories
         
       
@router.get("/restaurant-category/details/{category_id}")  
def restaurant_category(category_id:str,user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
     if user["role"]!="super-admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")  
     result=db.restaurant_category.find_one({"_id":ObjectId(category_id)})
     result["_id"]=str(result["_id"])
     restos=result["restaurants"]
     resto_details=[]
     for one in restos:
               one_resto=db.restaurants.find_one({"_id":ObjectId(one)})
               print(one_resto)
               one_resto["_id"]=str(one_resto["_id"])
               one_resto['ownerId'] = str(one_resto['ownerId'])
               one_resto.pop('latitude', None)
               one_resto.pop('longitude', None)
               one_resto.pop('contactNumber',None)
               one_resto.pop('business_hours',None)
               one_resto.pop('holidays',None)
               
               one_resto.pop('dateAdded',None)
               resto_details.append(one_resto)
     result["restaurants"]=resto_details
     return result   
       


@router.post("/vip-status/{restaurantId}")
async def add_vip_status(restaurantId:str,Status:bool=True,user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    
    try:
         print(Status)
         if user["role"]!="super-admin":
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed") 
         resto=db.restaurants.find_one({"_id":ObjectId(restaurantId)})
         if not resto:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Restaurant not found")
         if resto["vipStatus"]==Status:
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Trying to set the same status")
         
              
              
         db.restaurants.update_one({"_id":ObjectId(restaurantId)},{"$set":{"vipStatus":Status}}) 
         await utils.invalidate_all_cache()

         return "VIP status added"
    except Exception as e:
         raise e
    
              
         

@router.get("/vip-status")
def get_vip_restaurants(user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
     if user["role"]!="super-admin":
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed") 
     vip_resto=list(db.restaurants.find({"vipStatus":True}))
     print(vip_resto)
     for one in vip_resto:
          one["_id"]=str(one["_id"])
          one["_id"]=str(one["_id"])
          one['ownerId'] = str(one['ownerId'])
          one.pop('latitude', None)
          one.pop('longitude', None)
          one.pop('contactNumber',None)
          one.pop('business_hours',None)
          one.pop('holidays',None)
               
          one.pop('dateAdded',None)
     return vip_resto
 

       