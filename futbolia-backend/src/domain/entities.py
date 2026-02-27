"""
GoalMind Domain Entities
Core business objects that represent the football prediction domain
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class MatchStatus(StrEnum):
    """Match status enumeration"""

    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class PredictionOutcome(StrEnum):
    """Prediction outcome types"""

    HOME_WIN = "home_win"
    AWAY_WIN = "away_win"
    DRAW = "draw"


@dataclass
class User:
    """User entity for authentication"""

    id: str | None = None
    email: str = ""
    username: str = ""
    hashed_password: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    language: str = "es"  # Default language
    theme: str = "dark"  # Default theme

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "language": self.language,
            "theme": self.theme,
        }


@dataclass
class PlayerAttributes:
    """Player attributes from FIFA dataset (ChromaDB)"""

    player_id: str = ""
    name: str = ""
    team: str = ""
    position: str = ""
    overall_rating: int = 0
    pace: int = 0  # Velocidad
    shooting: int = 0  # Tiro
    passing: int = 0  # Pase
    dribbling: int = 0  # Regate
    defending: int = 0  # Defensa
    physical: int = 0  # Físico

    def to_dict(self) -> dict:
        return {
            "player_id": self.player_id,
            "name": self.name,
            "team": self.team,
            "position": self.position,
            "overall_rating": self.overall_rating,
            "pace": self.pace,
            "shooting": self.shooting,
            "passing": self.passing,
            "dribbling": self.dribbling,
            "defending": self.defending,
            "physical": self.physical,
        }

    def get_summary(self) -> str:
        """Get a summary string for the LLM prompt"""
        return (
            f"{self.name} ({self.position}) - "
            f"Overall: {self.overall_rating}, "
            f"Pace: {self.pace}, Shooting: {self.shooting}, "
            f"Passing: {self.passing}, Defending: {self.defending}"
        )


@dataclass
class Player:
    """Player entity with basic info"""

    id: str = ""
    name: str = ""
    position: str = ""
    number: int = 0
    photo_url: str = ""
    attributes: PlayerAttributes | None = None


@dataclass
class Team:
    """Team entity"""

    id: str = ""
    name: str = ""
    short_name: str = ""
    logo_url: str = ""
    country: str = ""
    league: str = ""
    manager: str = ""  # Current head coach / director técnico
    form: str = ""  # Recent form: "WWDLW"
    attack_rating: int = 0
    defense_rating: int = 0
    players: list[Player] = field(default_factory=list)
    has_players: bool = False  # Si tiene jugadores en ChromaDB
    player_count: int = 0  # Cantidad de jugadores

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
            "logo_url": self.logo_url,
            "country": self.country,
            "league": self.league,
            "manager": self.manager,
            "form": self.form,
            "attack_rating": self.attack_rating,
            "defense_rating": self.defense_rating,
            "has_players": self.has_players,
            "player_count": self.player_count,
        }


@dataclass
class Match:
    """Match entity representing a football game"""

    id: str = ""
    home_team: Team | None = None
    away_team: Team | None = None
    date: datetime = field(default_factory=lambda: datetime.now(UTC))
    venue: str = ""
    league: str = ""
    status: MatchStatus = MatchStatus.SCHEDULED
    home_score: int | None = None
    away_score: int | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "home_team": self.home_team.to_dict() if self.home_team else None,
            "away_team": self.away_team.to_dict() if self.away_team else None,
            "date": self.date.isoformat(),
            "venue": self.venue,
            "league": self.league,
            "status": self.status.value,
            "home_score": self.home_score,
            "away_score": self.away_score,
        }


@dataclass
class PredictionResult:
    """The AI-generated prediction result"""

    winner: str = ""  # Team name or "draw"
    predicted_score: str = ""  # e.g., "2-1"
    confidence: int = 0  # 0-100 percentage
    reasoning: str = ""  # Tactical analysis explanation
    key_factors: list[str] = field(default_factory=list)
    star_player_home: str = ""
    star_player_away: str = ""
    match_preview: str = ""  # Exciting opening line about the match
    tactical_insight: str = ""  # Specific tactical insight


@dataclass
class Prediction:
    """Complete prediction entity stored in database"""

    id: str | None = None
    user_id: str = ""
    match: Match | None = None
    result: PredictionResult | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_correct: bool | None = None  # Verified after match ends
    language: str = "es"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "match": self.match.to_dict() if self.match else None,
            "result": {
                "winner": self.result.winner,
                "predicted_score": self.result.predicted_score,
                "confidence": self.result.confidence,
                "reasoning": self.result.reasoning,
                "key_factors": self.result.key_factors,
                "star_player_home": self.result.star_player_home,
                "star_player_away": self.result.star_player_away,
                "match_preview": getattr(self.result, "match_preview", ""),
                "tactical_insight": getattr(self.result, "tactical_insight", ""),
            }
            if self.result
            else None,
            "created_at": self.created_at.isoformat(),
            "is_correct": self.is_correct,
            "language": self.language,
        }
