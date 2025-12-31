import unittest
import sys
import os
sys.path.append(os.getcwd())
from agent import EpisodeCompanionAgent, INSUFFICIENT_MSG
from orchestrator import Orchestrator


class TestRAGQualityFixes(unittest.TestCase):
    """Tests for RAG quality improvements: grounding, routing, and variation."""
    
    def setUp(self):
        """Initialize agent and orchestrator before each test."""
        self.agent = EpisodeCompanionAgent()
        self.orchestrator = Orchestrator()
        self.episode_id = "ai-research-daily-2025-11-18"
    
    # ============ Grounding Tests ============
    
    def test_jvm_question_returns_insufficient(self):
        """
        Test that agent doesn't fabricate JVM answer with fake citations.
        This is the critical grounding leak fix.
        """
        resp = self.agent.get_answer(
            episode_id=self.episode_id,
            mode="plain_english",
            query="Explain the Java Virtual Machine based on this episode.",
            user_id="test_user",
            conversation_history="",
            debug=False,
        )
        
        # Should return insufficient message (JVM not in episode)
        self.assertEqual(resp["answer"], INSUFFICIENT_MSG)
        
        # Should have grounding_failed flag
        self.assertTrue(resp["metadata"]["quality_checks"].get("grounding_failed", False))
    
    def test_generic_computer_science_blocked(self):
        """Test that other generic CS questions also get blocked."""
        resp = self.agent.get_answer(
            episode_id=self.episode_id,
            mode="engineer_angle",
            query="How does garbage collection work in Python?",
            user_id="test_user",
            conversation_history="",
            debug=False,
        )
        
        # Should return insufficient (Python GC not in AI research episode)
        self.assertIn(INSUFFICIENT_MSG, resp["answer"])
    
    # ============ Routing Tests ============
    
    def test_within_episode_comparison_uses_rag(self):
        """
        Test that within-episode comparisons don't get mis-routed to timeline.
        Critical bug: 'compare to other paper in this episode' was going to timeline.
        """
        query = "Compare Back to Basics to the other big paper in this episode"
        
        # Should NOT be detected as timeline query
        is_timeline = self.orchestrator._is_timeline_query(query)
        self.assertFalse(is_timeline, "Within-episode comparison shouldn't route to timeline")
    
    def test_explicit_multi_episode_uses_timeline(self):
        """Test that explicit multi-episode queries DO route to timeline."""
        queries = [
            "Compare today's episode to yesterday",
            "What changed this week?",
            "Show me trends across the last 3 days"
        ]
        
        for query in queries:
            is_timeline = self.orchestrator._is_timeline_query(query)
            self.assertTrue(is_timeline, f"'{query}' should route to timeline")
    
    def test_generic_compare_stays_in_rag(self):
        """Test that generic 'compare' without episode context stays in RAG."""
        queries = [
            "Compare these two approaches",
            "How does this compare to traditional methods?",
            "Compare the results"
        ]
        
        for query in queries:
            is_timeline = self.orchestrator._is_timeline_query(query)
            self.assertFalse(is_timeline, f"'{query}' shouldn't route to timeline")
    
    # ============ Variation Tests ============
    # Note: Harder to test automatically, but we can verify the wiring
    
    def test_founder_mode_uses_specific_sections(self):
        """
        Test that founder mode applies question-specific sections.
        We can't easily verify output variation in unit test, but we can verify the wiring.
        """
        from prompts import FOUNDER_SPECIFIC_SECTIONS
        
        # Verify sections are defined
        self.assertIn("mvp", FOUNDER_SPECIFIC_SECTIONS)
        self.assertIn("paid_product", FOUNDER_SPECIFIC_SECTIONS)
        self.assertIn("prototype", FOUNDER_SPECIFIC_SECTIONS)
        self.assertIn("month", FOUNDER_SPECIFIC_SECTIONS)
        
        # Verify each is different
        mvp_section = FOUNDER_SPECIFIC_SECTIONS["mvp"]
        paid_section = FOUNDER_SPECIFIC_SECTIONS["paid_product"]
        
        self.assertNotEqual(mvp_section, paid_section, "MVP and Paid sections should be different")
        self.assertIn("weekend", mvp_section.lower(), "MVP should mention weekend scope")
        self.assertIn("pricing", paid_section.lower(), "Paid should mention pricing")


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)
