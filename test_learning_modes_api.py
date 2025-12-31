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

def test_trigger(trigger_text, expected_mode, expected_content_hint=None):
    episode_id = get_episode_id()
    payload = {
        "message": trigger_text,
        "user_id": "test_learner",
        "episode_id": episode_id,
        "mode": "auto",
        "debug": True
    }
    
    print(f"\nTesting Trigger: '{trigger_text}'")
    try:
        start = time.time()
        resp = requests.post(COMPANION_QUERY_URL, json=payload)
        latency = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json()
            # The API might not return "mode" in the top level for these special types if they short-circuit,
            # but let's check the answer content.
            # Actually, agent.get_answer returns a dict.
            # If it short-circuits, it returns {"answer": ..., "metadata": ...}
            # The orchestrator wraps this.
            
            answer = data.get("answer", "")
            print(f"✅ Status: 200 OK ({latency:.2f}s)")
            print(f"   Answer Preview: {answer[:150]}...")
            
            if expected_content_hint:
                if expected_content_hint.lower() in answer.lower():
                    print(f"   ✅ Found expected content: '{expected_content_hint}'")
                else:
                    print(f"   ⚠️ Content hint '{expected_content_hint}' NOT found. Check output.")
            
            # We can't easily check the internal 'question_type' from the API response unless we added it to metadata.
            # But if the answer looks like a quiz or critique, it worked.
            
        else:
            print(f"❌ Failed: Status {resp.status_code}")
            print(f"   Response: {resp.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    tests = [
        # Quiz Triggers
        ("Quiz me on this episode.", "quiz_me", "1."),
        ("Give me 5 questions to test if I understood today’s episode.", "quiz_me", "5."),
        ("Ask me multiple-choice questions about the main papers.", "quiz_me", "A)"),
        ("Mix easy and hard questions.", "quiz_me", "[Easy]"),
        
        # Self-Explain Triggers
        ("Let me try to explain [Paper Name] in my own words.", "self_explain", "What you got right"),
        ("Grade my explanation from 0-10: The paper is about...", "self_explain", "Score:"),
        ("Rewrite it and highlight what I missed.", "self_explain", "improved explanation")
    ]
    
    for text, mode, hint in tests:
        test_trigger(text, mode, hint)
        time.sleep(1)

if __name__ == "__main__":
    main()
