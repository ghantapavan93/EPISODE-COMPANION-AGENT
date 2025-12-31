"""
Episode Repository

Data access layer for Episode model.
"""

import logging
import json
from typing import Optional, List
from sqlalchemy.orm import Session
from models import Episode
from database import get_db
from ingest import EpisodeBundleGpk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EpisodeRepository:
    """Repository for Episode CRUD operations"""
    
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
    
    def save_episode(self, bundle: EpisodeBundleGpk, total_submissions: int = 0) -> Episode:
        """
        Save episode bundle to database.
        
        Args:
            bundle: EpisodeBundleGpk object
            total_submissions: Total papers fetched
            
        Returns:
            Saved Episode model
        """
        db = self._get_db()
        
        # Build metadata
        metadata = {
            "papers": [
                {
                    "title": p.title,
                    "url": p.url,
                    "rank": p.rank,
                    "in_audio": p.in_audio
                }
                for p in bundle.papers
            ],
            "hook": bundle.hook,
            "listen_url": bundle.listen_url,
        }
        
        # Check if exists
        existing = db.query(Episode).filter(Episode.episode_id == bundle.episode_id).first()
        
        if existing:
            logger.debug(f"Episode {bundle.episode_id} already exists, updating")
            # Update
            existing.date_str = bundle.date_str
            existing.total_submissions = total_submissions
            existing.selected_count = len(bundle.papers)
            existing.report_text = bundle.full_report
            existing.episode_metadata = metadata
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new
            db_episode = Episode(
                episode_id=bundle.episode_id,
                date_str=bundle.date_str,
                total_submissions=total_submissions,
                selected_count=len(bundle.papers),
                report_text=bundle.full_report,
                episode_metadata=metadata
            )
            db.add(db_episode)
            db.commit()
            db.refresh(db_episode)
            logger.debug(f"Saved episode {bundle.episode_id}")
            return db_episode
    
    def get_episode_by_id(self, episode_id: str) -> Optional[Episode]:
        """
        Get episode by ID.
        
        Args:
            episode_id: Episode ID (e.g., "ai-research-daily-2025-11-19")
            
        Returns:
            Episode model or None
        """
        db = self._get_db()
        return db.query(Episode).filter(Episode.episode_id == episode_id).first()
    
    def get_episode_by_date(self, date: str) -> Optional[Episode]:
        """
        Get episode by date.
        
        Args:
            date: Date string "YYYY-MM-DD"
            
        Returns:
            Episode model or None
        """
        db = self._get_db()
        return db.query(Episode).filter(Episode.date_str == date).first()
    
    def get_all_episodes(self, limit: int = 100) -> List[Episode]:
        """
        Get all episodes, ordered by date descending.
        
        Args:
            limit: Maximum number to return
            
        Returns:
            List of Episode models
        """
        db = self._get_db()
        return db.query(Episode).order_by(Episode.date_str.desc()).limit(limit).all()
    
    def delete_episode(self, episode_id: str) -> bool:
        """
        Delete episode by ID.
        
        Args:
            episode_id: Episode ID
            
        Returns:
            True if deleted, False if not found
        """
        db = self._get_db()
        episode = db.query(Episode).filter(Episode.episode_id == episode_id).first()
        if episode:
            db.delete(episode)
            db.commit()
            logger.info(f"Deleted episode {episode_id}")
            return True
        return False


if __name__ == "__main__":
    # Test
    print("Testing EpisodeRepository...")
    
    repo = EpisodeRepository()
    
    # Get all episodes
    episodes = repo.get_all_episodes()
    print(f"Found {len(episodes)} episodes in database")
    
    for ep in episodes:
        print(f"- {ep.episode_id} ({ep.date_str}): {ep.selected_count} papers")
