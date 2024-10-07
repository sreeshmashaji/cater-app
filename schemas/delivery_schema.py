from pydantic import BaseModel

class Delivery_input(BaseModel):
    Name:str
    Address:str
    city:str
    state:str
    zipCode:str
    phoneNumber:str
    status:bool=False
