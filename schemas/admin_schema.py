from pydantic import BaseModel
import strawberry





@strawberry.input
class Register:
    firstName: str = strawberry.field()
    lastName: str = strawberry.field()
    email: str= strawberry.field()
    password: str = strawberry.field()
    phoneNumber: str = strawberry.field()
    role:str="admin"
    status:bool=True



@strawberry.type
class RegisterSave:
    firstName: str = strawberry.field()
    lastName: str = strawberry.field()
    email: str= strawberry.field()
    password: str= strawberry.field()
    phoneNumber: str = strawberry.field()
    role:str="admin"
    status:bool=True
    profilePicture:str|None=None
    
    

@strawberry.input
class Login:
    role:str
    email: str = strawberry.field()
    password: str = strawberry.field()

@strawberry.type
class RegisterResponse:
    _id:str=strawberry.field()
    firstName: str = strawberry.field()
    lastName: str = strawberry.field()
    email: str= strawberry.field()
    
    phoneNumber: str = strawberry.field()
    role:str="admin"
    status:bool=True
    profilePicture:str|None=None    

@strawberry.type
class ReturnUser:
    message:str
    data:RegisterResponse


@strawberry.type
class LoginResponse:
    token: str = strawberry.field()
  

@strawberry.input
class Reset:
    
    currentPassword: str = strawberry.field()
    newPassword: str = strawberry.field()
    confirmPassword: str = strawberry.field()


@strawberry.input
class ManageSubAdmin:
    email: str= strawberry.field()
    password: str = strawberry.field()
    phoneNumber: str = strawberry.field()
    role:str="sub-admin"
    status:bool=True

@strawberry.input
class VerifyEmailOtp:
    otp:str
    toMail:str


@strawberry.input
class ForgotPassword:
    email:str


@strawberry.input
class PasswordRest:
    email:str
    newPassword:str
    confirmPassword:str



@strawberry.input
class BlackList:
    resetToken:str
    
