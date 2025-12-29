"""Quick test of the upstream pipeline endpoint"""
import requests
from datetime import datetime, timedelta

# Use a date 7 days ago
target_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

print("=" * 70)
print("Testing Upstream Pipeline Endpoint")
print("=" * 70)
print(f"Target date: {target_date}")
print()

# Test the endpoint
headers = {'X-API-Key': 'my-secret-antigravity-password'}

print("Calling /admin/generate-episode...")
print("(This may take 30-60 seconds as it fetches from arXiv and calls Gemini)")
print()

try:
    response = requests.post(
        f'http://localhost:8000/admin/generate-episode?target_date={target_date}&max_results=20',
        headers=headers,
        timeout=90
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"  Papers found: {result.get('papers_found', 0)}")
        print(f"  Top papers selected: {result.get('top_papers_selected', 0)}")
        
        if result.get('paper_titles'):
            print(f"\n  Top 3 Papers:")
            for i, title in enumerate(result['paper_titles'][:3], 1):
                print(f"    {i}. {title[:60]}...")
        
        if result.get('generated_report'):
            print(f"\n  Report Preview (first 300 chars):")
            print(f"  {result['generated_report'][:300]}...")
    else:
        print(f"\n❌ FAILED")
        print(f"  Response: {response.text[:200]}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
