from typing import Optional
from pydantic import BaseModel



class Login(BaseModel):
    email:str
    password:str
    role:str


class Reset(BaseModel):
    currentPassword: str
    newPassword: str 
    confirmPassword: str 

class Category(BaseModel):
    location:str
    categoryName:str
    description:str
    restaurants:list[str]

class UpdateCategory(BaseModel):
    restaurants:Optional[list[str]]
    categoryName:Optional[str]
    description:str

    
    