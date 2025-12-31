import unittest
from agent import EpisodeCompanionAgent

class TestEpisodeCompanionSmoke(unittest.TestCase):
    """
    Smoke tests to verify that the agent enforces the correct structure
    for different persona modes.
    """
    
    def setUp(self):
        # Initialize agent (mocking backend to avoid real init overhead if possible, 
        # but here we just need the helper methods so standard init is fine 
        # if it doesn't do heavy lifting in __init__)
        # The agent __init__ does get_vector_store and get_llm_client. 
        # If those fail without env vars, this might be an issue.
        # Assuming environment is set up since uvicorn is running.
        try:
            self.agent = EpisodeCompanionAgent()
        except Exception:
            # Fallback for CI/headless where init might fail
            # We only need _check_structure so we can mock the instance
            from unittest.mock import MagicMock
            self.agent = MagicMock()
            # Restore the method we want to test
            self.agent._check_structure = EpisodeCompanionAgent._check_structure.__get__(self.agent, EpisodeCompanionAgent)

    def test_plain_english_structure(self):
        """Assert that plain_english requires tl;dr, Key Ideas, Why this matters."""
        valid_response = """
        Here is the tl;dr: It's great.
        
        Key Ideas:
        - AI is fast
        
        Why this matters:
        - It changes everything
        """
        self.assertTrue(
            self.agent._check_structure("plain_english", valid_response),
            "Should accept valid plain_english structure"
        )
        
        invalid_response = "Just some text without sections."
        self.assertFalse(
            self.agent._check_structure("plain_english", invalid_response),
            "Should reject missing sections"
        )

    def test_founder_mode_sections(self):
        """Assert that founder_takeaway requires Big Idea, Product Directions, Risks."""
        valid_response = """
        Big Idea: A startup for cats.
        
        Product Directions:
        - Cat app
        
        Risks & Unknowns:
        - Dogs
        """
        self.assertTrue(
            self.agent._check_structure("founder_takeaway", valid_response),
            "Should accept valid founder_takeaway structure"
        )

    def test_engineer_mode_sections(self):
        """Assert that engineer_angle requires Core Principle, Architecture, etc."""
        valid_response = """
        Core Principle: Gradient Descent.
        
        Architecture:
        - Transformer
        
        Training Setup:
        - 8x H100
        
        Inference Pipeline:
        - vLLM
        
        Trade-offs:
        - High cost
        """
        self.assertTrue(
            self.agent._check_structure("engineer_angle", valid_response),
            "Should accept valid engineer_angle structure"
        )

if __name__ == "__main__":
    unittest.main()
