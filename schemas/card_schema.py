from bson import ObjectId
from pydantic import BaseModel

class CardInput(BaseModel):
    cardNumber:int
    cardHolder:str
    expireDate:str
    cvc:int
    type:str

class Card(BaseModel):
    ownerId:ObjectId
    cardNumber:int
    cardHolder:str
    expireDate:str
    cvc:int
    type:str
    class Config:
        arbitrary_types_allowed = True  
        from_attributes = True