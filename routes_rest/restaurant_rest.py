from datetime import time
from datetime import datetime


import json,requests
import mimetypes
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
import pytz
import oauth2,utils
from services import phone_no_validation
from config.path import restaurant_path
from typing import  List, Optional
from bson import ObjectId
from fastapi import  Body, Depends, File, Form, HTTPException, Response, UploadFile, status,APIRouter
from config.database import db
from schemas import restaurant_schema
from dotenv import dotenv_values
import boto3,httpx
from botocore.exceptions import NoCredentialsError
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim

env = dict(dotenv_values(".env_admin"))

auth_scheme = HTTPBearer()

router=APIRouter(prefix=restaurant_path,tags=["Restaurant"])


collection = db.restaurants

AWS_ACCESS_KEY_ID = env.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION_NAME = env.get("AWS_REGION_NAME")
S3_BUCKET_NAME = env.get("S3_BUCKET_NAME")
S3_IMAGE_LINK=env.get("S3_IMAGE_LINK")

geolocator = Nominatim(user_agent="restaurant_geocoder")



s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)


# ORS_API_KEY = "5b3ce3597851110001cf6248f4c7d953aa414dfcb1e5e67b0cb34c25"

# OPENCAGE_API_KEY = "0d8161a042384e0b90e192f8473bea9d"


@router.post('', summary="Add restaurant by a registered cater")
async def add_restaurant(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    user_data: str = Depends(oauth2.verify_access_token),
    name: str = Form(...),
    location: str = Form(...),
    address:str=Form(...),
    description:str=Form(...),
    longitude:str=Form(...),
    latitude:str=Form(...),
    contactNumber: str = Form(...),
    cuisine_types:list[str]=Form(),
    minimum_price:int=Form(...),
    website:str=Form(None),
    business_hours: Optional[str] = Form(None),
    restaurant_image: UploadFile = File(None),
    banner_image:UploadFile=File(None),
    holidays: List[str] = Form(None)
):
    try:
            existing_restaurant = collection.find_one({'name': name})
            ownerId = user_data["user_id"]
            owner = db.register.find_one({'_id': ObjectId(ownerId)})

            if not owner:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid owner_id")

            cleaned_phone_number = phone_no_validation.validate_phone_number(contactNumber)
            if not cleaned_phone_number.isdigit():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number must contain only digits")
            if len(contactNumber) > 10:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Phone Number")

            image_link = None
            if restaurant_image:
                allowed_extensions = ['png', 'jpg', 'jpeg']
                file_ext = restaurant_image.filename.split('.')[-1]
                if file_ext.lower() not in allowed_extensions:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="Only PNG, JPG, and JPEG formats are allowed for the image")

                try:
                    contents = await restaurant_image.read()
                    content_type, _ = mimetypes.guess_type(restaurant_image.filename)
                    s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=restaurant_image.filename, Body=contents,
                                        ContentType=content_type)
                    image_link = f"{S3_IMAGE_LINK}{restaurant_image.filename}"
                except NoCredentialsError:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                        detail="Failed to upload image: AWS credentials not found")
            
            banner=None
            
            if banner_image:
                allowed_extensions = ['png', 'jpg', 'jpeg']
                file_ext = banner_image.filename.split('.')[-1]
                if file_ext.lower() not in allowed_extensions:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="Only PNG, JPG, and JPEG formats are allowed for the image")

                try:
                    contents = await banner_image.read()
                    content_type, _ = mimetypes.guess_type(banner_image.filename)
                    s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=banner_image.filename, Body=contents,
                                        ContentType=content_type)
                    banner = f"{S3_IMAGE_LINK}{banner_image.filename}"
                except NoCredentialsError:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                        detail="Failed to upload image: AWS credentials not found")
            
            # try:
            #     location_data = geolocator.geocode(location)
            #     latitude = location_data.latitude
            #     longitude = location_data.longitude
            # except (AttributeError, GeocoderTimedOut):
            #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to geocode location")
            default_hours = "00:00:00"  

            if business_hours:
                try:
                    business_hours_dict = {}
                    provided_hours = json.loads(business_hours)
                    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                        if day in provided_hours:
                            start_time_str, end_time_str = provided_hours[day].split("-")
                            start_time = datetime.strptime(start_time_str, "%H:%M").time().isoformat()
                            end_time = datetime.strptime(end_time_str, "%H:%M").time().isoformat()
                            business_hours_dict[day] = {'start_time': start_time, 'end_time': end_time}
                        else:
                            business_hours_dict[day] = {'start_time': default_hours, 'end_time': default_hours}
                except (ValueError, KeyError):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid business hours format")
            else:
                
                business_hours_dict = {day : {'start_time': default_hours, 'end_time': default_hours} for day in
                                    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
            
            
            data = {
                'ownerId': ObjectId(ownerId),
                'name': name,
                'location': location,
                'address':address,
                'description':description,
                'latitude': latitude,   
                'longitude': longitude,
                'image': image_link,
                'bannerImage':banner,
                'contactNumber': cleaned_phone_number,
                "cuisine_types":cuisine_types,
                "minimum_price":minimum_price,
                "website":website,
                'business_hours': business_hours_dict,
                'holidays': holidays,
                'status': False,
                'dateAdded':datetime.now(pytz.utc),
                "vipStatus":False,
                 
                'averageStarCount':0
            }
            

            inserted_data = collection.insert_one(data)

            result_data = collection.find_one({'_id': inserted_data.inserted_id})
            result_data["_id"] = str(result_data["_id"])
            result_data["ownerId"] = str(result_data["ownerId"])

            if not result_data:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sorry Operation Failed")
            await utils.invalidate_all_cache()
            return {"message": "success", "data": result_data}
    except Exception as e:
        raise e







@router.put('/update-business-hours', summary="Update business hours of a restaurant by the owner")
async def update_business_hours(
    update_data:restaurant_schema.UpdateRestaurant,
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    user_data: str = Depends(oauth2.verify_access_token),
    
):
      try:
            ownerId = user_data["user_id"]
            owner = db.register.find_one({'_id': ObjectId(ownerId)})
            if not owner:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid owner_id")
            
            try:
                restaurant_id = ObjectId(update_data.restaurant_id)
            except:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid restaurant_id")
            
            existing_restaurant = collection.find_one({'_id': restaurant_id, 'ownerId': ObjectId(ownerId)})
            if not existing_restaurant:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

            if update_data.business_hours:
                try:
                    new_business_hours_dict = update_data.business_hours.dict()
                    existing_business_hours = existing_restaurant.get('business_hours', {})
                    
                    # Update existing business hours with the new ones
                    for day, hours_str in new_business_hours_dict.items():
                        start_time_str, end_time_str = hours_str.split("-")
                        existing_business_hours[day] = {
                            'start_time': datetime.strptime(start_time_str, "%H:%M").time().isoformat(),
                            'end_time': datetime.strptime(end_time_str, "%H:%M").time().isoformat()
                        }
                    
                    # Update the restaurant document in the database with the merged business hours
                    collection.update_one(
                        {'_id': restaurant_id},
                        {'$set': {'business_hours': existing_business_hours}}
                    )
                    
                    return {"message": "Business hours updated successfully"}
                
                except (ValueError, KeyError):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid business hours format")

            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Business hours data is required")
            
      except Exception as e:
          raise e

  








@router.put('', summary="Update restaurant, Only restaurant owner can update")
async def update_restaurant(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    user_data: str = Depends(oauth2.verify_access_token),
    restaurant_id: str = Form(...),
    cuisine_types:list[str]=Form(None),
    name: Optional[str] = Form(None),
    contactNumber: Optional[str] = Form(None),
    minimum_price:int=Form(None),
    address:Optional[str]=Form(None),
    description:Optional[str]=Form(None),
    website:str=Form(None),
    business_hours: Optional[str] = Form(None),
    restaurant_image: UploadFile = File(None),
    banner_image:UploadFile=File(None),
    holidays: List[str] = Form(None)
):
        try:
            ownerId = user_data["user_id"]
            existing_restaurant = collection.find_one({'_id': ObjectId(restaurant_id)})
            if not existing_restaurant:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Restaurant doesn't exist")

            if ObjectId(ownerId) != existing_restaurant["ownerId"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ownerId")

            
            data = {}


        
            if name:
                data['name'] = name
            
            if description:
                data['description'] = description
            if contactNumber:
                cleaned_phone_number = phone_no_validation.validate_phone_number(contactNumber)
                if not cleaned_phone_number.isdigit():
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number must contain only digits")
                if len(cleaned_phone_number) != 10:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Phone Number")
                data['contactNumber'] = cleaned_phone_number
            if address:
                data['address']=address
            if minimum_price:
                data['minimum_price']=minimum_price
            if business_hours:
                
                try:
                    new_business_hours_dict = json.loads(business_hours)
                    existing_business_hours = existing_restaurant.get('business_hours', {})
                    
                    # Update existing business hours with the new ones
                    for day, hours_str in new_business_hours_dict.items():
                        start_time_str, end_time_str = hours_str.split("-")
                        existing_business_hours[day] = {
                            'start_time': datetime.strptime(start_time_str, "%H:%M").time().isoformat(),
                            'end_time': datetime.strptime(end_time_str, "%H:%M").time().isoformat()
                        }
                except (ValueError, KeyError):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid business hours format")

                data['business_hours'] = existing_business_hours

            if restaurant_image:
                contents = await restaurant_image.read()
                content_type, _ = mimetypes.guess_type(restaurant_image.filename)
                s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=restaurant_image.filename, Body=contents,
                                    ContentType=content_type)
                image_link = f"{S3_IMAGE_LINK}{restaurant_image.filename}"
                data['image'] = str(image_link)
            if banner_image:
                allowed_extensions = ['png', 'jpg', 'jpeg']
                file_ext = banner_image.filename.split('.')[-1]
                if file_ext.lower() not in allowed_extensions:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="Only PNG, JPG, and JPEG formats are allowed for the image")

                
                contents = await banner_image.read()
                content_type, _ = mimetypes.guess_type(banner_image.filename)
                s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=banner_image.filename, Body=contents,
                                        ContentType=content_type)
                data["bannerImage"] = f"{S3_IMAGE_LINK}{banner_image.filename}"
                
            
            if holidays:
                data['holidays'] = holidays
            if website:
                data['website'] = website
            if cuisine_types:
                print(cuisine_types)
                data["cuisine_types"]=cuisine_types
            

            print("data",data)

            # Perform the update operation only if there are fields to update
            if data:
                updated_menu = collection.update_one({'_id': ObjectId(restaurant_id)}, {"$set": data})

                if not updated_menu:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sorry Operation Failed")
                await utils.invalidate_all_cache()
                
                return {"message": "success"}
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
        except Exception as e:
            raise e

# @router.get('/{cater_id}',summary="By giving cater_id ,list the resaturants added by that cater  ")
# def restaurants_by_cater(cater_id:str,user=Depends(oauth2.verify_access_token),token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
#     try:
#         print("entering by caterId inside rest")
#         if user["user_id"]!=cater_id:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")

#         data=list(collection.find({"ownerId":ObjectId(cater_id)}))
        
        
#         print("data",data)
#         if data is None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resataurants not found")
        
#         for one in data:
#             one["_id"]=str(one["_id"])
#             one["ownerId"]=str(one["ownerId"])
#             cuisine=one.get("cuisine_types", [])
#             print(cuisine)
#             cuisine_list=[]
#             for one in cuisine:
#                 cuisine=db.cuisine.find_one({"_id":ObjectId(one)})
#                 cuisine["_id"]=str(cuisine["_id"])
#                 cuisine_list.append(cuisine)
#             print("list",cuisine_list)
#             one["cuisine_types"]=cuisine_list
        
#         # data = [{**resultdata, '_id': str(resultdata['_id']),'ownerId': str(resultdata['ownerId'])} for resultdata in data]
#         return data
#     except Exception as e:
#         raise e
@router.get('/{cater_id}', summary="List the restaurants added by that caterer by giving cater_id")
def restaurants_by_cater(cater_id: str, user=Depends(oauth2.verify_access_token), token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    try:
        print("Entering by caterId inside rest")
        if user["user_id"] != cater_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

        data = list(collection.find({"ownerId": ObjectId(cater_id)}))
        print("data", data)
        
        if not data:  # Check if the data list is empty
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurants not found")
        
        for restaurant in data:
            restaurant["_id"] = str(restaurant["_id"])
            restaurant["ownerId"] = str(restaurant["ownerId"])
            cuisine_ids = restaurant.get("cuisine_types", [])
            cuisine_list = []
            
            for cuisine_id in cuisine_ids:
                try:
                    cuisine = db.cuisine.find_one({"_id": ObjectId(cuisine_id)})
                    if cuisine:
                        cuisine["_id"] = str(cuisine["_id"])
                        cuisine_list.append(cuisine)
                except Exception as ex:
                    print(f"Error fetching cuisine {cuisine_id}: {ex}")
                    continue  # Skip this cuisine and move to the next
            
            print("cuisine_list", cuisine_list)
            restaurant["cuisine_types"] = cuisine_list
        
        return data
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")








@router.delete('', summary="Delete multiple restaurants by restaurant_ids, only restaurant owner can delete corresponding restaurants")
async def delete_multiple(resto_ids:restaurant_schema.DeleteResto, token: HTTPAuthorizationCredentials = Depends(auth_scheme), user_data: str = Depends(oauth2.verify_access_token)):
    try:
        ownerId = user_data["user_id"]
        deleted_resto = []

        # Ensure resto_ids is a list of strings
        if isinstance(resto_ids.id, list):
            for id in resto_ids.id:
                result = collection.find_one({'_id': ObjectId(id)})
                if result:
                    if ObjectId(ownerId) == result["ownerId"]:
                        collection.delete_one({"_id": ObjectId(id)})
                        rest_menu=list(db.restaurant_menu.find({"restaurantId":id}))
                        if rest_menu:
                          db.restaurant_menu.delete_many({"restaurantId":id})
                        print(rest_menu)
                        menu_ids = [item['menuId'] for item in rest_menu]
                        
                        for ids in menu_ids:
                            print(ids)
                            menu_detail=db.menus.find_one({"_id":ObjectId(ids)})
                            if menu_detail:
                                menu_detail["restaurantId"].remove(ObjectId(id))
                                db.menus.update_one({"_id": ObjectId(ids)}, {"$set": {"restaurantId": menu_detail["restaurantId"]}})
                                print("menu",menu_detail)
                        resto_category=db.restaurant_category.find_one({"restaurants":id})
                        if resto_category:
                            resto=resto_category["restaurants"]
                            resto.remove(id)
                            db.restaurant_category.update_one({"_id": ObjectId(resto_category["_id"])}, {"$set": {"restaurants": resto}})

                        offer=db.offers.find_one({"restaurants":id})
                        if offer:
                            resto_offer=offer["restaurants"]
                            resto_offer.remove(id)
                            db.offers.update_one({"_id":offer["_id"]},{"$set":{"restaurants":resto_offer}})


                        deleted_resto.append(id)
                else: 
                    continue
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid restaurant IDs provided")

        if deleted_resto:
            await utils.invalidate_all_cache()

            return {"message": "Restaurants Deleted", "Deleted_restaurants": deleted_resto}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No restaurants found")
    except Exception as e:
        raise e





@router.get('/name/{cater_id}',summary="By giving cater_id ,list the resaturantname and id  added by that cater  ")
def restaurants_by_cater(cater_id:str,user=Depends(oauth2.verify_access_token),token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
      try:
        print("entering by caterId")
        if cater_id != user['user_id']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not the owner")

        data=collection.find({"ownerId":ObjectId(cater_id)})
        
        
        print("data",data)
        if data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resataurants not found")
        data = [{ '_id': str(resultdata['_id']),'name':resultdata['name']} for resultdata in data]
        return data
      except Exception as e:
          raise e


@router.put('/change-status',summary="block or unblock restaurant")
async def restaurants_status(data:restaurant_schema.Status,user=Depends(oauth2.verify_access_token),token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
        try:
            owner_id=user["user_id"]
            exist_resto=collection.find_one({"_id":ObjectId(data.id)})
            
            if not exist_resto:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Restaurant not found")
            
            if exist_resto['ownerId']!=ObjectId(owner_id):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are  not the restaurant owner")
            if exist_resto['status']==data.status:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Trying to set the same status")

            
            try:
                result = collection.update_one({"_id": ObjectId(data.id)}, {"$set": {'status': data.status}})
                print("rs",result)
                if result.modified_count == 0:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update restaurant status")
                await utils.invalidate_all_cache()
                
                return {"message": "Restaurant status updated successfully"}
            
            except Exception as e:
                
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred during the update operation")
        except Exception as e:
            raise e
            














@router.get('/id/{id}')
async def get_one_by_id(id:str,user=Depends(oauth2.verify_access_token),token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
        try:
            restaurants=collection.find_one({"_id":ObjectId(id)})
            if not restaurants:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
            if ObjectId(user["user_id"])!=restaurants["ownerId"]:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
            restaurants["ownerId"]=str(restaurants["ownerId"])
            restaurants["_id"]=str(restaurants["_id"])
            return restaurants
        except Exception as e :
            raise e


# @router.put("/add-offer/{restaurantId}")
# def add_offer(restaurantId:str,data:restaurant_schema.Coupon,user=Depends(oauth2.verify_access_token),token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
#     try:
#         restaurant=collection.find_one({"_id":ObjectId(restaurantId)})
#         if not restaurant:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
#         if ObjectId(user["user_id"])!=restaurant["ownerId"]:
#                     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
#         if len(data.title)<=10:
        
#             collection.update_one({"_id":ObjectId(restaurantId)},{"$set":{"offers.enabled":data.enabled,"offers.title":data.title}})
#             return "offer added"
#         else:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Ensure the title length is 10 or less than 10")
#     except Exception as e:
#         raise e


# @router.put("/delete-offer/{restaurantId}")
# def delete_offer(restaurantId:str,user=Depends(oauth2.verify_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
#     try:
#         restaurant=collection.find_one({"_id":ObjectId(restaurantId)})
#         if not restaurant:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Restaurant not found")
#         if ObjectId(user["user_id"])!=restaurant["ownerId"]:
#                     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
#         collection.update_one({"_id":ObjectId(restaurantId)},{"$set":{"offers.enabled":False,"offers.title":None}})
#         return "Offer removed"
#     except Exception as e:
#         raise e
    
