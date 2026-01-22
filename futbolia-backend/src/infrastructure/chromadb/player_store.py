"""
ChromaDB Vector Store
Stores and retrieves player attributes for RAG-based predictions
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Optional
import os

from src.core.config import settings
from src.domain.entities import PlayerAttributes


class PlayerVectorStore:
    """Vector store for player attributes using ChromaDB"""
    
    _client: Optional[chromadb.Client] = None
    _collection = None
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize ChromaDB client and collection"""
        # Ensure persist directory exists
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        
        # Create persistent client
        cls._client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        cls._collection = cls._client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"description": "FIFA Player Attributes for tactical analysis"}
        )
        
        print(f"✅ ChromaDB initialized: {settings.CHROMA_COLLECTION_NAME}")
        print(f"📊 Collection has {cls._collection.count()} players")
    
    @classmethod
    def add_player(cls, player: PlayerAttributes) -> None:
        """Add a player to the vector store"""
        if cls._collection is None:
            cls.initialize()
        
        # Create document text for embedding
        document = (
            f"Player: {player.name}, Team: {player.team}, Position: {player.position}. "
            f"Overall Rating: {player.overall_rating}. "
            f"Attributes - Pace: {player.pace}, Shooting: {player.shooting}, "
            f"Passing: {player.passing}, Dribbling: {player.dribbling}, "
            f"Defending: {player.defending}, Physical: {player.physical}."
        )
        
        # Add to collection
        cls._collection.add(
            ids=[player.player_id],
            documents=[document],
            metadatas=[player.to_dict()]
        )
    
    @classmethod
    def add_players_batch(cls, players: List[PlayerAttributes]) -> None:
        """Add multiple players to the vector store"""
        if cls._collection is None:
            cls.initialize()
        
        ids = []
        documents = []
        metadatas = []
        
        for player in players:
            ids.append(player.player_id)
            documents.append(
                f"Player: {player.name}, Team: {player.team}, Position: {player.position}. "
                f"Overall Rating: {player.overall_rating}. "
                f"Attributes - Pace: {player.pace}, Shooting: {player.shooting}, "
                f"Passing: {player.passing}, Dribbling: {player.dribbling}, "
                f"Defending: {player.defending}, Physical: {player.physical}."
            )
            metadatas.append(player.to_dict())
        
        cls._collection.add(ids=ids, documents=documents, metadatas=metadatas)
        print(f"✅ Added {len(players)} players to vector store")
    
    @classmethod
    def search_by_team(cls, team_name: str, limit: int = 11) -> List[PlayerAttributes]:
        """Search for players by team name - EXACT MATCH ONLY"""
        if cls._collection is None:
            cls.initialize()
        
        # First try exact match with where filter
        try:
            results = cls._collection.query(
                query_texts=[f"Team: {team_name}"],
                n_results=limit,
                where={"team": {"$eq": team_name}}
            )
            
            players = cls._results_to_players(results)
            
            # Only return if we found players for THIS team
            if players and all(p.team.lower() == team_name.lower() for p in players):
                print(f"✅ Found {len(players)} players for {team_name} in ChromaDB")
                return players
            
        except Exception as e:
            print(f"⚠️ ChromaDB query error: {e}")
        
        # No exact match found - return empty to trigger AI generation
        print(f"⚠️ No players found in ChromaDB for '{team_name}' - will use AI generation")
        return []
    
    @classmethod
    def search_by_name(cls, player_name: str, limit: int = 5) -> List[PlayerAttributes]:
        """Search for players by name (semantic search)"""
        if cls._collection is None:
            cls.initialize()
        
        results = cls._collection.query(
            query_texts=[f"Player: {player_name}"],
            n_results=limit
        )
        
        return cls._results_to_players(results)
    
    @classmethod
    def get_star_players(cls, team_name: str, top_n: int = 3) -> List[PlayerAttributes]:
        """Get top rated players from a team"""
        players = cls.search_by_team(team_name, limit=20)
        
        # Sort by overall rating and return top N
        sorted_players = sorted(players, key=lambda p: p.overall_rating, reverse=True)
        return sorted_players[:top_n]
    
    @classmethod
    def get_player_comparison(cls, team_a: str, team_b: str) -> dict:
        """Get player comparison between two teams for prediction"""
        stars_a = cls.get_star_players(team_a, top_n=3)
        stars_b = cls.get_star_players(team_b, top_n=3)
        
        # Calculate team averages
        def calc_averages(players: List[PlayerAttributes]) -> dict:
            if not players:
                return {"pace": 0, "shooting": 0, "passing": 0, "defending": 0, "overall": 0}
            
            return {
                "pace": sum(p.pace for p in players) // len(players),
                "shooting": sum(p.shooting for p in players) // len(players),
                "passing": sum(p.passing for p in players) // len(players),
                "defending": sum(p.defending for p in players) // len(players),
                "overall": sum(p.overall_rating for p in players) // len(players),
            }
        
        return {
            "team_a": {
                "name": team_a,
                "stars": [p.to_dict() for p in stars_a],
                "averages": calc_averages(stars_a),
            },
            "team_b": {
                "name": team_b,
                "stars": [p.to_dict() for p in stars_b],
                "averages": calc_averages(stars_b),
            }
        }
    
    @classmethod
    def count(cls) -> int:
        """Get total number of players in the store"""
        if cls._collection is None:
            cls.initialize()
        return cls._collection.count()
    
    @classmethod
    def clear_all(cls) -> None:
        """Clear all players from the vector store"""
        if cls._client is None:
            cls.initialize()
        
        # Delete and recreate collection
        try:
            cls._client.delete_collection(settings.CHROMA_COLLECTION_NAME)
            print(f"🗑️ Deleted collection: {settings.CHROMA_COLLECTION_NAME}")
        except Exception as e:
            print(f"⚠️ Error deleting collection: {e}")
        
        # Recreate collection
        cls._collection = cls._client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"description": "FIFA Player Attributes for tactical analysis"}
        )
        print(f"✅ Recreated collection: {settings.CHROMA_COLLECTION_NAME}")
    
    @classmethod
    def get_all_teams(cls) -> List[str]:
        """Get list of all unique teams in the store"""
        if cls._collection is None:
            cls.initialize()
        
        # Get all documents
        results = cls._collection.get(include=["metadatas"])
        
        teams = set()
        if results and results.get("metadatas"):
            for metadata in results["metadatas"]:
                if metadata.get("team"):
                    teams.add(metadata["team"])
        
        return sorted(list(teams))
    
    @staticmethod
    def _results_to_players(results: dict) -> List[PlayerAttributes]:
        """Convert ChromaDB results to PlayerAttributes list"""
        players = []
        
        if results and results.get("metadatas"):
            for metadata in results["metadatas"][0]:
                player = PlayerAttributes(
                    player_id=metadata.get("player_id", ""),
                    name=metadata.get("name", ""),
                    team=metadata.get("team", ""),
                    position=metadata.get("position", ""),
                    overall_rating=metadata.get("overall_rating", 0),
                    pace=metadata.get("pace", 0),
                    shooting=metadata.get("shooting", 0),
                    passing=metadata.get("passing", 0),
                    dribbling=metadata.get("dribbling", 0),
                    defending=metadata.get("defending", 0),
                    physical=metadata.get("physical", 0),
                )
                players.append(player)
        
        return players
