from pydantic import BaseModel


class Customer(BaseModel):
    email:str
    firstName:str
    lastName:str
    password:str
    phoneNumber:str
    avatarId:str


class CustomerSave(BaseModel):
    firstName: str 
    lastName: str 
    email: str
    password: str
    phoneNumber: str 
    avatarId:str
    status:bool=True
    
    

class Login(BaseModel):
    email:str
    password:str


class ForgotPassword(BaseModel):
    email:str



class PasswordRest(BaseModel):
    email:str
    newPassword:str
    confirmPassword:str


class Reset(BaseModel):
    currentPassword: str 
    newPassword: str 
    confirmPassword: str 

class MenuDetails(BaseModel):
    restaurantId:str
    menuId:str


class VerifyEmailOtp(BaseModel):
    otp:str
    toMail:str