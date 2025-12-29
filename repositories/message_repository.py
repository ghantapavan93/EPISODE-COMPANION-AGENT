"""
Repository pattern for Message database operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import Message
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class MessageRepository:
    """Handles all database operations for Messages"""
    
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        conversation_id: int,
        role: str,
        content: str,
        meta_data: Optional[dict] = None,
        commit: bool = True
    ) -> Message:
        """Create a new message. Set commit=False for atomic transactions."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            meta_data=meta_data
        )
        self.db.add(message)
        if commit:
            self.db.commit()
        self.db.flush()  # Get ID without committing
        self.db.refresh(message)
        
        return message

    def add_turn(
        self,
        conversation_id: int,
        user_query: str,
        assistant_response: str,
        meta_data: Optional[dict] = None,
        commit: bool = True
    ) -> tuple[Message, Message]:
        """
        Add a complete turn (user question + assistant response).
        Returns (user_message, assistant_message).
        Set commit=False for atomic transactions.
        """
        # Create user message (no commit yet)
        user_msg = self.create(
            conversation_id=conversation_id,
            role="user",
            content=user_query,
            commit=False
        )
        
        # Create assistant message with metadata (no commit yet)
        assistant_msg = self.create(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_response,
            meta_data=meta_data,
            commit=False
        )
        
        if commit:
            self.db.commit()
        
        logger.debug(f"Added turn to conversation {conversation_id}")
        return user_msg, assistant_msg

    def get_recent_messages(
        self,
        conversation_id: int,
        limit: int = 10
    ) -> List[Message]:
        """
        Get most recent messages for a conversation.
        Returns in chronological order (oldest first).
        """
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.timestamp)).limit(limit).all()
        
        # Reverse to chronological order
        return messages[::-1]

    def get_message_count(self, conversation_id: int) -> int:
        """Get total message count for conversation"""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).count()

    def format_as_context(
        self,
        conversation_id: int,
        limit: int = 6
    ) -> str:
        """
        Format recent messages as context string for LLM.
        """
        messages = self.get_recent_messages(conversation_id, limit)
        
        if not messages:
            return ""
        
        context_lines = ["Previous conversation:"]
        for msg in messages:
            role_title = "User" if msg.role == "user" else "Assistant"
            context_lines.append(f"{role_title}: {msg.content}")
        
        return "\n".join(context_lines)
