"""
Repository pattern for Conversation database operations.
Separates data access logic from business logic.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from models import Conversation
from typing import Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ConversationRepository:
    """Handles all database operations for Conversations"""
    
    def __init__(self, db: Session):
        self.db = db

    def find_by_user_and_episode(
        self,
        user_id: str,
        episode_id: str
    ) -> Optional[Conversation]:
        """
        Find existing conversation for user+episode.
        Returns None if not found.
        """
        return self.db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.episode_id == episode_id
            )
        ).first()

    def create(
        self,
        user_id: str,
        episode_id: str,
        first_question: Optional[str] = None,
        commit: bool = True
    ) -> Conversation:
        """
        Create new conversation.
        Set commit=False to defer commit for atomic transactions.
        """
        conv = Conversation(
            user_id=user_id,
            episode_id=episode_id
        )
        self.db.add(conv)
        if commit:
            self.db.commit()
        self.db.flush()  # Get ID without committing
        self.db.refresh(conv)
        
        logger.info(f"Created conversation {conv.id} for user {user_id}, episode {episode_id}")
        return conv

    def get_or_create(
        self,
        user_id: str,
        episode_id: str,
        first_question: Optional[str] = None
    ) -> Conversation:
        """
        Atomic get-or-create operation.
        Thread-safe using database constraints.
        """
        # Try to find existing
        conv = self.find_by_user_and_episode(user_id, episode_id)
        
        if conv:
            return conv
        
        # Create new (race condition handled by unique constraint)
        try:
            return self.create(user_id, episode_id, first_question)
        except Exception as e:
            # If unique constraint violated, another thread created it
            self.db.rollback()
            logger.debug(f"Race condition in get_or_create, retrying: {e}")
            
            # Retry once
            conv = self.find_by_user_and_episode(user_id, episode_id)
            if conv:
                return conv
            
            # If still None, something's wrong
            raise Exception(f"Failed to get or create conversation for {user_id}/{episode_id}")

    def update_metadata(
        self,
        conversation_id: int,
        last_mode: Optional[str] = None,
        commit: bool = True
    ):
        """
        Update conversation metadata.
        Set commit=False to defer commit for atomic transactions.
        """
        conv = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        
        if not conv:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        if last_mode:
            conv.last_mode = last_mode
        
        conv.updated_at = datetime.utcnow()
        if commit:
            self.db.commit()

    def get_last_episode_for_user(self, user_id: str) -> Optional[str]:
        """
        Get the episode_id of the user's most recent conversation.
        Useful for "continue" without specifying episode.
        """
        conv = self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(desc(Conversation.updated_at)).first()
        
        return conv.episode_id if conv else None

    def get_user_conversations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Conversation]:
        """Get user's recent conversations"""
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(desc(Conversation.updated_at)).limit(limit).all()

    def delete_old_conversations(self, days_old: int = 30) -> int:
        """
        Delete conversations older than specified days.
        Returns count of deleted conversations.
        """
        cutoff = datetime.utcnow() - timedelta(days=days_old)
        
        count = self.db.query(Conversation).filter(
            Conversation.updated_at < cutoff
        ).delete()
        
        self.db.commit()
        logger.info(f"Deleted {count} conversations older than {days_old} days")
        
        return count
