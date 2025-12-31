"""
Unit tests for repository layer.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from database import Base
from models import Conversation, Message
from repositories.conversation_repository import ConversationRepository
from repositories.message_repository import MessageRepository


@pytest.fixture
def test_db():
    """Create in-memory test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestConversationRepository:
    
    def test_create_conversation(self, test_db):
        repo = ConversationRepository(test_db)
        
        conv = repo.create(
            user_id="user123",
            episode_id="ep-001"
        )
        
        assert conv.id is not None
        assert conv.user_id == "user123"
        assert conv.episode_id == "ep-001"
    
    def test_find_by_user_and_episode(self, test_db):
        repo = ConversationRepository(test_db)
        
        # Create conversation
        conv1 = repo.create("user123", "ep-001")
        
        # Find it
        conv2 = repo.find_by_user_and_episode("user123", "ep-001")
        
        assert conv2 is not None
        assert conv1.id == conv2.id
    
    def test_find_nonexistent_returns_none(self, test_db):
        repo = ConversationRepository(test_db)
        
        conv = repo.find_by_user_and_episode("nobody", "ep-999")
        
        assert conv is None
    
    def test_get_or_create_creates_new(self, test_db):
        repo = ConversationRepository(test_db)
        
        conv = repo.get_or_create("user123", "ep-001")
        
        assert conv.id is not None
        assert test_db.query(Conversation).count() == 1
    
    def test_get_or_create_returns_existing(self, test_db):
        repo = ConversationRepository(test_db)
        
        # First call creates
        conv1 = repo.get_or_create("user123", "ep-001")
        
        # Second call returns same
        conv2 = repo.get_or_create("user123", "ep-001")
        
        assert conv1.id == conv2.id
        assert test_db.query(Conversation).count() == 1
    
    def test_get_last_episode_for_user(self, test_db):
        repo = ConversationRepository(test_db)
        
        # Create multiple conversations
        conv1 = repo.create("user123", "ep-001")
        conv2 = repo.create("user123", "ep-002")
        conv3 = repo.create("user123", "ep-003")
        
        # Update timestamps manually
        conv1.updated_at = datetime.utcnow() - timedelta(hours=2)
        conv2.updated_at = datetime.utcnow() - timedelta(hours=1)
        conv3.updated_at = datetime.utcnow()
        test_db.commit()
        
        last_episode = repo.get_last_episode_for_user("user123")
        
        assert last_episode == "ep-003"
    
    def test_delete_old_conversations(self, test_db):
        repo = ConversationRepository(test_db)
        
        # Create old and new conversations
        old_conv = repo.create("user123", "ep-old")
        new_conv = repo.create("user123", "ep-new")
        
        # Make one old
        old_conv.updated_at = datetime.utcnow() - timedelta(days=31)
        test_db.commit()
        
        # Delete conversations older than 30 days
        deleted_count = repo.delete_old_conversations(days_old=30)
        
        assert deleted_count == 1
        assert test_db.query(Conversation).count() == 1


class TestMessageRepository:
    
    def test_create_message(self, test_db):
        # Setup conversation
        conv_repo = ConversationRepository(test_db)
        conv = conv_repo.create("user123", "ep-001")
        
        # Create message
        msg_repo = MessageRepository(test_db)
        msg = msg_repo.create(
            conversation_id=conv.id,
            role="user",
            content="What is AI?"
        )
        
        assert msg.id is not None
        assert msg.conversation_id == conv.id
        assert msg.role == "user"
        assert msg.content == "What is AI?"
    
    def test_add_turn(self, test_db):
        # Setup
        conv_repo = ConversationRepository(test_db)
        conv = conv_repo.create("user123", "ep-001")
        
        msg_repo = MessageRepository(test_db)
        
        # Add turn
        user_msg, assistant_msg = msg_repo.add_turn(
            conversation_id=conv.id,
            user_query="What is AI?",
            assistant_response="AI is artificial intelligence."
        )
        
        assert user_msg.role == "user"
        assert user_msg.content == "What is AI?"
        assert assistant_msg.role == "assistant"
        assert assistant_msg.content == "AI is artificial intelligence."
    
    def test_format_as_context(self, test_db):
        # Setup
        conv_repo = ConversationRepository(test_db)
        conv = conv_repo.create("user123", "ep-001")
        
        msg_repo = MessageRepository(test_db)
        
        # Add turns
        msg_repo.add_turn(
            conversation_id=conv.id,
            user_query="What is AI?",
            assistant_response="AI is artificial intelligence."
        )
        
        # Format as context
        context = msg_repo.format_as_context(conv.id, limit=4)
        
        assert "Previous conversation:" in context
        assert "User: What is AI?" in context
        assert "Assistant: AI is artificial intelligence." in context
