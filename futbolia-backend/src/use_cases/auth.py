"""
Authentication Use Cases
Handles user registration, login, and JWT token management
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt

from src.core.config import settings, get_i18n_string
from src.domain.entities import User
from src.infrastructure.db.user_repository import UserRepository


class AuthUseCase:
    """Authentication use cases"""
    
    @staticmethod
    def create_access_token(user_id: str) -> str:
        """Create a JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @classmethod
    async def register(cls, email: str, username: str, password: str, language: str = "es") -> dict:
        """Register a new user"""
        # Check if user already exists
        existing = await UserRepository.find_by_email(email)
        if existing:
            return {
                "success": False,
                "error": "Email already registered" if language == "en" else "Email ya registrado",
            }
        
        # Create new user
        user = User(
            email=email,
            username=username,
            language=language,
            theme="dark",
        )
        
        created_user = await UserRepository.create(user, password)
        
        # Generate token
        token = cls.create_access_token(created_user.id)
        
        return {
            "success": True,
            "message": get_i18n_string("user_created", language),
            "data": {
                "user": created_user.to_dict(),
                "access_token": token,
                "token_type": "bearer",
            }
        }
    
    @classmethod
    async def login(cls, email: str, password: str, language: str = "es") -> dict:
        """Authenticate user and return token"""
        user = await UserRepository.authenticate(email, password)
        
        if not user:
            return {
                "success": False,
                "error": get_i18n_string("auth_invalid", language),
            }
        
        # Generate token
        token = cls.create_access_token(user.id)
        
        return {
            "success": True,
            "data": {
                "user": user.to_dict(),
                "access_token": token,
                "token_type": "bearer",
            }
        }
    
    @classmethod
    async def get_current_user(cls, token: str) -> Optional[User]:
        """Get current user from token"""
        user_id = cls.verify_token(token)
        if not user_id:
            return None
        
        return await UserRepository.find_by_id(user_id)
