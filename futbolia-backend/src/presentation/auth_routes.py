"""
Authentication API Routes
Handles user registration, login, and profile management
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, EmailStr
from typing import Optional

from src.use_cases.auth import AuthUseCase
from src.infrastructure.db.user_repository import UserRepository


router = APIRouter(prefix="/auth", tags=["Authentication"])


# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    language: str = "es"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    language: str = "es"


class UpdatePreferencesRequest(BaseModel):
    language: Optional[str] = None
    theme: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Dependency to get current user
async def get_current_user(authorization: str = Header(None)):
    """Extract and verify JWT token from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    
    token = authorization.split(" ")[1]
    user = await AuthUseCase.get_current_user(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    return user


# Routes
@router.post("/register")
async def register(request: RegisterRequest):
    """Register a new user"""
    result = await AuthUseCase.register(
        email=request.email,
        username=request.username,
        password=request.password,
        language=request.language,
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/login")
async def login(request: LoginRequest):
    """Login and get access token"""
    result = await AuthUseCase.login(
        email=request.email,
        password=request.password,
        language=request.language,
    )
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return result


@router.get("/me")
async def get_profile(current_user = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "success": True,
        "data": {
            "user": current_user.to_dict()
        }
    }


@router.put("/preferences")
async def update_preferences(
    request: UpdatePreferencesRequest,
    current_user = Depends(get_current_user)
):
    """Update user preferences (language, theme)"""
    success = await UserRepository.update_preferences(
        user_id=current_user.id,
        language=request.language,
        theme=request.theme,
    )
    
    if success:
        # Fetch updated user
        updated_user = await UserRepository.find_by_id(current_user.id)
        return {
            "success": True,
            "data": {
                "user": updated_user.to_dict() if updated_user else current_user.to_dict()
            }
        }
    
    return {
        "success": True,
        "message": "No changes made"
    }
