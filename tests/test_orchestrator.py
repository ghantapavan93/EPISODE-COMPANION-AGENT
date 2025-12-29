import pytest
from unittest.mock import MagicMock
from orchestrator import Orchestrator

@pytest.fixture
def orchestrator():
    # Mock the internal agents to avoid actual API calls
    orch = Orchestrator()
    orch.episode_agent = MagicMock()
    orch.chat_agent = MagicMock()
    orch.builder_agent = MagicMock()
    
    # Setup mock returns
    orch.episode_agent.get_answer.return_value = {"agent": "episode"}
    orch.chat_agent.get_answer.return_value = {"agent": "chat"}
    orch.builder_agent.get_answer.return_value = {"agent": "builder"}
    
    return orch

def test_route_to_builder(orchestrator):
    # Test explicit build intent
    response = orchestrator.route_request("user1", "I want to build an app based on this")
    assert orchestrator.builder_agent.get_answer.called
    assert response == {"agent": "builder"}

def test_route_to_chat_no_context(orchestrator):
    # Test general chat when no episode context exists
    response = orchestrator.route_request("user2", "What is AI?")
    assert orchestrator.chat_agent.get_answer.called
    assert response == {"agent": "chat"}

def test_route_to_episode_explicit_id(orchestrator):
    # Test routing when episode_id is provided
    response = orchestrator.route_request("user3", "What is the main idea?", episode_id="episode_123")
    
    # Check if episode agent was called with correct arguments
    # "idea" triggers founder_takeaway
    orchestrator.episode_agent.get_answer.assert_called_with("episode_123", "founder_takeaway", "What is the main idea?", user_id="user3")
    assert response == {"agent": "episode"}
    
    # Check if state was updated
    assert orchestrator.user_state["user3"]["last_episode_id"] == "episode_123"

def test_route_to_episode_implicit_context(orchestrator):
    # 1. Set context
    orchestrator.route_request("user4", "context setup", episode_id="episode_456")
    
    # 2. Follow-up query without episode_id
    response = orchestrator.route_request("user4", "How can I implement this?")
    
    # Should route to episode agent with "engineer_angle" mode
    orchestrator.episode_agent.get_answer.assert_called_with("episode_456", "engineer_angle", "How can I implement this?", user_id="user4")
    assert response == {"agent": "episode"}

def test_mode_classification(orchestrator):
    # Test mode classification logic
    assert orchestrator._classify_mode("What is the business value?") == "founder_takeaway"
    assert orchestrator._classify_mode("Show me the code") == "engineer_angle"
    assert orchestrator._classify_mode("Explain simply") == "plain_english"
