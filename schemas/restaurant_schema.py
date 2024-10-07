
from datetime import time

import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel
from bson import ObjectId






class BusinessHours(BaseModel):
    start_time: time
    end_time: time


class BusinessDays(BaseModel):
    Monday: str
    Tuesday: str
    Wednesday: str
    Thursday: str
    Friday: str
    Saturday: str
    Sunday:str


class UpdateRestaurant(BaseModel):
    restaurant_id:str
    business_hours:BusinessDays


class RestaurantInput(BaseModel):
    ownerId: ObjectId
    name: str
    location: str
    image: Optional[str]
    contactNumber: str
    businessHours: Optional[Dict[str, BusinessHours]] = None
    holidays: Optional[list[str]] = None
    status: bool = False
    dateAdded: datetime
    class Config:
        arbitrary_types_allowed = True  
        from_attributes = True







class DeleteResto(BaseModel):
    id:list[str]


class Status(BaseModel):
    id:str
    status:bool



class SearchByName(BaseModel):
    name:str


class Coupon(BaseModel):
    enabled:bool=True
    title:str




# @strawberry.input
# class MenuItems:
#     name: str
#     desc: str
#     price: float
#     minimum_serve: int
#     type: str

# @strawberry.input
# class RestaurantInputs:
#     name: str
#     location: str
#     image: str
#     menu: Dict[str, List[MenuItem]]



# @strawberry.type
# class RestaurantOtputs:
#     _id:str
#     name:str
#     location:str
#     image:str

