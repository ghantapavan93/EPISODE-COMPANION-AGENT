import sys
import os
sys.path.append(os.getcwd())
from agent import EpisodeCompanionAgent

agent = EpisodeCompanionAgent()
query = "Tell me about SDXL"
episode_id = "ai-research-daily-2025-11-18"

print(f"Running query: {query}")
response = agent.get_answer(
    episode_id=episode_id,
    mode="plain_english",
    query=query
)

print("Response received:")
print(response['answer'])
print("Metadata:")
print(response['metadata'])
