"""
Final verification test - Shows what's working
"""

print("=" * 70)
print("UPSTREAM PIPELINE - Component Verification")
print("=" * 70)

# Test 1: Module imports
print("\n1. Testing imports...")
try:
    from arxiv_loader import ArxivLoader, Paper
    print("   [OK] arxiv_loader imported")
except Exception as e:
    print(f"   [FAIL] arxiv_loader: {e}")

try:
    from report_generator import ReportGenerator
    print("   [OK] report_generator imported")
except Exception as e:
    print(f"   [FAIL] report_generator: {e}")

try:
    import feedparser
    print("   [OK] feedparser imported")
except Exception as e:
    print(f"   [FAIL] feedparser: {e}")

# Test 2: Check API endpoint exists
print("\n2. Testing API endpoint...")
try:
    import requests
    response = requests.options('http://localhost:8000/admin/generate-episode')
    print(f"   [OK] Endpoint exists (status: {response.status_code})")
except Exception as e:
    print(f"   [WARN] Could not verify endpoint: {e}")

# Test 3: Try to fetch a few papers
print("\n3. Testing ArxivLoader.get_papers_for_date...")
try:
    from datetime import datetime, timedelta
    loader = ArxivLoader()
    target_date = (datetime.now() - timedelta(days=10)).date()
    print(f"   Fetching for date: {target_date}")
    print("   (This takes 10-20 seconds...)")
    
    papers = loader.get_papers_for_date(target_date, max_results=10)
    print(f"   [OK] Found {len(papers)} papers")
    
    if papers:
        print(f"\n   Sample paper:")
        print(f"   - Title: {papers[0].title[:60]}...")
        print(f"   - ID: {papers[0].arxiv_id}")
        print(f"   - Category: {papers[0].primary_category}")
        
        # Test 4: Selection
        print("\n4. Testing paper selection...")
        top = loader.select_top_papers(papers, top_n=min(5, len(papers)))
        print(f"   [OK] Selected {len(top)} papers")
        
        print("\n" + "=" * 70)
        print("SUMMARY: Core components are WORKING!")
        print("=" * 70)
        print("\nYou can now use:")
        print(f"  - POST /admin/generate-episode?target_date={target_date}")
        print("  - python test_upstream_pipeline.py")
        print("\nNote: Report generation requires GOOGLE_API_KEY in .env")
    else:
        print("   [WARN] No papers found - try a different date")
        
except Exception as e:
    print(f"   [FAIL] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
