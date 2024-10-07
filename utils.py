from passlib.context import CryptContext
import redis.asyncio as aioredis

pwd_context=CryptContext(schemes=['argon2'],deprecated="auto")






async def invalidate_all_cache():
    redis = aioredis.from_url("redis://localhost")  # Adjust the URL if needed
    try:
        await redis.flushdb()  # Clears all keys in the current database
        print("All Redis cache keys have been invalidated.")
    except Exception as e:
        print(f"Failed to invalidate cache keys: {e}")
    finally:
        await redis.close()  # Close the Redis connection

def hash(password:str):
    return pwd_context.hash(password)

def verify(plain_pass,hashed_pass):
    print(plain_pass,hashed_pass)
    return pwd_context.verify(plain_pass,hashed_pass)




