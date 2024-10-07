import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, HttpUrl

from fastapi import UploadFile
from bson import ObjectId




class Stauts(BaseModel):
    status:str

class Order(BaseModel):
    customerId:str
    productName:str
    quantity:int 
    totalAmount:float
    restaurantId:str
    menuId:str
    caterId:str
    status:str="pending"
    shippingAddress:dict=None
    paymentId:str=None
    payment_status:str="pending"





class BuyItem(BaseModel):
   menuId:str
   restaurantId:str
   quantity:int

class CartItemsRequest(BaseModel):
    cart_item_ids: list[str]
    delivery_time:str
    delivery_date:str
    delivery_address_id:str

class BuyRequest(BaseModel):
    menuId:str
    restaurantId:str
    quantity:int=1
    delivery_time:str
    delivery_date:str
    delivery_address_id:str