#!/usr/bin/env python3
"""
Fetch and Ingest CLI Tool

End-to-end workflow for generating daily episodes:
1. Fetch papers from arXiv by date
2. Score and rank papers
3. Generate report with LLM
4. Save to database
5. Ingest into RAG system

Usage:
    python fetch_and_ingest.py --date 2025-11-19
    python fetch_and_ingest.py --date 2025-11-20 --top-k 7 --categories cs.AI cs.LG cs.CV
"""

import argparse
import logging
import sys
from typing import List, Optional

from episode_generator import generate_episode
from ingest import ingest_bundle_gpk
from repositories.paper_repository import PaperRepository
from repositories.episode_repository import EpisodeRepository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_and_ingest(
    date: str,
    categories: Optional[List[str]] = None,
    top_k: int = 7,
    max_results: int = 1000,
    skip_ingest: bool = False
):
    """
    Fetch papers, generate episode, save to DB, and ingest into RAG.
    
    Args:
        date: Date string "YYYY-MM-DD"
        categories: arXiv categories to fetch
        top_k: Number of top papers to select
        max_results: Max papers to fetch
        skip_ingest: If True, skip RAG ingestion (only save to DB)
    """
    logger.info(f"{'='*60}")
    logger.info(f"Fetch and Ingest for {date}")
    logger.info(f"{'='*60}")
    
    try:
        # 1. Generate episode
        logger.info("\n📥 Step 1: Generating episode...")
        bundle = generate_episode(date, categories, top_k, max_results)
        logger.info(f"✓ Episode generated: {bundle.episode_id}")
        logger.info(f"  - Papers selected: {len(bundle.papers)}")
        
        # 2. Save episode to database
        logger.info("\n💾 Step 2: Saving episode to database...")
        episode_repo = EpisodeRepository()
        db_episode = episode_repo.save_episode(bundle, total_submissions=max_results)
        logger.info(f"✓ Episode saved: {db_episode.episode_id}")
        
        # 3. Save papers to database (optional, for caching)
        logger.info("\n💾 Step 3: Saving papers to database...")
        # Note: We don't save individual papers here since we only have PaperEntryGpk
        # which doesn't include all metadata. Papers would be saved during fetching
        # if we integrate that into the workflow.
        logger.info("✓ Skipping individual paper saves (not needed for this workflow)")
        
        # 4. Ingest into RAG
        if not skip_ingest:
            logger.info("\n🔍 Step 4: Ingesting into RAG system...")
            ingest_result = ingest_bundle_gpk(bundle)
            logger.info(f"✓ Ingestion complete:")
            logger.info(f"  - Report chunks: {ingest_result['report_chunks']}")
            logger.info(f"  - Audio chunks: {ingest_result['audio_chunks']}")
            logger.info(f"  - Paper entries: {ingest_result['paper_entries']}")
            logger.info(f"  - Total vectors: {ingest_result['ids_count']}")
        else:
            logger.info("\n⏭️  Step 4: Skipping RAG ingestion (--skip-ingest flag)")
        
        # 5. Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ SUCCESS!")
        logger.info(f"{'='*60}")
        logger.info(f"Episode ID: {bundle.episode_id}")
        logger.info(f"Date: {bundle.date_str}")
        logger.info(f"Papers: {len(bundle.papers)}")
        logger.info(f"\nHook: {bundle.hook}")
        logger.info(f"\nYou can now query the Episode Companion Agent about this episode!")
        logger.info(f"Example: 'What is AI Research Daily {date} about in simple terms?'")
        logger.info(f"{'='*60}\n")
        
        return bundle
        
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Fetch papers from arXiv and generate daily episode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate episode for today
  python fetch_and_ingest.py --date 2025-11-19
  
  # Generate with specific categories
  python fetch_and_ingest.py --date 2025-11-20 --categories cs.AI cs.LG cs.CV
  
  # Generate with custom top K
  python fetch_and_ingest.py --date 2025-11-19 --top-k 10
  
  # Save to DB only, skip RAG ingestion
  python fetch_and_ingest.py --date 2025-11-19 --skip-ingest
        """
    )
    
    parser.add_argument(
        "--date",
        required=True,
        help="Date to fetch papers for (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--categories",
        nargs="+",
        default=None,
        help="arXiv categories to fetch (default: cs.AI cs.LG cs.CV cs.CL)"
    )
    
    parser.add_argument(
        "--top-k",
        type=int,
        default=7,
        help="Number of top papers to select (default: 7)"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        default=1000,
        help="Maximum papers to fetch from arXiv (default: 1000)"
    )
    
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Skip RAG ingestion, only save to database"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    fetch_and_ingest(
        date=args.date,
        categories=args.categories,
        top_k=args.top_k,
        max_results=args.max_results,
        skip_ingest=args.skip_ingest
    )


if __name__ == "__main__":
    main()
