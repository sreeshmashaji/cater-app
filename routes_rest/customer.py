import asyncio
from datetime import datetime, timedelta
import json
import math
import re
from haversine import Unit
import haversine as hs
import time
import aiohttp
import redis.asyncio as aioredis
from typing import Annotated, Optional, Tuple
from bson import ObjectId
from fastapi import Body, File, Form, HTTPException, Query, UploadFile, status,APIRouter,Depends,BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter
import requests
from config.database import db
from schemas import customer_schema
import utils,oauth2
from services import emailvalidation,verify_password,phone_no_validation
from server import send_mail,otp_api
from server import send_mail
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from geopy.geocoders import Nominatim
import openrouteservice,googlemaps
from geopy import distance
import geocoder


auth_scheme = HTTPBearer()









router=APIRouter(prefix='/customers',tags=["Customer"])


geolocator = Nominatim(user_agent="my_app")
client = openrouteservice.Client(key='5b3ce3597851110001cf6248849362c01bdb4ee1b0597d2b71832179')

gmaps = googlemaps.Client(key='AIzaSyCD42xKGUAkd-0gWIPzAZzNHtNVZGYCS-4')

# geolocator = Nominatim(user_agent="myGeocoder")
# client = openrouteservice.Client(key='5b3ce3597851110001cf6248f4c7d953aa414dfcb1e5e67b0cb34c25')


collection = db.customer


redis = aioredis.from_url("redis://localhost")











@router.post('')
async def add_customer(data:customer_schema.Customer):
    try:
        if not emailvalidation.validate_email(data.email):
            raise HTTPException(status_code=400, detail="Invalid Email Address")

        existing_user = collection.find_one({'email': data.email})
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email Already Exists")
        if len(data.password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")
        
        is_valid, message = verify_password.validate_password(data.password)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
        
        if len(data.firstName) < 3:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please provide a valid name")
        phone_number=data.phoneNumber
        # cleaned_phone_number = phone_no_validation.validate_phone_number(data.phoneNumber)
        if not phone_number.isdigit():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number must contain only digits")
        if   len(phone_number) > 10:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Phone Number")

        data.password=utils.hash(data.password)
        print(data.password)
        update_data=customer_schema.CustomerSave(
        firstName= data.firstName,
        lastName= data.lastName ,
        email=data.email,
        password=data.password,
        phoneNumber=data.phoneNumber ,
        avatarId=data.avatarId
        

        )
        
        data= collection.insert_one(update_data.__dict__)
        resultdata= collection.find_one({'_id':data.inserted_id})
        resultdata["_id"]=str(resultdata["_id"])
        if not resultdata:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Sorry Operation Failed")
        
        send_mail.sendMail(resultdata["email"],"register")
        return {"message":"success","data":resultdata}
    except Exception as e:
        raise e










@router.get('/{id}',summary="  Fetching  registered customer by id")
async def geting(id:str,user=Depends(oauth2.verify_customer_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
        print("inside customer get")
        data = collection.find_one({"_id":ObjectId(id)})
        if user["customer_id"]!=id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")

        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
        data["_id"]=str(data["_id"])
        return data
    except Exception as e:
        raise e
    





@router.post('/customer-login')
def login(data: customer_schema.Login):
   try:
        user=collection.find_one({"email":data.email})
        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid credentials")
        if not utils.verify(data.password,user['password']):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid credentials")
        
        
        token=oauth2.create_customer_access_token({"email":data.email,"customer_id":str(user["_id"])})
        
        send_mail.sendMail(user["email"],"login")
        #    background_task.add_task(send_mail.sendMail,user["email"],"login" )
        name=user["firstName"]+" "+user["lastName"]   
        return {"token":token,"customer_id":str(user["_id"]),"avatar_id":user["avatarId"],"name":name}
   except Exception as e:
       raise e




@router.post('/verify-email-otp',summary="After login a verification otp will be send to the login mail ...we can verify that otp using this api ")
def verify_email(data:customer_schema.VerifyEmailOtp):
     try:
        data=otp_api.verify(data.otp,data.toMail)
        print("success ::",data)
        if data=="pending":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="OTP Verification Pending")
        elif data=="approved":
            return {"detail":data}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="OTP Expired")
     except Exception as e:
       raise e




@router.delete('/{customer_id}')
def delete_customer(customer_id:str,token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    user: str = Depends(oauth2.verify_customer_access_token)):
    try:
        customer=collection.find_one({"_id":ObjectId(customer_id)})
        
        if customer is None:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No customer Found")
        if ObjectId(user["customer_id"])!=customer["_id"]:
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
        collection.delete_one({"_id":ObjectId(customer_id)})
        return "Customer Deleted successfully"

    except Exception as e:
        raise e



@router.post('/forgot-password',summary="send mail to corresponding email address with reset password link")
def forgot_password(data:customer_schema.ForgotPassword,background_task:BackgroundTasks):
    try:
        user=collection.find_one({"email":data.email})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
        token= oauth2.create_reset_token({"email":data.email})
        print(token)
        # background_task.add_task(send_mail.sendMail,data.email,"forgot-password",token )
        send_mail.sendMail(data.email,"customer-forgot-password",token)
        return {"message":"email sent","reset_token":token}
    except Exception as e:
        raise e


@router.post('/reset-password',summary=" api working with  reset password  link send through forgot password email")
def pasword_reset(data:customer_schema.PasswordRest,email=Depends(oauth2.verify_reset_token),token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    try:
        if email != data.email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Email mismatch")
        if data.newPassword ==data.confirmPassword:
            existing_user=collection.find_one({"email":email})
            hashpass=utils.hash(data.newPassword)
            existing_user["password"]=hashpass
            collection.update_one({"email":email},{'$set':{"password":hashpass}})
            print(existing_user)
            return "Password Updated"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password mismatch")
    except Exception as e:
         raise e



@router.post('/resend-link',summary="resend otp when 1st attempt failed")
def resend_otp(data:customer_schema.ForgotPassword,background_task:BackgroundTasks):
    try:
        start_time = time.time()  

        user=collection.find_one({"email":data.email})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
        token= oauth2.create_reset_token({"email":data.email})
        print(token)
        background_task.add_task(send_mail.sendMail,data.email,"forgot-password",token )
        end_time = time.time()  
        total_time = end_time - start_time  
        print(f"Total time taken: {total_time} seconds")
        return "email sent"
    except Exception as e:
        raise e





@router.post('/customer-reset-password',summary="customer can change their current password into new one ")
def reset(data:customer_schema.Reset,user=Depends(oauth2.verify_customer_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
        existing_user = collection.find_one({'email': user["email"]})
        if not existing_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
        if not utils.verify(data.currentPassword,existing_user['password']):
          raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Incorrect Password")
        if data.newPassword != data.confirmPassword:
          raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password Mismatch")
        hashpass=utils.hash(data.newPassword)
        existing_user["password"]=hashpass
        collection.update_one({"email":user["email"]},{'$set':{"password":hashpass}})
        print(existing_user)
        return "Password Updated"
    except Exception as e:
        raise e



  
# NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org/search"
# OSRM_BASE_URL = "https://router.project-osrm.org/route"

# redis = aioredis.from_url("redis://localhost")

# async def get_geocode_cache(location: str):
#     cached_value = await redis.get(location)
#     if cached_value:
#         return tuple(map(float, cached_value.decode("utf-8").split(',')))
#     return None

# async def set_geocode_cache(location: str, latitude: float, longitude: float):
#     await redis.set(location, f"{latitude},{longitude}", ex=300)  # Cache for 24 hours

# async def fetch_distance_duration(user_coords: Tuple[float, float], restaurant_coords: Tuple[float, float]) -> Optional[Tuple[float, float]]:
#   async with aiohttp.ClientSession() as session:
#     url = f"{OSRM_BASE_URL}/v1/driving/{user_coords[1]},{user_coords[0]};{restaurant_coords[1]},{restaurant_coords[0]}"
#     params = {
#       "overview": "full",
#       "geometries": "geojson",
#       "annotations": "duration,distance"
#     }
#     async with session.get(url, params=params) as response:
#       if response.status == 200:
#         data = await response.json()
#         if data.get("code") == "Ok":
#           duration = data["routes"][0]["duration"] / 60
#           distance = data["routes"][0]["distance"] / 1000
#           return distance, duration
#       return None, None


# @router.get('/restaurants-distance/{location}')
# async def get_restaurant_by_location(location: str, offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)):
#     try:
#         # Use OSM Nominatim to geocode location
#         params = {
#             "format": "json",
#             "q": location,
#             "limit": 1
#         }
#         response = requests.get(NOMINATIM_BASE_URL, params=params)
#         print(response)
#         response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
#         data = response.json()
#         print(data)
#         if data:
#             latitude = float(data[0]["lat"])
#             longitude = float(data[0]["lon"])
#         else:
#             raise HTTPException(status_code=404, detail="Location not found")
#     except (requests.RequestException, ValueError) as e:
#         raise HTTPException(status_code=500, detail=f"Failed to geocode location : {e}")

#     user_coords = (latitude, longitude)

#     regex = re.compile(location, re.IGNORECASE)
#     # Fetch restaurant data from MongoDB based on location regex
#     cursor = db.restaurants.find({"location": {"$regex": regex}}).skip(offset).limit(limit)
#     data = list(cursor)

#     restaurant_data = []
#     tasks = []

#     for doc in data:
#         doc['_id'] = str(doc['_id'])
#         doc['ownerId'] = str(doc['ownerId'])
#         restaurant_coords = (doc.get('latitude'), doc.get('longitude'))

#         if restaurant_coords:
#             tasks.append(fetch_distance_duration(user_coords, restaurant_coords))
#         else:
#             doc['distance_km'] = None
#             doc['duration_min'] = None

#         # Remove unnecessary fields
#         doc.pop('latitude', None)
#         doc.pop('longitude', None)
#         doc.pop('contactNumber', None)
#         doc.pop('business_hours', None)
#         doc.pop('holidays', None)
#         doc.pop('status', None)
#         doc.pop('dateAdded', None)

#         restaurant_data.append(doc)

#     distances_durations = await asyncio.gather(*tasks)
#     for i, (distance, duration) in enumerate(distances_durations):
#         restaurant_data[i]['distance_km'] = distance
#         restaurant_data[i]['duration_min'] = duration

#     return JSONResponse(content=restaurant_data)


# @router.get('/restaurants/{location}')
# def get_restaurant_by_location(location: str, offset: int = Query(0), limit: int = Query(20)):
   
    
    
    # try:
    #     location_data = geolocator.geocode(location)
    #     latitude = location_data.latitude
    #     longitude = location_data.longitude
    # except (AttributeError, GeocoderTimedOut):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to geocode location")
    
    
    
#     # user_coords = (longitude, latitude)
    
    
#     regex = re.compile(location, re.IGNORECASE)
#     data = list(db.restaurants.find({"location": {"$regex": regex}}).skip(offset).limit(limit))
    
#     restaurant_data = []
#     for doc in data:

#         doc['_id'] = str(doc['_id'])
#         doc['ownerId'] = str(doc['ownerId'])
        
        
#         restaurant_coords = (doc.get('longitude'), doc.get('latitude'))
#         print(f"Restaurant coordinates: {restaurant_coords}")
        
#         # try:
#         #     routes = client.directions(coordinates=[user_coords, restaurant_coords], profile='driving-car', format='geojson')
#         #     distance = routes['features'][0]['properties']['segments'][0]['distance'] / 1000  # Convert meters to kilometers
#         #     duration = routes['features'][0]['properties']['segments'][0]['duration'] / 60  # Convert seconds to minutes

           
#         #     doc['distance_km'] = distance
#         #     doc['duration_min'] = duration
#         # except openrouteservice.exceptions.ApiError as e:
#         #     print(f"Error calculating directions: {e}")
            
            
            
#             # doc['distance_km'] = None
#             # doc['duration_min'] = None
            

       
#         doc.pop('latitude', None)
#         doc.pop('longitude', None)
#         doc.pop('contactNumber',None)
#         doc.pop('business_hours',None)
#         doc.pop('holidays',None)
        
#         doc.pop('dateAdded',None)





        
        
#         restaurant_data.append(doc)
    
    
    
#     return restaurant_data






@router.get('/restaurant-details/{restaurant_id}')
async def get_restaurant(restaurant_id: str):
    try:
       

    # Check if the data is in cache
        cache_key = f"restaurant-detail:{restaurant_id}"
    
    # Check if the data is in cache
        cached_data = await redis.get(cache_key)
        if cached_data:
           return json.loads(cached_data)
        restaurant_details = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
        print(restaurant_details)
        restaurant_details.pop("dateAdded",None)
        if not restaurant_details:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        owner=db.register.find_one({"_id":restaurant_details["ownerId"]})
        if not owner:
            raise HTTPException(status_code=404, detail="Owner not found")

        if owner["status"]==False:
            raise HTTPException(status_code=403, detail="Restaurant details not available")
        

        # Initialize menu details list
        menu_details = []
        
        # Retrieve menu data from restaurant_menu collection
        datas = list(db.restaurant_menu.find({"restaurantId": restaurant_id}))
        print(datas)
        
        for data in datas:
            # Directly use data from restaurant_menu
            menu_data = {
                
                "_id": str(data["menuId"]),
                "name": data.get("name"),
                "desc": data.get("desc"),
                "price": data.get("price"),
                "minimumServe": data.get("minimumServe"),
                "type": data.get("type"),
                "image": data.get("image"),
                "categoryId": data.get("categoryId"),
                "averageStarCount":data.get("averageStarCount",0)
            }

            # Retrieve and append category details
            if data.get("categoryId"):
                category = db.default_category.find_one({"_id": ObjectId(data["categoryId"])})
                if not category:
                   category = db.category.find_one({"_id": ObjectId(data["categoryId"])})
                       
                if category:
                    category_details = {'_id': str(category.get("_id")), 'name': category.get("name")}
                    menu_data['categoryId'] = category_details

            menu_details.append(menu_data)


        # Convert ObjectId to string for restaurant details
        restaurant_details["_id"] = str(restaurant_details["_id"])
        offer=db.offers.find_one({"restaurants":restaurant_details["_id"]})
        if offer:
            offer["_id"]=str(offer["_id"])
            offer.pop("ownerId")
            offer.pop("restaurants")
            offer["createdAt"]=offer["createdAt"].isoformat()
            restaurant_details["offer"]=offer
        restaurant_details["ownerId"] = str(restaurant_details["ownerId"])
        ratingCount=db.reviews.count_documents({"restaurantId":ObjectId(restaurant_id)})
        restaurant_details["ratingCount"]=ratingCount 
        full_details = {
            'restaurant_details': restaurant_details,
            'menu_details': menu_details
        }
        await redis.set(cache_key,json.dumps(full_details),ex=200)
        return full_details
    except Exception as e:
        raise e




@router.get('/menu-details/{menuId}')
async def get_menus_by_id(menuId:str,restaurantId:str):
    try:  
            cache_key = f"menu_detail:{menuId}:{restaurantId}"
    
    # Check if the data is in cache
            cached_data = await redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        
            data = db.restaurant_menu.find_one({"restaurantId":restaurantId,"menuId":menuId})
            if not data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No menus found")
            resto=db.restaurants.find_one({"_id":ObjectId(restaurantId)})
            owner=db.register.find_one({"_id":ObjectId(resto["ownerId"])})
            if owner:
                if owner["status"]==False:
                        raise HTTPException(status_code=403, detail="Menu details not available")    
            category=db.default_category.find_one({"_id":ObjectId(data["categoryId"])})
            if not category:
              category=db.category.find_one({"_id":ObjectId(data["categoryId"])})

            if category:
             category_details={'_id':str(data["categoryId"]),'name':category["name"]}

                
                
            formatted_doc = {
                    **data,
                    
                    '_id': str(data['_id']),
                    
                    
                    'categoryId': category_details,
                    
                    
                }
            # resultdata.append(formatted_doc)
            
            await redis.set(cache_key,json.dumps(formatted_doc),ex=200)
            return formatted_doc
    except Exception as e:
        raise e







@router.get('/restaurants-filter/{name}')
async def get_restaurant_by_name(name: str, location:str,offset: int = Query(0), limit: int = Query(20)):
    try:
            cache_key = f"restaurants-name:{name}:{location}:{offset}:{limit}"
    
    # Check if the data is in cache
            cached_data = await redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            regex = re.compile(name, re.IGNORECASE)
            data = list(db.restaurants.find({"name": {"$regex": regex},"location":location}))
            
            print("data",data)
            restaurant_data = []
            for doc in data:
                
                owner_detail=db.register.find_one({"_id":doc["ownerId"]})
                print("Onwer",owner_detail)
                if owner_detail["status"]==True:
                    ratingCount=db.reviews.count_documents({"restaurantId":ObjectId(doc["_id"])})
                    doc["ratingCount"]=ratingCount
                    doc['_id'] = str(doc['_id'])
                    offers=db.offers.find({"restaurants":doc["_id"]})
                    offerList=[]
                    if offers:
                        for offer in offers:
                                    offer["_id"]=str(offer["_id"])
                                    offer["createdAt"]=offer["createdAt"].isoformat()
                                    offer.pop("ownerId")
                                    offer.pop("restaurants")
                                    offerList.append(offer)
                        doc["offer"]=offerList


                    doc['ownerId'] = str(doc['ownerId'])
                    # doc.pop('latitude', None)
                    # doc.pop('longitude', None)
                    doc.pop('contactNumber',None)
                    doc.pop('business_hours',None)
                    doc.pop('holidays',None)
                    
                    doc.pop('dateAdded',None)
                    restaurant_data.append(doc)

            
            resto_menu=list(db.restaurant_menu.find({"location":location,"name": {"$regex": regex}}))
            if resto_menu:
                        for i in resto_menu:
                            doc=db.restaurants.find_one({"_id":ObjectId(i["restaurantId"])})
                            owner_detail=db.register.find_one({"_id":doc["ownerId"]})

                            if owner_detail["status"]==True:
                                ratingCount=db.reviews.count_documents({"restaurantId":ObjectId(doc["_id"])})
                                doc["ratingCount"]=ratingCount
                                doc['_id'] = str(doc['_id'])
                                doc['ownerId'] = str(doc['ownerId'])
                                
                                doc.pop('contactNumber',None)
                                doc.pop('business_hours',None)
                                doc.pop('holidays',None)
                        
                                doc.pop('dateAdded',None)

                                restaurant_data.append(doc)

                    
            
            unique=remove_duplicates(restaurant_data)
            result=unique[offset:offset + limit]
            for one in result:
                price_aggregation = db.restaurant_menu.aggregate([
                                            {"$match": {"restaurantId": one["_id"]}},
                                            {"$group": {"_id": None, "low_price": {"$min": "$price"}}}
                                        ])
                price_aggregation = list(price_aggregation)
                if price_aggregation:
                                print(price_aggregation[0]["low_price"])
                                one["low_price"] = price_aggregation[0]["low_price"]
            await redis.set(cache_key,json.dumps(result),ex=200)
            return result
    except Exception as e:
        raise e





def remove_duplicates(items):
    seen_ids = set()
    unique_items = []
    for item in items:
        if item["_id"] not in seen_ids:
            unique_items.append(item)
            seen_ids.add(item["_id"])
    return unique_items

#  

# @router.get('/restaurants/{location}') #withoutv redis
# async def get_restaurant_by_location(location: str, offset: int = Query(0), limit: int = Query(20)):
#     try:
#         location_data = geolocator.geocode(location)
#         if not location_data:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to geocode location")
#         latitude = location_data.latitude
#         longitude = location_data.longitude
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

#     user_coords = (latitude, longitude)
#     regex = re.compile(location, re.IGNORECASE)


#     data = list(db.restaurants.find({"location": {"$regex": regex}}).sort("dateAdded", -1).skip(offset).limit(limit))
      
#     restaurant_data = []
#     for doc in data:
#         time = doc['dateAdded']
#         current_time = datetime.utcnow()
#         seven_days_ago = current_time - timedelta(days=7)
#         doc["is_new"] = time >= seven_days_ago

#         owner = db.register.find_one({"_id": ObjectId(doc["ownerId"])})
#         if owner and owner["status"]:
#             doc['_id'] = str(doc['_id'])
#             offer = db.offers.find_one({"restaurants": doc["_id"]})
#             if offer:
#                 doc["offer"] = {
#                     "_id": str(offer['_id']),
#                     "title": offer["title"],
#                     "description": offer["description"],
#                     "createdAt": offer["createdAt"]
#                 }
#             doc['ownerId'] = str(doc['ownerId'])

#             rating_count = db.reviews.count_documents({"restaurantId": ObjectId(doc["_id"])})
#             doc["ratingCount"] = rating_count

#             restaurant_coords = (doc.get('latitude'), doc.get('longitude'))
#             # if restaurant_coords[0] and restaurant_coords[1]:
#             #     dist = geopy_distance.distance(user_coords, restaurant_coords).km
#             #     doc["distance"] = dist

#             price_aggregation = db.restaurant_menu.aggregate([
#                 {"$match": {"restaurantId": doc["_id"]}},
#                 {"$group": {"_id": None, "low_price": {"$min": "$price"}}}
#             ])
#             price_aggregation = list(price_aggregation)
#             if price_aggregation:
#                 print(price_aggregation[0]["low_price"])
#                 doc["low_price"] = price_aggregation[0]["low_price"]

#             doc.pop('contactNumber', None)
#             doc.pop('business_hours', None)
#             doc.pop('holidays', None)
#             doc.pop('dateAdded', None)
#             print(doc)
#             restaurant_data.append(doc)

#     result = restaurant_data
#     return result




@router.get('/restaurants/{location}')
async def get_restaurant_by_location(location: str, offset: int = Query(0), limit: int = Query(20)):
    cache_key = f"restaurants:{location}:{offset}:{limit}"
    
    # Check if the data is in cache
    cached_data = await redis.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    try:
        location_data = geolocator.geocode(location)
        if not location_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to geocode location")
        latitude = location_data.latitude
        longitude = location_data.longitude
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    user_coords = (latitude, longitude)
    regex = re.compile(location, re.IGNORECASE)

    data = list(db.restaurants.find({"location": {"$regex": regex}}).sort("dateAdded", -1).skip(offset).limit(limit))
    
    restaurant_data = []
    for doc in data:
        time = doc['dateAdded']
        current_time = datetime.utcnow()
        seven_days_ago = current_time - timedelta(days=7)
        doc["is_new"] = time >= seven_days_ago

        owner = db.register.find_one({"_id": ObjectId(doc["ownerId"])})
        if owner and owner["status"]:
            doc['_id'] = str(doc['_id'])
            offers=db.offers.find({"restaurants":doc["_id"]})
            offerList=[]
            if offers:
                for offer in offers:
                                    offer["_id"]=str(offer["_id"])
                                    offer["createdAt"]=offer["createdAt"].isoformat()
                                    offer.pop("ownerId")
                                    offer.pop("restaurants")
                                    offerList.append(offer)
                doc["offer"]=offerList
            doc['ownerId'] = str(doc['ownerId'])

            rating_count = db.reviews.count_documents({"restaurantId": ObjectId(doc["_id"])})
            doc["ratingCount"] = rating_count

            restaurant_coords = (doc.get('latitude'), doc.get('longitude'))
            # if restaurant_coords[0] and restaurant_coords[1]:
            #     dist = geopy_distance.distance(user_coords, restaurant_coords).km
            #     doc["distance"] = dist

            price_aggregation = db.restaurant_menu.aggregate([
                {"$match": {"restaurantId": doc["_id"]}},
                {"$group": {"_id": None, "low_price": {"$min": "$price"}}}
            ])
            price_aggregation = list(price_aggregation)
            if price_aggregation:
                print(price_aggregation[0]["low_price"])
                doc["low_price"] = price_aggregation[0]["low_price"]

            doc.pop('contactNumber', None)
            doc.pop('business_hours', None)
            doc.pop('holidays', None)
            doc.pop('dateAdded', None)
            for key, value in doc.items():
                if isinstance(value, datetime):
                    doc[key] = value.isoformat()
            # print(doc)
            restaurant_data.append(doc)

    result = restaurant_data
    print(result)

    
    await redis.set(cache_key, json.dumps(result),ex=200)
#     await redis.set(location, f"{latitude},{longitude}", ex=300)  # Cache for 24 hours

    
    return result










@router.get("/all-restaurants/{location}")
async def get_all_restaurants(location:str):
    try:
            

            cache_key = f"restaurants:{location}"
    
            cached_data = await redis.get(cache_key)
            if cached_data:
               return json.loads(cached_data)

            regex = re.compile(location, re.IGNORECASE)
            # restos=list(db.restaurants.find({"location": {"$regex": regex}}))
            restos = list(db.restaurants.find({"location": {"$regex": regex}}).sort("dateAdded", -1))

            # print(restos)
            result=[]
            for resto in restos:
                owner=db.register.find_one({"_id":resto["ownerId"]})
                if owner:
                    if owner["status"]==True:
                            resto["_id"]=str(resto["_id"])
                            offers=db.offers.find({"restaurants":resto["_id"]})
                            offerList=[]
                            if offers:
                                for offer in offers:
                                    offer["_id"]=str(offer["_id"])
                                    offer["createdAt"]=offer["createdAt"].isoformat()
                                    offer.pop("ownerId")
                                    offer.pop("restaurants")
                                    offerList.append(offer)
                                resto["offer"]=offerList


                            ratingCount=db.reviews.count_documents({"restaurantId":ObjectId(resto["_id"])})
                            resto["ratingCount"]=ratingCount
                            resto.pop("ownerId")
                            price_aggregation = db.restaurant_menu.aggregate([
                {"$match": {"restaurantId": resto["_id"]}},
                {"$group": {"_id": None, "low_price": {"$min": "$price"}}}
            ])
                            price_aggregation = list(price_aggregation)
                            if price_aggregation:
                                print(price_aggregation[0]["low_price"])
                                resto["low_price"] = price_aggregation[0]["low_price"]
                            resto.pop("contactNumber")
                            resto.pop("business_hours")
                            resto.pop("holidays")
                            resto.pop("dateAdded")
                            result.append(resto)

            await redis.set(cache_key,json.dumps(result),ex=200)
            return result   
    except Exception as  e:
        raise e


# @router.get("/top-five-restaurants/{location}")
# def get_five_restaurants(location:str):
#     restos=list(db.restaurants.find({"location":location}).limit(5))
#     # print(restos)
#     for resto in restos:
#         resto["_id"]=str(resto["_id"])
#         resto.pop("ownerId")
#         resto.pop("latitude")
#         resto.pop("longitude")
#         resto.pop("contactNumber")
#         resto.pop("business_hours")
#         resto.pop("holidays")
#         resto.pop("dateAdded")

#     print(restos)
#     return restos


# @router.get("/top-five-restaurants/{location}")
# def get_five_restaurants(location:str):
#     try:
#         regex = re.compile(location, re.IGNORECASE)
#         restos=list(db.restaurants.find({"location": {"$regex": regex}}))
        
        
#         count_dict=[]
#         for resto in restos:
#             owner=db.register.find_one({"_id":resto["ownerId"]})
#             if owner:
#                 if owner["status"]==True:
#                     resto["_id"]=str(resto["_id"])
#                     resto.pop("ownerId")
#                     resto.pop("latitude")
#                     resto.pop("longitude")
#                     resto.pop("contactNumber")
#                     resto.pop("business_hours")
#                     resto.pop("holidays")
#                     resto.pop("dateAdded")
                    
#                     count=db.restaurants.find_one({"_id":ObjectId(resto["_id"])})
#                     starcount=count.get('averageStarCount', 0)
                    
#                     count_dict.append({"resto":resto,"count":starcount})
#         top_5 = sorted(count_dict, key=lambda x: x['count'], reverse=True)[:5]
#         for one in top_5:
#             ratingCount=db.reviews.count_documents({"restaurantId":ObjectId(one["resto"]["_id"])})

#             one["resto"]["ratingCount"]=ratingCount
#             one.pop("count")
#         return top_5
        
#     except Exception as e:
#         raise e
        



@router.get("/top-five-restaurants/{location}")
async def get_five_restaurants(location: str):
    try:

        cache_key=f"top-five:{location}"

        cache_data=await redis.get(cache_key)
        if cache_data:
            return json.loads(cache_data)

        regex = re.compile(location, re.IGNORECASE)
        
        # Aggregation pipeline to filter, join, and project necessary fields
        pipeline = [
            {"$match": {"location": {"$regex": regex}}},
            {"$lookup": {
                "from": "register",
                "localField": "ownerId",
                "foreignField": "_id",
                "as": "owner"
            }},
            {"$unwind": "$owner"},
            {"$match": {"owner.status": True}},
            {"$project": {
                "_id": 1,
                "name": 1,
                "location": 1,
                "image": 1,
                "averageStarCount": 1,
            }},
            {"$sort": {"averageStarCount": -1}},
            {"$limit": 5}
        ]
        
        top_5_restos = list(db.restaurants.aggregate(pipeline))
        
        for resto in top_5_restos:
            resto["_id"] = str(resto["_id"])
            rating_count = db.reviews.count_documents({"restaurantId": ObjectId(resto["_id"])})
            resto["ratingCount"] = rating_count
        await redis.set(cache_key,json.dumps(top_5_restos),ex=600)
        return top_5_restos
        # return []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))     



@router.get("/restaurants/category/{location}")
async def get_category(location:str):

     cache_key=f"category:{location}"
     cache_data=await redis.get(cache_key)
     if cache_data:
         return json.loads(cache_data)
     regex = re.compile(location, re.IGNORECASE)
     categories=list(db.restaurant_category.find({"location":{"$regex": regex}}))
     print(categories)
     for i in categories:
          i["_id"]=str(i["_id"])
          restos=i["restaurants"]
          resto_details=[]
          for one in restos:
               one_resto=db.restaurants.find_one({"_id":ObjectId(one)})
               print(one_resto)
               if one_resto:
                    one_resto["_id"]=str(one_resto["_id"])
                    offers=db.offers.find({"restaurants":one_resto["_id"]})
                    offerList=[]
                    if offers:
                        for offer in offers:
                                            offer["_id"]=str(offer["_id"])
                                            offer["createdAt"]=offer["createdAt"].isoformat()
                                            offer.pop("ownerId")
                                            offer.pop("restaurants")
                                            offerList.append(offer)
                        one_resto["offer"]=offerList
                        
                    one_resto['ownerId'] = str(one_resto['ownerId'])
                    price_aggregation = db.restaurant_menu.aggregate([
                        {"$match": {"restaurantId": one_resto["_id"]}},
                        {"$group": {"_id": None, "low_price": {"$min": "$price"}}}
                    ])
                    price_aggregation = list(price_aggregation)
                    if price_aggregation:
                        print(price_aggregation[0]["low_price"])
                        one_resto["low_price"] = price_aggregation[0]["low_price"]
                    one_resto.pop('contactNumber',None)
                    one_resto.pop('business_hours',None)
                    one_resto.pop('holidays',None)
                    
                    one_resto.pop('dateAdded',None)
                    resto_details.append(one_resto)
          i["restaurants"]=resto_details
     filtered_categories = [category for category in categories if category["restaurants"]]
     await redis.set(cache_key,json.dumps(filtered_categories),ex=600)  

     return filtered_categories
     

    

@router.get("/restaurants/search/category")
async def serach_category(category_id:str,location:str):

    cache_key=f"search:{location}:{category_id}"  
    cache_data=await redis.get(cache_key)
    if cache_data:
        return json.loads(cache_data)
    restaurants=list(db.restaurants.find({"location":location}))
    
    
    restaurant_detail=[]
    for one in restaurants:
        id=one["_id"]
        restos=list(db.restaurant_menu.find({"restaurantId":str(id),"categoryId":ObjectId(category_id)}))
        print("resto",restos)
        for resto in restos:
            restoone=db.restaurants.find_one({"_id":ObjectId(resto["restaurantId"])})
            if restoone:
                restoone["_id"]=str(restoone["_id"])
                offers=db.offers.find({"restaurants":restoone["_id"]})
                offerList=[]
                if offers:
                    for offer in offers:
                                            offer["_id"]=str(offer["_id"])
                                            offer["createdAt"]=offer["createdAt"].isoformat()
                                            offer.pop("ownerId")
                                            offer.pop("restaurants")
                                            offerList.append(offer)
                    restoone["offer"]=offerList
                restoone["ownerId"]=str(restoone["ownerId"])

                fields_to_remove = [
                   'contactNumber', 'business_hours', 
                    'holidays', 'dateAdded'
                ]
                for field in fields_to_remove:
                    restoone.pop(field, None)
                price_aggregation = db.restaurant_menu.aggregate([
                {"$match": {"restaurantId": restoone["_id"]}},
                {"$group": {"_id": None, "low_price": {"$min": "$price"}}}
            ])
                price_aggregation = list(price_aggregation)
                if price_aggregation:
                    print(price_aggregation[0]["low_price"])
                    restoone["low_price"] = price_aggregation[0]["low_price"]
                restaurant_detail.append(restoone)
    result=remove_duplicates(restaurant_detail)
    await redis.set(cache_key,json.dumps(result),ex=600)
    return result
    




            


@router.get("/category/restaurant")
async def category_with_restaurants(restaurantId:str,category_id:str):
    cache_key=f"category_restaurant:{restaurantId}:{category_id}"
    cache_data=await redis.get(cache_key)
    if cache_data:
        return json.loads(cache_data)
    restos=list(db.restaurant_menu.find({"restaurantId":restaurantId,"categoryId":category_id}))
    menus=[]
    for one in restos:
        # category=db.default_category.find_one({"_id":ObjectId(one["categoryId"])})
        # if not category:
        #  category=db.category.find_one({"_id":ObjectId(one["categoryId"])})
        
        # if categoryName==category["name"]:
            one.pop("_id")
            one.pop("location")

            one.pop("restaurantId")
            one["categoryId"]=str(one["categoryId"])
            menus.append(one)
    print(menus)
    await redis.set(cache_key,json.dumps(menus),ex=300)
    return menus

            

@router.get("/restaurants/search/price")
async def get_by_price(location:str,price:int):

    cache_key=f"price:{location}:{price}"
    cache_data=await redis.get(cache_key)
    if cache_data:
        return json.loads(cache_data)
    print("inside")
    resto_list=list(db.restaurants.find({"location":location}))
    resto_result=[]
    for resto in resto_list:
         id=resto["_id"]
         print(id)
         if resto["minimum_price"]<=price:
                print("equal")
                # restaurant=db.restaurants.find_one({"_id":ObjectId(id)})
                # print("restaurant",restaurant)
                resto["_id"]=str(resto["_id"])
                offers=db.offers.find({"restaurants":resto["_id"]})
                offerList=[]
                if offers:
                    for offer in offers:
                                            offer["_id"]=str(offer["_id"])
                                            offer["createdAt"]=offer["createdAt"].isoformat()
                                            offer.pop("ownerId")
                                            offer.pop("restaurants")
                                            offerList.append(offer)
                    resto["offer"]=offerList
                resto['ownerId'] = str(resto['ownerId'])
             
                resto.pop('contactNumber',None)
                resto.pop('business_hours',None)
                resto.pop('holidays',None)
                price_aggregation = db.restaurant_menu.aggregate([
                {"$match": {"restaurantId": resto["_id"]}},
                {"$group": {"_id": None, "low_price": {"$min": "$price"}}}
            ])
                price_aggregation = list(price_aggregation)
                if price_aggregation:
                    print(price_aggregation[0]["low_price"])
                    resto["low_price"] = price_aggregation[0]["low_price"]
                    
                resto.pop('dateAdded',None)
                resto_result.append(resto)
    result=remove_duplicates(resto_result)
    await redis.set(cache_key,json.dumps(result),ex=300)
    return result
         












    
    # resto_result=[]
    # for resto in resto_list:
    #     id=resto["_id"]
    #     print(id)
    #     resto_menu=list(db.restaurant_menu.find({"restaurantId":str(id)}))
    #     print("resto",resto_menu)
    #     for one in resto_menu:
    #         print(one["price"])
    #         if one["price"]<=price:
    #             print("equal")
    #             restaurant=db.restaurants.find_one({"_id":ObjectId(id)})
    #             print("restaurant",restaurant)
    #             restaurant["_id"]=str(restaurant["_id"])
    #             offers=db.offers.find({"restaurants":restaurant["_id"]})
    #             offerList=[]
    #             if offers:
    #                 for offer in offers:
    #                                         offer["_id"]=str(offer["_id"])
    #                                         offer["createdAt"]=offer["createdAt"].isoformat()
    #                                         offer.pop("ownerId")
    #                                         offer.pop("restaurants")
    #                                         offerList.append(offer)
    #                 restaurant["offer"]=offerList
    #             restaurant['ownerId'] = str(restaurant['ownerId'])
             
    #             restaurant.pop('contactNumber',None)
    #             restaurant.pop('business_hours',None)
    #             restaurant.pop('holidays',None)
    #             price_aggregation = db.restaurant_menu.aggregate([
    #             {"$match": {"restaurantId": restaurant["_id"]}},
    #             {"$group": {"_id": None, "low_price": {"$min": "$price"}}}
    #         ])
    #             price_aggregation = list(price_aggregation)
    #             if price_aggregation:
    #                 print(price_aggregation[0]["low_price"])
    #                 restaurant["low_price"] = price_aggregation[0]["low_price"]
                    
    #             restaurant.pop('dateAdded',None)
    #             resto_result.append(restaurant)
    # result=remove_duplicates(resto_result)
    # await redis.set(cache_key,json.dumps(result),ex=300)
    # return result




@router.get("/categories/{restaurantId}")
async def category_with_restoId(restaurantId:str):

    print("herer")
    cache_key=f"categories:{restaurantId}"
    cache_data=await redis.get(cache_key)
    if cache_data:
        return json.loads(cache_data)
    resto_details=db.restaurant_menu.find({"restaurantId":restaurantId})
    categories=[]
    for one in resto_details:
        
        category=db.default_category.find_one({"_id":ObjectId(one["categoryId"])})
        if not category:
            category=db.category.find_one({"_id":ObjectId(one["categoryId"])})
        category["_id"]=str(category["_id"])
        category.pop("ownerId",None)

        categories.append(category)
    print(categories)
    result=remove_duplicates(categories)
    await redis.set(cache_key,json.dumps(result),ex=600)
    return result




@router.get("/location/coordinates/{location}")
def get_coordinates(location: str):
    try:
        # Basic validation for location input
        if not location or not re.match(r"^[a-zA-Z0-9\s,.-]+$", location):
            raise ValueError("Invalid location input")
        
        location_data = geolocator.geocode(location)
        
        if location_data is None:
            raise ValueError("Location not found")

        # Additional checks to validate the location further
        if len(location_data.address.split(',')) < 2:
            raise ValueError("Location not specific enough")

        latitude = location_data.latitude
        longitude = location_data.longitude

        return {"longitude": longitude, "latitude": latitude}

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except AttributeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to geocode location")
    



@router.get('/cuisine/all')
async def get_categories():
    try:
        data = list(db.cuisine.find().limit(10000))  
        data = [{**doc, '_id': str(doc['_id'])} for doc in data]
       
        return data
    except Exception as e:
        raise e
    





@router.get("/restaurants/search/cuisine")
async def serach_category(cuisine_id:str,location:str):

    # cache_key=f"search:{location}:{category_id}"  
    # cache_data=await redis.get(cache_key)
    # if cache_data:
    #     return json.loads(cache_data)
    restaurants=list(db.restaurants.find({"location":location}))
    resto_list=[]
    for resto in restaurants:
        # resto_detail=db.restaurants.find_one({"_id":ObjectId(resto["_id"])})
        cuisine=resto["cuisine_types"]
        
        for one in cuisine:
            
            if one==cuisine_id:
                print(resto["name"])
                owner=db.register.find_one({"_id":resto["ownerId"]})
                if owner:
                    if owner["status"]==True:
                            resto["_id"]=str(resto["_id"])
                            offers=db.offers.find({"restaurants":resto["_id"]})
                            offerList=[]
                            if offers:
                              for offer in offers:
                                            offer["_id"]=str(offer["_id"])
                                            offer["createdAt"]=offer["createdAt"].isoformat()
                                            offer.pop("ownerId")
                                            offer.pop("restaurants")
                                            offerList.append(offer)
                              resto["offer"]=offerList


                            ratingCount=db.reviews.count_documents({"restaurantId":ObjectId(resto["_id"])})
                            resto["ratingCount"]=ratingCount
                            resto.pop("ownerId")
                            price_aggregation = db.restaurant_menu.aggregate([
                {"$match": {"restaurantId": resto["_id"]}},
                {"$group": {"_id": None, "low_price": {"$min": "$price"}}}
            ])
                            price_aggregation = list(price_aggregation)
                            if price_aggregation:
                                print(price_aggregation[0]["low_price"])
                                resto["low_price"] = price_aggregation[0]["low_price"]
                            resto.pop("contactNumber")
                            resto.pop("business_hours")
                            resto.pop("holidays")
                            resto.pop("dateAdded")
                            resto_list.append(resto)
    return resto_list



@router.get("/top-reviews/{restaurantId}")
async def get_top_review(restaurantId:str):
     reviews=list(db.reviews.find({"restaurantId":ObjectId(restaurantId)}).sort("starCount",-1).limit(10))
     for one in reviews:
          one["_id"]=str(one["_id"])
          one["restaurantId"]=str(one["restaurantId"])

          one["menuId"]=str(one["menuId"])

     return reviews



@router.get("/advertisement/{location}")
async def get_ads(location:str            
):    
      
       results=list(db.advertisement.find({"location":location}))
       if results:
            for ones in results:
                resto_detail=[]
                
                ones["_id"]=str(ones["_id"])
                restos=ones["restaurants"]
                print("restos",restos)
           
                
                restaurant=db.restaurants.find_one({"_id":ObjectId(restos)})
                    
                detail={"_id":str(restaurant["_id"]),"name":restaurant["name"]}
                resto_detail.append(detail)
                print(resto_detail)
                ones["restaurants"]=resto_detail

       return results


    
    