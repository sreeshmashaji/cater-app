from datetime import datetime
from typing import Annotated
from bson import ObjectId
from fastapi import Body, Form, HTTPException, status,APIRouter,Depends,BackgroundTasks
from fastapi_limiter.depends import RateLimiter
import pytz
from config.database import db
from schemas import sub_admin_schema
import utils, oauth2
from services import emailvalidation,verify_password,phone_no_validation
from server import send_mail,otp_api
from config.path import cater_path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

auth_scheme = HTTPBearer()

router=APIRouter(prefix='/sub-admin',tags=["sub-admin"])



collection=db.sub_admin















@router.post('',summary="Register new cater(role will be sub-admin), Only admin can add ")
def add_sub_admin(data:sub_admin_schema.SubAdminInput,
                  user=Depends(oauth2.verify_access_token),token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    try:
        role=user["role"]
        owner_id=user["user_id"]
        if role =="admin":
            if not emailvalidation.validate_email(data.email):
             raise HTTPException(status_code=400, detail="Invalid Email Address")
            existing_admin=db.register.find_one({"email":data.email})
            if existing_admin:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is registered as cater")
            existing_user = collection.find_one({'email':data.email})
            if existing_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email Already Exists")


            # date_obj = datetime.strptime(data.dateAdded, "%Y-%m-%d %H:%M:%S")
            user_data=sub_admin_schema.SubAdmin(email=data.email,name=data.name,password=utils.hash(data.password),ownerId=ObjectId(owner_id),dateAdded=datetime.now(pytz.utc))
            data= collection.insert_one(user_data.__dict__)
            resultdata= collection.find_one({'_id':data.inserted_id})
            resultdata["_id"]=str(resultdata["_id"])
            resultdata["ownerId"]=str(resultdata["ownerId"])

            if not resultdata:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Sorry Operation Failed")
            
            return {"message":"success","data":resultdata}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Please make sure you are an admin")
    except Exception as e:
        raise e




#delete sub admin
# @router.delete('',summary="Delete sub-admin by id , Only admin can remove sub-admin ")
# def delete_sub_admin(data:sub_admin_schema.SubAdminDelete,user=Depends(oauth2.verify_access_token),token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
#     role=user["role"]
#     owner_id=user["user_id"]
#     if role =="admin":

#         resultdata = collection.find_one({'_id':ObjectId(data.id)}) 
        
#         if not resultdata:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Doesnt Exists")
#         if resultdata["ownerId"]!=ObjectId(owner_id):
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You are not the owner")
            
#         collection.delete_one({"_id":ObjectId(data.id)})
#         return "User Removed"
#     else:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Please make sure you are an admin")








@router.delete('', summary="Delete multiple restaurants by restaurant_ids, only restaurant owner can delete corresponding restaurants")
def delete_multiple(subadmin_ids:sub_admin_schema.SubAdminDelete, token: HTTPAuthorizationCredentials = Depends(auth_scheme), user_data: str = Depends(oauth2.verify_access_token)):
    try:
        ownerId = user_data["user_id"]
        delete_sub_admin = []

        
        if isinstance(subadmin_ids.id, list):
            for id in subadmin_ids.id:
                result = collection.find_one({'_id': ObjectId(id)})
                if result:
                    if ObjectId(ownerId) == result["ownerId"]:
                        collection.delete_one({"_id": ObjectId(id)})
                        delete_sub_admin.append(id)
                else: 
                    continue
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid subAdmin ids provided")

        if delete_sub_admin:
            return {"message": "SubAdmins Deleted", "Deleted_sub_Admins": delete_sub_admin}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subAdmins found")
    except Exception as e:
        raise e












@router.get('/{owner_id}')
def get_sub_admin(owner_id:str,user=Depends(oauth2.verify_access_token),token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    try:
    
        data = list(collection.find({"ownerId": ObjectId(owner_id)}))
        if data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No sub-admins found")
        
        for resultdata in data:
            if resultdata["ownerId"] != ObjectId(owner_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You are not the owner")
        
        datas = [{'_id': str(resultdata['_id']), 'name': resultdata['name'], 'email': resultdata['email'], 'dateAdded': resultdata['dateAdded']} for resultdata in data]
        return datas
    except Exception as e:
        raise e




