"""
Team Repository
Handles dynamic team storage in MongoDB for user-added teams
"""
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId

from src.domain.entities import Team, PlayerAttributes
from src.infrastructure.db.mongodb import MongoDB, COLLECTIONS


class TeamRepository:
    """Repository for dynamic team operations"""
    
    @staticmethod
    def _get_collection():
        return MongoDB.get_collection(COLLECTIONS.get("teams", "teams"))
    
    @classmethod
    async def create(cls, team: Team, added_by: str = "system") -> Team:
        """Create a new team in the database"""
        collection = cls._get_collection()
        
        # Check if team already exists
        existing = await collection.find_one({
            "$or": [
                {"api_id": team.id},
                {"name": {"$regex": f"^{team.name}$", "$options": "i"}}
            ]
        })
        
        if existing:
            team.id = str(existing["_id"])
            return team
        
        team_doc = {
            "api_id": team.id,
            "name": team.name,
            "short_name": team.short_name,
            "logo_url": team.logo_url,
            "country": team.country or "",
            "league": team.league or "",
            "form": team.form or "DDDDD",
            "added_by": added_by,
            "created_at": datetime.now(timezone.utc),
            "has_players": False,
            "player_count": 0,
        }
        
        result = await collection.insert_one(team_doc)
        team.id = str(result.inserted_id)
        return team
    
    @classmethod
    async def find_by_name(cls, name: str) -> Optional[Team]:
        """Find team by name (case-insensitive partial match)"""
        collection = cls._get_collection()
        doc = await collection.find_one({
            "name": {"$regex": name, "$options": "i"}
        })
        
        if doc:
            return cls._doc_to_team(doc)
        return None
    
    @classmethod
    async def find_by_id(cls, team_id: str) -> Optional[Team]:
        """Find team by ID"""
        collection = cls._get_collection()
        
        try:
            doc = await collection.find_one({"_id": ObjectId(team_id)})
        except:
            doc = await collection.find_one({"api_id": team_id})
        
        if doc:
            return cls._doc_to_team(doc)
        return None
    
    @classmethod
    async def search(cls, query: str, limit: int = 20) -> List[Team]:
        """Search teams by name"""
        collection = cls._get_collection()
        
        cursor = collection.find({
            "name": {"$regex": query, "$options": "i"}
        }).limit(limit)
        
        teams = []
        async for doc in cursor:
            teams.append(cls._doc_to_team(doc))
        
        return teams
    
    @classmethod
    async def get_all(cls, limit: int = 100) -> List[Team]:
        """Get all teams"""
        collection = cls._get_collection()
        
        cursor = collection.find().sort("name", 1).limit(limit)
        
        teams = []
        async for doc in cursor:
            teams.append(cls._doc_to_team(doc))
        
        return teams
    
    @classmethod
    async def get_teams_with_players(cls) -> List[Team]:
        """Get teams that have players in the database"""
        collection = cls._get_collection()
        
        cursor = collection.find({"has_players": True}).sort("name", 1)
        
        teams = []
        async for doc in cursor:
            teams.append(cls._doc_to_team(doc))
        
        return teams
    
    @classmethod
    async def update_player_status(cls, team_name: str, player_count: int) -> bool:
        """Update the player count for a team"""
        collection = cls._get_collection()
        
        result = await collection.update_one(
            {"name": {"$regex": f"^{team_name}$", "$options": "i"}},
            {
                "$set": {
                    "has_players": player_count > 0,
                    "player_count": player_count
                }
            }
        )
        return result.modified_count > 0
    
    @classmethod
    async def bulk_create(cls, teams: List[Team], added_by: str = "system") -> int:
        """Create multiple teams at once"""
        collection = cls._get_collection()
        
        created = 0
        for team in teams:
            # Check if exists
            existing = await collection.find_one({
                "$or": [
                    {"api_id": team.id},
                    {"name": {"$regex": f"^{team.name}$", "$options": "i"}}
                ]
            })
            
            if not existing:
                await cls.create(team, added_by)
                created += 1
        
        return created
    
    @staticmethod
    def _doc_to_team(doc: dict) -> Team:
        """Convert MongoDB document to Team entity"""
        return Team(
            id=str(doc["_id"]),
            name=doc["name"],
            short_name=doc.get("short_name", ""),
            logo_url=doc.get("logo_url", ""),
            country=doc.get("country", ""),
            league=doc.get("league", ""),
            form=doc.get("form", "DDDDD"),
        )


# Add teams collection to COLLECTIONS
def register_teams_collection():
    """Register the teams collection"""
    if "teams" not in COLLECTIONS:
        COLLECTIONS["teams"] = "teams"

register_teams_collection()
