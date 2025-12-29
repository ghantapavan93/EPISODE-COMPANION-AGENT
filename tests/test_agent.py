import pytest
from unittest.mock import MagicMock, patch

def test_agent_initialization():
    """Test that agent initializes correctly"""
    with patch("agent.get_vector_store") as mock_get_vs, \
         patch("agent.ChatGoogleGenerativeAI") as mock_llm:
        
        mock_get_vs.return_value = MagicMock()
        mock_llm.return_value = MagicMock()
        
        from agent import EpisodeCompanionAgent
        agent = EpisodeCompanionAgent()
        
        assert agent.vector_store is not None
        assert agent.llm is not None
        mock_get_vs.assert_called_once()
        mock_llm.assert_called_once()

def test_get_answer_invalid_mode():
    """Test that invalid mode raises ValueError"""
    with patch("agent.get_vector_store") as mock_get_vs, \
         patch("agent.ChatGoogleGenerativeAI") as mock_llm:
        
        mock_get_vs.return_value = MagicMock()
        mock_llm.return_value = MagicMock()
        
        from agent import EpisodeCompanionAgent
        agent = EpisodeCompanionAgent()
        
        with pytest.raises(ValueError) as excinfo:
            agent.get_answer("test_ep", "super_mode", "query")
        assert "Invalid mode" in str(excinfo.value)

def test_prompt_templates_exist():
    """Test that all expected prompt templates are defined"""
    from prompts import PROMPT_TEMPLATES
    
    expected_modes = ["plain_english", "founder_takeaway", "engineer_angle"]
    
    for mode in expected_modes:
        assert mode in PROMPT_TEMPLATES, f"Missing prompt template for mode: {mode}"
        assert PROMPT_TEMPLATES[mode] is not None
