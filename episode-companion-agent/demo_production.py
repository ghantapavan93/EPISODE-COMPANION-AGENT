"""
Production Demo Script for Episode Companion Agent
Demonstrates all industry-grade features for Bart
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("EPISODE COMPANION AGENT - PRODUCTION DEMO")
print("Kochi Interactive Mode Backend v1.0.0")
print("=" * 80)
print()

# ============================================================================
# 1. HEALTH CHECK (Load Balancer / Monitoring)
# ============================================================================
print("[1] Health Check (for load balancers/monitoring)")
print("-" * 80)
response = requests.get(f"{BASE_URL}/health")
health = response.json()
print(f"Status: {health['status']}")
print(f"Version: {health['version']}")
print(f"Agent Ready: {'✅' if health['agent_ready'] else '❌'}")
print(f"Vector Store Ready: {'✅' if health['vector_store_ready'] else '❌'}")
print()

# ============================================================================
# 2. LIST AVAILABLE EPISODES
# ============================================================================
print("[2] List Available Episodes")
print("-" * 80)
response = requests.get(f"{BASE_URL}/episodes")
episodes = response.json()
print(f"Found {len(episodes)} episode(s):")
for ep in episodes:
    print(f"  - {ep}")
print()

# ============================================================================
# 3. DYNAMIC INGESTION (New Episode via API)
# ============================================================================
print("[3] Dynamic Ingestion (Simulating Kochi Daily Report Pipeline)")
print("-" * 80)

new_episode_text = """
AI Research Daily 11/19

Executive Summary:
Novel research on transformer efficiency achieves 3x speedup with minimal accuracy loss.
Breakthrough in multi-modal learning enables unified vision-language models.

Top Papers:
1. Efficient Transformers via Sparse Attention
2. Unified Vision-Language Foundation Models
"""

print(f"Ingesting new episode: 'ai-research-daily-2025-11-19'")
response = requests.post(
    f"{BASE_URL}/episodes/ai-research-daily-2025-11-19/ingest",
    json={
        "text": new_episode_text,
        "title": "AI Research Daily 11/19"
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Successfully ingested!")
    print(f"   Episodes: {result['episode_id']}")
    print(f"   Chunks: {result['data']['chunks_count']}")
    print(f"   Title: {result.get('title', 'N/A')}")
else:
    print(f"❌ Ingestion failed: {response.status_code}")
print()

# ============================================================================
# 4. VERIFY NEW EPISODE IN LIST
# ============================================================================
print("[4] Verify New Episode Appears in List")
print("-" * 80)
response = requests.get(f"{BASE_URL}/episodes")
episodes = response.json()
print(f"Now showing {len(episodes)} episode(s):")
for ep in episodes:
    print(f"  - {ep}")
print()

# ============================================================================
# 5. QUERY WITH THREE PERSONAS (Interactive Mode Simulation)
# ============================================================================
print("[5] Querying Episode (Simulating Kochi Interactive Mode)")
print("-" * 80)

EPISODE_ID = "ai_daily_2025_11_18"  # Use the existing episode

test_cases = [
    {
        "mode": "plain_english",
        "query": "What is the main idea of today's episode?",
        "persona": "General Audience"
    },
    {
        "mode": "founder_takeaway",
        "query": "What should a founder build or watch from this?",
        "persona": "Founder/CEO"
    },
    {
        "mode": "engineer_angle",
        "query": "What should I try in code or infrastructure?",
        "persona": "Engineer/Researcher"
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n[5.{i}] {test['persona']} Query")
    print(f"Mode: {test['mode']}")
    print(f"Q: \"{test['query']}\"")
    print()
    
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/episodes/{EPISODE_ID}/query",
        params={"mode": test['mode']},
        json={"query": test['query']}
    )
    latency = (time.time() - start) * 1000
    
    if response.status_code == 200:
        data = response.json()
        print(f"A: {data['answer'][:200]}...")
        print(f"\nMetrics:")
        print(f"  - Latency: {data['metadata']['latency_ms']:.0f}ms (total: {latency:.0f}ms)")
        print(f"  - Chunks Used: {data['metadata']['used_chunks']}")
        print(f"  - Episode: {data['episode_id']}")
    else:
        print(f"❌ Query failed: {response.status_code} - {response.json()}")

print("\n" + "=" * 80)
print("DEMO COMPLETE")
print("=" * 80)
print()
print("📊 Production Features Demonstrated:")
print("  ✅ Health check endpoint (/health)")
print("  ✅ Episode listing (/episodes)")
print("  ✅ Dynamic ingestion API (/episodes/{id}/ingest)")
print("  ✅ Multi-persona querying (plain_english, founder_takeaway, engineer_angle)")
print("  ✅ Comprehensive logging and error handling")
print("  ✅ API documentation (http://localhost:8000/docs)")
print()
print("🚀 Ready for Kochi Integration!")
print("   The Interactive Mode button can call /episodes/{id}/query directly.")
print("   Kochi's Daily Report pipeline can POST to /episodes/{id}/ingest.")
