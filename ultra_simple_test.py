"""
Ultra-simple test - just check if arxiv_loader can fetch
"""
from datetime import datetime, timedelta
from arxiv_loader import ArxivLoader

print("Starting test...")
print("-" * 50)

loader = ArxivLoader()
date = (datetime.now() - timedelta(days=10)).date()

print(f"Fetching papers for: {date}")
print("Wait 15 seconds...")

try:
    papers = loader.get_papers_for_date(date, max_results=5)
    print(f"\nRESULT: Got {len(papers)} papers")
    
    if papers:
        print(f"\nFirst paper title:")
        print(papers[0].title)
        print("\nSUCCESS!")
    else:
        print("No papers found")
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("-" * 50)
