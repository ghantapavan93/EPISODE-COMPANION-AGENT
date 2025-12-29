"""
Direct test of arx iv_loader and report_generator modules
This tests the core components without hitting the API endpoint
"""

from datetime import datetime, timedelta
from arxiv_loader import ArxivLoader
from report_generator import ReportGenerator

print("=" * 70)
print("Direct Module Test - Upstream Pipeline Components")
print("=" * 70)

# Test 1: ArxivLoader
print("\n1. Testing ArxivLoader...")
print("-" * 70)

loader = ArxivLoader()
target_date = (datetime.now() - timedelta(days=7)).date()

print(f"Fetching papers for: {target_date}")
print("(This may take 10-20 seconds...)")

try:
    papers = loader.get_papers_for_date(target_date, max_results=20)
    print(f"✅ Found {len(papers)} papers")
    
    if papers:
        print(f"\nFirst paper:")
        print(f"  Title: {papers[0].title[:60]}...")
        print(f"  ID: {papers[0].arxiv_id}")
        print(f"  Category: {papers[0].primary_category}")
        print(f"  Authors: {len(papers[0].authors)} authors")
        
        # Test 2: Paper selection
        print(f"\n2. Testing paper selection...")
        print("-" * 70)
        
        top_papers = loader.select_top_papers(papers, top_n=7)
        print(f"✅ Selected {len(top_papers)} top papers")
        
        print(f"\nTop 3:")
        for i, p in enumerate(top_papers[:3], 1):
            print(f"  {i}. {p.title[:50]}... ({p.primary_category})")
        
        # Test 3: Report Generator (this requires Gemini API)
        print(f"\n3. Testing ReportGenerator (requires Gemini API)...")
        print("-" * 70)
        print("Calling Gemini to generate report...")
        print("(This may take 30-60 seconds...)")
        
        try:
            generator = ReportGenerator()
            report = generator.generate_markdown(
                date_str=str(target_date),
                total_count=len(papers),
                papers=top_papers[:3]  # Use only 3 papers to speed up
            )
            
            print(f"✅ Report generated successfully!")
            print(f"\nReport preview (first 400 chars):")
            print("-" * 70)
            print(report[:400])
            print("...")
            print("-" * 70)
            
            print(f"\n✅ ALL TESTS PASSED!")
            
        except Exception as e:
            print(f"❌ ReportGenerator failed: {e}")
            print("This might be due to Gemini API issues")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️  No papers found for this date. Try a different date.")
        
except Exception as e:
    print(f"❌ ArxivLoader failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
