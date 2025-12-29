"""
Comprehensive Unit Tests for Episode Companion Agent
Tests all functionality: backend, API endpoints, modes, and edge cases
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from main import app
from agent import EpisodeCompanionAgent
from ingest import ingest_episode


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def sample_episode_data():
    """Sample episode data for testing"""
    return {
        "episode_id": "test_episode_001",
        "text": """
        AI Research Daily - Test Episode
        
        Paper 1: Neural Network Optimization
        Authors: John Doe, Jane Smith
        This paper presents a novel approach to optimizing neural networks
        using gradient descent with momentum. The key innovation is adaptive
        learning rates that adjust based on the gradient history.
        
        Paper 2: Computer Vision Advancements  
        Authors: Alice Johnson
        A breakthrough in object detection using transformer architectures.
        The system achieves 95% accuracy on benchmark datasets.
        
        Paper 3: Natural Language Processing
        Authors: Bob Wilson
        Improvements in language models through better tokenization.
        """
    }


@pytest.fixture
def agent():
    """Episode companion agent instance"""
    return EpisodeCompanionAgent()


# ============================================================================
# Backend Unit Tests
# ============================================================================

class TestAgentInitialization:
    """Test agent initialization and setup"""
    
    def test_agent_creates_successfully(self, agent):
        """Test that agent initializes without errors"""
        assert agent is not None
        assert agent.llm is not None
        assert agent.vector_store is not None
    
    def test_agent_has_correct_model(self, agent):
        """Test that agent uses correct Gemini model"""
        assert agent.llm.model_name == "gemini-1.5-flash"


class TestQueryProcessing:
    """Test query processing logic"""
    
    def test_valid_modes(self):
        """Test all valid persona modes"""
        valid_modes = ['plain_english', 'founder_takeaway', 'engineer_angle']
        from prompts import PROMPT_TEMPLATES
        
        for mode in valid_modes:
            assert mode in PROMPT_TEMPLATES, f"Mode {mode} not found in templates"
    
    def test_invalid_mode_raises_error(self, agent):
        """Test that invalid mode raises ValueError"""
        with pytest.raises(ValueError, match="Invalid mode"):
            agent.get_answer(
                episode_id="test_episode_001",
                mode="invalid_mode",
                query="Test query"
            )
    
    def test_empty_query_handling(self):
        """Test that empty queries are handled properly"""
        # The API should validate this at the Pydantic level
        from pydantic import ValidationError
        from main import QueryRequest
        
        with pytest.raises(ValidationError):
            QueryRequest(query="")


# ============================================================================
# API Endpoint Tests
# ============================================================================

class TestHealthEndpoint:
    """Test /health endpoint"""
    
    def test_health_check_returns_ok(self, client):
        """Test health endpoint returns 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_check_structure(self, client):
        """Test health response has correct structure"""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert "agent_ready" in data
        assert "vector_store_ready" in data
        assert data["status"] == "ok"


class TestEpisodesEndpoint:
    """Test /episodes endpoint"""
    
    def test_list_episodes_returns_200(self, client):
        """Test episodes list endpoint"""
        response = client.get("/episodes")
        assert response.status_code == 200
    
    def test_list_episodes_returns_list(self, client):
        """Test episodes endpoint returns a list"""
        response = client.get("/episodes")
        data = response.json()
        assert isinstance(data, list)


class TestQueryEndpoint:
    """Test /episodes/{id}/query endpoint"""
    
    def test_query_with_plain_english_mode(self, client):
        """Test query with plain_english mode"""
        response = client.post(
            "/episodes/ai_daily_2025_11_18/query?mode=plain_english",
            json={"query": "What is this episode about?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "metadata" in data
        assert data["mode"] == "plain_english"
    
    def test_query_with_founder_mode(self, client):
        """Test query with founder_takeaway mode"""
        response = client.post(
            "/episodes/ai_daily_2025_11_18/query?mode=founder_takeaway",
            json={"query": "What are the business implications?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "founder_takeaway"
        assert "answer" in data
    
    def test_query_with_engineer_mode(self, client):
        """Test query with engineer_angle mode"""
        response = client.post(
            "/episodes/ai_daily_2025_11_18/query?mode=engineer_angle",
            json={"query": "What are the technical details?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "engineer_angle"
        assert "answer" in data
    
    def test_query_with_invalid_mode(self, client):
        """Test query with invalid mode returns 400"""
        response = client.post(
            "/episodes/ai_daily_2025_11_18/query?mode=invalid_mode",
            json={"query": "Test query"}
        )
        assert response.status_code == 400
    
    def test_query_with_missing_query_field(self, client):

        """Test query without query field returns 422"""
        response = client.post(
            "/episodes/ai_daily_2025_11_18/query?mode=plain_english",
            json={}
        )
        assert response.status_code == 422
    
    def test_query_with_too_short_query(self, client):
        """Test query with very short text (< 3 chars)"""
        response = client.post(
            "/episodes/ai_daily_2025_11_18/query?mode=plain_english",
            json={"query": "ab"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_query_with_long_query(self, client):
        """Test query with very long text (at max length)"""
        long_query = "a" * 500  # Max length from QueryRequest validator
        response = client.post(
            "/episodes/ai_daily_2025_11_18/query?mode=plain_english",
            json={"query": long_query}
        )
        # Should succeed or fail gracefully
        assert response.status_code in [200, 400, 422]


class TestRootEndpoint:
    """Test / (root) endpoint"""
    
    def test_root_returns_html(self, client):
        """Test root endpoint serves HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


# ============================================================================
# Integration Tests
# ============================================================================

class TestFullQueryFlow:
    """Test complete end-to-end query flow"""
    
    def test_plain_english_full_flow(self, client):
        """Test complete flow for plain English query"""
        # 1. Check health
        health = client.get("/health")
        assert health.status_code == 200
        
        # 2. Check episodes exist
        episodes = client.get("/episodes")
        assert len(episodes.json()) > 0
        
        # 3. Query episode
        query = client.post(
            "/episodes/ai_daily_2025_11_18/query?mode=plain_english",
            json={"query": "Summarize this episode"}
        )
        assert query.status_code == 200
        assert "answer" in query.json()
    
    def test_mode_switching_flow(self, client):
        """Test switching between different modes"""
        queries = [
            ("plain_english", "What is this about?"),
            ("founder_takeaway", "What's the business value?"),
            ("engineer_angle", "What's the technical approach?"),
        ]
        
        for mode, question in queries:
            response = client.post(
                f"/episodes/ai_daily_2025_11_18/query?mode={mode}",
                json={"query": question}
            )
            assert response.status_code == 200
            assert response.json()["mode"] == mode


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_special_characters_in_query(self, client):
        """Test query with special characters"""
        response = client.post(
            "/episodes/ai_daily_2025_11_18/query?mode=plain_english",
            json={"query": "What about AI & ML? (neural networks)"}
        )
        assert response.status_code == 200
    
    def test_unicode_in_query(self, client):
        """Test query with unicode characters"""
        response = client.post(
            "/episodes/ai_daily_2025_11_18/query?mode=plain_english",
            json={"query": "What is AI research? 机器学习"}
        )
        assert response.status_code == 200
    
    def test_nonexistent_episode(self, client):
        """Test querying non-existent episode"""
        response = client.post(
            "/episodes/nonexistent_episode/query?mode=plain_english",
            json={"query": "Test query"}
        )
        # Should either return empty results or 404
        assert response.status_code in [200, 404]


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Test performance and metadata"""
    
    def test_query_response_includes_latency(self, client):
        """Test that response includes latency metadata"""
        response = client.post(
            "/episodes/ai_daily_2025_11_18/query?mode=plain_english",
            json={"query": "Quick test"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "metadata" in data
        assert "latency_ms" in data["metadata"]
        assert isinstance(data["metadata"]["latency_ms"], (int, float))
    
    def test_query_response_includes_chunk_count(self, client):
        """Test that response includes chunks used"""
        response = client.post(
            "/episodes/ai_daily_2025_11_18/query?mode=plain_english",
            json={"query": "Test query"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "used_chunks" in data["metadata"]
        assert data["metadata"]["used_chunks"] > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
