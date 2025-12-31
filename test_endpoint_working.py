"""
Working test - calls the actual API endpoint
"""
import requests
import json

API_KEY = "my-secret-antigravity-password"
BASE_URL = "http://localhost:8000"

# Use yesterday's date (2025-11-20) which we know has papers
target_date = "2025-11-20"

print("=" * 70)
print("TESTING /admin/generate-episode ENDPOINT")
print("=" * 70)
print(f"Target date: {target_date}")
print(f"URL: {BASE_URL}/admin/generate-episode")
print()
print("Calling endpoint (may take 30-60 seconds)...")
print("This will:")
print("  1. Fetch papers from arXiv")
print("  2. Select top 7")
print("  3. Call Gemini to generate report")
print()

headers = {"X-API-Key": API_KEY}

try:
    response = requests.post(
        f"{BASE_URL}/admin/generate-episode",
        headers=headers,
        params={
            "target_date": target_date,
            "max_results": 50
        },
        timeout=120
    )
    
    print(f"Response status: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        
        print("SUCCESS!")
        print("=" * 70)
        print(f"Papers found: {result.get('papers_found', 0)}")
        print(f"Top papers selected: {result.get('top_papers_selected', 0)}")
        print()
        
        if result.get('paper_titles'):
            print("Top papers:")
            for i, title in enumerate(result['paper_titles'], 1):
                print(f"  {i}. {title[:65]}...")
        
        print()
        if result.get('generated_report'):
            report = result['generated_report']
            print("Generated report preview (first 500 chars):")
            print("-" * 70)
            print(report[:500])
            print("...")
            print("-" * 70)
            print()
            print(f"Full report length: {len(report)} characters")
        
        print()
        print("=" * 70)
        print("ENDPOINT IS WORKING PERFECTLY!")
        print("=" * 70)
    else:
        print(f"ERROR - Status {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
