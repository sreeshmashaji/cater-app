from fastapi import Body, Form, HTTPException, status,APIRouter,Depends,BackgroundTasks
from config.database import db
from schemas import category_schema
from config.path import category_path
from bson import ObjectId
import oauth2
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer


auth_scheme = HTTPBearer()


router=APIRouter(prefix='/menus/default-category',tags=["default_category"])

collection=db.default_category

@router.get('')
async def get_categories():
    try:
        data = list(collection.find().limit(10000))  
        data = [{**doc, '_id': str(doc['_id'])} for doc in data]
       
        return data
    except Exception as e:
        raise e
    
@router.get('/all-category/{owner_id}')
def get_owned_default_category(owner_id:str,user=Depends(oauth2.verify_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    if user["user_id"]!= owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
    owned_categories=list(db.category.find({"ownerId":ObjectId(owner_id)}))
    print(owned_categories)
    for one in owned_categories:
        one["ownerId"]=str(one["ownerId"])
    default_categories = list(collection.find().limit(10000)) 
    all_categories=owned_categories+default_categories
    print(all_categories)
    data=[{**doc,"_id":str(doc["_id"])} for doc  in all_categories]
    return data
    

