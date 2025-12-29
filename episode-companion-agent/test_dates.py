"""
Test with multiple dates to find papers
"""
from datetime import datetime, timedelta
from arxiv_loader import ArxivLoader

print("Testing ArxivLoader with different dates")
print("=" * 60)

loader = ArxivLoader()

# Try last 3 days
for days_ago in [1, 2, 3, 5, 7]:
    date = (datetime.now() - timedelta(days=days_ago)).date()
    print(f"\nTrying date: {date} ({days_ago} days ago)")
    
    try:
        papers = loader.get_papers_for_date(date, max_results=10)
        print(f"  Found: {len(papers)} papers")
        
        if papers:
            print(f"  Sample: {papers[0].title[:50]}...")
            print("  SUCCESS - This date has papers!")
            
            # Test selection
            top = loader.select_top_papers(papers, top_n=3)
            print(f"  Top 3 selected successfully")
            break
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "=" * 60)
print("\n" + "=" * 60)
