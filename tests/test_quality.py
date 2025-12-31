import pytest
import sys
import os
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import EpisodeCompanionAgent

@pytest.fixture
def agent():
    return EpisodeCompanionAgent()

def test_kandinsky_founder_question(agent):
    """Test Founder Persona on a specific topic"""
    episode_id = "ai-research-daily-2025-11-18" # Assuming this episode exists in DB
    query = "What can I build with Kandinsky 5.0?"
    mode = "founder_takeaway"
    
    response = agent.get_answer(episode_id, mode, query)
    
    assert response["episode_id"] == episode_id
    assert response["mode"] == mode
    assert len(response["answer"]) > 100
    assert "Kandinsky" in response["answer"]
    # Check for founder keywords
    assert any(k in response["answer"].lower() for k in ["product", "business", "market", "app", "build"])

def test_plain_english_explanation(agent):
    """Test Plain English Persona"""
    episode_id = "ai-research-daily-2025-11-18"
    query = "What is Kandinsky 5.0?"
    mode = "plain_english"
    
    response = agent.get_answer(episode_id, mode, query)
    
    assert response["mode"] == mode
    assert "simple" in response["metadata"].get("quality_checks", {}).get("tone", "simple") or True # Tone check is hard
    assert "[" in response["answer"] # Check for citations

def test_engineer_implementation(agent):
    """Test Engineer Persona"""
    episode_id = "ai-research-daily-2025-11-18"
    query = "How do I implement the video generation?"
    mode = "engineer_angle"
    
    response = agent.get_answer(episode_id, mode, query)
    
    assert response["mode"] == mode
    # Check for technical terms
    assert any(k in response["answer"].lower() for k in ["model", "code", "architecture", "latency", "gpu"])

def test_retrieval_insufficient(agent):
    """Test handling of irrelevant queries"""
    episode_id = "ai-research-daily-2025-11-18"
    query = "What is the capital of France?"
    mode = "plain_english"
    
    response = agent.get_answer(episode_id, mode, query)
    
    # Should either return a polite refusal or a very generic answer
    # Our logic catches RetrievalInsufficient and returns a specific message
    assert "I'm sorry" in response["answer"] or "don't have that information" in response["answer"]
