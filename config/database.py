


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import dotenv_values

env = dict(dotenv_values(".env"))

mongo_db_uri = env.get("MONGO_DB_URI")
print(mongo_db_uri)

uri = mongo_db_uri

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')

    print(f"Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


db = client.corporate_caters

async def get_database():
    yield db

















# import asyncio
# import logging
# from pymongo import MongoClient
# from pymongo.server_api import ServerApi
# from dotenv import dotenv_values
# import redis.asyncio as aioredis

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Load environment variables
# env = dict(dotenv_values(".env_admin"))
# mongo_db_uri = env.get("MONGO_DB_URI")
# redis_url = env.get("REDIS_URL")

# # Initialize MongoDB and Redis clients
# client = MongoClient(mongo_db_uri, server_api=ServerApi('1'))
# db = client.corporate_caters
# redis = aioredis.from_url("redis://localhost")


# # List of collections to monitor
# collections = ['restaurants', 'menus', 'offers']  # Add your collections here

# async def invalidate_redis_cache():
#     patterns = [
#         "restaurants:*", "top-five:*", "category:*", 
#         "search:*", "category_restaurant:*", "price:*", 
#         "categories:*", "restaurant-detail:*", "menu_detail:*"
#     ]
#     for pattern in patterns:
#         keys = await redis.keys(pattern)
#         if keys:
#             await redis.delete(*keys)
#             logger.info(f"Invalidated Redis keys for pattern: {pattern}")

# async def monitor_collection(collection_name):
#     logger.info(f"Starting to monitor changes in collection: {collection_name}")
#     collection = db[collection_name]
#     async with collection.watch() as stream:
#         async for change in stream:
#             logger.info(f"Change detected in {collection_name}: {change}")
#             await invalidate_redis_cache()

# async def main():
#     tasks = [monitor_collection(collection) for collection in collections]
#     await asyncio.gather(*tasks)

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except Exception as e:
#         logger.error(f"Error: {e}")