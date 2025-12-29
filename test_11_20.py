import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent import EpisodeCompanionAgent

EPISODE_ID = "ai-research-daily-2025-11-20"

@pytest.fixture(scope="module")
def agent():
    """Episode companion agent instance"""
    return EpisodeCompanionAgent()

class TestEpisode1120:
    """Specific tests for the 11/20 episode"""

    def test_plain_english_summary(self, agent):
        """Test plain English summary covers key topics"""
        query = "What is AI Research Daily 11/20 about in simple terms?"
        response = agent.get_answer(EPISODE_ID, "plain_english", query)
        answer = response["answer"].lower()
        
        # Check for key topics
        assert "kandinsky" in answer, "Answer should mention Kandinsky"
        assert "video" in answer or "vrbench" in answer, "Answer should mention video reasoning or VRBench"
        assert "visplay" in answer, "Answer should mention VISPLAY"

    def test_founder_takeaway(self, agent):
        """Test founder takeaway focuses on product/business"""
        query = "If I’m a founder, what should I care about from today’s episode?"
        response = agent.get_answer(EPISODE_ID, "founder_takeaway", query)
        answer = response["answer"].lower()
        
        # Check for business-oriented language
        keywords = ["product", "startup", "app", "business", "market", "opportunity"]
        assert any(k in answer for k in keywords), "Answer should contain business-oriented keywords"

    def test_engineer_angle(self, agent):
        """Test engineer angle focuses on implementation"""
        query = "What should I try implementing from Kandinsky 5.0 or VISPLAY?"
        response = agent.get_answer(EPISODE_ID, "engineer_angle", query)
        answer = response["answer"].lower()
        
        # Check for technical language
        keywords = ["implement", "architecture", "training", "pipeline", "code", "model", "fine-tuning"]
        assert any(k in answer for k in keywords), "Answer should contain technical keywords"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
