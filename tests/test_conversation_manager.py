"""
Unit tests for ConversationManager service layer.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from conversation_manager import ConversationManager


@pytest.fixture
def test_db():
    """Create in-memory test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestConversationManager:
    
    def test_start_or_continue_creates_new(self, test_db):
        manager = ConversationManager(test_db)
        
        conv_id = manager.start_or_continue_conversation(
            user_id="user123",
            episode_id="ep-001"
        )
        
        assert conv_id is not None
        assert isinstance(conv_id, int)
    
    def test_start_or_continue_returns_existing(self, test_db):
        manager = ConversationManager(test_db)
        
        # First call
        conv_id1 = manager.start_or_continue_conversation("user123", "ep-001")
        
        # Second call
        conv_id2 = manager.start_or_continue_conversation("user123", "ep-001")
        
        assert conv_id1 == conv_id2
    
    def test_add_interaction_creates_messages(self, test_db):
        manager = ConversationManager(test_db)
        
        result = manager.add_interaction(
            user_id="user123",
            episode_id="ep-001",
            user_query="What is AI?",
            assistant_response="AI is artificial intelligence.",
            mode_used="plain_english"
        )
        
        assert result["conversation_id"] is not None
        assert result["user_message_id"] is not None
        assert result["assistant_message_id"] is not None
    
    def test_get_conversation_context_empty(self, test_db):
        manager = ConversationManager(test_db)
        
        context = manager.get_conversation_context("user123", "ep-001")
        
        assert context == ""
    
    def test_get_conversation_context_with_history(self, test_db):
        manager = ConversationManager(test_db)
        
        # Add interaction
        manager.add_interaction(
            user_id="user123",
            episode_id="ep-001",
            user_query="What is AI?",
            assistant_response="AI is artificial intelligence.",
            mode_used="plain_english"
        )
        
        # Get context
        context = manager.get_conversation_context("user123", "ep-001")
        
        assert "Previous conversation:" in context
        assert "What is AI?" in context
        assert "AI is artificial intelligence." in context
    
    def test_has_messages(self, test_db):
        manager = ConversationManager(test_db)
        
        # Before adding
        assert manager.has_messages("user123", "ep-001") is False
        
        # Add interaction
        manager.add_interaction(
            user_id="user123",
            episode_id="ep-001",
            user_query="Test",
            assistant_response="Response",
            mode_used="plain_english"
        )
        
        # After adding
        assert manager.has_messages("user123", "ep-001") is True
    
    def test_cleanup_old_conversations(self, test_db):
        manager = ConversationManager(test_db)
        
        # Create conversation
        manager.add_interaction("user123", "ep-001", "Q1", "A1", "plain_english")
        
        # Cleanup (won't delete recent conversations)
        deleted = manager.cleanup_old_conversations(days_old=30)
        
        assert deleted == 0  # Nothing older than 30 days
