"""
Test script for guardrails and episode-native flavor questions.
"""

import requests

API_URL = "http://localhost:8000/companion/query"

def test_guardrails():
    """Test that off-topic questions return insufficient context message."""
    print("\n" + "="*70)
    print("TESTING GUARDRAILS")
    print("="*70)
    
    test_cases = [
        {
            "query": "Explain the Java Virtual Machine based on this episode.",
            "should_block": True,
            "term": "JVM"
        },
        {
            "query": "Explain Python's garbage collector using today's episode only.",
            "should_block": True,
            "term": "Python GC"
        },
        {
            "query": "How do I implement SDXL from this episode?",
            "should_block": True,
            "term": "SDXL"
        },
        {
            "query": "What does GPT-4o do in this episode?",
            "should_block": True,
            "term": "GPT-4o"
        },
        {
            "query": "Tell me about reinforcement learning from this episode.",
            "should_block": False,
            "term": "RL (on-episode)"
        },
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test['query'][:60]}...")
        payload = {
            "user_id": "test_user",
            "episode_id": "ai-research-daily-2025-11-20",
            "message": test['query'],
            "mode": "auto"
        }
        
        try:
            response = requests.post(API_URL, json=payload, timeout=30)
            data = response.json()
            
            answer = data.get("answer", "")
            has_insufficient = "does not give enough detail to answer" in answer.lower()
            
            if test['should_block']:
                if has_insufficient:
                    print(f"✅ {test['term']}: Correctly blocked with insufficient message")
                else:
                    print(f"❌ {test['term']}: Should have blocked but got answer:")
                    print(f"   {answer[:150]}...")
            else:
                if has_insufficient:
                    print(f"❌ {test['term']}: Should NOT have blocked but got insufficient message")
                else:
                    print(f"✅ {test['term']}: Correctly answered (on-episode concept)")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")


def test_episode_native():
    """Test episode-native flavor questions for proper structure."""
    print("\n" + "="*70)
    print("TESTING EPISODE-NATIVE FLAVOR QUESTIONS")
    print("="*70)
    
    test_cases = [
        {
            "query": "What's the most 'builder-friendly' insight from this episode?",
            "expected_structure": ["TL;DR", "Key Ideas", "Why this matters"]
        },
        {
            "query": "If I'm only half paying attention, what should I definitely not miss?",
            "expected_structure": ["If you only catch 10%", "Don't miss"]
        },
        {
            "query": "Give me one crazy but plausible side-project idea inspired by this episode.",
            "expected_structure": ["side-project", "Why it's interesting", "First 3 steps"]
        },
        {
            "query": "Which part of this episode do you think will age the best, and which part might look silly in 2 years?",
            "expected_structure": ["Will age well", "Might look silly in 2 years"]
        },
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test['query'][:60]}...")
        payload = {
            "user_id": "test_user",
            "episode_id": "ai-research-daily-2025-11-20",
            "message": test['query'],
            "mode": "auto"
        }
        
        try:
            response = requests.post(API_URL, json=payload, timeout=30)
            data = response.json()
            
            answer = data.get("answer", "")
            
            # Check for expected structure elements
            found_elements = []
            missing_elements = []
            for element in test['expected_structure']:
                if element.lower() in answer.lower():
                    found_elements.append(element)
                else:
                    missing_elements.append(element)
            
            if len(found_elements) >= 2:  # At least 2 out of 3 structure elements
                print(f"✅ Status: {response.status_code}")
                print(f"   Found structure: {', '.join(found_elements)}")
                if missing_elements:
                    print(f"   Missing (optional): {', '.join(missing_elements)}")
            else:
                print(f"⚠️ Status: {response.status_code}")
                print(f"   Missing structure elements: {', '.join(missing_elements)}")
                print(f"   Answer preview: {answer[:200]}...")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")


if __name__ == "__main__":
    print("\n🧪 TESTING GUARDRAILS AND EPISODE-NATIVE QUESTIONS")
    test_guardrails()
    test_episode_native()
    print("\n" + "="*70)
    print("✅ Testing complete!")
    print("="*70)
