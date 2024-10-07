from pydantic import BaseModel
from bson import ObjectId

class Category(BaseModel):
    name:str
    
    