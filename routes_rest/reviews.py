from datetime import datetime
import re
import time
from typing import Annotated
from bson import ObjectId
from fastapi import Body, File, Form, HTTPException, UploadFile, status,APIRouter,Depends,BackgroundTasks
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
import pytz
# from fastapi_limiter.depends import RateLimiter
from config.database import db
from schemas import review_schema
import utils,oauth2
from services import emailvalidation



collection=db.reviews

router=APIRouter(prefix="/reviews",tags=["review"])

auth_scheme=HTTPBearer()





@router.post("")
async def create_review(review_input: review_schema.ReviewInput,user=Depends(oauth2.verify_customer_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
        customer_id=user["customer_id"]
        customer=db.customer.find_one({"_id":ObjectId(customer_id)})
        if not customer:
            HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
        menu = db.restaurant_menu.find_one({"menuId": review_input.menuId,"restaurantId":review_input.restaurantId})
        if not menu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
        # if not emailvalidation.validate_email(review_input.email):
        #     raise HTTPException(status_code=400, detail="Invalid Email Address")
        
        review_data = {
            "menuId": ObjectId(review_input.menuId),
            "restaurantId": ObjectId(review_input.restaurantId),

            "email": customer["email"],
            "name": customer["firstName"],
            "review": review_input.review,
            "starCount": review_input.starCount,
            "likeCount":0,
            "dislikeCount":0,
            "createdAt":datetime.now(pytz.utc)
        }


        data=db.reviews.insert_one(review_data)
        result= collection.find_one({'_id':data.inserted_id})
        result["_id"]=str(result["_id"])
        result["menuId"]=str(result["menuId"])
        result["restaurantId"]=str(result["restaurantId"])


        await update_menu_average_star_count(review_input.menuId,review_input.restaurantId)
        await update_restaurant_average_star_count(review_input.restaurantId)
        await utils.invalidate_all_cache()

        return {"message": "Review created successfully","data":result}
    except Exception as e:
        raise e











async def update_menu_average_star_count(menu_id,restaurant_id):
  

    total_reviews = db.reviews.count_documents({"menuId": ObjectId(menu_id),"restaurantId":ObjectId(restaurant_id)})
    total_star_count = db.reviews.aggregate([
        {"$match": {"menuId": ObjectId(menu_id),"restaurantId":ObjectId(restaurant_id)}},
        {"$group": {"_id": None, "total_star_count": {"$sum": "$starCount"}}}
    ])
    total_star_count = list(total_star_count)
    if total_star_count:
        total_star_count = total_star_count[0]["total_star_count"]
        average_star_count =float( round(total_star_count / total_reviews, 1))
    else:
        average_star_count = 0.0
    
    resto_menu=db.restaurant_menu.find_one({"menuId":menu_id,"restaurantId":restaurant_id})
    if resto_menu is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Menu item not found in this restaurant")
    db.restaurant_menu.update_one(
        {"_id": ObjectId(resto_menu["_id"])},
        {"$set": {"averageStarCount": average_star_count}}
    )
    await utils.invalidate_all_cache()






# def update_restaurant_average_star_count(restaurant_id):
    
#     total_reviews = db.restaurant_menu.count_documents({"restaurantId":(restaurant_id)})
#     if total_reviews==0:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Restaurant not found")
#     print(total_reviews)
#     total_star_count = db.reviews.aggregate([
#         {"$match": {"restaurantId":ObjectId(restaurant_id)}},
#         {"$group": {"_id": None, "total_star_count": {"$sum": "$starCount"}}}
#     ])
#     total_star_count = list(total_star_count)
#     if total_star_count:
#         total_star_count = total_star_count[0]["total_star_count"]
#         print(total_star_count)

#         average_star_count =float( round(total_star_count / total_reviews, 1))
#         print(average_star_count)
#     else:
#         average_star_count = 0.0
    
#     resto=db.restaurants.find_one({"_id":ObjectId(restaurant_id)})
#     if resto is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Restaurant not found ")
#     db.restaurants.update_one(
#         {"_id": ObjectId(resto["_id"])},
#         {"$set": {"averageStarCount": average_star_count}}
#     )
#     resto=db.restaurants.find_one({"_id":ObjectId(restaurant_id)})

#     print(resto)


async def update_restaurant_average_star_count(restaurant_id: str):
    try:
        # Retrieve all menus associated with the restaurant
        menus = list(db.restaurant_menu.find({"restaurantId": restaurant_id}))
        print(menus)
        # Calculate the total star count and number of menus
        total_star_count = 0
        total_menus = 0
        for menu in menus:
            if "averageStarCount" in menu and menu["averageStarCount"] is not None:
                total_star_count += menu["averageStarCount"]
                # total_menus += 1
        print(total_star_count)
        # Calculate the average star count
        total_menus = db.restaurant_menu.count_documents({"restaurantId":(restaurant_id)})
        print(total_menus)
        if total_menus > 0:
            average_star_count = float(round(total_star_count / total_menus, 1))
        else:
            average_star_count = 0.0
        
        # Update the restaurant's average star count
        result = db.restaurants.update_one(
            {"_id": ObjectId(restaurant_id)},
            {"$set": {"averageStarCount": average_star_count}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

        print(f"Updated average star count for restaurant {restaurant_id}: {average_star_count}")
        await utils.invalidate_all_cache()
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))










@router.get("")
def get_reviews_by_menu_id(menuId:str,restaurantId:str):
    try:
        menu = db.menus.find_one({"_id": ObjectId(menuId)})
        if not menu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

        
        reviews = list(db.reviews.find({"menuId": ObjectId(menuId),"restaurantId":ObjectId(restaurantId)}))

        
        for review in reviews:
            review["_id"] = str(review["_id"])
            review["menuId"] = str(review["menuId"])
            review["restaurantId"]=str(review["restaurantId"])


        return {"reviews": reviews}
    except Exception as e:
        raise e







@router.put("/{review_id}")
async def update_review(review_id: str,data:review_schema.ReviewLike):
    try:

    
        review = collection.find_one({"_id": ObjectId(review_id)})
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
        
        
        current_like_count = review["likeCount"]
        current_dislike_count = review["dislikeCount"]
        
        
    
        updated_review = collection.update_one(
            {"_id": ObjectId(review_id)},
            {
                "$set": {
                    "likeCount": current_like_count + data.likeCount,
                    "dislikeCount": current_dislike_count + data.dislikeCount
                }
            }
            
        )
        
    
        updated_review = collection.find_one({"_id": ObjectId(review_id)})
        print(updated_review)
        updated_review["_id"] = str(updated_review["_id"])
        updated_review["menuId"] = str(updated_review["menuId"])
        updated_review["restaurantId"]=str(updated_review["restaurantId"])
    

        await utils.invalidate_all_cache()
        
        return {"message": "Review updated successfully", "data": updated_review}
    except Exception as e:
        raise e