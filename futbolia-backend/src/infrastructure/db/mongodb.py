"""
MongoDB Database Client
Handles connection and operations with MongoDB using Motor (async)
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.core.config import settings


class MongoDB:
    """MongoDB async client wrapper"""

    _client: AsyncIOMotorClient | None = None
    _database: AsyncIOMotorDatabase | None = None

    @classmethod
    async def connect(cls) -> None:
        """Connect to MongoDB"""
        if cls._client is None:
            cls._client = AsyncIOMotorClient(settings.MONGODB_URL)
            cls._database = cls._client[settings.MONGODB_DB_NAME]
            print(f"✅ Connected to MongoDB: {settings.MONGODB_DB_NAME}")

    @classmethod
    async def disconnect(cls) -> None:
        """Disconnect from MongoDB"""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._database = None
            print("🔌 Disconnected from MongoDB")

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if cls._database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return cls._database

    @classmethod
    def get_collection(cls, name: str):
        """Get a collection by name"""
        return cls.get_database()[name]


# Convenience functions
async def get_db() -> AsyncIOMotorDatabase:
    """Dependency for FastAPI routes"""
    return MongoDB.get_database()


# Collection names
COLLECTIONS = {
    "users": "users",
    "predictions": "predictions",
    "matches": "matches",
}
