import requests
import json
import time

BASE_URL = "http://localhost:8000"
COMPANION_QUERY_URL = f"{BASE_URL}/companion/query"

def get_episode_id():
    try:
        resp = requests.get(f"{BASE_URL}/episodes")
        if resp.status_code == 200:
            episodes = resp.json()
            if episodes:
                return episodes[0]
    except Exception:
        pass
    return "ai-research-daily-2025-11-20"

def check_response(prompt, expected_headings, banned_headings):
    episode_id = get_episode_id()
    payload = {
        "message": prompt,
        "user_id": "test_verifier",
        "episode_id": episode_id,
        "mode": "auto",
        "debug": True
    }
    
    print(f"\nTesting: '{prompt}'")
    try:
        resp = requests.post(COMPANION_QUERY_URL, json=payload)
        if resp.status_code != 200:
            print(f"❌ API Error: {resp.status_code}")
            return False
            
        data = resp.json()
        answer = data.get("answer", "")
        
        # Check headings
        missing = [h for h in expected_headings if h not in answer]
        present_banned = [h for h in banned_headings if h in answer]
        
        if not missing and not present_banned:
            print("✅ Passed structure check")
            return True
        else:
            if missing:
                print(f"❌ Missing headings: {missing}")
            if present_banned:
                print(f"❌ Found banned headings: {present_banned}")
            print(f"Preview: {answer[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    tests = [
        {
            "prompt": "If I only had a weekend to build an MVP",
            "expected": ["Weekend MVP Scope", "Why this Paper"],
            "banned": ["Risks & Unknowns", "Product Directions"]
        },
        {
            "prompt": "What is one 4-hour project I could build?",
            "expected": ["4-Hour Prototype", "Why this Paper"],
            "banned": ["Risks & Unknowns", "Web App"]
        },
        {
            "prompt": "What are the top 3 risks?",
            "expected": ["Top 3 Risks", "Scrappy Tests"],
            "banned": ["Product Directions"]
        },
        {
            "prompt": "What is the realistic moat here?",
            "expected": ["Types of Moat", "Where the Real Moat Is"],
            "banned": ["Product Directions"]
        },
        {
            "prompt": "Is this over-hyped?",
            "expected": ["Where It Fails in Reality", "What Still Survives"],
            "banned": ["Pricing", "Product Directions"]
        },
        {
            "prompt": "I am a solo indie dev building browser tools",
            "expected": ["Two-Week Plan", "Scope Cuts"],
            "banned": ["Risks & Unknowns"]
        },
        {
            "prompt": "I'm a PM at a SaaS startup in fintech",
            "expected": ["Experiment Hypothesis", "Metric", "Experiment Design"],
            "banned": ["Product Directions"]
        }
    ]
    
    passed = 0
    for t in tests:
        if check_response(t["prompt"], t["expected"], t["banned"]):
            passed += 1
        time.sleep(1)
        
    print(f"\n{passed}/{len(tests)} tests passed.")

if __name__ == "__main__":
    main()
