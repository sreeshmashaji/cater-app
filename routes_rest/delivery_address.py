from fastapi import Body, Form, HTTPException, status,APIRouter,Depends,BackgroundTasks
from config.database import db
from schemas import delivery_schema

from bson import ObjectId
import oauth2
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
auth_scheme=HTTPBearer()

collection=db.delivery_address

router=APIRouter(prefix="/customers/delivery-address",tags=["delivery-address"])


@router.post('')
def add_delivery_address(data:delivery_schema.Delivery_input,token:HTTPAuthorizationCredentials=Depends(auth_scheme),user=Depends(oauth2.verify_customer_access_token)):
    try:
            customerId=user["customer_id"]
            phone_number=data.phoneNumber
            # cleaned_phone_number = phone_no_validation.validate_phone_number(data.phoneNumber)
            if not phone_number.isdigit():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number must contain only digits")
            if   len(phone_number) > 10:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Phone Number")
            # if data.status:
            #     collection.update_many(
            #     {"customerId": ObjectId(customerId), "status": True},
            #     {"$set": {"status": False}}
            # )
            add_data={**data.__dict__,"customerId":ObjectId(customerId)}
            print(add_data)
            updated_data=collection.insert_one(add_data)
            resultdata= collection.find_one({'_id':updated_data.inserted_id})
            resultdata["_id"]=str(resultdata["_id"])
            resultdata["customerId"]=str(resultdata["customerId"])
            if not resultdata:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Sorry Operation Failed")
            return {"message":"success","data":resultdata}
    except Exception as e:
         raise e



# @router.put('/{address_id}')
# def update_delivery_address_status(
#     address_id: str,
#     token: HTTPAuthorizationCredentials = Depends(auth_scheme),
#     user=Depends(oauth2.verify_customer_access_token)
# ):
#     customer_id = user["customer_id"]
#     address_object_id = ObjectId(address_id)

    
#     address = collection.find_one({"_id": address_object_id, "customerId": ObjectId(customer_id)})
    
#     if not address:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery address not found")
#     # if ObjectId(user["customer_id"]) !=address["customerId"]:
#     #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    
#     collection.update_many(
#         {"customerId": ObjectId(customer_id), "status": True},
#         {"$set": {"status": False}}
#     )

#     collection.update_one(
#         {"_id": address_object_id, "customerId": ObjectId(customer_id)},
#         {"$set": {"status": True}}
#     )

  
#     updated_address = collection.find_one({"_id": address_object_id})

#     if not updated_address:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update the address status")

#     updated_address["_id"] = str(updated_address["_id"])
#     updated_address["customerId"] = str(updated_address["customerId"])

#     return {"message": "Set to default", "data": updated_address}





@router.get('/all')
def get_all_delivery_addresses(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    user=Depends(oauth2.verify_customer_access_token)
):
    try:
        customer_id = user["customer_id"]

    
        addresses = list(collection.find({"customerId": ObjectId(customer_id)}))
        print(addresses)
        
        for address in addresses:
            address["_id"] = str(address["_id"])
            address["customerId"] = str(address["customerId"])

        return  addresses
    except Exception as e:
         raise e





@router.delete('/{address_id}')
def delete_address(address_id:str,user=Depends(oauth2.verify_customer_access_token),token:HTTPAuthorizationCredentials=Depends(auth_scheme)):
    try:
        address = collection.find_one({"_id": ObjectId(address_id)})

        if not address:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
        
        
        if ObjectId(user["customer_id"]) !=address["customerId"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
        

        collection.delete_one({"_id":ObjectId(address_id)})
        return "Address revomed"
    except Exception as e:
         raise e