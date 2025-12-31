import asyncio
import logging
from agent import EpisodeCompanionAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_explain_like_12():
    agent = EpisodeCompanionAgent()
    
    # Test case: "explain this episode to me like I'm 12 years old"
    # This previously might have failed due to poor retrieval or structure mismatch
    query = "explain this episode to me like I'm 12 years old"
    episode_id = "ai-research-daily-2025-11-20"
    mode = "plain_english"
    
    print(f"Testing query: '{query}'")
    
    try:
        response = agent.get_answer(
            episode_id=episode_id,
            mode=mode,
            query=query,
            debug=True
        )
        
        print("\nResponse received:")
        print(f"Answer length: {len(response['answer'])}")
        print(f"Answer preview: {response['answer'][:200]}...")
        
        # Check if it returned the insufficient message
        if "does not give enough detail" in response['answer']:
            print("\nFAILED: Returned INSUFFICIENT_MSG")
        else:
            print("\nSUCCESS: Generated a valid answer")
            
        # Check structure validation in metadata
        checks = response['metadata'].get('quality_checks', {})
        print(f"\nQuality Checks: {checks}")
        
        if checks.get('structure_ok'):
            print("Structure Check: PASSED")
        else:
            print("Structure Check: FAILED (might be expected if model didn't follow strict format, but shouldn't block answer)")

    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    test_explain_like_12()
