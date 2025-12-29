"""
Business logic for managing conversations.
Uses repositories for data access, implements conversation flow logic.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from repositories.conversation_repository import ConversationRepository
from repositories.message_repository import MessageRepository
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    High-level conversation management service.
    Orchestrates repositories and implements business logic.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.conv_repo = ConversationRepository(db)
        self.msg_repo = MessageRepository(db)
        logger.info("ConversationManager initialized with repository pattern.")

    def start_or_continue_conversation(
        self,
        user_id: str,
        episode_id: str,
        first_question: Optional[str] = None
    ) -> int:
        """
        Start a new conversation or get existing one.
        Returns conversation_id.
        """
        conv = self.conv_repo.get_or_create(
            user_id=user_id,
            episode_id=episode_id,
            first_question=first_question
        )
        return conv.id

    def add_interaction(
        self,
        user_id: str,
        episode_id: str,
        user_query: str,
        assistant_response: str,
        mode_used: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record a complete interaction (question + answer) atomically.
        Updates conversation metadata automatically.
        
        All database operations are committed in a single transaction.
        """
        try:
            # 1. Get or create conversation (commits internally for get_or_create safety)
            conversation = self.conv_repo.get_or_create(
                user_id=user_id,
                episode_id=episode_id,
                first_question=user_query
            )
            
            # 2. Add messages (no commit yet)
            user_msg, assistant_msg = self.msg_repo.add_turn(
                conversation_id=conversation.id,
                user_query=user_query,
                assistant_response=assistant_response,
                meta_data=metadata,
                commit=False  # Defer commit
            )
            
            # 3. Update conversation metadata (no commit yet)
            self.conv_repo.update_metadata(
                conversation_id=conversation.id,
                last_mode=mode_used,
                commit=False  # Defer commit
            )
            
            # 4. Commit everything atomically
            self.db.commit()
            
            logger.info(f"Interaction saved atomically for user {user_id}, conv {conversation.id}")
            return conversation
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to save interaction: {e}")
            raise

    def get_conversation_context(
        self,
        user_id: str,
        episode_id: str,
        max_messages: int = 6,
        max_chars: int = 12000
    ) -> str:
        """
        Get formatted conversation history for LLM context with token safety.
        Returns empty string if no conversation exists.
        
        Args:
            max_chars: Maximum characters (~3k tokens) to prevent context overflow
        """
        conv = self.conv_repo.find_by_user_and_episode(user_id, episode_id)
        
        if not conv:
            return ""
        
        context = self.msg_repo.format_as_context(conv.id, limit=max_messages)
        
        # Token safety: truncate if too long
        if len(context) > max_chars:
            context = context[:max_chars] + "\n\n[...Older messages omitted for brevity...]"
        
        return context

    def submit_feedback(
        self,
        message_id: int,
        rating: int,
        comment: Optional[str] = None
    ):
        """
        Store user feedback for a specific message.
        
        Args:
            message_id: ID of the assistant message
            rating: -1 (bad), 0 (neutral), or 1 (good)
            comment: Optional text feedback
        """
        try:
            from models import Message
            
            msg = self.db.query(Message).filter(Message.id == message_id).first()
            
            if not msg:
                raise ValueError(f"Message {message_id} not found")
            
            # Update meta_data with feedback
            if msg.meta_data is None:
                msg.meta_data = {}
            
            msg.meta_data["feedback"] = {
                "rating": rating,
                "comment": comment
            }
            
            self.db.commit()
            logger.info(f"Feedback stored for message {message_id}: rating={rating}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to store feedback: {e}")
            raise

    def has_messages(self, user_id: str, episode_id: str) -> bool:
        """Check if conversation exists and has messages"""
        conv = self.conv_repo.find_by_user_and_episode(user_id, episode_id)
        if not conv:
            return False
        
        return self.msg_repo.get_message_count(conv.id) > 0

    def get_last_episode_id(self, user_id: str) -> Optional[str]:
        """
        Get the user's most recently updated episode.
        Useful for "continue" commands without specifying episode.
        """
        return self.conv_repo.get_last_episode_for_user(user_id)

    def cleanup_old_conversations(self, days_old: int = 30) -> int:
        """
        Delete conversations older than specified days.
        Returns count of deleted conversations.
        """
        return self.conv_repo.delete_old_conversations(days_old)
