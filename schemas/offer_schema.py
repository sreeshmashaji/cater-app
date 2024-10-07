from pydantic import BaseModel

class AddOffer(BaseModel):
    title:str
    description:str
    restaurants:list[str]

class OfferUpdate(BaseModel):
    restaurants:list[str]