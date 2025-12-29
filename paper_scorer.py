"""
Paper Scoring and Ranking Module

Scores papers based on heuristics:
- Field popularity (cs.CV, cs.AI, cs.LG preferred)
- Author collaboration (more authors = higher score)
- Abstract quality (length, completeness)
"""

import logging
from typing import List
from arxiv_fetcher import ArxivPaper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Field popularity weights
CATEGORY_WEIGHTS = {
    "cs.CV": 1.5,   # Computer Vision (very popular)
    "cs.AI": 1.4,   # Artificial Intelligence
    "cs.LG": 1.3,   # Machine Learning
    "cs.CL": 1.2,   # Computation and Language (NLP)
    "cs.NE": 1.1,   # Neural and Evolutionary Computing
    "cs.RO": 1.0,   # Robotics
    "cs.HC": 0.9,   # Human-Computer Interaction
    "stat.ML": 1.2, # Machine Learning (Statistics)
}

DEFAULT_WEIGHT = 0.8


class PaperScorer:
    """Scores and ranks papers"""
    
    def __init__(self, category_weights: dict = None):
        """
        Initialize scorer with category weights.
        
        Args:
            category_weights: Dictionary mapping categories to weights
        """
        self.category_weights = category_weights or CATEGORY_WEIGHTS
    
    def score_paper(self, paper: ArxivPaper) -> float:
        """
        Calculate score for a single paper.
        
        Args:
            paper: ArxivPaper object
            
        Returns:
            Score (float, higher is better)
        """
        score = 0.0
        
        # 1. Field popularity score (max 1.5)
        categories = [cat.strip() for cat in paper.categories.split(",")]
        category_score = max(
            [self.category_weights.get(cat, DEFAULT_WEIGHT) for cat in categories]
        )
        score += category_score
        
        # 2. Collaboration score (0.0 - 1.0)
        # More authors = more collaboration (capped at 10 authors)
        author_count = len([a.strip() for a in paper.authors.split(",") if a.strip()])
        collaboration_score = min(author_count / 10.0, 1.0)
        score += collaboration_score
        
        # 3. Abstract quality score (0.0 - 1.0)
        # Longer abstracts tend to be more comprehensive
        # Typical abstract is 150-300 words, ~1000-2000 chars
        abstract_len = len(paper.abstract)
        if abstract_len >= 1500:
            quality_score = 1.0
        elif abstract_len >= 1000:
            quality_score = 0.8
        elif abstract_len >= 500:
            quality_score = 0.6
        else:
            quality_score = 0.4
        score += quality_score
        
        logger.debug(
            f"Paper: {paper.title[:50]}... | "
            f"Category: {category_score:.2f} | "
            f"Collab: {collaboration_score:.2f} | "
            f"Quality: {quality_score:.2f} | "
            f"Total: {score:.2f}"
        )
        
        return score
    
    def rank_papers(self, papers: List[ArxivPaper], top_k: int = 7) -> List[ArxivPaper]:
        """
        Rank papers by score and return top K.
        
        Args:
            papers: List of ArxivPaper objects
            top_k: Number of top papers to return
            
        Returns:
            List of top K papers, sorted by score descending
        """
        logger.info(f"Ranking {len(papers)} papers, selecting top {top_k}")
        
        # Score all papers
        scored_papers = [(self.score_paper(p), p) for p in papers]
        
        # Sort by score descending
        scored_papers.sort(key=lambda x: x[0], reverse=True)
        
        # Return top K papers
        top_papers = [p for score, p in scored_papers[:top_k]]
        
        logger.info(f"Top {len(top_papers)} papers selected")
        if top_papers:
            logger.info(f"Top paper: {top_papers[0].title}")
            logger.info(f"Score range: {scored_papers[0][0]:.2f} - {scored_papers[min(top_k-1, len(scored_papers)-1)][0]:.2f}")
        
        return top_papers


def score_paper(paper: ArxivPaper) -> float:
    """
    Convenience function to score a single paper.
    
    Args:
        paper: ArxivPaper object
        
    Returns:
        Score (float)
    """
    scorer = PaperScorer()
    return scorer.score_paper(paper)


def rank_papers(papers: List[ArxivPaper], top_k: int = 7) -> List[ArxivPaper]:
    """
    Convenience function to rank papers.
    
    Args:
        papers: List of ArxivPaper objects
        top_k: Number of top papers to return
        
    Returns:
        List of top K papers
    """
    scorer = PaperScorer()
    return scorer.rank_papers(papers, top_k)


if __name__ == "__main__":
    # Test with mock data
    from arxiv_fetcher import fetch_papers_by_date
    import sys
    
    if len(sys.argv) > 1:
        test_date = sys.argv[1]
    else:
        test_date = "2025-11-19"
    
    print(f"Fetching and ranking papers for {test_date}...")
    papers = fetch_papers_by_date(test_date, max_results=100)
    
    if papers:
        print(f"\nFetched {len(papers)} papers")
        top_papers = rank_papers(papers, top_k=7)
        
        print(f"\n🌟 Top {len(top_papers)} Papers:\n")
        for i, paper in enumerate(top_papers, 1):
            score = score_paper(paper)
            print(f"{i}. {paper.title}")
            print(f"   Score: {score:.2f}")
            print(f"   Categories: {paper.categories}")
            print(f"   Authors: {len(paper.authors.split(','))} authors")
            print()
