import requests
import json
import time

BASE_URL = "http://localhost:8000"
COMPANION_QUERY_URL = f"{BASE_URL}/companion/query"

# We need a valid episode ID. I'll try to fetch one first.
def get_episode_id():
    try:
        resp = requests.get(f"{BASE_URL}/episodes")
        if resp.status_code == 200:
            episodes = resp.json()
            if episodes:
                return episodes[0]
    except Exception as e:
        print(f"Failed to fetch episodes: {e}")
    return "ai-research-daily-2025-11-20" # Fallback

def test_prompt(episode_id, prompt, expected_mode_hint):
    payload = {
        "message": prompt,
        "user_id": "test_user_123",
        "episode_id": episode_id,
        "mode": "auto", # Let the orchestrator infer it
        "debug": True
    }
    
    print(f"\n--- Testing Prompt: '{prompt}' ---")
    try:
        start = time.time()
        resp = requests.post(COMPANION_QUERY_URL, json=payload)
        latency = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json()
            mode = data.get("mode")
            answer = data.get("answer", "")[:200].replace("\n", " ") + "..."
            
            print(f"✅ Status: 200 OK ({latency:.2f}s)")
            print(f"   Inferred Mode: {mode}")
            print(f"   Answer Preview: {answer}")
            
            if expected_mode_hint in mode:
                print(f"   ✅ Mode matches expected '{expected_mode_hint}'")
            else:
                print(f"   ❌ Mode mismatch! Expected '{expected_mode_hint}', got '{mode}'")
                
        else:
            print(f"❌ Failed: Status {resp.status_code}")
            print(f"   Response: {resp.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    print("Fetching episode ID...")
    episode_id = get_episode_id()
    print(f"Using Episode ID: {episode_id}")
    
    test_cases = [
        # Founder Prompts
        ("If I only had a weekend to build an MVP", "founder_takeaway"),
        ("What is the realistic moat here?", "founder_takeaway"),
        ("What are the top 3 risks?", "founder_takeaway"),
        
        # Engineer Prompts
        ("Describe a minimal data pipeline", "engineer_angle"),
        ("Sketch a minimal API", "engineer_angle"),
        ("What metrics and logs should I track?", "engineer_angle"),
        
        # Plain English Prompts
        ("Give me a summary", "plain_english"),
        ("TL;DR please", "plain_english"),
    ]
    
    for prompt, expected_mode in test_cases:
        test_prompt(episode_id, prompt, expected_mode)
        time.sleep(1) # Be nice to the server

if __name__ == "__main__":
    main()
