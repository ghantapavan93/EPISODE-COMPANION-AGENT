import requests
import time
import subprocess
import sys

BASE_URL = "http://localhost:8000"

def test_api():
    print("Waiting for server to start...")
    time.sleep(5)  # Give uvicorn time to start
    
    # 1. Test Root
    try:
        resp = requests.get(f"{BASE_URL}/")
        assert resp.status_code == 200
        print("✅ Root endpoint working")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return

    # 2. Test Founder Takeaway
    print("\nTesting Founder Takeaway...")
    payload = {"query": "What is the business opportunity?"}
    resp = requests.post(f"{BASE_URL}/episodes/ai_daily_2025_11_18/founder_takeaway", json=payload)
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Success! Answer: {data['answer'][:100]}...")
        print(f"   Latency: {data['metadata']['latency_ms']}ms")
    else:
        print(f"❌ Failed: {resp.text}")

    # 3. Test Engineer Angle
    print("\nTesting Engineer Angle...")
    payload = {"query": "How does the architecture work?"}
    resp = requests.post(f"{BASE_URL}/episodes/ai_daily_2025_11_18/engineer_angle", json=payload)
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Success! Answer: {data['answer'][:100]}...")
    else:
        print(f"❌ Failed: {resp.text}")

if __name__ == "__main__":
    test_api()
