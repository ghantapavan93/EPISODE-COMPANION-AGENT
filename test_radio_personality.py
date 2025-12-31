"""
Test the new radio host personality improvements for Plain English mode.
Testing the specific queries mentioned in the requirements.
"""
import logging
from agent import EpisodeCompanionAgent
from behavior import classify_question

logging.basicConfig(level=logging.WARNING)

# Test cases for radio host personality
test_cases = [
    {
        "query": "Give me a 3-bullet TL;DR of this episode",
        "expected_type": "tldr",
        "what_to_check": "Should be EXACTLY 3 bullets, no headings, no extra sections",
    },
    {
        "query": "explain this episode to me like I'm 12 years old",
        "expected_type": "why_how",
        "what_to_check": "Should be 2-3 paragraphs, one analogy, simple words, ~180 words",
    },
    {
        "query": "Explain one of the core ideas using a real-world example",
        "expected_type": "general",
        "what_to_check": "Should pick ONE paper, one story, conversational, ~220 words",
    },
    {
        "query": "If I only remember one thing from this episode, what should it be?",
        "expected_type": "relevance",
        "what_to_check": "Should be very short, punchy, one-sentence hook + why it matters",
    },
    {
        "query": "give me a summary",
        "expected_type": "summary",
        "what_to_check": "Should be 3-5 paragraphs, conversational, radio host recapping, ~250 words",
    },
]

episode_id = "ai-research-daily-2025-11-20"
mode = "plain_english"
agent = EpisodeCompanionAgent()

print("=" * 80)
print("TESTING KOCHI RADIO HOST PERSONALITY")
print("=" * 80)
print()

for i, test in enumerate(test_cases, 1):
    print(f"Test {i}/{len(test_cases)}: {test['query']}")
    print("-" * 80)
    
    # Classify
    question_type = classify_question(test['query'])
    expected = test['expected_type']
    
    if question_type == expected:
        print(f"✅ Classification: {question_type} (expected: {expected})")
    else:
        print(f"⚠️  Classification: {question_type} (expected: {expected})")
    
    print(f"What to check: {test['what_to_check']}")
    print()
    
    # Get answer
    try:
        response = agent.get_answer(
            episode_id=episode_id,
            mode=mode,
            query=test['query'],
            debug=False
        )
        
        # Strip HTML for analysis
        import re
        text_only = re.sub(r'<[^>]+>', '', response['answer'])
        
        answer_len = len(text_only)
        word_count = len(text_only.split())
        
        print(f"Answer length: {answer_len} chars, ~{word_count} words")
        
        # Show preview
        preview_lines = text_only.strip().split('\n')[:5]
        print()
        print("Preview (first 5 lines):")
        for line in preview_lines:
            if line.strip():
                print(f"  {line.strip()[:100]}")
        
        # Check for specific issues
        if question_type == "tldr":
            # Count bullet points
            bullet_count = text_only.count('\n-') + text_only.count('\n•') + text_only.count('\n*')
            print(f"\nBullet count: {bullet_count} (should be exactly 3)")
            if "Key Ideas" in text_only or "Why This Matters" in text_only:
                print("⚠️  WARNING: Contains unwanted sections (Key Ideas, Why This Matters)")
        
        elif question_type == "why_how":
            if word_count > 200:
                print(f"⚠️  WARNING: Too long ({word_count} words, should be ~180)")
            if "Key Ideas" in text_only or "Why This Matters" in text_only:
                print("⚠️  WARNING: Contains unwanted headings")
        
        elif question_type == "relevance":
            if word_count > 80:
                print(f"⚠️  WARNING: Too long ({word_count} words, should be very short)")
            if "If you remember one thing" not in text_only and "If I remember one thing" not in text_only:
                print("⚠️  WARNING: Doesn't start with expected hook")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()
    print("=" * 80)
    print()

print("\nTEST COMPLETE")
print("Review the answers above to ensure they match the radio host personality requirements.")
