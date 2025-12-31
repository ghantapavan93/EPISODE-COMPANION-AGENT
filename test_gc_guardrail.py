"""
Quick test for Python GC guardrail to verify it's working.
"""

import requests

API_URL = "http://localhost:8000/companion/query"

print("\n🧪 Testing Python GC Guardrail")
print("="*70)

payload = {
    "user_id": "test_user",
    "episode_id": "ai-research-daily-2025-11-20",
    "message": "Explain Python's garbage collector using today's episode only.",
    "mode": "auto"
}

try:
    response = requests.post(API_URL, json=payload, timeout=30)
    data = response.json()
    
    answer = data.get("answer", "")
    has_insufficient = "does not give enough detail to answer" in answer.lower()
    
    print(f"\nQuery: {payload['message']}")
    print(f"Status: {response.status_code}")
    
    if has_insufficient:
        print("✅ PASS: Correctly blocked with insufficient message")
        print(f"   Answer: {answer[:100]}...")
    else:
        print("❌ FAIL: Should have blocked but got answer:")
        print(f"   {answer[:200]}...")
        
except Exception as e:
    print(f"❌ Exception: {e}")

print("="*70)
