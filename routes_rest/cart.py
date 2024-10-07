

from datetime import datetime
from fastapi import Body, Form, HTTPException, status,APIRouter,Depends,BackgroundTasks
from config.database import db
from schemas import cart_schema

from bson import ObjectId
import oauth2
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
auth_scheme=HTTPBearer()

collection=db.cart

router=APIRouter(prefix="/cart",tags=["cart"])














# @router.post('')
# def add_to_cart(data: cart_schema.CartInput, user=Depends(oauth2.verify_customer_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    
#     menu_details = db.menus.find_one({"_id": ObjectId(data.menuId)})
#     if not menu_details:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

    
#     price = menu_details["price"]
#     total_price = price * data.quantity

    
#     existing_item = db.cart.find_one({"customerId": ObjectId(user["customer_id"]), "menuId": ObjectId(data.menuId),"restaurantId":ObjectId(data.restaurantId)})
#     if existing_item:
       
#         new_quantity = existing_item["quantity"] + data.quantity
#         new_total_price = price * new_quantity
#         new_maxServe=menu_details["minimumServe"] * new_quantity
#         db.cart.update_one(
#             {"_id": existing_item["_id"]},
#             {"$set": {"quantity": new_quantity, "totalPrice": new_total_price,"maxServe":new_maxServe}}
#         )
#         return {"message": "Quantity updated in cart"}

    
#     cart_data = cart_schema.Cart(
#         customerId=ObjectId(user["customer_id"]),
#         menuId=ObjectId(data.menuId),
#         restaurantId=ObjectId(data.restaurantId),
#         name=menu_details["name"],
#         totalPrice=total_price,
#         maxServe=menu_details["minimumServe"] * data.quantity,
#         quantity=data.quantity,
#         caterId=menu_details["ownerId"]
#     )
#     datas = db.cart.insert_one(cart_data.__dict__)
#     resultdata= collection.find_one({'_id':datas.inserted_id})
#     resultdata["_id"]=str(resultdata["_id"])
#     resultdata["customerId"]=str(resultdata["customerId"])
#     resultdata["menuId"]=str(resultdata["menuId"])

#     resultdata["restaurantId"]=str(resultdata["restaurantId"])
#     resultdata["caterId"]=str(resultdata["caterId"])
#     return {"message": "Item added to cart successfully", "data": resultdata}



@router.post('')
def add_to_cart(data: cart_schema.CartInput, user=Depends(oauth2.verify_customer_access_token), token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    try:

            menu_details = db.restaurant_menu.find_one({"menuId": data.menuId,"restaurantId":data.restaurantId})
            if not menu_details:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

            price = menu_details["price"]
            total_price = price * data.quantity

            
            existing_items = db.cart.find({"customerId": ObjectId(user["customer_id"])})
            for item in existing_items:
                if item["restaurantId"] != ObjectId(data.restaurantId):
                    
                    db.cart.delete_many({"customerId": ObjectId(user["customer_id"])})
                    break
            existing_item = db.cart.find_one({"customerId": ObjectId(user["customer_id"]), "menuId": ObjectId(data.menuId),"restaurantId":ObjectId(data.restaurantId)})
            if existing_item:
            
                new_quantity = existing_item["quantity"] + data.quantity
                new_total_price = price * new_quantity
                # new_maxServe=menu_details["minimumServe"] * new_quantity
                db.cart.update_one(
                    {"_id": existing_item["_id"]},
                    {"$set": {"quantity": new_quantity, "totalPrice": new_total_price}}
                )
                return {"message": "Quantity updated in cart"}

            menu=db.menus.find_one({"_id":ObjectId(data.menuId)})
            cart_data = cart_schema.Cart(
                customerId=ObjectId(user["customer_id"]),
                menuId=ObjectId(data.menuId),
                restaurantId=ObjectId(data.restaurantId),
                name=menu_details["name"],
                image=menu_details["image"],
                totalPrice=total_price,
                minimumServe=menu_details["minimumServe"],
                quantity=data.quantity,
                caterId=ObjectId(menu["ownerId"])
            )
            datas = db.cart.insert_one(cart_data.__dict__)
            resultdata= collection.find_one({'_id':datas.inserted_id})
            resultdata["_id"]=str(resultdata["_id"])
            resultdata["customerId"]=str(resultdata["customerId"])
            resultdata["menuId"]=str(resultdata["menuId"])

            resultdata["restaurantId"]=str(resultdata["restaurantId"])
            resultdata["caterId"]=str(resultdata["caterId"])
            return {"message": "Item added to cart successfully", "data": resultdata}
    except Exception as e:
        raise e




@router.get("/{customer_id}")
def get_cart_items(customer_id: str, user=Depends(oauth2.verify_customer_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
   
            if str(user["customer_id"]) != customer_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource")

        
            cart_items = db.cart.find({"customerId": ObjectId(customer_id)})
            formatted_cart_items = []
            for resultdata in cart_items:
            
                resultdata["_id"]=str(resultdata["_id"])
                resultdata["customerId"]=str(resultdata["customerId"])
                resultdata["menuId"]=str(resultdata["menuId"])

                resultdata["restaurantId"]=str(resultdata["restaurantId"])
                resultdata["caterId"]=str(resultdata["caterId"])
                formatted_cart_items.append(resultdata)
            
            return formatted_cart_items
    except Exception as e:
         raise e











@router.delete('/{cart_item_id}')
def delete_cart_item(cart_item_id:str,user=Depends(oauth2.verify_customer_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    
    try:
    
            cart_item = db.cart.find_one({"_id": ObjectId(cart_item_id)})

            if not cart_item:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
            
            
            if ObjectId(user["customer_id"]) !=cart_item["customerId"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
            

            collection.delete_one({"_id":ObjectId(cart_item_id)})
            return "Cart item revomed"
    except Exception as e:
         raise e



# @router.put("/{cart_item_id}")
# def edit_cart_item(cart_item_id:str, data:cart_schema.CartEdit,user=Depends(oauth2.verify_customer_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
#     customer_id=user["customer_id"]
#     if str(user["customer_id"]) != customer_id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    
#     cart_item = db.cart.find_one({"_id": ObjectId(cart_item_id)})

#     if not cart_item:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
#     menu_details = db.menus.find_one({"_id": cart_item["menuId"]})
#     if not menu_details:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
   
#     price = menu_details["price"]
#     new_total_price = price * data.newQuantity
# #     new_max_serve = menu_details["minimumServe"] * data.newQuantity

    
#     db.cart.update_one(
#         {"_id": cart_item["_id"]},
#         {"$set": {"quantity": data.newQuantity, "totalPrice": new_total_price, "minimumServe": new_max_serve}}
#     )

    
#     resultdata = db.cart.find_one({"_id": cart_item["_id"]})
#     resultdata["_id"]=str(resultdata["_id"])
#     resultdata["customerId"]=str(resultdata["customerId"])
#     resultdata["menuId"]=str(resultdata["menuId"])

#     resultdata["restaurantId"]=str(resultdata["restaurantId"])
#     resultdata["caterId"]=str(resultdata["caterId"])
#     return {"message": "Cart item quantity updated successfully", "data": resultdata}