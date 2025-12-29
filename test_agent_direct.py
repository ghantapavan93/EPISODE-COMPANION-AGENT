import sys
import logging
logging.basicConfig(level=logging.DEBUG)

from agent import EpisodeCompanionAgent

# Test the agent directly
agent = EpisodeCompanionAgent()

print("Agent initialized successfully")
print("\nTesting query...")

try:
    result = agent.get_answer(
        episode_id="ai_daily_2025_11_18",
        mode="plain_english",
        query="What is this episode about?"
    )
    print("\n✅ SUCCESS!")
    print(f"Answer: {result['answer'][:200]}...")
    print(f"Metadata: {result['metadata']}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
