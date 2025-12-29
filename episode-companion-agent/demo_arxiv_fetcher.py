"""
Demo: ArXiv Paper Fetching System

Quick demonstration of the complete workflow:
1. Fetch papers from arXiv
2. Score and rank them
3. Generate episode with LLM
4. Save to database
5. Ingest into RAG
6. Query the companion agent

This is a simplified demo that shows all the pieces working together.
"""

import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def demo_workflow():
    """Run a complete demo of the arXiv fetching workflow"""
    
    print("=" * 70)
    print("ArXiv Paper Fetching System - Demo")
    print("=" * 70)
    
    # Use a recent date (7 days ago to ensure papers exist)
    test_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    print(f"\n📅 Demo Date: {test_date}")
    
    # Step 1: Fetch papers
    print(f"\n{'='*70}")
    print("Step 1: Fetching papers from arXiv...")
    print("=" * 70)
    
    from arxiv_fetcher import fetch_papers_by_date
    
    papers = fetch_papers_by_date(test_date, categories=["cs.AI", "cs.LG"], max_results=20)
    print(f"✓ Fetched {len(papers)} papers")
    
    if not papers:
        print("\n⚠️  No papers found for this date. Try a different date.")
        return
    
    # Show first paper
    print(f"\nExample paper:")
    print(f"  Title: {papers[0].title}")
    print(f"  Authors: {papers[0].authors[:100]}...")
    print(f"  Categories: {papers[0].categories}")
    print(f"  arXiv ID: {papers[0].arxiv_id}")
    
    # Step 2: Score and rank
    print(f"\n{'='*70}")
    print("Step 2: Scoring and ranking papers...")
    print("=" * 70)
    
    from paper_scorer import rank_papers, score_paper
    
    top_papers = rank_papers(papers, top_k=5)
    print(f"✓ Selected top {len(top_papers)} papers")
    
    print(f"\nTop 3 papers by score:")
    for i, paper in enumerate(top_papers[:3], 1):
        score = score_paper(paper)
        print(f"{i}. {paper.title[:60]}... (score: {score:.2f})")
    
    # Step 3: Generate episode (requires Ollama)
    print(f"\n{'='*70}")
    print("Step 3: Generating episode with LLM...")
    print("=" * 70)
    
    try:
        from episode_generator import generate_episode
        
        print("⚠️  This step requires Ollama to be running locally.")
        print("If Ollama is not running, this will fail.\n")
        
        bundle = generate_episode(test_date, top_k=3, max_results=20)
        
        print(f"✓ Episode generated: {bundle.episode_id}")
        print(f"  Papers: {len(bundle.papers)}")
        print(f"  Hook: {bundle.hook[:100]}...")
        
        # Step 4: Save to database
        print(f"\n{'='*70}")
        print("Step 4: Saving to database...")
        print("=" * 70)
        
        from repositories.episode_repository import EpisodeRepository
        
        repo = EpisodeRepository()
        db_episode = repo.save_episode(bundle, total_submissions=len(papers))
        
        print(f"✓ Episode saved: {db_episode.episode_id}")
        
        # Step 5: Ingest into RAG
        print(f"\n{'='*70}")
        print("Step 5: Ingesting into RAG system...")
        print("=" * 70)
        
        from ingest import ingest_bundle_gpk
        
        result = ingest_bundle_gpk(bundle)
        
        print(f"✓ Ingestion complete:")
        print(f"  Report chunks: {result['report_chunks']}")
        print(f"  Paper entries: {result['paper_entries']}")
        print(f"  Total vectors: {result['ids_count']}")
        
        # Step 6: Quick query test
        print(f"\n{'='*70}")
        print("Step 6: Testing companion agent query...")
        print("=" * 70)
        
        from agent import EpisodeCompanionAgent
        
        agent = EpisodeCompanionAgent()
        query = f"What is AI Research Daily {test_date} about in simple terms?"
        
        print(f"Query: {query}\n")
        
        response = agent.get_answer(
            episode_id=bundle.episode_id,
            mode="plain_english",
            query=query
        )
        
        print(f"Agent Response:\n{response['answer'][:300]}...\n")
        
        # Success summary
        print(f"\n{'='*70}")
        print("✅ SUCCESS! All steps completed")
        print("=" * 70)
        print(f"\nYour episode '{bundle.episode_id}' is now ready!")
        print(f"You can query it using the Episode Companion Agent.")
        print(f"\nExample queries:")
        print(f"  - What is AI Research Daily {test_date} about in simple terms?")
        print(f"  - If I'm a founder, what should I care about from today's episode?")
        print(f"  - What are the main technical innovations from the papers?")
        
    except Exception as e:
        print(f"\n❌ Error in LLM/database steps: {e}")
        print("\nNote: This is expected if Ollama is not running.")
        print("The fetching and scoring steps still work!")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_workflow()
