



from bson import ObjectId
from pydantic import BaseModel





class CartInput(BaseModel):
    restaurantId:str
    menuId:str
    quantity:int=1


class Cart(BaseModel):
    customerId:ObjectId
    menuId:ObjectId
    name:str
    image:list[str]
    restaurantId:ObjectId
    quantity:int
    minimumServe:int
    totalPrice:float
    caterId:ObjectId
    class Config:
        arbitrary_types_allowed = True  
        from_attributes = True


class CartEdit(BaseModel):
    newQuantity:int