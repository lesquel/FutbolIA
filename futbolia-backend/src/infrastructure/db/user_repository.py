"""
User Repository
Handles user CRUD operations with MongoDB
"""

from datetime import UTC, datetime

import bcrypt
from bson import ObjectId

from src.domain.entities import User
from src.infrastructure.db.mongodb import COLLECTIONS, MongoDB


class UserRepository:
    """Repository for User operations"""

    @staticmethod
    def _get_collection():
        return MongoDB.get_collection(COLLECTIONS["users"])

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt directly"""
        # Truncate password to 72 bytes (bcrypt limit)
        password_bytes = password.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            password_bytes = plain_password.encode("utf-8")[:72]
            hashed_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False

    @classmethod
    async def create(cls, user: User, password: str) -> User:
        """Create a new user"""
        collection = cls._get_collection()

        user_doc = {
            "email": user.email,
            "username": user.username,
            "hashed_password": cls.hash_password(password),
            "is_active": user.is_active,
            "created_at": datetime.now(UTC),
            "language": user.language,
            "theme": user.theme,
        }

        result = await collection.insert_one(user_doc)
        user.id = str(result.inserted_id)
        return user

    @classmethod
    async def find_by_email(cls, email: str) -> User | None:
        """Find user by email"""
        collection = cls._get_collection()
        doc = await collection.find_one({"email": email})

        if doc:
            return User(
                id=str(doc["_id"]),
                email=doc["email"],
                username=doc["username"],
                hashed_password=doc["hashed_password"],
                is_active=doc.get("is_active", True),
                created_at=doc.get("created_at", datetime.now(UTC)),
                language=doc.get("language", "es"),
                theme=doc.get("theme", "dark"),
            )
        return None

    @classmethod
    async def find_by_id(cls, user_id: str) -> User | None:
        """Find user by ID"""
        collection = cls._get_collection()
        doc = await collection.find_one({"_id": ObjectId(user_id)})

        if doc:
            return User(
                id=str(doc["_id"]),
                email=doc["email"],
                username=doc["username"],
                hashed_password=doc["hashed_password"],
                is_active=doc.get("is_active", True),
                created_at=doc.get("created_at", datetime.now(UTC)),
                language=doc.get("language", "es"),
                theme=doc.get("theme", "dark"),
            )
        return None

    @classmethod
    async def update_preferences(
        cls, user_id: str, language: str = None, theme: str = None
    ) -> bool:
        """Update user preferences"""
        collection = cls._get_collection()

        update_data = {}
        if language:
            update_data["language"] = language
        if theme:
            update_data["theme"] = theme

        if update_data:
            result = await collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
            return result.modified_count > 0
        return False

    @classmethod
    async def authenticate(cls, email: str, password: str) -> User | None:
        """Authenticate user with email and password"""
        user = await cls.find_by_email(email)
        if user and cls.verify_password(password, user.hashed_password):
            return user
        return None
