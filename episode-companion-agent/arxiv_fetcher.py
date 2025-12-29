"""
ArXiv Paper Fetcher Module

Fetches papers from arXiv API by date and categories.
Handles rate limiting and retries automatically.
"""

import time
import logging
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime, timedelta
import arxiv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ArxivPaper:
    """Represents a paper fetched from arXiv"""
    arxiv_id: str
    title: str
    authors: str  # Comma-separated author names
    abstract: str
    categories: str  # Comma-separated categories
    submitted_date: str  # "YYYY-MM-DD"
    pdf_url: str
    arxiv_url: str
    
    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)


class ArxivFetcher:
    """Fetches papers from arXiv with rate limiting"""
    
    def __init__(self, delay_seconds: float = 3.0):
        """
        Initialize fetcher with rate limiting.
        
        Args:
            delay_seconds: Seconds to wait between API calls (arXiv recommends 3s)
        """
        self.delay_seconds = delay_seconds
        self.last_request_time = 0
    
    def _throttle(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay_seconds:
            sleep_time = self.delay_seconds - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def fetch_papers_by_date(
        self, 
        date: str, 
        categories: Optional[List[str]] = None,
        max_results: int = 1000
    ) -> List[ArxivPaper]:
        """
        Fetch papers submitted on a specific date.
        
        Args:
            date: Date string in format "YYYY-MM-DD"
            categories: List of arXiv categories (e.g., ["cs.AI", "cs.LG", "cs.CV"])
                       If None, defaults to ["cs.AI", "cs.LG", "cs.CV", "cs.CL"]
            max_results: Maximum number of papers to fetch
            
        Returns:
            List of ArxivPaper objects
        """
        if categories is None:
            categories = ["cs.AI", "cs.LG", "cs.CV", "cs.CL"]
        
        logger.info(f"Fetching papers for {date} in categories: {categories}")
        
        # Parse date
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {date}. Expected YYYY-MM-DD")
        
        # Build search query for categories
        # Format: cat:cs.AI OR cat:cs.LG OR cat:cs.CV
        category_query = " OR ".join([f"cat:{cat}" for cat in categories])
        
        # arXiv API doesn't support exact date filtering in the query,
        # so we need to fetch papers and filter by date
        # We'll fetch from the target date and a bit before/after
        start_date = target_date - timedelta(days=1)
        end_date = target_date + timedelta(days=1)
        
        # Add date range to query (submittedDate)
        # Format: submittedDate:[20250101000000 TO 20250102000000]
        start_str = start_date.strftime("%Y%m%d000000")
        end_str = end_date.strftime("%Y%m%d235959")
        
        query = f"({category_query}) AND submittedDate:[{start_str} TO {end_str}]"
        
        logger.info(f"Query: {query}")
        
        # Throttle before API call
        self._throttle()
        
        # Search arXiv
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        papers = []
        try:
            for result in client.results(search):
                # Extract arxiv ID (remove version)
                arxiv_id = result.entry_id.split("/")[-1].replace("v1", "").replace("v2", "").replace("v3", "")
                
                # Get submission date
                submitted = result.published.strftime("%Y-%m-%d")
                
                # Filter to exact date
                if submitted != date:
                    continue
                
                # Extract authors
                authors = ", ".join([author.name for author in result.authors])
                
                # Extract categories
                cats = ", ".join(result.categories)
                
                paper = ArxivPaper(
                    arxiv_id=arxiv_id,
                    title=result.title.strip(),
                    authors=authors,
                    abstract=result.summary.strip().replace("\n", " "),
                    categories=cats,
                    submitted_date=submitted,
                    pdf_url=result.pdf_url,
                    arxiv_url=result.entry_id
                )
                
                papers.append(paper)
                
        except Exception as e:
            logger.error(f"Error fetching papers: {e}")
            raise
        
        logger.info(f"Fetched {len(papers)} papers for {date}")
        return papers


def fetch_papers_by_date(
    date: str, 
    categories: Optional[List[str]] = None,
    max_results: int = 1000
) -> List[ArxivPaper]:
    """
    Convenience function to fetch papers by date.
    
    Args:
        date: Date string in format "YYYY-MM-DD"
        categories: List of arXiv categories
        max_results: Maximum number of papers to fetch
        
    Returns:
        List of ArxivPaper objects
    """
    fetcher = ArxivFetcher()
    return fetcher.fetch_papers_by_date(date, categories, max_results)


if __name__ == "__main__":
    # Test
    import sys
    
    if len(sys.argv) > 1:
        test_date = sys.argv[1]
    else:
        test_date = "2025-11-19"
    
    print(f"Fetching papers for {test_date}...")
    papers = fetch_papers_by_date(test_date)
    print(f"\nFound {len(papers)} papers\n")
    
    if papers:
        print("First 3 papers:")
        for i, paper in enumerate(papers[:3], 1):
            print(f"\n{i}. {paper.title}")
            print(f"   Authors: {paper.authors[:100]}...")
            print(f"   Categories: {paper.categories}")
            print(f"   arXiv ID: {paper.arxiv_id}")
