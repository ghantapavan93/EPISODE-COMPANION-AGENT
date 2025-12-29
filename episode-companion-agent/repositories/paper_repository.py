"""
Paper Repository

Data access layer for Paper model.
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from models import Paper
from database import get_db
from arxiv_fetcher import ArxivPaper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PaperRepository:
    """Repository for Paper CRUD operations"""
    
    def __init__(self, db: Optional[Session] = None):
        """
        Initialize repository.
        
        Args:
            db: SQLAlchemy session (if None, will use get_db())
        """
        self.db = db
    
    def _get_db(self) -> Session:
        """Get database session"""
        if self.db:
            return self.db
        return next(get_db())
    
    def save_paper(self, paper: ArxivPaper) -> Paper:
        """
        Save a single paper to database.
        
        Args:
            paper: ArxivPaper object
            
        Returns:
            Saved Paper model
        """
        db = self._get_db()
        
        # Check if exists
        existing = db.query(Paper).filter(Paper.arxiv_id == paper.arxiv_id).first()
        
        if existing:
            logger.debug(f"Paper {paper.arxiv_id} already exists, updating")
            # Update
            existing.title = paper.title
            existing.authors = paper.authors
            existing.abstract = paper.abstract
            existing.categories = paper.categories
            existing.submitted_date = paper.submitted_date
            existing.pdf_url = paper.pdf_url
            existing.arxiv_url = paper.arxiv_url
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new
            db_paper = Paper(
                arxiv_id=paper.arxiv_id,
                title=paper.title,
                authors=paper.authors,
                abstract=paper.abstract,
                categories=paper.categories,
                submitted_date=paper.submitted_date,
                pdf_url=paper.pdf_url,
                arxiv_url=paper.arxiv_url
            )
            db.add(db_paper)
            db.commit()
            db.refresh(db_paper)
            logger.debug(f"Saved paper {paper.arxiv_id}")
            return db_paper
    
    def save_papers(self, papers: List[ArxivPaper]) -> List[Paper]:
        """
        Save multiple papers to database.
        
        Args:
            papers: List of ArxivPaper objects
            
        Returns:
            List of saved Paper models
        """
        logger.info(f"Saving {len(papers)} papers to database")
        saved = []
        for paper in papers:
            saved.append(self.save_paper(paper))
        logger.info(f"Saved {len(saved)} papers")
        return saved
    
    def get_paper_by_arxiv_id(self, arxiv_id: str) -> Optional[Paper]:
        """
        Get paper by arXiv ID.
        
        Args:
            arxiv_id: arXiv ID (e.g., "2511.14993")
            
        Returns:
            Paper model or None
        """
        db = self._get_db()
        return db.query(Paper).filter(Paper.arxiv_id == arxiv_id).first()
    
    def get_papers_by_date(self, date: str) -> List[Paper]:
        """
        Get all papers submitted on a specific date.
        
        Args:
            date: Date string "YYYY-MM-DD"
            
        Returns:
            List of Paper models
        """
        db = self._get_db()
        return db.query(Paper).filter(Paper.submitted_date == date).all()
    
    def get_papers_by_date_range(self, start_date: str, end_date: str) -> List[Paper]:
        """
        Get papers in a date range.
        
        Args:
            start_date: Start date "YYYY-MM-DD"
            end_date: End date "YYYY-MM-DD"
            
        Returns:
            List of Paper models
        """
        db = self._get_db()
        return db.query(Paper).filter(
            Paper.submitted_date >= start_date,
            Paper.submitted_date <= end_date
        ).all()


if __name__ == "__main__":
    # Test
    from arxiv_fetcher import fetch_papers_by_date
    
    print("Testing PaperRepository...")
    
    # Fetch some papers
    papers = fetch_papers_by_date("2025-11-19", max_results=10)
    print(f"Fetched {len(papers)} papers")
    
    # Save to DB
    repo = PaperRepository()
    saved = repo.save_papers(papers)
    print(f"Saved {len(saved)} papers to database")
    
    # Retrieve
    retrieved = repo.get_papers_by_date("2025-11-19")
    print(f"Retrieved {len(retrieved)} papers from database")
    
    if retrieved:
        print(f"\nFirst paper: {retrieved[0].title}")
