"""
FutbolIA - Dixie Statistics
Tracks prediction accuracy and generates stats
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from bson import ObjectId

from src.infrastructure.db.mongodb import MongoDB, COLLECTIONS


class DixieStats:
    """
    Track and calculate Dixie's prediction statistics
    
    Stats tracked:
    - Total predictions
    - Correct predictions (when actual result is known)
    - Accuracy percentage
    - Predictions by confidence level
    - Most predicted teams
    """
    
    @staticmethod
    def _get_collection():
        return MongoDB.get_collection(COLLECTIONS.get("predictions", "predictions"))
    
    @staticmethod
    def _get_stats_collection():
        return MongoDB.get_collection("dixie_stats")
    
    @classmethod
    async def record_prediction(
        cls,
        prediction_id: str,
        home_team: str,
        away_team: str,
        predicted_winner: str,
        confidence: float,
        user_id: Optional[str] = None
    ) -> None:
        """Record a new prediction for stats tracking"""
        collection = cls._get_stats_collection()
        
        await collection.insert_one({
            "prediction_id": prediction_id,
            "home_team": home_team,
            "away_team": away_team,
            "predicted_winner": predicted_winner,
            "confidence": confidence,
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "actual_result": None,  # To be updated when match ends
            "is_correct": None,
        })
    
    @classmethod
    async def update_result(
        cls,
        prediction_id: str,
        actual_winner: str
    ) -> bool:
        """
        Update prediction with actual result
        
        Call this when the real match result is known
        """
        collection = cls._get_stats_collection()
        
        # Find the prediction
        prediction = await collection.find_one({"prediction_id": prediction_id})
        if not prediction:
            return False
        
        # Determine if correct
        is_correct = prediction["predicted_winner"].lower() == actual_winner.lower()
        
        # Update
        await collection.update_one(
            {"prediction_id": prediction_id},
            {
                "$set": {
                    "actual_result": actual_winner,
                    "is_correct": is_correct,
                    "verified_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return is_correct
    
    @classmethod
    async def get_overall_stats(cls) -> Dict[str, Any]:
        """Get overall Dixie statistics"""
        collection = cls._get_stats_collection()
        
        # Total predictions
        total = await collection.count_documents({})
        
        # Verified predictions (with actual result)
        verified = await collection.count_documents({"actual_result": {"$ne": None}})
        
        # Correct predictions
        correct = await collection.count_documents({"is_correct": True})
        
        # Calculate accuracy
        accuracy = (correct / verified * 100) if verified > 0 else 0
        
        # Predictions by confidence level
        high_confidence = await collection.count_documents({"confidence": {"$gte": 0.7}})
        medium_confidence = await collection.count_documents({
            "confidence": {"$gte": 0.5, "$lt": 0.7}
        })
        low_confidence = await collection.count_documents({"confidence": {"$lt": 0.5}})
        
        # High confidence accuracy
        high_conf_correct = await collection.count_documents({
            "confidence": {"$gte": 0.7},
            "is_correct": True
        })
        high_conf_verified = await collection.count_documents({
            "confidence": {"$gte": 0.7},
            "actual_result": {"$ne": None}
        })
        high_conf_accuracy = (high_conf_correct / high_conf_verified * 100) if high_conf_verified > 0 else 0
        
        return {
            "total_predictions": total,
            "verified_predictions": verified,
            "correct_predictions": correct,
            "accuracy_percentage": round(accuracy, 1),
            "confidence_breakdown": {
                "high": {"count": high_confidence, "accuracy": round(high_conf_accuracy, 1)},
                "medium": {"count": medium_confidence},
                "low": {"count": low_confidence}
            },
            "unverified_predictions": total - verified
        }
    
    @classmethod
    async def get_team_stats(cls, team_name: str) -> Dict[str, Any]:
        """Get stats for predictions involving a specific team"""
        collection = cls._get_stats_collection()
        
        # Find predictions with this team
        query = {
            "$or": [
                {"home_team": {"$regex": team_name, "$options": "i"}},
                {"away_team": {"$regex": team_name, "$options": "i"}}
            ]
        }
        
        total = await collection.count_documents(query)
        
        # How often Dixie predicted this team to win
        predicted_wins = await collection.count_documents({
            **query,
            "predicted_winner": {"$regex": team_name, "$options": "i"}
        })
        
        # Actual correct predictions for this team
        correct = await collection.count_documents({
            **query,
            "is_correct": True
        })
        
        verified = await collection.count_documents({
            **query,
            "actual_result": {"$ne": None}
        })
        
        accuracy = (correct / verified * 100) if verified > 0 else 0
        
        return {
            "team": team_name,
            "total_predictions": total,
            "predicted_wins": predicted_wins,
            "verified": verified,
            "correct": correct,
            "accuracy": round(accuracy, 1)
        }
    
    @classmethod
    async def get_recent_predictions(
        cls,
        limit: int = 10,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent predictions"""
        collection = cls._get_stats_collection()
        
        query = {}
        if user_id:
            query["user_id"] = user_id
        
        cursor = collection.find(query).sort("created_at", -1).limit(limit)
        
        predictions = []
        async for doc in cursor:
            predictions.append({
                "id": str(doc.get("_id", "")),
                "home_team": doc["home_team"],
                "away_team": doc["away_team"],
                "predicted_winner": doc["predicted_winner"],
                "confidence": doc["confidence"],
                "actual_result": doc.get("actual_result"),
                "is_correct": doc.get("is_correct"),
                "created_at": doc["created_at"].isoformat() if doc.get("created_at") else None
            })
        
        return predictions
    
    @classmethod
    async def get_leaderboard(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get prediction accuracy leaderboard by user
        (for gamification)
        """
        collection = cls._get_stats_collection()
        
        pipeline = [
            {"$match": {"user_id": {"$ne": None}, "is_correct": {"$ne": None}}},
            {"$group": {
                "_id": "$user_id",
                "total": {"$sum": 1},
                "correct": {"$sum": {"$cond": ["$is_correct", 1, 0]}}
            }},
            {"$project": {
                "user_id": "$_id",
                "total": 1,
                "correct": 1,
                "accuracy": {
                    "$multiply": [
                        {"$divide": ["$correct", "$total"]},
                        100
                    ]
                }
            }},
            {"$sort": {"accuracy": -1, "total": -1}},
            {"$limit": limit}
        ]
        
        results = []
        async for doc in collection.aggregate(pipeline):
            results.append({
                "user_id": doc["user_id"],
                "total_predictions": doc["total"],
                "correct_predictions": doc["correct"],
                "accuracy": round(doc["accuracy"], 1)
            })
        
        return results
    
    @classmethod
    async def get_daily_stats(cls, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily prediction stats for the last N days"""
        collection = cls._get_stats_collection()
        
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {"$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                },
                "count": {"$sum": 1},
                "avg_confidence": {"$avg": "$confidence"}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        results = []
        async for doc in collection.aggregate(pipeline):
            results.append({
                "date": doc["_id"],
                "predictions": doc["count"],
                "avg_confidence": round(doc["avg_confidence"], 2)
            })
        
        return results
