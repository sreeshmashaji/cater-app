import time
from fastapi import APIRouter, HTTPException,status
import haversine as hs   
from haversine import Unit
import geopy.geocoders
import requests
geolocator = geopy.geocoders.Nominatim(user_agent="my_unique_application/1.0")
router = APIRouter(tags=["card"])
from geopy import distance
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

API_KEY="5b3ce3597851110001cf6248849362c01bdb4ee1b0597d2b71832179"
ORS_API_KEY = "5b3ce3597851110001cf6248849362c01bdb4ee1b0597d2b71832179"

def get_osrm_route(start, end):
    osrm_url = "http://router.project-osrm.org/route/v1/driving/{},{};{},{}".format(
        start[1], start[0], end[1], end[0]
    )
    response = requests.get(osrm_url)
    data = response.json()

    if response.status_code == 200 and data['code'] == 'Ok':
        route = data['routes'][0]
        distance = route['distance']  # distance in meters
        duration = route['duration']  # duration in seconds
        return distance, duration
    else:
        raise Exception("Error getting route: {}".format(data))



@router.get("/")
def get_location(location1: str,location2:str):
    # Get the latitude and longitude of the location
    location_obj1 = geolocator.geocode(location1)
    if location_obj1:
        latitude1 = location_obj1.latitude
        longitude1= location_obj1.longitude

    location_obj2 = geolocator.geocode(location2)
    if location_obj2:
        latitude2= location_obj2.latitude
        longitude2 = location_obj2.longitude

    print(f"{location1} :{latitude1},{longitude1}")
    print(f"{location2} :{latitude2},{longitude2}")

    loc1=( latitude1,longitude1)
    loc2=( latitude2,longitude2)

    # result=hs.haversine(loc1,loc2,unit=Unit.KILOMETERS)
    # result=distance.distance(loc1, loc2).km
    # print("The distance calculated is:",result)
    try:
            distance, duration = get_osrm_route(loc1, loc2)
            print("Distance: {:.2f} km".format(distance / 1000))
            print("Duration: {:.2f} hours".format(duration / 3600))
    except Exception as e:
        print(e)

    



# class RateLimitError(Exception):
#     pass

# class ServiceUnavailableError(Exception):
#     pass

# @retry(
#     retry=(retry_if_exception_type(RateLimitError) | retry_if_exception_type(ServiceUnavailableError)),
#     wait=wait_exponential(multiplier=1, min=4, max=60),
#     stop=stop_after_attempt(5)
# )
# def make_ors_request(url, headers):
#     response = requests.get(url, headers=headers)

#     if response.status_code == 429:
#         raise RateLimitError("Rate limit exceeded, retrying...")
#     elif response.status_code == 503:
#         raise ServiceUnavailableError("Service unavailable, retrying...")
#     response.raise_for_status()
#     return response.json()

# @router.get("/distance_matrix")
# async def get_distance_matrix(origin: str, destination: str):
#     try:
#         origin_data = geolocator.geocode(origin)
#         destination_data = geolocator.geocode(destination)

#         if not origin_data or not destination_data:
#             raise ValueError("Failed to geocode one or both locations")

#         origin_lat = origin_data.latitude
#         origin_lon = origin_data.longitude
#         destination_lat = destination_data.latitude
#         destination_lon = destination_data.longitude

#         # Construct URL for OpenRouteService Matrix API
#         url = f"https://api.openrouteservice.org/v2/matrix/driving-car?start={origin_lon},{origin_lat}&end={destination_lon},{destination_lat}"
#         headers = {'Authorization': f"Bearer {API_KEY}"}

#         print("Constructed URL:", url)  # Added for debugging

#         data = make_ors_request(url, headers)

#         try:
#             distance = data['distances'][0][1] / 1000  # Convert to kilometers
#             duration = data['durations'][0][1] / 60  # Convert to minutes
#             return {"distance_km": distance, "duration_min": duration}
#         except (KeyError, IndexError):
#             raise Exception("Error: Could not extract distance or duration from response")

#     except RateLimitError as e:
#         raise HTTPException(status_code=429, detail=str(e))
#     except ServiceUnavailableError as e:
#         raise HTTPException(status_code=503, detail=str(e))
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))



# @router.get("/distance_matrix")
# async def get_distance_matrix(origin: str, destination: str):
#     try:
#         origin_data = geolocator.geocode(origin)
#         destination_data = geolocator.geocode(destination)

#         if not origin_data or not destination_data:
#             raise ValueError("Failed to geocode one or both locations")

#         origin_lat = origin_data.latitude
#         origin_lon = origin_data.longitude
#         destination_lat = destination_data.latitude
#         destination_lon = destination_data.longitude

#         # Correct URL for OpenRouteService Matrix API
#         url = "https://api.openrouteservice.org/v2/matrix/driving-car"
#         headers = {'Authorization': f"Bearer {API_KEY}"}
#         payload = {
#             "locations": [[origin_lon, origin_lat], [destination_lon, destination_lat]],
#             "metrics": ["distance", "duration"]
#         }

#         response = requests.post(url, json=payload, headers=headers)

#         if response.status_code == 200:
#             data = response.json()
#             try:
#                 distance = data['distances'][0][1] / 1000  # Convert to kilometers
#                 duration = data['durations'][0][1] / 60  # Convert to minutes
#                 return {"distance_km": distance, "duration_min": duration}
#             except (KeyError, IndexError):
#                 raise Exception("Error: Could not extract distance or duration from response")
#         else:
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"API request failed with status code {response.status_code}")

#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
       





# from fastapi import Body, Form, HTTPException, status,APIRouter,Depends,BackgroundTasks
# from config.database import db
# from schemas import card_schema

# from bson import ObjectId
# import oauth2
# from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer


# auth_scheme = HTTPBearer()


# router=APIRouter(tags=["card"])

# collection=db.card



# @router.post('/caters/cards')
# def add_card_for_cater(data:card_schema.CardInput,token:HTTPAuthorizationCredentials=Depends(auth_scheme),user=Depends(oauth2.verify_access_token)):
#     ownerId=user["user_id"]
#     insert_data={"ownerId":ObjectId(ownerId),**data.__dict__}
#     print(insert_data)
#     data= collection.insert_one(insert_data)
#     resultdata= collection.find_one({'_id':data.inserted_id})
#     resultdata["_id"]=str(resultdata["_id"])
#     resultdata["ownerId"]=str(resultdata["ownerId"])
#     return {"message":"success","data":resultdata}



# @router.get('/caters/cards/{cater_id}')
# def get_card(cater_id:str,token:HTTPAuthorizationCredentials=Depends(auth_scheme),user=Depends(oauth2.verify_access_token)):
#     ownerId=user["user_id"]
#     if cater_id!=ownerId:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
   
#     data = list(collection.find({"ownerId":ObjectId(cater_id)}))  
#     return_data = [{**doc,'_id': str(doc['_id']),'ownerId': str(doc['ownerId'])} for doc in data]
#     return return_data
     


# @router.delete('/caters/cards/{card_id}')
# def delete_card(card_id:str,token:HTTPAuthorizationCredentials=Depends(auth_scheme),user=Depends(oauth2.verify_access_token)):
#     card=collection.find_one({"_id":ObjectId(card_id)})
#     if not card:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Card not found")
#     if card["ownerId"]!=ObjectId(user["user_id"]):
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not the owner")
#     collection.delete_one({"_id":ObjectId(card_id)})
#     return "Card removed"









# @router.post('/customer/cards')
# def add_card_for_cater(data:card_schema.CardInput,token:HTTPAuthorizationCredentials=Depends(auth_scheme),user=Depends(oauth2.verify_customer_access_token)):
#     ownerId=user["customer_id"]
#     insert_data={"ownerId":ObjectId(ownerId),**data.__dict__}
#     print(insert_data)
#     data= collection.insert_one(insert_data)
#     resultdata= collection.find_one({'_id':data.inserted_id})
#     resultdata["_id"]=str(resultdata["_id"])
#     resultdata["ownerId"]=str(resultdata["ownerId"])
#     return {"message":"success","data":resultdata}



# @router.get('/customer/cards/{customer_id}')
# def get_card(customer_id:str,token:HTTPAuthorizationCredentials=Depends(auth_scheme),user=Depends(oauth2.verify_customer_access_token)):
#     ownerId=user["customer_id"]
#     if customer_id!=ownerId:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
   
#     data = list(collection.find({"ownerId":ObjectId(customer_id)}))  
#     return_data = [{**doc,'_id': str(doc['_id']),'ownerId': str(doc['ownerId'])} for doc in data]
#     return return_data
     


# @router.delete('/customer/cards/{card_id}')
# def delete_card(card_id:str,token:HTTPAuthorizationCredentials=Depends(auth_scheme),user=Depends(oauth2.verify_customer_access_token)):
#     card=collection.find_one({"_id":ObjectId(card_id)})
#     if not card:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Card not found")
#     if card["ownerId"]!=ObjectId(user["customer_id"]):
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not the owner")
#     collection.delete_one({"_id":ObjectId(card_id)})
#     return "Card removed"

