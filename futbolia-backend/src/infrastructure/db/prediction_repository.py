"""
Prediction Repository
Handles prediction CRUD operations with MongoDB
"""
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from src.domain.entities import Prediction, Match, PredictionResult, Team, MatchStatus
from src.infrastructure.db.mongodb import MongoDB, COLLECTIONS


class PredictionRepository:
    """Repository for Prediction operations"""
    
    @staticmethod
    def _get_collection():
        return MongoDB.get_collection(COLLECTIONS["predictions"])
    
    @classmethod
    async def save(cls, prediction: Prediction) -> Prediction:
        """Save a prediction to the database"""
        collection = cls._get_collection()
        
        doc = {
            "user_id": prediction.user_id,
            "match": prediction.match.to_dict() if prediction.match else None,
            "result": {
                "winner": prediction.result.winner,
                "predicted_score": prediction.result.predicted_score,
                "confidence": prediction.result.confidence,
                "reasoning": prediction.result.reasoning,
                "key_factors": prediction.result.key_factors,
                "star_player_home": prediction.result.star_player_home,
                "star_player_away": prediction.result.star_player_away,
            } if prediction.result else None,
            "created_at": datetime.utcnow(),
            "is_correct": prediction.is_correct,
            "language": prediction.language,
        }
        
        result = await collection.insert_one(doc)
        prediction.id = str(result.inserted_id)
        return prediction
    
    @classmethod
    async def find_by_user(cls, user_id: str, limit: int = 20) -> List[Prediction]:
        """Find all predictions for a user"""
        collection = cls._get_collection()
        
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        predictions = []
        
        async for doc in cursor:
            prediction = cls._doc_to_prediction(doc)
            predictions.append(prediction)
        
        return predictions
    
    @classmethod
    async def find_by_id(cls, prediction_id: str) -> Optional[Prediction]:
        """Find prediction by ID"""
        collection = cls._get_collection()
        doc = await collection.find_one({"_id": ObjectId(prediction_id)})
        
        if doc:
            return cls._doc_to_prediction(doc)
        return None
    
    @classmethod
    async def get_stats(cls, user_id: str) -> dict:
        """Get prediction statistics for a user"""
        collection = cls._get_collection()
        
        total = await collection.count_documents({"user_id": user_id})
        correct = await collection.count_documents({"user_id": user_id, "is_correct": True})
        
        accuracy = (correct / total * 100) if total > 0 else 0
        
        return {
            "total_predictions": total,
            "correct_predictions": correct,
            "accuracy": round(accuracy, 1),
        }
    
    @staticmethod
    def _doc_to_prediction(doc: dict) -> Prediction:
        """Convert MongoDB document to Prediction entity"""
        match_doc = doc.get("match", {})
        result_doc = doc.get("result", {})
        
        # Reconstruct Match
        match = None
        if match_doc:
            home_team = Team(**match_doc.get("home_team", {})) if match_doc.get("home_team") else None
            away_team = Team(**match_doc.get("away_team", {})) if match_doc.get("away_team") else None
            
            match = Match(
                id=match_doc.get("id", ""),
                home_team=home_team,
                away_team=away_team,
                date=datetime.fromisoformat(match_doc.get("date", datetime.utcnow().isoformat())),
                venue=match_doc.get("venue", ""),
                league=match_doc.get("league", ""),
                status=MatchStatus(match_doc.get("status", "scheduled")),
            )
        
        # Reconstruct PredictionResult
        result = None
        if result_doc:
            result = PredictionResult(
                winner=result_doc.get("winner", ""),
                predicted_score=result_doc.get("predicted_score", ""),
                confidence=result_doc.get("confidence", 0),
                reasoning=result_doc.get("reasoning", ""),
                key_factors=result_doc.get("key_factors", []),
                star_player_home=result_doc.get("star_player_home", ""),
                star_player_away=result_doc.get("star_player_away", ""),
            )
        
        return Prediction(
            id=str(doc["_id"]),
            user_id=doc.get("user_id", ""),
            match=match,
            result=result,
            created_at=doc.get("created_at", datetime.utcnow()),
            is_correct=doc.get("is_correct"),
            language=doc.get("language", "es"),
        )
