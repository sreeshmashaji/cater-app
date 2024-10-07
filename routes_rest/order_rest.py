import asyncio
from datetime import datetime,time
from decimal import Decimal
import json
from fastapi import Body, Form, HTTPException, status,APIRouter,Depends,BackgroundTasks
from config.database import db
from schemas import order_schema
import paypalrestsdk
from bson import ObjectId
import oauth2
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
import stripe
import httpx,logging
from pydantic import HttpUrl
from dotenv import dotenv_values


env = dict(dotenv_values(".env_admin"))
auth_scheme=HTTPBearer()

collection=db.orders

router=APIRouter(prefix="/orders",tags=["Order"])



stripe.api_key = env.get("STRIPE_API_KEY")
# stripe.api_key = "sk_test_51OoMWSSIWafKYQ7MUJ88TA2bbR7pL9kp9vrwz22YPnlJupvNfCH7dHJiFPiKtdB3LQjVpN5OhBoST0xeGNEHa75S00L1OqbuiU"



    
print(stripe.api_key)

# def get_or_create_product_price(product_name, unit_amount, image,currency="aed"):
#     print("enterrrrr")
#     try:
#         all_products = stripe.Product.list()
#         existing_product = next((p for p in all_products.data if p.name == product_name), None)

#         if existing_product:
#             product_id = existing_product.id
#         else:
#             product = stripe.Product.create(name=product_name,images=[HttpUrl(image["image"][0])])
#             product_id = product.id

#         existing_prices = stripe.Price.list(product=product_id, active=True)
#         print("here")
#         if existing_prices and existing_prices.data:
#             price_id = existing_prices.data[0].id
#         else:
#             unit_amount_integer = int(Decimal(str(unit_amount)) * 100)
#             price = stripe.Price.create(
#                 unit_amount=unit_amount_integer,
#                 currency=currency,
#                 product=product_id,
                
#             )
#             price_id = price.id
#             print("price",price_id)
#         return price_id
#     except stripe.error.StripeError as e:
#         print(f"Stripe API error: {e}")
#         return None
#     except Exception as e:
#         print(f"Error: {e}")
#         return None



# @router.post("/buy-now")
# async def buy_now(buy_request: order_schema.BuyRequest,user=Depends(oauth2.verify_customer_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
#     try: 
#         owner=user["customer_id"]
#         delivery_address=db.delivery_address.find_one({"_id":ObjectId(buy_request.delivery_address_id)})
#         if not delivery_address:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Address not found")
#         if str(delivery_address["customerId"])!=owner:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allwed")


#         delivery_address.pop("customerId")
#         delivery_address.pop("_id")
#         delivery_address.pop("status")
        
#         menu_item=db.restaurant_menu.find_one({"menuId":buy_request.menuId,"restaurantId":buy_request.restaurantId})
#         if not menu_item:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Menu item not found")
#         if menu_item:

#             customer = db.customer.find_one({"_id": ObjectId(user["customer_id"])})
#             if not customer:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        
#             resto = db.restaurants.find_one({"_id": ObjectId(menu_item["restaurantId"])})
            
#             if resto["status"]==True:
#                 raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="This restaurant is currently not accepting orders.")

#             print(menu_item)
            
#             customer_data = {
#                 "email": customer["email"],
#                 "name": customer["firstName"],
                
                
                
                
                
#             }

#             existing_customers = stripe.Customer.list(email=customer_data["email"])
#             if existing_customers.data:
#                 customer_id = existing_customers.data[0].id
#             else:
#                 stripe_customer = stripe.Customer.create(**customer_data)
#                 customer_id = stripe_customer.id

           
#         customer = stripe.Customer.modify(
#         customer_id,
#         shipping={
#           'name': delivery_address["Name"],
#         'address': {
#             'line1': delivery_address["Address"],
#             'city': delivery_address["city"],
#             'state': delivery_address["state"],
#             'postal_code': delivery_address["zipCode"],
#             'country': 'US',
#     },}
# )
#         line_items = []
#         Price=menu_item["price"]*buy_request.quantity
          
#         line_items.append({
#                 'price_data': {
#                     'currency': "usd",
#                     'product_data': {
#                         'name':menu_item["name"] ,
#                         'images':[HttpUrl(menu_item["image"][0])],
                       
#                     },
#                     'unit_amount': int(Decimal(str(menu_item["price"])) * 100),
#                 },
                
#                 'quantity':buy_request.quantity,
#             }
        
                
                
                
               
#             )
#         print("line_items",line_items)
#         menu_item['minumumServe']=menu_item['minimumServe']*buy_request.quantity
#         menu_item['quantity']=buy_request.quantity
#         menu_item['price']=menu_item["price"]*buy_request.quantity
        
#         menu_item.pop("_id")
#         menu_item.pop("type")

#         menu_item.pop("categoryId")

#         menu_item.pop("averageStarCount")
#         menu_item.pop("desc")
#         menu_item.pop("image")






#         encoded_list_menu = json.dumps(menu_item)

#         checkout_session = stripe.checkout.Session.create(
#             # success_url=f"http://localhost:8000/orders/success?session_id={{CHECKOUT_SESSION_ID}}",
#             success_url="http://localhost:3032/order-success/",
#             cancel_url=f"http://localhost:3032/order-cancelled/",
#             payment_method_types=["card"],
#             mode="payment",
#             billing_address_collection=None,
            
#             line_items=line_items,
            
           
            
#             payment_intent_data={
#         "metadata": {
#                        "cart_details":None,
#                        "menu_details":encoded_list_menu,
#                        "customerId":user["customer_id"],
#                        "delivery_time": buy_request.delivery_time,
#                        "delivery_date": buy_request.delivery_date,
#                        "delivery_address": json.dumps(delivery_address)
#         }
#     },
            
#             customer=customer_id
#         )
#         print(checkout_session)
#         return {"sessionId": checkout_session["id"],"url":checkout_session["url"]}
#     except Exception as e:
#         print("error", e)
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'There was an error with the Stripe session : {e}')



# @router.post("/create-checkout-session")
# async def create_checkout_session(
#     cart_items_request: order_schema.CartItemsRequest,
#     background_tasks: BackgroundTasks,
#     user=Depends(oauth2.verify_customer_access_token),
#     token: HTTPAuthorizationCredentials = Depends(auth_scheme)
# ):
#     try:
#         owner = user["customer_id"]
#         delivery_address = db.delivery_address.find_one({"_id": ObjectId(cart_items_request.delivery_address_id)})
#         if not delivery_address:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
        
#         if str(delivery_address["customerId"]) != owner:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

#         delivery_address.pop("customerId")
#         delivery_address.pop("_id")
#         delivery_address.pop("status")

#         cart_items = []
#         for item_id in cart_items_request.cart_item_ids:
#             cart_item = db.cart.find_one({"_id": ObjectId(item_id)})
#             if not cart_item:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found in cart")
#             cart_items.append(cart_item)

#         if not cart_items:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid cart items found")

#         customer = db.customer.find_one({"_id": ObjectId(cart_items[0]["customerId"])})
#         if not customer or str(customer["_id"]) != user["customer_id"]:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
        
#         resto = db.restaurants.find_one({"_id": ObjectId(cart_items[0]["restaurantId"])})
#         if resto and resto["status"]:
#             raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="This restaurant is currently not accepting orders.")
        
#         customer_data = {
#             "email": customer["email"],
#             "name": customer["firstName"]
#         }

#         existing_customers = stripe.Customer.list(email=customer_data["email"])
#         if existing_customers.data:
#             customer_id = existing_customers.data[0].id
#         else:
#             stripe_customer = stripe.Customer.create(**customer_data)
#             customer_id = stripe_customer.id

#         stripe.Customer.modify(
#             customer_id,
#             shipping={
#                 'name': delivery_address["Name"],
#                 'address': {
#                     'line1': delivery_address["Address"],
#                     'city': delivery_address["city"],
#                     'state': delivery_address["state"],
#                     'postal_code': delivery_address["zipCode"],
#                     'country': 'US',
#                 },
#             }
#         )

#         line_items = []
#         for cart_item in cart_items:
#             price=cart_item["totalPrice"]/cart_item["quantity"]
           
#             line_items.append({
#                 'price_data': {
#                     'currency': "usd",
#                     'product_data': {
#                         'name': cart_item["name"],
                        
#                         'images':[HttpUrl(cart_item["image"][0])],

#                     },
#                     'unit_amount': int(Decimal(str(price)) * 100),
#                 },
#                 'quantity': cart_item["quantity"],
#             })

#         encoded_list = json.dumps(cart_items_request.cart_item_ids)

#         checkout_session = stripe.checkout.Session.create(
#             success_url="http://localhost:3032/order-success/",
#             cancel_url=f"http://localhost:3032/order-cancelled/",
#             payment_method_types=["card"],
#             mode="payment",
#             billing_address_collection=None,
#             line_items=line_items,
#             payment_intent_data={
#                 "metadata": {
#                     # "menu_details": None,
#                     "cart_details": encoded_list,
#                     "delivery_time": cart_items_request.delivery_time,
#                     "delivery_date": cart_items_request.delivery_date,
#                     "delivery_address": json.dumps(delivery_address)
#                 }
#             },
#             customer=customer_id
#         )
#         print(checkout_session)
#         background_tasks.add_task(check_payment_status, checkout_session.id)
#         return {"sessionId": checkout_session["id"], "url": checkout_session["url"]}
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'There was an error with the Stripe session: {e}')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/create-checkout-session")
async def create_checkout_session(
    cart_items_request: order_schema.CartItemsRequest,
    background_tasks: BackgroundTasks,
    user=Depends(oauth2.verify_customer_access_token),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    try:
        owner = user["customer_id"]
        delivery_address = db.delivery_address.find_one({"_id": ObjectId(cart_items_request.delivery_address_id)})
        if not delivery_address:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
        
        if str(delivery_address["customerId"]) != owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

        delivery_address.pop("customerId")
        delivery_address.pop("_id")
        delivery_address.pop("status")

        cart_items = []
        for item_id in cart_items_request.cart_item_ids:
            cart_item = db.cart.find_one({"_id": ObjectId(item_id)})
            if not cart_item:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found in cart")
            cart_items.append(cart_item)

        if not cart_items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid cart items found")

        customer = db.customer.find_one({"_id": ObjectId(cart_items[0]["customerId"])})
        if not customer or str(customer["_id"]) != user["customer_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
        
        resto = db.restaurants.find_one({"_id": ObjectId(cart_items[0]["restaurantId"])})
        if resto and resto["status"]:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="This restaurant is currently not accepting orders.")
        
        customer_data = {
            "email": customer["email"],
            "name": customer["firstName"]
        }

        existing_customers = stripe.Customer.list(email=customer_data["email"])
        if existing_customers.data:
            customer_id = existing_customers.data[0].id
        else:
            stripe_customer = stripe.Customer.create(**customer_data)
            customer_id = stripe_customer.id

        stripe.Customer.modify(
            customer_id,
            shipping={
                'name': delivery_address["Name"],
                'address': {
                    'line1': delivery_address["Address"],
                    'city': delivery_address["city"],
                    'state': delivery_address["state"],
                    'postal_code': delivery_address["zipCode"],
                    'country': 'US',
                },
            }
        )

        line_items = []
        for cart_item in cart_items:
            price = cart_item["totalPrice"] / cart_item["quantity"]
            line_items.append({
                'price_data': {
                    'currency': "usd",
                    'product_data': {
                        'name': cart_item["name"],
                        'images': [HttpUrl(cart_item["image"][0])] if cart_item.get("image") else [HttpUrl("https://example.com/default-image.png")],
                    },
                    'unit_amount': int(Decimal(str(price)) * 100),
                },
                'quantity': cart_item["quantity"],
            })

        encoded_list = json.dumps(cart_items_request.cart_item_ids)

        checkout_session = stripe.checkout.Session.create(
            success_url="https://alacater.com/order-success/",
            cancel_url="http://alacater.com/order-cancelled",
            payment_method_types=["card"],
            mode="payment",
            line_items=line_items,
            metadata={
                "cart_details": encoded_list,
                "delivery_time": cart_items_request.delivery_time,
                "delivery_date": cart_items_request.delivery_date,
                "delivery_address": json.dumps(delivery_address)
            },
            customer=customer_id
        )

        logger.info(f"Created checkout session with ID: {checkout_session.id}")

        # Schedule the background task to check payment status
        background_tasks.add_task(delayed_payment_check, checkout_session.id)

        return {"sessionId": checkout_session["id"], "url": checkout_session["url"]}
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'There was an error with the Stripe session: {e}')
    

async def delayed_payment_check(session_id: str):
    # await asyncio.sleep(120) 
    await check_payment_status(session_id)  

async def check_payment_status(session_id: str):
    max_checks = 10 # Number of times to check
    wait_time = 12  # Wait time between checks in seconds

    for _ in range(max_checks):
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            
            print(f"Checking session {session_id} - payment_status: {checkout_session.payment_status}")
            print(f"Checking session {session_id} - payment_status: {checkout_session.status}")

            
            if checkout_session.payment_status == 'paid':
                await handle_payment_success(checkout_session)
                return
            elif checkout_session.status == 'expired':
                # await handle_payment_failure(checkout_session)
                return
        except Exception as e:
            print(f"Error retrieving checkout session {session_id}: {e}")
            

        print("waiting")
        await asyncio.sleep(wait_time)

    print(f"Failed to determine payment status for session {session_id} after {max_checks * wait_time} seconds")
    await handle_payment_failure(checkout_session)


async def handle_payment_success(checkout_session):
    print("inside sucess")
    try:
        
        metadata = checkout_session.metadata

        if 'cart_details' in metadata:
            cart_ids = json.loads(metadata["cart_details"])
            cart_items, total_amount = [], 0
            for cart_id in cart_ids:
                cart_item = db.cart.find_one({"_id": ObjectId(cart_id)})
                if not cart_item:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {cart_id} not found in cart")
                cart_items.append(cart_item)
                total_amount += cart_item["totalPrice"]

            if not cart_items:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid cart items found")
            

            order_data = {
                "customerId": str(cart_items[0]["customerId"]),
                "restaurantId": str(cart_items[0]["restaurantId"]),
                "caterId": str(cart_items[0]["caterId"]),
                "totalAmount": total_amount,
                "items": [
                    {
                        "menuId": str(item["menuId"]),
                        "name": item["name"],
                        "quantity": item["quantity"],
                        "minimumServe": item["minimumServe"],
                        "totalPrice": item["totalPrice"]
                    }
                    for item in cart_items
                ],
                "status": "Pending",
                "shippingAddress": json.loads(metadata["delivery_address"]),
                "delivery_date": datetime.strptime(metadata["delivery_date"], '%d-%m-%Y'),
                "delivery_time": datetime.strptime(metadata["delivery_time"], '%H.%M').time().isoformat(),
                "paymentId": checkout_session.payment_intent,
                "payment_status": checkout_session.payment_status,
                "order_time":datetime.utcnow()
            }

            result = db.orders.insert_one(order_data)
            result_data = db.orders.find_one({'_id': result.inserted_id})
            result_data["_id"] = str(result_data["_id"])

            # Delete cart items
            object_ids = [ObjectId(id) for id in cart_ids]
            delete_criteria = {"_id": {"$in": object_ids}}
            db.cart.delete_many(delete_criteria)

            logger.info(f"Order created and cart items deleted for session {checkout_session.id}")
    except Exception as e:
        logger.error(f"Error handling payment success for session {checkout_session.id}: {e}")




async def handle_payment_failure(checkout_session):
    try:
        metadata = checkout_session.metadata
        if 'cart_details' in metadata:
            cart_ids = json.loads(metadata["cart_details"])
            # Delete cart items
            object_ids = [ObjectId(id) for id in cart_ids]
            delete_criteria = {"_id": {"$in": object_ids}}
            db.cart.delete_many(delete_criteria)
            session = stripe.checkout.Session.expire(checkout_session)
            logger.info(f"Cart items deleted for session {checkout_session.id} due to payment failure")
    except Exception as e:
        logger.error(f"Error handling payment failure for session {checkout_session.id}: {e}")

@router.post("/cancel")
async def payment_cancel(session_id: str):
     try:
            session = stripe.checkout.Session.retrieve(session_id)
            print('Session:', session)
            await  handle_payment_failure(session)

     except stripe.error.StripeError as e:
            print('Error retrieving session:', e)
            raise e

# @router.post("/cart-update")
# async def cart_status(session:str):

#     session = stripe.checkout.Session.retrieve(session)
#     # data=collection.find_one({"_id":ObjectId(id)})
#     dictone={"status":session.status}
#     print(dictone)
#     # if session.status=="complete":
#     #     # collection.delete_one({"_id":ObjectId(id)})
#     #     collection.update_one({"_id":ObjectId(id)},{"$set":dictone})
#     # elif session.status=="expire":
#     #     collection.update_one({"_id":ObjectId(id)},{"$set":dictone})
#     # else:
#     #     collection.update_one({"_id":ObjectId(id)},{"$set":dictone})

#     # return {
#     #         "session_url": session.status
#     #     }


# @router.post("/success")
# async def payment_success(session_id: str):
#     try:
#         checkout_session = stripe.checkout.Session.retrieve(session_id)
#         order_data = db.orders.find_one({"paymentId": checkout_session["payment_intent"]})
#         if order_data:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Data already recorded with this payment")

#         payment_intent = stripe.PaymentIntent.retrieve(checkout_session.payment_intent)
#         metadata = payment_intent.metadata

#         if 'cart_details' in metadata:
#             cart_ids = json.loads(metadata["cart_details"])
#             cart_items, total_amount = [], 0
#             for cart_id in cart_ids:
#                 cart_item = db.cart.find_one({"_id": ObjectId(cart_id)})
#                 if not cart_item:
#                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {cart_id} not found in cart")
#                 cart_items.append(cart_item)
#                 total_amount += cart_item["totalPrice"]

#             if not cart_items:
#                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid cart items found")

#             first_item = cart_items[0]
#             order_data = {
#                 "customerId": str(first_item["customerId"]),
#                 "restaurantId": str(first_item["restaurantId"]),
#                 "caterId": str(first_item["caterId"]),
#                 "totalAmount": total_amount,
#                 "items": [
#                     {
#                         "menuId": str(item["menuId"]),
#                         "name": item["name"],
#                         "quantity": item["quantity"],
#                         "minimumServe": item["minimumServe"],
#                         "totalPrice": item["totalPrice"]
#                     }
#                     for item in cart_items
#                 ],
#                 "status": "Pending",
#                 "shippingAddress": json.loads(metadata["delivery_address"]),
#                 "delivery_date": datetime.strptime(metadata["delivery_date"], '%d-%m-%Y'),
#                 "delivery_time": datetime.strptime(metadata["delivery_time"], '%H.%M').time().isoformat(),
#                 "paymentId": checkout_session["payment_intent"],
#                 "payment_status": checkout_session["payment_status"]
#             }
#             print(cart_ids)
#             try:
#                 object_ids = [ObjectId(id) for id in cart_ids]

#                 delete_criteria = {"_id": {"$in": object_ids}}

#                 result = db.cart.delete_many(delete_criteria)
#                 if result.deleted_count == 0:
#                       raise HTTPException(status_code=404, detail="No documents found to delete")
#             except Exception as e:
#                   raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

            

#         # elif 'menu_details' in metadata:
#         #     menu_details = json.loads(metadata["menu_details"])
#         #     resto = db.restaurants.find_one({"_id": ObjectId(menu_details["restaurantId"])})
#         #     if not resto:
#         #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

#         #     order_data = {
#         #         "customerId": str(metadata["customerId"]),
#         #         "restaurantId": str(menu_details["restaurantId"]),
#         #         "caterId": str(resto["ownerId"]),
#         #         "totalAmount": menu_details["price"],
#         #         "items": {
#         #             "menuId": str(menu_details["menuId"]),
#         #             "name": menu_details["name"],
#         #             "quantity": menu_details["quantity"],
#         #             "minimumServe": menu_details["minimumServe"],
#         #             "totalPrice": menu_details["price"]
#         #         },
#         #         "status": "Pending",
#         #         "shippingAddress": json.loads(metadata["delivery_address"]),
#         #         "delivery_date": datetime.strptime(metadata["delivery_date"], '%d-%m-%Y'),
#         #         "delivery_time": datetime.strptime(metadata["delivery_time"], '%H.%M').time().isoformat(),
#         #         "paymentId": checkout_session["payment_intent"],
#         #         "payment_status": checkout_session["payment_status"]
#         #     }

#         else:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment metadata")

#         result = db.orders.insert_one(order_data)
#         result_data = db.orders.find_one({'_id': result.inserted_id})
#         result_data["_id"] = str(result_data["_id"])

#         return {"message": "Payment successful", "session_id": session_id, "order": result_data}

#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Error with Payment: {e}")

@router.get('/customer/{id}',summary="  Fetching  registered customer by id")
async def geting(id:str,user=Depends(oauth2.verify_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
        print("inside customer get")
        data = db.customer.find_one({"_id":ObjectId(id)})
        if user["customer_id"]!=id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
    
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
        data["_id"]=str(data["_id"])
        return data
    except Exception as e:
         raise e











@router.get("/{cater_id}")
def get_order(cater_id:str,user=Depends(oauth2.verify_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
        orders=list(collection.find({"caterId":cater_id}).sort("order_time", -1))
        if cater_id!=user["user_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
        if not orders:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No orders found")
            
        print(orders)
        result=[]
        for order in orders:
            order["_id"]=str(order["_id"])
            if order["status"]!="Cancelled":
                result.append(order)

        return result
    except Exception as e:
         raise e





# @router.put('/{order_id}')
# def order_status(data:order_schema.Stauts,order_id:str,user=Depends(oauth2.verify_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
#     order=collection.find_one({"_id":ObjectId(order_id)})
    
#     if order is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found")
    
#     if user["user_id"]!=order["caterId"]:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
    
#     if order["status"]=="Pending":
           
#             if data.status =="Accept":
#                 update_result={"status": "Processing"}
                
#             elif data.status == "Reject":
#                     update_result={"status": "Rejected"}
                 
#                 # try:
#                 #     payment_intent = order["paymentId"]
#                 #     refund = stripe.Refund.create(payment_intent=payment_intent)
#                 #     print("refund success")
#                 #     update_result={"status": "Rejected","refundId":refund.id,"payment_status":"Refunded"}

#                 # except Exception as e:
#                 #    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refund failed: " + str(e))
#             else:
#                  raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid status")

#     else:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Updation cancelled")
#     updated_data = collection.update_one(
#             {'_id': ObjectId(order_id)}, 
#             {"$set":  update_result} 
#         )
#     if not updated_data:
#                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sorry, operation failed")
#     return f"status changed to {update_result["status"]}"













@router.get("/customer-orders/{customer_id}")
async def get_customer_order(
    customer_id: str,
    user=Depends(oauth2.verify_customer_access_token),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    
    try:
        orders=list(collection.find({"customerId":customer_id}).sort("order_time", -1))
        if not orders:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No orders found")
        if customer_id!=user["customer_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")


        print(orders)
        result_data=[{**doc, "_id": str(doc["_id"])} for doc in orders]
        return result_data
    except Exception as e:
         raise e




@router.put('/cancel-order/{order_id}')
async def cancel_customer_order(
    order_id: str,user=Depends(oauth2.verify_customer_access_token),token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    
    try:
        orders=collection.find_one({"_id":ObjectId(order_id)})
        if not orders:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found")
        if orders["customerId"]!=user["customer_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not alllowed to cancel the order")
        if orders["status"]=="Pending":
            try:
                        payment_intent = orders["paymentId"]
                        refund = stripe.Refund.create(payment_intent=payment_intent)
                        print("refund success")
                        

            except Exception as e:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refund failed: " + str(e))
            updated_data = collection.update_one(
                {'_id': ObjectId(order_id)}, 
                {"$set":  {"status":"Cancelled"}} 
            )
            if not updated_data:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sorry, operation failed")
            return "Order cancelled"
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You can't cancel the order ")
    except Exception as e:
         raise e









@router.put('/{order_id}')
def order_status(data:order_schema.Stauts,order_id:str,user=Depends(oauth2.verify_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    
    try:
            order=collection.find_one({"_id":ObjectId(order_id)})
            
            if order is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found")
            
            if user["user_id"]!=order["caterId"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not allowed")
            if order["status"]=="Pending":
                
                    
                    if data.status =="Accept":
                        update_result={"status": "Processing"}
                        
                    elif data.status == "Reject":
                        
                        try:
                            payment_intent = order["paymentId"]
                            refund = stripe.Refund.create(payment_intent=payment_intent)
                            print(refund)
                            print("refund success")
                            update_result={"status": "Rejected","payment_status":"Refunded"}

                        except Exception as e:
                          raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refund failed: " + str(e))
                    else:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid status")

                    
                    
            elif order["status"]=="Processing":
                if data.status =="Delivered":
                        update_result={"status": "Delivered"}
                else:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid status")

            else:
                raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED,detail="Updation cancelled")
            updated_data = collection.update_one(
                    {'_id': ObjectId(order_id)}, 
                    {"$set":  update_result} 
                )
            if not updated_data:
                        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sorry, operation failed")
            return f"status changed to {update_result["status"]}"
    except Exception as e:
         raise e












