"""
FutbolIA Configuration Module
Manages all environment variables and application settings
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "FutbolIA - Dixie"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "futbolia")
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chromadb")
    CHROMA_COLLECTION_NAME: str = "player_attributes"
    
    # DeepSeek (Dixie)
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # API-Football (RapidAPI)
    RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")
    RAPIDAPI_HOST: str = "api-football-v1.p.rapidapi.com"
    
    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "futbolia-super-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    
    # CORS
    CORS_ORIGINS: list = None
    
    def __post_init__(self):
        if self.CORS_ORIGINS is None:
            self.CORS_ORIGINS = [
                "http://localhost:3000",
                "http://localhost:8081",
                "http://localhost:19006",
                "exp://localhost:8081",
            ]


# Global settings instance
settings = Settings()


# i18n Strings for Backend Responses
I18N_STRINGS = {
    "es": {
        "prediction_generated": "Predicción generada exitosamente",
        "match_not_found": "Partido no encontrado",
        "auth_invalid": "Credenciales inválidas",
        "auth_required": "Autenticación requerida",
        "user_created": "Usuario creado exitosamente",
        "prediction_saved": "Predicción guardada",
        "error_generic": "Ha ocurrido un error",
        "welcome_dixie": "¡Hola! Soy Dixie, tu analista deportivo de élite 🏆",
    },
    "en": {
        "prediction_generated": "Prediction generated successfully",
        "match_not_found": "Match not found",
        "auth_invalid": "Invalid credentials",
        "auth_required": "Authentication required",
        "user_created": "User created successfully",
        "prediction_saved": "Prediction saved",
        "error_generic": "An error occurred",
        "welcome_dixie": "Hello! I'm Dixie, your elite sports analyst 🏆",
    }
}


def get_i18n_string(key: str, lang: str = "es") -> str:
    """Get internationalized string"""
    return I18N_STRINGS.get(lang, I18N_STRINGS["es"]).get(key, key)
