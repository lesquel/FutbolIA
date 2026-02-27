"""
GoalMind Configuration Module
Manages all environment variables and application settings
"""
import os
import secrets
from dataclasses import dataclass, field
from typing import List, Dict
from dotenv import load_dotenv

# Load .env file
load_dotenv()


# =============================================================================
# GLOBAL LEAGUES CONFIGURATION - 50+ LEAGUES WORLDWIDE
# =============================================================================

# Mapeo de ligas soportadas con sus códigos de API
SUPPORTED_LEAGUES: Dict[str, Dict[str, str]] = {
    # EUROPA - Top 5
    "PL": {"name": "Premier League", "country": "England", "football_data": "PL", "thesportsdb": "4328"},
    "PD": {"name": "La Liga", "country": "Spain", "football_data": "PD", "thesportsdb": "4335"},
    "SA": {"name": "Serie A", "country": "Italy", "football_data": "SA", "thesportsdb": "4332"},
    "BL1": {"name": "Bundesliga", "country": "Germany", "football_data": "BL1", "thesportsdb": "4331"},
    "FL1": {"name": "Ligue 1", "country": "France", "football_data": "FL1", "thesportsdb": "4334"},
    # EUROPA - Otras
    "PPL": {"name": "Primeira Liga", "country": "Portugal", "football_data": "PPL", "thesportsdb": "4344"},
    "DED": {"name": "Eredivisie", "country": "Netherlands", "football_data": "DED", "thesportsdb": "4337"},
    "ELC": {"name": "EFL Championship", "country": "England", "football_data": "ELC", "thesportsdb": "4329"},
    "BEL": {"name": "Jupiler Pro League", "country": "Belgium", "thesportsdb": "4355"},
    "TUR": {"name": "Süper Lig", "country": "Turkey", "thesportsdb": "4339"},
    "SCO": {"name": "Scottish Premiership", "country": "Scotland", "thesportsdb": "4330"},
    "GRE": {"name": "Super League Greece", "country": "Greece", "thesportsdb": "4356"},
    "AUT": {"name": "Austrian Bundesliga", "country": "Austria", "thesportsdb": "4357"},
    "SUI": {"name": "Swiss Super League", "country": "Switzerland", "thesportsdb": "4354"},
    "POL": {"name": "Ekstraklasa", "country": "Poland", "thesportsdb": "4360"},
    "DEN": {"name": "Danish Superliga", "country": "Denmark", "thesportsdb": "4352"},
    "NOR": {"name": "Eliteserien", "country": "Norway", "thesportsdb": "4358"},
    "SWE": {"name": "Allsvenskan", "country": "Sweden", "thesportsdb": "4359"},
    # SUDAMÉRICA
    "BSA": {"name": "Brasileirão Série A", "country": "Brazil", "football_data": "BSA", "thesportsdb": "4351"},
    "ARG": {"name": "Liga Profesional Argentina", "country": "Argentina", "thesportsdb": "4406"},
    "ECU": {"name": "Liga Pro Ecuador", "country": "Ecuador", "thesportsdb": "4407"},
    "COL": {"name": "Liga BetPlay Dimayor", "country": "Colombia", "thesportsdb": "4410"},
    "PER": {"name": "Liga 1 Perú", "country": "Peru", "thesportsdb": "4411"},
    "CHI": {"name": "Primera División Chile", "country": "Chile", "thesportsdb": "4409"},
    "URU": {"name": "Primera División Uruguay", "country": "Uruguay", "thesportsdb": "4412"},
    "PAR": {"name": "Primera División Paraguay", "country": "Paraguay", "thesportsdb": "4413"},
    # NORTEAMÉRICA
    "MLS": {"name": "Major League Soccer", "country": "USA", "thesportsdb": "4346"},
    "MX": {"name": "Liga MX", "country": "Mexico", "thesportsdb": "4350"},
    # ASIA
    "JPN": {"name": "J1 League", "country": "Japan", "thesportsdb": "4350"},
    "KOR": {"name": "K League 1", "country": "South Korea", "thesportsdb": "4378"},
    "CHN": {"name": "Chinese Super League", "country": "China", "thesportsdb": "4379"},
    "SAU": {"name": "Saudi Pro League", "country": "Saudi Arabia", "thesportsdb": "4380"},
    # OCEANÍA
    "AUS": {"name": "A-League", "country": "Australia", "thesportsdb": "4396"},
    # COMPETICIONES INTERNACIONALES
    "CL": {"name": "UEFA Champions League", "country": "Europe", "football_data": "CL", "thesportsdb": "4480"},
    "EL": {"name": "UEFA Europa League", "country": "Europe", "thesportsdb": "4481"},
    "WC": {"name": "FIFA World Cup", "country": "International", "football_data": "WC", "thesportsdb": "4429"},
    "EC": {"name": "UEFA Euro Championship", "country": "Europe", "football_data": "EC", "thesportsdb": "4424"},
    "CA": {"name": "Copa América", "country": "South America", "thesportsdb": "4477"},
    "COPA": {"name": "Copa Libertadores", "country": "South America", "thesportsdb": "4478"},
}

# Mapeo expandido para predicciones (nombre completo -> código)
LEAGUE_MAPPING_PREDICTIONS: Dict[str, str] = {
    # Europa Top 5
    "Premier League": "PL",
    "La Liga": "PD",
    "Serie A": "SA",
    "Bundesliga": "BL1",
    "Ligue 1": "FL1",
    # Europa Otras
    "Primeira Liga": "PPL",
    "Eredivisie": "DED",
    "EFL Championship": "ELC",
    "Jupiler Pro League": "BEL",
    "Süper Lig": "TUR",
    "Scottish Premiership": "SCO",
    "Super League Greece": "GRE",
    "Austrian Bundesliga": "AUT",
    "Swiss Super League": "SUI",
    "Ekstraklasa": "POL",
    "Danish Superliga": "DEN",
    "Eliteserien": "NOR",
    "Allsvenskan": "SWE",
    # Sudamérica
    "Brasileirão Série A": "BSA",
    "Brasileirao": "BSA",
    "Liga Profesional Argentina": "ARG",
    "Liga Argentina": "ARG",
    "Liga Pro Ecuador": "ECU",
    "Liga Pro": "ECU",
    "LigaPro": "ECU",
    "Liga BetPlay Dimayor": "COL",
    "Liga BetPlay": "COL",
    "Liga 1 Perú": "PER",
    "Liga 1 Peru": "PER",
    "Primera División Chile": "CHI",
    "Primera División Uruguay": "URU",
    "Primera División Paraguay": "PAR",
    # Norteamérica
    "Major League Soccer": "MLS",
    "MLS": "MLS",
    "Liga MX": "MX",
    # Asia
    "J1 League": "JPN",
    "J-League": "JPN",
    "K League 1": "KOR",
    "K-League": "KOR",
    "Chinese Super League": "CHN",
    "Saudi Pro League": "SAU",
    # Oceanía
    "A-League": "AUS",
    # Internacionales
    "UEFA Champions League": "CL",
    "Champions League": "CL",
    "UEFA Europa League": "EL",
    "Europa League": "EL",
    "FIFA World Cup": "WC",
    "World Cup": "WC",
    "UEFA Euro Championship": "EC",
    "Euro": "EC",
    "Copa América": "CA",
    "Copa America": "CA",
    "Copa Libertadores": "COPA",
    "Libertadores": "COPA",
}


@dataclass
class Settings:
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "GoalMind"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("ENVIRONMENT", "development") == "development"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DATABASE", "goalmind")
    
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
    # In development, a random key is generated if not set.
    # In production, JWT_SECRET_KEY env var MUST be set explicitly.
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "10080"))  # 7 days default
    
    # CORS
    CORS_ORIGINS: List[str] = field(default_factory=list)
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    def __post_init__(self):
        # Generate a random JWT secret for development if not provided
        if not self.JWT_SECRET_KEY:
            if self.is_production():
                raise ValueError(
                    "JWT_SECRET_KEY environment variable is REQUIRED in production. "
                    "Generate one with: openssl rand -hex 32"
                )
            self.JWT_SECRET_KEY = secrets.token_hex(32)

        # Parse CORS origins from environment
        cors_env = os.getenv("CORS_ORIGINS", "")
        if cors_env:
            self.CORS_ORIGINS = [origin.strip() for origin in cors_env.split(",")]
        elif self.is_production():
            self.CORS_ORIGINS = []  # Must be set explicitly in production
        else:
            self.CORS_ORIGINS = [
                "http://localhost:3000",
                "http://localhost:8081",
                "http://localhost:19006",
                "exp://localhost:8081",
                "http://127.0.0.1:8081",
                "*",  # Allow all origins in development
            ]
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == "production"
    
    def validate(self) -> List[str]:
        """Validate critical settings and return list of warnings"""
        warnings = []

        if self.is_production():
            if not self.DEEPSEEK_API_KEY:
                warnings.append("⚠️ DEEPSEEK_API_KEY not set - Dixie will use mock responses")
            if not self.CORS_ORIGINS:
                warnings.append("⚠️ CORS_ORIGINS not set - no origins will be allowed")
        else:
            if not self.DEEPSEEK_API_KEY:
                warnings.append("ℹ️ DEEPSEEK_API_KEY not set - Dixie will use mock responses")

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
