"""
FutbolIA Backend - Main Application
FastAPI server with Clean Architecture
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.infrastructure.db.mongodb import MongoDB
from src.infrastructure.chromadb.player_store import PlayerVectorStore
from src.infrastructure.chromadb.seed_data import seed_players
from src.infrastructure.llm.dixie import DixieAI
from src.presentation.auth_routes import router as auth_router
from src.presentation.prediction_routes import router as prediction_router
from src.presentation.team_routes import router as team_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting FutbolIA Backend...")
    print(f"   App: {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Connect to MongoDB
    await MongoDB.connect()
    
    # Initialize ChromaDB and seed data
    PlayerVectorStore.initialize()
    seed_players()
    
    # Initialize Dixie AI
    DixieAI.initialize()
    
    print("✅ All systems ready!")
    print(f"📡 API running at http://{settings.HOST}:{settings.PORT}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down FutbolIA Backend...")
    await MongoDB.disconnect()
    print("👋 Goodbye!")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    🏆 **FutbolIA - El Oráculo Deportivo**
    
    Una plataforma de predicciones de fútbol impulsada por IA que combina:
    - 📊 Estadísticas en vivo (API-Football)
    - 🧠 Análisis de atributos de jugadores (ChromaDB/FIFA)
    - 🤖 IA experta "Dixie" (DeepSeek)
    
    ---
    
    **Características:**
    - Predicciones de partidos con análisis táctico
    - Historial de predicciones por usuario
    - Comparación de equipos y jugadores
    - Soporte multiidioma (ES/EN)
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(prediction_router, prefix="/api/v1")
app.include_router(team_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "message": "🏆 ¡Bienvenido a FutbolIA! Tu oráculo deportivo con IA.",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "predictions": "/api/v1/predictions",
            "teams": "/api/v1/teams",
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
