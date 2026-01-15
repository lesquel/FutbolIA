"""
League API Routes
Handles league standings and statistics
"""
from fastapi import APIRouter, Query
from typing import List, Optional

from src.core.logger import log_info, log_error
from src.core.cache import api_cache
from src.infrastructure.external_api.football_api import FootballAPIClient
from src.infrastructure.clustering.team_clustering import TeamClustering


router = APIRouter(prefix="/leagues", tags=["Leagues"])


# Mock standings data for Premier League 2025-2026
MOCK_STANDINGS = [
    {"position": 1, "team": {"id": 64, "name": "Liverpool", "shortName": "LIV", "crest": "https://crests.football-data.org/64.png"}, "playedGames": 20, "won": 14, "draw": 5, "lost": 1, "points": 47, "goalsFor": 48, "goalsAgainst": 18, "goalDifference": 30},
    {"position": 2, "team": {"id": 57, "name": "Arsenal", "shortName": "ARS", "crest": "https://crests.football-data.org/57.png"}, "playedGames": 20, "won": 12, "draw": 7, "lost": 1, "points": 43, "goalsFor": 41, "goalsAgainst": 18, "goalDifference": 23},
    {"position": 3, "team": {"id": 351, "name": "Nottingham Forest", "shortName": "NFO", "crest": "https://crests.football-data.org/351.png"}, "playedGames": 20, "won": 12, "draw": 4, "lost": 4, "points": 40, "goalsFor": 35, "goalsAgainst": 22, "goalDifference": 13},
    {"position": 4, "team": {"id": 61, "name": "Chelsea", "shortName": "CHE", "crest": "https://crests.football-data.org/61.png"}, "playedGames": 20, "won": 10, "draw": 7, "lost": 3, "points": 37, "goalsFor": 41, "goalsAgainst": 25, "goalDifference": 16},
    {"position": 5, "team": {"id": 67, "name": "Newcastle United", "shortName": "NEW", "crest": "https://crests.football-data.org/67.png"}, "playedGames": 20, "won": 10, "draw": 5, "lost": 5, "points": 35, "goalsFor": 35, "goalsAgainst": 24, "goalDifference": 11},
    {"position": 6, "team": {"id": 65, "name": "Manchester City", "shortName": "MCI", "crest": "https://crests.football-data.org/65.png"}, "playedGames": 20, "won": 10, "draw": 4, "lost": 6, "points": 34, "goalsFor": 38, "goalsAgainst": 28, "goalDifference": 10},
    {"position": 7, "team": {"id": 1044, "name": "AFC Bournemouth", "shortName": "BOU", "crest": "https://crests.football-data.org/1044.png"}, "playedGames": 20, "won": 9, "draw": 6, "lost": 5, "points": 33, "goalsFor": 33, "goalsAgainst": 25, "goalDifference": 8},
    {"position": 8, "team": {"id": 58, "name": "Aston Villa", "shortName": "AVL", "crest": "https://crests.football-data.org/58.png"}, "playedGames": 20, "won": 9, "draw": 5, "lost": 6, "points": 32, "goalsFor": 30, "goalsAgainst": 29, "goalDifference": 1},
    {"position": 9, "team": {"id": 63, "name": "Fulham", "shortName": "FUL", "crest": "https://crests.football-data.org/63.png"}, "playedGames": 20, "won": 8, "draw": 7, "lost": 5, "points": 31, "goalsFor": 32, "goalsAgainst": 27, "goalDifference": 5},
    {"position": 10, "team": {"id": 397, "name": "Brighton & Hove Albion", "shortName": "BHA", "crest": "https://crests.football-data.org/397.png"}, "playedGames": 20, "won": 7, "draw": 9, "lost": 4, "points": 30, "goalsFor": 32, "goalsAgainst": 29, "goalDifference": 3},
    {"position": 11, "team": {"id": 402, "name": "Brentford", "shortName": "BRE", "crest": "https://crests.football-data.org/402.png"}, "playedGames": 20, "won": 8, "draw": 5, "lost": 7, "points": 29, "goalsFor": 36, "goalsAgainst": 32, "goalDifference": 4},
    {"position": 12, "team": {"id": 66, "name": "Manchester United", "shortName": "MUN", "crest": "https://crests.football-data.org/66.png"}, "playedGames": 20, "won": 7, "draw": 5, "lost": 8, "points": 26, "goalsFor": 26, "goalsAgainst": 27, "goalDifference": -1},
    {"position": 13, "team": {"id": 73, "name": "Tottenham Hotspur", "shortName": "TOT", "crest": "https://crests.football-data.org/73.png"}, "playedGames": 20, "won": 7, "draw": 4, "lost": 9, "points": 25, "goalsFor": 43, "goalsAgainst": 35, "goalDifference": 8},
    {"position": 14, "team": {"id": 563, "name": "West Ham United", "shortName": "WHU", "crest": "https://crests.football-data.org/563.png"}, "playedGames": 20, "won": 6, "draw": 5, "lost": 9, "points": 23, "goalsFor": 27, "goalsAgainst": 36, "goalDifference": -9},
    {"position": 15, "team": {"id": 354, "name": "Crystal Palace", "shortName": "CRY", "crest": "https://crests.football-data.org/354.png"}, "playedGames": 20, "won": 4, "draw": 9, "lost": 7, "points": 21, "goalsFor": 21, "goalsAgainst": 27, "goalDifference": -6},
    {"position": 16, "team": {"id": 62, "name": "Everton", "shortName": "EVE", "crest": "https://crests.football-data.org/62.png"}, "playedGames": 20, "won": 4, "draw": 8, "lost": 8, "points": 20, "goalsFor": 17, "goalsAgainst": 26, "goalDifference": -9},
    {"position": 17, "team": {"id": 76, "name": "Wolverhampton Wanderers", "shortName": "WOL", "crest": "https://crests.football-data.org/76.png"}, "playedGames": 20, "won": 5, "draw": 5, "lost": 10, "points": 20, "goalsFor": 29, "goalsAgainst": 42, "goalDifference": -13},
    {"position": 18, "team": {"id": 338, "name": "Leicester City", "shortName": "LEI", "crest": "https://crests.football-data.org/338.png"}, "playedGames": 20, "won": 4, "draw": 6, "lost": 10, "points": 18, "goalsFor": 26, "goalsAgainst": 42, "goalDifference": -16},
    {"position": 19, "team": {"id": 349, "name": "Ipswich Town", "shortName": "IPS", "crest": "https://crests.football-data.org/349.png"}, "playedGames": 20, "won": 3, "draw": 8, "lost": 9, "points": 17, "goalsFor": 21, "goalsAgainst": 37, "goalDifference": -16},
    {"position": 20, "team": {"id": 340, "name": "Southampton", "shortName": "SOU", "crest": "https://crests.football-data.org/340.png"}, "playedGames": 20, "won": 1, "draw": 4, "lost": 15, "points": 7, "goalsFor": 13, "goalsAgainst": 42, "goalDifference": -29}
]


@router.get("/standings")
async def get_standings(
    league: str = Query(default="PL", description="League code (PL, PD, SA, BL1, FL1)")
):
    """
    📊 Get current league standings
    
    Returns the current table for the specified league.
    Uses Football-Data.org API with caching.
    
    League codes:
    - PL: Premier League (England)
    - PD: La Liga (Spain)
    - SA: Serie A (Italy)
    - BL1: Bundesliga (Germany)
    - FL1: Ligue 1 (France)
    """
    log_info("Standings request", league=league)
    
    # Check cache first (5 minutes TTL)
    cache_key = f"standings:{league}"
    cached = await api_cache.get(cache_key)
    if cached:
        log_info("Standings from cache", league=league)
        return {"standings": cached, "league": league, "cached": True}
    
    try:
        # Try to get from API
        standings = await FootballAPIClient.get_standings(league)
        
        if standings:
            # Transform to our format
            formatted = []
            for entry in standings:
                team_data = entry.get("team", {})
                formatted.append({
                    "position": entry.get("position", 0),
                    "team": {
                        "id": team_data.get("id"),
                        "name": team_data.get("name", "Unknown"),
                        "shortName": team_data.get("shortName", team_data.get("tla", "")),
                        "crest": team_data.get("crest", ""),
                    },
                    "playedGames": entry.get("playedGames", 0),
                    "won": entry.get("won", 0),
                    "draw": entry.get("draw", 0),
                    "lost": entry.get("lost", 0),
                    "points": entry.get("points", 0),
                    "goalsFor": entry.get("goalsFor", 0),
                    "goalsAgainst": entry.get("goalsAgainst", 0),
                    "goalDifference": entry.get("goalDifference", 0),
                })
            
            # Cache for 5 minutes
            await api_cache.set(cache_key, formatted, ttl=300)
            
            return {"standings": formatted, "league": league, "cached": False}
    except Exception as e:
        log_error("Error fetching standings", error=str(e), league=league)
    
    # Fallback to mock data
    log_info("Using mock standings", league=league)
    return {"standings": MOCK_STANDINGS, "league": league, "mock": True}


@router.get("/standings/premier-league")
async def get_premier_league_standings():
    """
    ⚽ Get Premier League 2025-2026 standings
    
    Shortcut endpoint for Premier League standings.
    """
    return await get_standings(league="PL")


@router.get("/clustering")
async def get_team_clustering(
    league: str = Query(default="PL", description="League code (PL, PD, SA, BL1, FL1)"),
    n_clusters: int = Query(default=4, ge=2, le=10, description="Number of clusters (2-10)"),
    method: str = Query(default="ward", description="Linkage method (ward, complete, average, single)")
):
    """
    🔬 Análisis de Clustering de Equipos
    
    Realiza clustering jerárquico de equipos basado en estadísticas de la tabla de posiciones.
    Utiliza técnicas de minería de datos para agrupar equipos con características similares.
    
    El clustering se basa en:
    - Puntos por partido jugado
    - Diferencia de goles por partido
    - Goles a favor/contra por partido
    - Tasas de victoria/empate/derrota
    
    Métodos de linkage disponibles:
    - ward: Minimiza la varianza dentro de los clusters (recomendado)
    - complete: Distancia máxima entre puntos de clusters
    - average: Distancia promedio entre puntos de clusters
    - single: Distancia mínima entre puntos de clusters
    
    Args:
        league: Código de liga (PL, PD, SA, BL1, FL1)
        n_clusters: Número de clusters deseados (2-10)
        method: Método de linkage jerárquico
        
    Returns:
        Resultados del clustering incluyendo:
        - Dendrograma para visualización
        - Asignación de clusters por equipo
        - Estadísticas descriptivas por cluster
        - Información sobre características de cada cluster
    """
    log_info("Clustering request", league=league, n_clusters=n_clusters, method=method)
    
    try:
        # Obtener tabla de posiciones
        standings_response = await get_standings(league=league)
        standings = standings_response.get("standings", [])
        
        if len(standings) < 2:
            log_error("Not enough teams for clustering", n_teams=len(standings))
            return {
                "success": False,
                "error": "Se necesitan al menos 2 equipos para realizar clustering",
                "n_teams": len(standings)
            }
        
        # Realizar clustering
        clustering_result = TeamClustering.perform_clustering(
            standings=standings,
            n_clusters=n_clusters,
            method=method
        )
        
        log_info("Clustering completed", 
                 league=league, 
                 n_clusters=n_clusters,
                 n_teams=clustering_result["n_teams"])
        
        return {
            "success": True,
            "data": {
                **clustering_result,
                "league": league,
            }
        }
        
    except ValueError as e:
        log_error("Clustering validation error", error=str(e), league=league)
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        log_error("Clustering error", error=str(e), league=league)
        return {
            "success": False,
            "error": f"Error al realizar clustering: {str(e)}"
        }


@router.get("/clustering/premier-league")
async def get_premier_league_clustering(
    n_clusters: int = Query(default=4, ge=2, le=10, description="Number of clusters (2-10)"),
    method: str = Query(default="ward", description="Linkage method")
):
    """
    🔬 Clustering de Premier League
    
    Shortcut endpoint para clustering de Premier League.
    """
    return await get_team_clustering(league="PL", n_clusters=n_clusters, method=method)

