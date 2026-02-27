"""
GoalMind Backend - Configuration Tests
Tests for application settings and environment configuration
"""
import os
import pytest
from unittest.mock import patch


class TestSettings:
    """Test suite for application Settings"""

    def test_default_settings_development(self):
        """Settings should load with development defaults"""
        from src.core.config import Settings

        settings = Settings()
        assert settings.ENVIRONMENT == "development"
        assert settings.DEBUG is True
        assert settings.APP_NAME == "GoalMind"
        assert settings.PORT == 8000

    def test_jwt_secret_auto_generated_in_dev(self):
        """JWT secret should be auto-generated in development"""
        from src.core.config import Settings

        with patch.dict(os.environ, {"JWT_SECRET_KEY": ""}, clear=False):
            settings = Settings()
            assert settings.JWT_SECRET_KEY != ""
            assert len(settings.JWT_SECRET_KEY) == 64  # hex of 32 bytes

    def test_jwt_secret_required_in_production(self):
        """JWT secret must be set in production"""
        from src.core.config import Settings

        with patch.dict(
            os.environ,
            {"ENVIRONMENT": "production", "JWT_SECRET_KEY": ""},
            clear=False,
        ):
            with pytest.raises(ValueError, match="JWT_SECRET_KEY"):
                Settings()

    def test_cors_defaults_in_development(self):
        """CORS should have localhost defaults in development"""
        from src.core.config import Settings

        settings = Settings()
        assert "http://localhost:3000" in settings.CORS_ORIGINS
        assert "http://localhost:8081" in settings.CORS_ORIGINS

    def test_cors_from_env(self):
        """CORS should parse from environment variable"""
        from src.core.config import Settings

        with patch.dict(
            os.environ,
            {"CORS_ORIGINS": "https://example.com,https://api.example.com"},
            clear=False,
        ):
            settings = Settings()
            assert "https://example.com" in settings.CORS_ORIGINS
            assert "https://api.example.com" in settings.CORS_ORIGINS

    def test_validate_warns_missing_api_key(self):
        """Validate should warn about missing DEEPSEEK_API_KEY"""
        from src.core.config import Settings

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": ""}, clear=False):
            settings = Settings()
            warnings = settings.validate()
            assert any("DEEPSEEK_API_KEY" in w for w in warnings)


class TestEntities:
    """Test suite for domain entities"""

    def test_user_creation(self):
        """User entity should be created with defaults"""
        from src.domain.entities import User

        user = User(email="test@example.com", username="testuser")
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.language == "es"

    def test_user_to_dict(self):
        """User.to_dict should return proper dictionary"""
        from src.domain.entities import User

        user = User(id="123", email="test@example.com", username="testuser")
        d = user.to_dict()
        assert d["id"] == "123"
        assert d["email"] == "test@example.com"
        assert "hashed_password" not in d

    def test_match_creation(self):
        """Match entity should be created with defaults"""
        from src.domain.entities import Match, MatchStatus

        match = Match(id="m1", league="PL")
        assert match.id == "m1"
        assert match.status == MatchStatus.SCHEDULED

    def test_prediction_result(self):
        """PredictionResult should hold prediction data"""
        from src.domain.entities import PredictionResult

        result = PredictionResult(
            winner="Barcelona",
            predicted_score="2-1",
            confidence=75,
            reasoning="Strong home form",
        )
        assert result.confidence == 75
        assert result.winner == "Barcelona"
