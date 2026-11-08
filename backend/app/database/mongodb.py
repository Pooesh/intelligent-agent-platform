
from pymongo import AsyncMongoClient

from app.core.config import settings


# Create MongoDB client
mongodb_client = AsyncMongoClient(settings.mongo_uri)

# Select application database
mongodb_database = mongodb_client[settings.mongo_db_name]


async def connect_to_mongodb():
    """
    Verify MongoDB connectivity.
    """
    await mongodb_client.admin.command("ping")
    print("Connected to MongoDB successfully")


async def close_mongodb_connection():
    """
    Close MongoDB client connection.
    """
    await mongodb_client.close()
    print("MongoDB connection closed")
