"""Test the refined radio host prompts with stricter enforcement."""
import logging
from agent import EpisodeCompanionAgent
from behavior import classify_question
import re

logging.basicConfig(level=logging.WARNING)

episode_id = "ai-research-daily-2025-11-20"
mode = "plain_english"
agent = EpisodeCompanionAgent()

tests = [
    ("Give me a 3-bullet TL;DR of this episode", "Should be EXACTLY 3 bullets, NO headings"),
    ("explain this episode to me like I'm 12 years old", "Should be 2-3 paragraphs, ONE analogy, NO headings"),
    ("Explain one of the core ideas using a real-world example", "Should pick ONE paper + story, NO headings"),
    ("If I only remember one thing from this episode, what should it be?", "Should be 1-3 sentences, start with hook"),
]

print("TESTING REFINED RADIO HOST PROMPTS")
print("=" * 80)

for query, expectation in tests:
    print(f"\nQuery: {query}")
    print(f"Expectation: {expectation}")
    print("-" * 80)
    
    qt = classify_question(query)
    print(f"Classified as: {qt}")
    
    response = agent.get_answer(episode_id=episode_id, mode=mode, query=query)
    text = re.sub(r'<[^>]+>', '', response['answer'])
    
    # Check for headings
    has_headings = any(heading in text for heading in ["TL;DR", "Key Ideas", "Why This Matters", "Explanation", "Analogy"])
    
    print(f"Word count: {len(text.split())}")
    print(f"Has unwanted headings: {'YES ⚠️' if has_headings else 'NO ✅'}")
    
    # Show preview
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    print(f"\nFirst 5 lines:")
    for i, line in enumerate(lines[:5], 1):
        print(f"  {i}. {line[:100]}")
    
    print("\n" + "=" * 80)

print("\n✅ Test complete. Check above for heading violations.")
