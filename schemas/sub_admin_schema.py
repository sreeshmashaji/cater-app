from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from bson import ObjectId


class SubAdmin(BaseModel):
    name:str
    email:str
    password:str
    ownerId:ObjectId
    role:str="sub-admin"
    dateAdded:datetime
    
    class Config:
        arbitrary_types_allowed = True  
        from_attributes = True


class SubAdminInput(BaseModel):
    email:str
    name:str
    
    password:str


class SubAdminDelete(BaseModel):
    id:list[str]

class SubAdminUpdate(BaseModel):
    id:str
    

