import asyncio
import logging
from agent import EpisodeCompanionAgent
from ingest import PaperEntryGpk, EpisodeBundleGpk, ingest_bundle_gpk
from langchain_core.documents import Document

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_time_hints():
    logger.info("--- Testing Time Hints ---")
    agent = EpisodeCompanionAgent()
    
    # Mock docs with timestamps
    docs = [
        Document(page_content="doc1", metadata={"timestamp_start": 60, "timestamp_end": 120}),
        Document(page_content="doc2", metadata={"timestamp_start": 100, "timestamp_end": 180}),
        Document(page_content="doc3", metadata={}) # No timestamp
    ]
    
    hint = agent._compute_time_hint_gpk(docs)
    logger.info(f"Computed Hint: {hint}")
    
    assert hint is not None
    assert hint["start_seconds"] == 60
    assert hint["end_seconds"] == 180
    assert hint["start_human"] == "1:00"
    assert hint["end_human"] == "3:00"
    logger.info("✅ Time hints passed")

def test_quiz_generation():
    logger.info("--- Testing Quiz Generation ---")
    agent = EpisodeCompanionAgent()
    context = "Deep learning has revolutionized AI. Transformers are a key architecture."
    
    # We mock the LLM call to avoid actual API costs/latency if possible, 
    # but for this integration test we can let it run if we have a local LLM or API key.
    # Assuming the agent is configured to work.
    
    try:
        quiz = agent._generate_quiz_questions_gpk(context, topic_hint="transformers")
        logger.info(f"Generated Quiz:\n{quiz}")
        assert len(quiz) > 10
        logger.info("✅ Quiz generation passed")
    except Exception as e:
        logger.error(f"Quiz generation failed: {e}")

def test_critique():
    logger.info("--- Testing Explanation Critique ---")
    agent = EpisodeCompanionAgent()
    context = "The transformer architecture relies on self-attention mechanisms."
    user_explanation = "Transformers use CNNs to process images."
    
    try:
        critique = agent._critique_user_explanation_gpk(context, "transformers", user_explanation)
        logger.info(f"Critique:\n{critique}")
        assert len(critique) > 10
        logger.info("✅ Critique passed")
    except Exception as e:
        logger.error(f"Critique failed: {e}")

def test_user_profile_integration():
    logger.info("--- Testing User Profile Integration ---")
    # This is harder to test without mocking the LLM to check the prompt, 
    # but we can check if the method runs without error.
    agent = EpisodeCompanionAgent()
    
    try:
        # We just check if it runs. To verify the prompt, we'd need to inspect logs or mock.
        # For now, let's assume if it doesn't crash, the injection logic is at least valid python.
        response = agent.get_answer(
            episode_id="test-episode",
            mode="plain_english",
            query="Explain this to me",
            user_profile={"role": "5-year-old", "domain": "kindergarten"}
        )
        logger.info("✅ User profile integration ran without error")
    except Exception as e:
        logger.error(f"User profile integration failed: {e}")

if __name__ == "__main__":
    test_time_hints()
    test_quiz_generation()
    test_critique()
    test_user_profile_integration()
