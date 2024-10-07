import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel
import strawberry
from fastapi import UploadFile
from bson import ObjectId





class MenuItem(BaseModel):
    ownerId:ObjectId
    restaurantId:list[ObjectId]
    name: str
    desc: str
    price: float
    categoryId:ObjectId
    minimumServe: int
    type: str
    image:Optional[list[str]]=None

    dateAdded:datetime
    

    class Config:
        arbitrary_types_allowed = True  
        from_attributes = True


class RestoId(BaseModel):
    ids:List[str]


class Delete_one(BaseModel):
    menuId:str
    restaurantId:str
    

class PriceServe(BaseModel):
    menuId: str
    
    restaurantId: str
    
    price: Optional[float]=None
    minimumServe: Optional[int]=None 
    categoryId:Optional[str]=None