
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from routes_rest import advertisement,offers,super_admin,reviews,cart,delivery_address,order_rest,customer,card_rest,admin_rest,restaurant_rest,menu_rest,category_rest,sub_admin_rest,default_category,socialmedia
from fastapi.middleware.cors import CORSMiddleware
# from routes_graphql import admin
# from config import database





@asynccontextmanager
async def lifespan(app:FastAPI):
    try:
        redis_connection = redis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis_connection)
        
        yield  # This marks the point where request handling can occur
        
        # await redis_connection.close()
        print("Connected to redis")
    except:
        print("Not connected to redis")
       




app = FastAPI(title="Alacater Admin Panel",lifespan=lifespan)







origin=['*']
app.add_middleware(   #runs before every rqst
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# app.include_router(admin.router,prefix='/graph')
app.include_router(admin_rest.router)
app.include_router(restaurant_rest.router)
app.include_router(offers.router)
app.include_router(advertisement.router)

app.include_router(menu_rest.router)
app.include_router(category_rest.router)
app.include_router(sub_admin_rest.router)
app.include_router(sub_admin_rest.router)
app.include_router(default_category.router)
app.include_router(socialmedia.router)
app.include_router(card_rest.router)
app.include_router(customer.router)
app.include_router(reviews.router)

app.include_router(order_rest.router)
app.include_router(delivery_address.router)
app.include_router(cart.router)

app.include_router(super_admin.router)

