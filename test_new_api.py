import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "my-secret-antigravity-password"

print("Testing new /companion/query endpoint with explicit modes...")
print("="*70)

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Test 1: Plain English mode (explicit)
print("\n1. Plain English Mode (Explicit)")
payload = {
    "user_id": "test-production-user",
    "message": "Explain Kandinsky 5.0 like I'm 12",
    "episode_id": "ai-research-daily-2025-11-18",
    "mode": "plain_english",
    "debug": True
}

resp = requests.post(f"{BASE_URL}/query", headers=headers, json=payload, timeout=30)
if resp.status_code == 200:
    data = resp.json()
    print(f"Mode Used: {data.get('mode')}")
    print(f"Answer Length: {len(data.get('answer', ''))}")
    print(f"Has Debug Info: {data.get('metadata', {}).get('debug') is not None}")
    print(f"Answer Preview: {data.get('answer', '')[:200]}...")
else:
    print(f"Error: {resp.status_code} - {resp.text}")

# Test 2: Founder mode
print("\n2. Founder Mode (Explicit)")
payload = {
    "user_id": "test-production-user",
    "message": "What startup opportunity does this research create?",
    "episode_id": "ai-research-daily-2025-11-18",
    "mode": "founder_takeaway",
    "debug": False
}

resp = requests.post(f"{BASE_URL}/query", headers=headers, json=payload, timeout=30)
if resp.status_code == 200:
    data = resp.json()
    print(f"Mode Used: {data.get('mode')}")
    print(f"Answer Length: {len(data.get('answer', ''))}")
    print(f"Answer Preview: {data.get('answer', '')[:200]}...")
else:
    print(f"Error: {resp.status_code} - {resp.text}")

print("\n" + "="*70)
print("Test complete!")
