
import redis.asyncio as redis

from app.core.config import settings


# Create Redis client
redis_client = redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


async def connect_to_redis():
    """
    Verify Redis connectivity.
    """
    await redis_client.ping()
    print("Connected to Redis successfully")


async def close_redis_connection():
    """
    Close Redis client connection.
    """
    await redis_client.aclose()
    print("Redis connection closed")
