"""
Simple test of upstream pipeline - NO EMOJIS for Windows terminal
"""

from datetime import datetime, timedelta
from arxiv_loader import ArxivLoader

print("=" * 70)
print("Testing ArxivLoader")
print("=" * 70)

loader = ArxivLoader()
target_date = (datetime.now() - timedelta(days=7)).date()

print(f"\nFetching papers for: {target_date}")
print("Please wait...")

try:
    papers = loader.get_papers_for_date(target_date, max_results=20)
    print(f"[OK] Found {len(papers)} papers")
    
    if papers:
        print(f"\nFirst paper:")
        print(f"  Title: {papers[0].title}")
        print(f"  ID: {papers[0].arxiv_id}")
        print(f"  Category: {papers[0].primary_category}")
        
        # Test paper selection
        top_papers = loader.select_top_papers(papers, top_n=7)
        print(f"\n[OK] Selected {len(top_papers)} top papers")
        
        print(f"\nTop 3:")
        for i, p in enumerate(top_papers[:3], 1):
            print(f"  {i}. {p.title[:70]}")
            print(f"     Category: {p.primary_category}")
        
        print(f"\n[SUCCESS] ArxivLoader is working!")
        
    else:
        print("[WARN] No papers found for this date")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
