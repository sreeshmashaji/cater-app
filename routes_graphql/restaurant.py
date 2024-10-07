# from fastapi import APIRouter
# from fastapi import Depends,HTTPException,status
# from schemas import restaurant_schema
# from config.database import db,get_database
# import strawberry
# from strawberry.fastapi import GraphQLRouter


# # router=APIRouter(prefix='/api/restaurant')


# collection=db.restaurants


# @strawberry.type
# class Query():
#     @strawberry.field
#     async def get_restaurants()->list[restaurant_schema.RestaurantOtputs]:
#         data = list(collection.find().limit(10000000))
#         return [restaurant_schema.RestaurantOtputs(
#             _id=str(resultdata['_id']),
#             name=resultdata.get('name', ''),
#             location=resultdata.get('location', ''),
#             image=resultdata.get('image', '')
            
#         ) for resultdata in data]
    
#     @strawberry.field
#     async def search_by_location(location:str)->list[restaurant_schema.RestaurantOtputs]:
#         restaurants=list(collection.find({"location":location}))
#         if not restaurants:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Restaurants found")


#         return [restaurant_schema.RestaurantOtputs(
#             _id=str(resultdata['_id']),
#             name=resultdata.get('name', ''),
#             location=resultdata.get('location', ''),
#             image=resultdata.get('image', '')
            
#         ) for resultdata in restaurants]

# @strawberry.type
# class Mutation():
#     @strawberry.field
#     async def add_restaurant(data:restaurant_schema.RestaurantInputs)->restaurant_schema.RestaurantOtputs:
#         exist_restaurant = collection.find_one({'name': data.name})
#         if exist_restaurant:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Restaurant already exists")
#         menu_dict = {key: [item.dict() for item in value] for key, value in data.menu.items()}
#         insert_data = {
#             'name': data.name,
#             'location': data.location,
#             'image': data.image,
#             'menu': menu_dict
#         }

#         data= collection.insert_one(insert_data)
#         resultdata= collection.find_one({'_id':data.inserted_id})
#         resultdata["_id"]=str(resultdata["_id"])
#         if not resultdata:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Sorry Operation Failed")
#         return  restaurant_schema.RestaurantOtputs(
#             _id=str(resultdata['_id']),
#             name=resultdata.get('name', ''),
#             location=resultdata.get('location', ''),
#             image=resultdata.get('image', ''))


    
#     @strawberry.field
#     async def delete_restaurant(name:str)->str:
#         exist_restaurant = collection.find_one({'name': name})
#         if not  exist_restaurant:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Restaurant doesn't exists")
        
#         collection.delete_one({"name":name})
#         return "deleted"


# graphSchema=strawberry.Schema(query=Query,mutation=Mutation)

# router=GraphQLRouter(graphSchema)


















# @router.post('/add-restaurant')
# async def add_item(data:restaurant_schema.Restaurant):
#     exist_restaurant = collection.find_one({'name': data.name})
#     if exist_restaurant:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Restaurant already exists")

#     data= collection.insert_one(data.model_dump())
#     resultdata= collection.find_one({'_id':data.inserted_id})
#     resultdata["_id"]=str(resultdata["_id"])
#     if not resultdata:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Sorry Operation Failed")
#     return {"message":"success","data":resultdata}



# @router.get('/view-restaurant')
# async def geting():
#     data = list(collection.find().limit(10000))  
#     data = [{**resultdata, '_id': str(resultdata['_id'])} for resultdata in data]
#     return data




# @router.delete('/delete-restaurant/{name}')
# async def get_one(name:str):
#     resultdata = collection.find_one({'name':name}) 
#     if not resultdata:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant doesnt exists")
        
#     collection.delete_one({"name":name})
#     return "deleted"






# @router.get('/view-restaurant/{name}')
# async def get_one(name:str):
#     resultdata = collection.find_one({'name':name}) 
#     if not resultdata:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant doesnt exists")
        
#     resultdata["_id"]=str(resultdata["_id"])
#     return resultdata