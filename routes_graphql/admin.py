import strawberry
from fastapi import HTTPException, status
from config.database import db
from schemas import admin_schema
import utils, oauth2
from strawberry.fastapi import GraphQLRouter

collection = db.register

@strawberry.type
class Query:
    @strawberry.field
    async def users() -> list[admin_schema.ReturnUser]:
        data = list(collection.find().limit(10))
        return [admin_schema.ReturnUser(
            _id=str(doc['_id']),
            firstname=doc.get('firstname', ''),
            lastname=doc.get('lastname', ''),
            email=doc.get('email', ''),
            phoneNumber=doc.get('phoneNumber',)
        ) for doc in data]


@strawberry.type
class Mutation:
    @strawberry.field
    async def register(data: admin_schema.Register) -> admin_schema.ReturnUser:
        existing_user = collection.find_one({'email': data.email})
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        
        phone_number=data.phoneNumber
        if not phone_number.isdigit() or len(phone_number) != 10:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid phone number")

        data.password = utils.hash(data.password)
        inserted_data = collection.insert_one(data.__dict__)
        resultdata = collection.find_one({'_id': inserted_data.inserted_id})
        resultdata["_id"] = str(resultdata["_id"])
        return admin_schema.ReturnUser(
            _id=resultdata['_id'],
            firstname=resultdata.get('firstname', ''),
            lastname=resultdata.get('lastname', ''),
            email=resultdata.get('email', ''),
            phoneNumber=resultdata.get('phoneNumber', )    
        )


    @strawberry.field
    async def login(data: admin_schema.Login) ->admin_schema.LoginResponse:
        user = collection.find_one({"email": data.email})
        if not user or not utils.verify(data.password, user['password']):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or invalid credentials")

        token = oauth2.create_access_token({"email": data.email})
        return admin_schema.LoginResponse(token=token)

    @strawberry.field
    async def reset_password(data: admin_schema.Reset) -> str:
        existing_user = collection.find_one({'email': data.email})
        if not existing_user or not utils.verify(data.previous_password, existing_user['password']):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or incorrect previous password")

        if data.new_password != data.confirm_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New passwords do not match")

        hashpass = utils.hash(data.new_password)
        collection.update_one({"email": data.email}, {'$set': {"password": hashpass}})
        return "Password reset successful"

graphSchema=strawberry.Schema(query=Query,mutation=Mutation)


router = GraphQLRouter(
    graphSchema,
   
)

        


# # # @router.get('/users')
# # # async def geting(db=Depends(get_database)):
# # #     # data= await collection.find().to_list(10)
    
# # #     data = list(collection.find().limit(10000))  # Retrieve the first 10 documents
# # #     data = [{**doc, '_id': str(doc['_id'])} for doc in data]
# # #     return data


# # # @router.post('/register')
# # # async def add_item(data:admin_schema.Register):
# # #     existing_user = collection.find_one({'email': data.email})
# # #     if existing_user:
# # #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

# # #     data.password=utils.hash(data.password)
# # #     print(data.password)
# # #     data= collection.insert_one(data.model_dump())
# # #     resultdata= collection.find_one({'_id':data.inserted_id})
# # #     resultdata["_id"]=str(resultdata["_id"])
# # #     if not resultdata:
# # #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Sorry Operation Failed")
# # #     return {"message":"success","data":resultdata}



# # # @router.post('/login')
# # # def login(data: admin_schema.Login):
# # #    user=collection.find_one({"email":data.email})
# # #    if not user:
# # #        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not Found , Please check username and password")
# # #    if not utils.verify(data.password,user['password']):
# # #        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=" Please check username and password")
# # #    print(user)
# # #    token=oauth2.create_access_token({"email":data.email})
# # #    print("token",token)
# # #    return {"token":token}


# # # @router.post('/reset-password')
# # # def reset(data:admin_schema.Reset):
# # #     existing_user = collection.find_one({'email': data.email})
# # #     if not existing_user:
# # #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not found")
# # #     if not utils.verify(data.previous_password,existing_user['password']):
# # #        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Inmcorrect Previous password")
# # #     if data.new_password != data.confirm_password:
# # #        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="mismatch password")
# # #     hashpass=utils.hash(data.new_password)
# # #     existing_user["password"]=hashpass
# # #     collection.update_one({"email":data.email},{'$set':{"password":hashpass}})
# # #     print(existing_user)
# # #     return "success"






       
   
