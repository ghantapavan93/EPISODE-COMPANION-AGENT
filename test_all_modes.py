"""
Comprehensive test suite for the interactive mode fixes.
Tests multiple question types to ensure they all work properly.
"""
import logging
from agent import EpisodeCompanionAgent
from behavior import classify_question

logging.basicConfig(level=logging.WARNING)

# Test cases from the user's requirements
test_cases = [
    {
        "query": "explain this episode to me like I'm 12 years old",
        "mode": "plain_english",
        "expected_type": "why_how",
        "description": "Explain like I'm 12"
    },
    {
        "query": "what are the main papers?",
        "mode": "plain_english",
        "expected_type": "summary",
        "description": "Main papers query"
    },
    {
        "query": "how does Kandinsky 5.0 work?",
        "mode": "engineer_angle",
        "expected_type": "why_how",
        "description": "Technical how question"
    },
    {
        "query": "what can I build with this?",
        "mode": "founder_takeaway",
        "expected_type": "brainstorm",
        "description": "Founder product idea"
    },
    {
        "query": "give me a summary",
        "mode": "plain_english",
        "expected_type": "summary",
        "description": "Simple summary"
    }
]

episode_id = "ai-research-daily-2025-11-20"
agent = EpisodeCompanionAgent()

print("=" * 80)
print("COMPREHENSIVE INTERACTIVE MODE TEST")
print("=" * 80)
print()

results = []

for i, test in enumerate(test_cases, 1):
    print(f"Test {i}/{ len(test_cases)}: {test['description']}")
    print(f"Query: '{test['query']}'")
    print(f"Mode: {test['mode']}")
    
    # Classify
    question_type = classify_question(test['query'])
    print(f"Classified as: {question_type}")
    
    # Get answer
    try:
        response = agent.get_answer(
            episode_id=episode_id,
            mode=test['mode'],
            query=test['query'],
            debug=False
        )
        
        answer_len = len(response['answer'])
        
        # Check result
        if "does not give enough detail" in response['answer']:
            status = "FAIL - INSUFFICIENT_MSG"
            success = False
        else:
            status = "SUCCESS"
            success = True
            
        results.append({
            "test": test['description'],
            "success": success,
            "answer_len": answer_len
        })
        
        print(f"Status: {status}")
        print(f"Answer length: {answer_len}")
        
        # Show quality checks
        checks = response['metadata'].get('quality_checks', {})
        print(f"Quality checks: {checks}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        results.append({
            "test": test['description'],
            "success": False,
            "error": str(e)
        })
    
    print()
    print("-" * 80)
    print()

# Summary
print()
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print()

passed = sum(1 for r in results if r.get('success', False))
total = len(results)

print(f"Passed: {passed}/{total}")
print()

for r in results:
    status_icon = "✅" if r.get('success') else "❌"
    print(f"{status_icon} {r['test']}")
    if not r.get('success') and 'error' in r:
        print(f"   Error: {r['error']}")

print()
if passed == total:
    print("🎉 ALL TESTS PASSED!")
else:
    print(f"⚠️ {total - passed} tests failed")
