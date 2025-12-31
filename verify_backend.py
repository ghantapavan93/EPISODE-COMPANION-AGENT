import requests
import json
import sys

BASE_URL = "http://localhost:8000"
API_KEY = "my-secret-antigravity-password"
EPISODE_ID = "ai-research-daily-2025-11-18"

def test_backend():
    print(f"Testing backend at {BASE_URL}...")
    
    # 1. Health Check
    try:
        resp = requests.get(f"{BASE_URL}/health")
        if resp.status_code == 200:
            print("✅ Health check passed")
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"❌ Health check failed: {resp.status_code}")
            print(resp.text)
            return
    except Exception as e:
        print(f"❌ Could not connect to backend: {e}")
        return

    # 2. Query Test
    print("\nTesting /query endpoint...")
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    payload = {
        "query": "What is Kandinsky 5.0?",
        "user_id": "test-user",
        "episode_id": EPISODE_ID
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/query", headers=headers, json=payload)
        if resp.status_code == 200:
            print("✅ Query successful")
            data = resp.json()
            print(f"Answer: {data.get('answer')}")
            print(f"Metadata: {json.dumps(data.get('metadata', {}), indent=2)}")
        else:
            print(f"❌ Query failed: {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"❌ Query request failed: {e}")

if __name__ == "__main__":
    test_backend()
