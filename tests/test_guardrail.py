import unittest
import sys
import os
sys.path.append(os.getcwd())
from agent import EpisodeCompanionAgent, INSUFFICIENT_MSG


class TestHallucinationGuardrail(unittest.TestCase):
    """Tests for the hallucination prevention guardrail."""
    
    def setUp(self):
        """Initialize agent before each test."""
        self.agent = EpisodeCompanionAgent()
        self.episode_id = "ai-research-daily-2025-11-18"
    
    def test_blocks_unknown_special_paper(self):
        """Test that the guardrail blocks queries about papers not in the episode."""
        resp = self.agent.get_answer(
            episode_id=self.episode_id,
            mode="engineer_angle",
            query="How do I implement SDXL from this episode?",
            user_id="test_user",
            conversation_history="",
            debug=False,
        )
        
        # Should return insufficient message
        self.assertIn(INSUFFICIENT_MSG, resp["answer"])
        
        # Check metadata
        self.assertFalse(resp["metadata"]["quality_checks"]["grounded"])
        self.assertEqual(resp["metadata"]["quality_checks"]["reason"], "sdxl not in episode papers")
    
    def test_allows_known_paper_in_episode(self):
        """Test that the guardrail does NOT block queries about papers that ARE in the episode."""
        resp = self.agent.get_answer(
            episode_id=self.episode_id,
            mode="engineer_angle",
            query="How does Kandinsky 5.0 work?",
            user_id="test_user",
            conversation_history="",
            debug=False,
        )
        
        # Should NOT return insufficient message (Kandinsky 5.0 is in episode 11/18)
        self.assertNotEqual(resp["answer"], INSUFFICIENT_MSG)
        
        # Should have actual content
        self.assertGreater(len(resp["answer"]), 100)
        
        # Should mention Kandinsky in the answer
        self.assertIn("kandinsky", resp["answer"].lower())
    
    def test_blocks_gpt4o_not_in_episode(self):
        """Test blocking another special paper (GPT-4o) not in this episode."""
        resp = self.agent.get_answer(
            episode_id=self.episode_id,
            mode="plain_english",
            query="What does GPT-4o do?",
            user_id="test_user",
            conversation_history="",
            debug=False,
        )
        
        # Should return insufficient message
        self.assertIn(INSUFFICIENT_MSG, resp["answer"])
        self.assertEqual(resp["metadata"]["quality_checks"]["reason"], "gpt-4o not in episode papers")
    
    def test_generic_question_not_blocked(self):
        """Test that the guardrail does NOT block normal, generic questions."""
        resp = self.agent.get_answer(
            episode_id=self.episode_id,
            mode="plain_english",
            query="What are the main ideas in this episode?",
            user_id="test_user",
            conversation_history="",
            debug=False,
        )
        
        # Should NOT return insufficient message
        self.assertNotEqual(resp["answer"], INSUFFICIENT_MSG)
        
        # Should have actual content
        self.assertGreater(len(resp["answer"]), 100)
        
        # Should not have guardrail flag
        self.assertFalse(resp["metadata"]["quality_checks"].get("hallucination_guardrail_triggered", False))


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)
