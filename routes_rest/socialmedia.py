from typing import Optional
from fastapi import Body, Form, HTTPException, status,APIRouter,Depends,BackgroundTasks
from config.database import db
from schemas import socialmedia
from bson import ObjectId
import oauth2
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
  
router=APIRouter(prefix='/caters/socialmedia/link',tags=["links"])
auth_scheme = HTTPBearer()

collection=db.media_links


@router.post('')
def add_link(data:socialmedia.MediaLink,user=Depends(oauth2.verify_access_token),token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    try:
        id=user["user_id"]
        print("enter")
        link_exist=collection.find_one({"ownerId":user["user_id"]})
        if link_exist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Already added links")
        update_data={"ownerId":id,"links":data.__dict__}
        print(update_data)
        
        data= collection.insert_one(update_data)
        resultdata= collection.find_one({'_id':data.inserted_id})
        resultdata["_id"]=str(resultdata["_id"])
        resultdata["ownerId"]=str(resultdata["ownerId"])
        return {"message":"success","data":resultdata}
    except Exception as e:
        raise e


@router.get('',summary="  Fetching  media links by id")
async def geting(user=Depends(oauth2.verify_access_token),token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    try:
    
        data = collection.find_one({"ownerId":user["user_id"]})
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Data not found")
        data["_id"]=str(data["_id"])
        return data
    except Exception as e:
        raise e












@router.put('/{link_id}')
def update_link(link_id: str, data: Optional[socialmedia.MediaLink] = None, user=Depends(oauth2.verify_access_token), token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    try:

        id = user["user_id"]
        link = collection.find_one({"_id": ObjectId(link_id)})
        if not link:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
        if link["ownerId"]!=id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner")
        if not data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

        collection.update_one({"_id": ObjectId(link_id)}, {"$set": {"links":data.__dict__}})
        updated_link = collection.find_one({"_id": ObjectId(link_id)})
        updated_link["_id"] = str(updated_link["_id"])
        updated_link["ownerId"] = str(updated_link["ownerId"])
        return {"message": "success", "data": updated_link}
    except Exception as e:
        raise e


















# @router.put('/{link_id}')
# def update_link(link_id: str, data: Optional[socialmedia.MediaLink] = None, user=Depends(oauth2.verify_access_token), token: HTTPAuthorizationCredentials = Depends(auth_scheme)):

#     id = user["user_id"]
#     link = collection.find_one({"_id": ObjectId(link_id), "ownerId": id})
#     if not link:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    
#     print(data)
#     update_fields=link["links"]
#     if data.facebook:
#         update_fields["facebook"]=data.facebook
#     if data.instagram:
#         update_fields["instagram"]=data.instagram
#     if data.linkedin:
#         update_fields["linkedin"]=data.linkedin
#     if data.twitter:
#         update_fields["twitter"]=data.twitter
#     print(update_fields)

#     if not update_fields:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

#     collection.update_one({"_id": ObjectId(link_id)}, {"$set": update_fields})
#     updated_link = collection.find_one({"_id": ObjectId(link_id)})
#     updated_link["_id"] = str(updated_link["_id"])
#     updated_link["ownerId"] = str(updated_link["ownerId"])
#     return {"message": "success", "data": updated_link}
