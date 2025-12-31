"""
End-to-End Integration Test for Episode Companion Agent

This script validates the entire system flow:
1. Ingestion of episode data
2. Agent queries in all three modes
3. API endpoint responses
4. Web UI accessibility
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"
EPISODE_ID = "ai_daily_2025_11_18"

print("=" * 70)
print("EPISODE COMPANION AGENT - END-TO-END INTEGRATION TEST")
print("=" * 70)
print()

# Test Suite
test_results = {
    "passed": 0,
    "failed": 0,
    "total": 0
}

def test(name, func):
    """Run a test and track results"""
    test_results["total"] += 1
    print(f"\n[Test {test_results['total']}] {name}")
    print("-" * 70)
    try:
        func()
        test_results["passed"] += 1
        print("✅ PASSED")
        return True
    except AssertionError as e:
        test_results["failed"] += 1
        print(f"❌ FAILED: {e}")
        return False
    except Exception as e:
        test_results["failed"] += 1
        print(f"❌ ERROR: {e}")
        return False

# Test 1: API Server is Running
def test_server_running():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print(f"  → Server is running and responding")

test("API Server Availability", test_server_running)

# Test 2: Web UI is Accessible
def test_web_ui():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Kochi" in response.text or "ai-research-daily" in response.text
    print(f"  → Web UI loaded successfully")
    print(f"  → Page size: {len(response.text)} bytes")

test("Web UI Accessibility", test_web_ui)

# Test 3: Plain English Mode
def test_plain_english():
    query = "What is Kaiming He's main contribution?"
    response = requests.post(
        f"{BASE_URL}/episodes/{EPISODE_ID}/plain_english",
        json={"query": query}
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "answer" in data
    assert "episode_id" in data
    assert data["mode"] == "plain_english"
    print(f"  → Query: {query}")
    print(f"  → Answer length: {len(data['answer'])} characters")
    print(f"  → Latency: {data['metadata']['latency_ms']}ms")
    print(f"  → Chunks used: {data['metadata']['used_chunks']}")

test("Plain English Mode Query", test_plain_english)

# Test 4: Founder Takeaway Mode
def test_founder_takeaway():
    query = "What is the business opportunity?"
    response = requests.post(
        f"{BASE_URL}/episodes/{EPISODE_ID}/founder_takeaway",
        json={"query": query}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["mode"] == "founder_takeaway"
    print(f"  → Query: {query}")
    print(f"  → Answer length: {len(data['answer'])} characters")
    print(f"  → Latency: {data['metadata']['latency_ms']}ms")

test("Founder Takeaway Mode Query", test_founder_takeaway)

# Test 5: Engineer Angle Mode
def test_engineer_angle():
    query = "How does the architecture work?"
    response = requests.post(
        f"{BASE_URL}/episodes/{EPISODE_ID}/engineer_angle",
        json={"query": query}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["mode"] == "engineer_angle"
    print(f"  → Query: {query}")
    print(f"  → Answer length: {len(data['answer'])} characters")
    print(f"  → Latency: {data['metadata']['latency_ms']}ms")

test("Engineer Angle Mode Query", test_engineer_angle)

# Test 6: Invalid Mode Error Handling
def test_invalid_mode():
    response = requests.post(
        f"{BASE_URL}/episodes/{EPISODE_ID}/invalid_mode",
        json={"query": "test"}
    )
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    print(f"  → Correctly returns 400 for invalid mode")

test("Invalid Mode Error Handling", test_invalid_mode)

# Test 7: Vector Store Has Data
def test_vector_store_populated():
    # Query should return results with chunks
    response = requests.post(
        f"{BASE_URL}/episodes/{EPISODE_ID}/plain_english",
        json={"query": "diffusion"}
    )
    data = response.json()
    assert data["metadata"]["used_chunks"] > 0, "No chunks retrieved from vector store"
    print(f"  → Vector store contains {data['metadata']['used_chunks']} relevant chunks")

test("Vector Store Population", test_vector_store_populated)

# Test 8: Response Quality Check
def test_response_quality():
    response = requests.post(
        f"{BASE_URL}/episodes/{EPISODE_ID}/plain_english",
        json={"query": "What papers are discussed?"}
    )
    data = response.json()
    answer = data["answer"].lower()
    # Check if answer contains relevant keywords from the episode
    keywords = ["kaiming", "diffusion", "transformer", "paper"]
    found_keywords = [kw for kw in keywords if kw in answer]
    assert len(found_keywords) > 0, "Answer doesn't contain any expected keywords"
    print(f"  → Answer contains relevant keywords: {found_keywords}")

test("Response Quality", test_response_quality)

# Test 9: Concurrent Requests (Stress Test)
def test_concurrent_requests():
    import concurrent.futures
    
    def make_request():
        response = requests.post(
            f"{BASE_URL}/episodes/{EPISODE_ID}/plain_english",
            json={"query": "test"}
        )
        return response.status_code == 200
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(make_request) for _ in range(3)]
        results = [f.result() for f in futures]
    
    assert all(results), "Some concurrent requests failed"
    print(f"  → All 3 concurrent requests succeeded")

test("Concurrent Request Handling", test_concurrent_requests)

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"Total Tests: {test_results['total']}")
print(f"✅ Passed: {test_results['passed']}")
print(f"❌ Failed: {test_results['failed']}")
print(f"Success Rate: {(test_results['passed'] / test_results['total'] * 100):.1f}%")
print()

if test_results['failed'] == 0:
    print("🎉 ALL TESTS PASSED - SYSTEM IS FULLY OPERATIONAL!")
    print()
    print("✅ Ingestion Pipeline: WORKING")
    print("✅ Vector Store: POPULATED")
    print("✅ Agent Logic: WORKING")
    print("✅ API Endpoints: WORKING")
    print("✅ Web UI: ACCESSIBLE")
    print("✅ All 3 Modes: WORKING")
    print()
    print("🚀 READY FOR PRODUCTION DEMO!")
    sys.exit(0)
else:
    print("⚠️  SOME TESTS FAILED - PLEASE REVIEW")
    sys.exit(1)
