"""
Test Upstream Pipeline - Generate Episode from arXiv

This script demonstrates the new /admin/generate-episode endpoint that:
1. Fetches papers from arXiv for a specific date
2. Selects top 7 papers using heuristics  
3. Generates a report with Gemini
4. Returns the report ready for ingestion
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
API_KEY = "my-secret-antigravity-password"  # Change this to your API key
BASE_URL = "http://localhost:8000"

# Use a recent date (7 days ago to ensure papers exist)
target_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

print("=" * 70)
print("Testing Upstream Pipeline - Episode Generation")
print("=" * 70)
print(f"\nTarget Date: {target_date}")
print(f"API Key: {API_KEY}")
print()

# Step 1: Generate episode from arXiv
print("Step 1: Calling /admin/generate-episode...")
print("-" * 70)

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

response = requests.post(
    f"{BASE_URL}/admin/generate-episode",
    headers=headers,
    params={
        "target_date": target_date,
        "max_results": 100
    }
)

if response.status_code == 200:
    result = response.json()
    
    print(f"✅ Success!")
    print(f"  Papers found: {result['papers_found']}")
    print(f"  Top papers selected: {result['top_papers_selected']}")
    print()
    
    print("Top Papers:")
    for i, title in enumerate(result['paper_titles'], 1):
        print(f"  {i}. {title[:60]}...")
    print()
    
    # Show report preview
    report = result['generated_report']
    print("Generated Report Preview (first 500 chars):")
    print("-" * 70)
    print(report[:500])
    print("...")
    print("-" * 70)
    print()
    
    # Step 2: Ingest the generated report
    print("\nStep 2: Would you like to ingest this report? (y/n)")
    user_input = input("> ")
    
    if user_input.lower() == 'y':
        episode_id = f"ai-research-daily-{target_date}"
        
        print(f"\nIngesting episode: {episode_id}")
        
        ingest_response = requests.post(
            f"{BASE_URL}/episodes/{episode_id}/ingest",
            headers=headers,
            json={
                "text": report,
                "title": f"AI Research Daily {target_date}"
            }
        )
        
        if ingest_response.status_code == 200:
            ingest_result = ingest_response.json()
            print(f"✅ Ingestion successful!")
            print(f"  Chunks: {ingest_result['data']['chunks_count']}")
            print()
            
            # Step 3: Test a query
            print("\nStep 3: Testing a query...")
            query_response = requests.post(
                f"{BASE_URL}/query",
                headers=headers,
                json={
                    "query": f"What is AI Research Daily {target_date} about in simple terms?",
                    "user_id": "test_user"
                },
                params={
                    "episode_id": episode_id
                }
            )
            
            if query_response.status_code == 200:
                query_result = query_response.json()
                print(f"✅ Query successful!")
                print(f"\nAgent Response:")
                print("-" * 70)
                print(query_result['answer'][:300])
                print("...")
                print("-" * 70)
            else:
                print(f"❌ Query failed: {query_response.text}")
        else:
            print(f"❌ Ingestion failed: {ingest_response.text}")
    else:
        print("\nSkipping ingestion. You can manually ingest using:")
        print(f"  POST {BASE_URL}/episodes/ai-research-daily-{target_date}/ingest")
        print(f"  Body: {{ \"text\": \"<report>\" }}")

else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

print("\n" + "=" * 70)
print("Test Complete!")
print("=" * 70)
