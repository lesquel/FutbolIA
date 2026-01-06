"""
FutbolIA Configuration Module
Manages all environment variables and application settings
"""
import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

# Load .env file
load_dotenv()


@dataclass
class Settings:
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "FutPredicIA - Dixie"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("ENVIRONMENT", "development") == "development"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DATABASE", "futbolia")
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMADB_PATH", "./data/chromadb")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMADB_COLLECTION", "player_attributes")
    
    # DeepSeek (Dixie)
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_TEMPERATURE: float = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))
    DEEPSEEK_MAX_TOKENS: int = int(os.getenv("DEEPSEEK_MAX_TOKENS", "2000"))
    
    # Football-Data.org API (GRATUITA)
    # Obtener en: https://www.football-data.org/client/register
    FOOTBALL_DATA_API_KEY: str = os.getenv("FOOTBALL_DATA_API_KEY", "")
    
    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "futbolia-super-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "10080"))  # 7 days default
    
    # CORS
    CORS_ORIGINS: List[str] = field(default_factory=list)
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    def __post_init__(self):
        # Parse CORS origins from environment
        cors_env = os.getenv("CORS_ORIGINS", "")
        if cors_env:
            self.CORS_ORIGINS = [origin.strip() for origin in cors_env.split(",")]
        else:
            self.CORS_ORIGINS = [
                "http://localhost:3000",
                "http://localhost:8081",
                "http://localhost:19006",
                "exp://localhost:8081",
                "http://127.0.0.1:8081",
                "http://192.168.1.101:8081",  # IP local común
                "*",  # Permite todas las conexiones en desarrollo
            ]
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == "production"
    
    def validate(self) -> List[str]:
        """Validate critical settings and return list of warnings"""
        warnings = []
        
        if self.is_production():
            if "change-in-production" in self.JWT_SECRET_KEY:
                warnings.append("⚠️ JWT_SECRET_KEY debe cambiarse en producción!")
            if not self.DEEPSEEK_API_KEY:
                warnings.append("⚠️ DEEPSEEK_API_KEY no configurada - Dixie usará respuestas mock")
        
        return warnings


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
