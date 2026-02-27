"""
GoalMind Backend - API Integration Tests
Tests for FastAPI endpoints
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
async def client():
    """Create test HTTP client"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestRootEndpoints:
    """Test root-level endpoints"""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Root endpoint should return app info"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "GoalMind" in data["app"]

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Health check should return healthy status"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_api_health_check(self, client):
        """API health check should return healthy status"""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_docs_endpoint(self, client):
        """OpenAPI docs should be accessible"""
        response = await client.get("/docs")
        assert response.status_code == 200
