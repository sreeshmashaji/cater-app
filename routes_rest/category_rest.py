from fastapi import Body, Form, HTTPException, status,APIRouter,Depends,BackgroundTasks
from config.database import db
from schemas import category_schema
from config.path import category_path
from bson import ObjectId
import oauth2
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer


auth_scheme = HTTPBearer()


router=APIRouter(prefix=category_path,tags=["category"])

collection=db.category


@router.post('')
def add_category(data:category_schema.Category,user=Depends(oauth2.verify_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
            category=collection.find_one({"name":data.name})
            owner = db.register.find_one({'_id': ObjectId(user["user_id"])})
            # print(owner)
            if not owner:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid owner_id")
            insert_data={"name":data.name,
                        "ownerId":ObjectId(user["user_id"])}
            data=collection.insert_one(insert_data)
            resultdata=collection.find_one({"_id":data.inserted_id})
            if not resultdata:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Operation Failed")
            resultdata["_id"]=str(resultdata["_id"])
            resultdata["ownerId"]=str(resultdata["ownerId"])
            return {"message":"success","data":resultdata}
    except Exception as e:
        raise e
            





@router.get('/{cater_id}')
async def get_categories(cater_id:str,user=Depends(oauth2.verify_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
        if cater_id!=user["user_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
        data = list(collection.find({"ownerId":ObjectId(cater_id)}))  
        data = [{'_id': str(doc['_id']),'name':doc['name']} for doc in data]
        return data
    except Exception as e:
        raise e





@router.delete('/{id}')
def delete_category(id:str,user=Depends(oauth2.verify_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
        category=collection.find_one({"_id":ObjectId(id)})
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found")
        if category["ownerId"]!=ObjectId(user["user_id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
        collection.delete_one({"_id":ObjectId(id)})
        return "Category Removed"
    except Exception as e:
        raise e 

