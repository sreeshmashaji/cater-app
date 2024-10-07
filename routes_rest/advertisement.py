from datetime import datetime,timedelta
import mimetypes
from typing import Optional
from dotenv import dotenv_values
from fastapi import Body, File, Form, HTTPException, status,APIRouter,Depends,BackgroundTasks,UploadFile
import pytz,boto3
from config.database import db
from schemas import offer_schema
from bson import ObjectId
import oauth2,utils
from botocore.exceptions import NoCredentialsError

from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer

  
router=APIRouter(prefix='/super-admin/restaurants/advertisement',tags=["advertisement"])
auth_scheme = HTTPBearer()

collection=db.advertisement

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


@router.post("")
async def add_ads(
    location: str = Form(...),
    title: str = Form(...),
    expire_time: int = Form(...),  
    image: UploadFile = File(None),
    restaurants: str = Form(...),
    user = Depends(oauth2.verify_super_access_token), 
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    if user["role"] != "super-admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    collection.create_index("expiresAt", expireAfterSeconds=0)
    count = collection.count_documents({"location": location})
    if count > 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"This advertisement is not applicable to {location}")

    image_link = None
    if image:
        allowed_extensions = ['png', 'jpg', 'jpeg']
        file_ext = image.filename.split('.')[-1]
        if file_ext.lower() not in allowed_extensions:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PNG, JPG, and JPEG formats are allowed for the image")

        try:
            contents = await image.read()
            content_type, _ = mimetypes.guess_type(image.filename)
            s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=image.filename, Body=contents, ContentType=content_type)
            image_link = f"{S3_IMAGE_LINK}{image.filename}"
        except NoCredentialsError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload image: AWS credentials not found")

    resto = db.restaurants.find_one({"_id": ObjectId(restaurants)})
    if resto["location"] != location:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Restaurant's location mismatch")

    created_at = datetime.now(pytz.utc)
    expires_at = created_at + timedelta(seconds=expire_time)

    datas = {
        "title": title,
        "restaurants": restaurants,
        "location": location,
        "image": image_link,
        "createdAt": created_at,
        "expiresAt": expires_at  
    }
    
    inserted_data = collection.insert_one(datas)

    result_data = collection.find_one({'_id': inserted_data.inserted_id})
    result_data["_id"] = str(result_data["_id"])

    if not result_data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sorry, Operation Failed")

    await utils.invalidate_all_cache()

    return {"message": "success", "data": result_data}
           
                    

@router.get("/{location}")
async def get_ads(location:str, user=Depends(oauth2.verify_super_access_token), token: HTTPAuthorizationCredentials = Depends(auth_scheme)             
):    
       if user["role"]!="super-admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
       results=list(collection.find({"location":location}))
       if results:
            for ones in results:
                resto_detail=[]
                
                ones["_id"]=str(ones["_id"])
                restos=ones["restaurants"]
                
                    
                restaurant=db.restaurants.find_one({"_id":ObjectId(restos)})
                    
                detail={"_id":str(restaurant["_id"]),"name":restaurant["name"]}
                resto_detail.append(detail)
                print(resto_detail)
                ones["restaurants"]=resto_detail

       return results


@router.get("/details/{ad_id}")
async def get_one_ad(ad_id:str,user=Depends(oauth2.verify_super_access_token), token: HTTPAuthorizationCredentials = Depends(auth_scheme)  ):
    ones=collection.find_one({"_id":ObjectId(ad_id)})
    if not ones:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Not found")
    ones["_id"]=str(ones["_id"])
    restos=ones["restaurants"]
    print("restos",restos)
    resto_detail=[]    
     
    restaurant=db.restaurants.find_one({"_id":ObjectId(restos)})
                    
    detail={"_id":str(restaurant["_id"]),"name":restaurant["name"]}
    resto_detail.append(detail)
    print(resto_detail)
    ones["restaurants"]=resto_detail
    return ones
     






@router.delete("/{ad_id}")
async def delete_ads(ad_id:str,user=Depends(oauth2.verify_super_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
        if user["role"]!="super-admin":
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
        ad=collection.find_one({"_id":ObjectId(ad_id)})
        if not ad:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="advertisement not found")
        
             

        collection.delete_one({"_id":ObjectId(ad_id)})
        await utils.invalidate_all_cache()

        return "advertisement removed"
    except Exception as e:
         raise e
    

















@router.put("/{ad_id}")
async def edit_ads(
     ad_id:str,
     location: str = Form(None),
    title: str = Form(None),
    expire_time: int = Form(None),  
    image: UploadFile = File(None),
    restaurants: str = Form(None),
    user=Depends(oauth2.verify_super_access_token), token: HTTPAuthorizationCredentials = Depends(auth_scheme)             
 ):
    
    try:
        if user["role"]!="super-admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
        ad=collection.find_one({"_id":ObjectId(ad_id)})
        if not ad:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
                 
        update_data={}
        if location:
            count=collection.count_documents({"location":location})
            print(count)
            print(count)
            if count>1:
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"This advertisement is not applicable to {location}")
                    
                
            update_data["location"]=location
        if title:
            update_data["title"]=title
        
        if restaurants:
            update_data["restaurants"]=restaurants
        if expire_time:
             created_at=ad["createdAt"]
             expires_at = created_at + timedelta(seconds=expire_time)
             update_data["expiresAt"]=expires_at
             
        if image:
                    allowed_extensions = ['png', 'jpg', 'jpeg']
                    file_ext = image.filename.split('.')[-1]
                    if file_ext.lower() not in allowed_extensions:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                            detail="Only PNG, JPG, and JPEG formats are allowed for the image")

                    try:
                        contents = await image.read()
                        content_type, _ = mimetypes.guess_type(image.filename)
                        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=image.filename, Body=contents,
                                            ContentType=content_type)
                        image_link = f"{S3_IMAGE_LINK}{image.filename}"
                        update_data["image"]=image_link
                    except NoCredentialsError:
                        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                            detail="Failed to upload image: AWS credentials not found")
        if update_data:
                    updated_ad= collection.update_one({'_id': ObjectId(ad_id)}, {"$set": update_data})
        await utils.invalidate_all_cache()
        
        return "Updated"
            
    except Exception as e:
         raise e        