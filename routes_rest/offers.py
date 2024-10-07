from datetime import datetime
from typing import Optional
from fastapi import Body, Form, HTTPException, status,APIRouter,Depends,BackgroundTasks
import pytz
from config.database import db
from schemas import offer_schema
from bson import ObjectId
import oauth2,utils
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
  
router=APIRouter(prefix='/caters/offers',tags=["offers"])
auth_scheme = HTTPBearer()

collection=db.offers


@router.post("")
async def add_offers(data:offer_schema.AddOffer,user=Depends(oauth2.verify_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
            restaurants=data.restaurants

            for one in restaurants:
                restodetail=db.restaurants.find_one({"_id":ObjectId(one)})
                
                if restodetail["ownerId"]!=ObjectId(user["user_id"]):
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are trying to add restaurants of another cater")
                already_exist=collection.count_documents({"restaurants":one})
                print(already_exist)
                if already_exist>2:
                     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"This offer is not applicable to {restodetail["name"]}")
                if len(data.title)>15:
                     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Title length exceeded")
                     
                     
            insert_data={
                "title":data.title,
                "description":data.description,
                "ownerId":user["user_id"],
                "restaurants":restaurants,
                "createdAt":datetime.now(pytz.utc)
            }

            added_data=collection.insert_one(insert_data)
            result_data = collection.find_one({'_id': added_data.inserted_id})
            result_data["_id"]=str(result_data["_id"])
            await utils.invalidate_all_cache()

            return {"message":"success","data":result_data}
    except Exception as e:
         raise e


@router.get("/{ownerId}")
def get_offers(ownerId:str,user=Depends(oauth2.verify_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
        if ownerId!=user["user_id"]:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
        offers=list(collection.find({"ownerId":ownerId}))
        # print(offers)
        
        if offers:
            for offer in offers:
                resto_detail=[]
                
                offer["_id"]=str(offer["_id"])
                restos=offer["restaurants"]
                print("restos",restos)
           
                for one in restos:
                    print("one",one)
                    restaurant=db.restaurants.find_one({"_id":ObjectId(one)})
                    
                    detail={"_id":str(restaurant["_id"]),"name":restaurant["name"]}
                    resto_detail.append(detail)
                    print(resto_detail)
                offer["restaurants"]=resto_detail
                
                 
                 
        return offers
    except Exception as e:
         raise e


@router.delete("/{offer_id}")
async def delete_offers(offer_id:str,user=Depends(oauth2.verify_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
        offer=collection.find_one({"_id":ObjectId(offer_id)})
        if not offer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Offer not found")
        if offer["ownerId"]!=user["user_id"]:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
             

        collection.delete_one({"_id":ObjectId(offer_id)})
        await utils.invalidate_all_cache()

        return "Offer removed"
    except Exception as e:
         raise e
    
@router.put("/{offer_id}")
async def update_offer(data:offer_schema.AddOffer,offer_id:str,user=Depends(oauth2.verify_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
     try:
        restaurants=data.restaurants
        offer=collection.find_one({"_id":ObjectId(offer_id)})
        if not offer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Offer not found")
        if offer["ownerId"]!=user["user_id"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
        for resto in restaurants:
            resto_detail=db.restaurants.find_one({"_id":ObjectId(resto)})
            if resto_detail["ownerId"]!=ObjectId(user["user_id"]):
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are trying to add restaurants of another cater")
            already_exist=collection.count_documents({"restaurants":resto})
            print(already_exist)
            if already_exist>2:   
                     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"This offer is not applicable to {resto_detail["name"]}")
            if len(data.title)>15:
                     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Title length exceeded")
                
            
        collection.update_one({"_id":offer["_id"]},{"$set":{"restaurants":restaurants,"title":data.title,"description":data.description}})
        await utils.invalidate_all_cache()
        
        return "offer updated"
     
     except Exception as e:
          raise e
          
               
               
    


     
     
          
     

        





