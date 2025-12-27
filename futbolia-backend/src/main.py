"""
FutbolIA Backend - Main Application
FastAPI server with Clean Architecture
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.logger import log_info, log_error, get_logger
from src.core.rate_limit import RateLimitMiddleware
from src.infrastructure.db.mongodb import MongoDB
from src.infrastructure.chromadb.player_store import PlayerVectorStore
from src.infrastructure.chromadb.seed_data import seed_players
from src.infrastructure.llm.dixie import DixieAI
from src.presentation.auth_routes import router as auth_router
from src.presentation.prediction_routes import router as prediction_router
from src.presentation.team_routes import router as team_router
from src.presentation.stats_routes import router as stats_router

# Initialize logger
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    log_info("Starting FutbolIA Backend...", 
             app=settings.APP_NAME, 
             version=settings.APP_VERSION,
             environment=settings.ENVIRONMENT)
    
    # Connect to MongoDB
    await MongoDB.connect()
    log_info("MongoDB connected", database=settings.MONGODB_DB_NAME)
    
    # Initialize ChromaDB and seed data
    PlayerVectorStore.initialize()
    seed_players()
    log_info("ChromaDB initialized", players=PlayerVectorStore.count())
    
    # Initialize Dixie AI
    DixieAI.initialize()
    log_info("Dixie AI initialized")
    
    log_info("All systems ready!", 
             host=settings.HOST, 
             port=settings.PORT)
    
    yield
    
    # Shutdown
    log_info("Shutting down FutbolIA Backend...")
    await MongoDB.disconnect()
    log_info("Goodbye!")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    🏆 **FutPredicIA - El Oráculo Deportivo**
    
    Una plataforma de predicciones de fútbol impulsada por IA que combina:
    - 📊 Estadísticas en vivo (API-Football)
    - 🧠 Análisis de atributos de jugadores (ChromaDB/FIFA)
    - 🤖 IA experta "Dixie" (DeepSeek)
    
    ---
    
    **Características:**
    - Predicciones de partidos con análisis táctico
    - Historial de predicciones por usuario
    - Comparación de equipos y jugadores
    - Estadísticas de precisión de Dixie
    - Búsqueda inteligente de equipos (fuzzy search)
    - Rate limiting para protección de API
    - Soporte multiidioma (ES/EN)
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Rate Limiting Middleware (add before CORS)
app.add_middleware(
    RateLimitMiddleware,
    default_limit=settings.RATE_LIMIT_PER_MINUTE,
    window_seconds=60
)

# CORS Middleware
# Note: allow_credentials=True is incompatible with allow_origins=["*"]
# We handle this by checking if "*" is in the origins list
is_all_origins = "*" in settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=not is_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
API_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(prediction_router, prefix=API_PREFIX)
app.include_router(team_router, prefix=API_PREFIX)
app.include_router(stats_router, prefix=API_PREFIX)


# Root endpoint
@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "message": "🏆 ¡Bienvenido a FutPredicIA! Tu oráculo deportivo con IA.",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "predictions": "/api/v1/predictions",
            "teams": "/api/v1/teams",
            "stats": "/api/v1/stats",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "vectorstore": f"{PlayerVectorStore.count()} players",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
