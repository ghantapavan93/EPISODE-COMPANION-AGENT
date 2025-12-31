"""Quick test to see if the radio host personality is working."""
import logging
from agent import EpisodeCompanionAgent
from behavior import classify_question
import re

logging.basicConfig(level=logging.WARNING)

episode_id = "ai-research-daily-2025-11-20"
mode = "plain_english"
agent = EpisodeCompanionAgent()

# Test 1: TL;DR
print("TEST 1: TL;DR Request")
print("=" * 60)
query = "Give me a 3-bullet TL;DR of this episode"
qt = classify_question(query)
print(f"Query: {query}")
print(f"Classified as: {qt}")

response = agent.get_answer(episode_id=episode_id, mode=mode, query=query)
text = re.sub(r'<[^>]+>', '', response['answer'])

print(f"\nAnswer ({len(text.split())} words):")
print(text[:400])
print("\n" + "=" * 60 + "\n")

# Test 2: ELI12
print("TEST 2: Explain Like I'm 12")
print("=" * 60)
query = "explain this episode to me like I'm 12 years old"
qt = classify_question(query)
print(f"Query: {query}")
print(f"Classified as: {qt}")

response = agent.get_answer(episode_id=episode_id, mode=mode, query=query)
text = re.sub(r'<[^>]+>', '', response['answer'])

print(f"\nAnswer ({len(text.split())} words):")
print(text[:400])
print("\n" + "=" * 60 + "\n")

# Test 3: One Thing
print("TEST 3: One Thing to Remember")
print("=" * 60)
query = "If I only remember one thing from this episode, what should it be?"
qt = classify_question(query)
print(f"Query: {query}")
print(f"Classified as: {qt}")

response = agent.get_answer(episode_id=episode_id, mode=mode, query=query)
text = re.sub(r'<[^>]+>', '', response['answer'])

print(f"\nAnswer ({len(text.split())} words):")
print(text[:400])
print("\n" + "=" * 60)

print("\n✅ All tests complete. Check if answers match radio host personality.")
