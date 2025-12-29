from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    episode_id = Column(String, index=True)
    
    # "Antigravity" feature: Remembers the last persona used (Founder, Engineer, etc.)
    last_mode = Column(String, default="plain_english") 
    
    # Auto-timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    # PRO FIX: Composite Index. Makes finding history 100x faster as table grows.
    __table_args__ = (
        Index('idx_user_episode', 'user_id', 'episode_id'),
    )

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    
    role = Column(String) # "user" or "assistant"
    content = Column(Text)
    
    # Future-proof: Store retrieval stats, quality checks, or sources here
    meta_data = Column(JSON, nullable=True) 
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")

class Paper(Base):
    """Stores fetched arXiv papers"""
    __tablename__ = "papers"
    
    arxiv_id = Column(String, primary_key=True, index=True)  # e.g. "2511.14993"
    title = Column(String, nullable=False)
    authors = Column(Text, nullable=True)  # JSON array or comma-separated
    abstract = Column(Text, nullable=True)
    categories = Column(String, nullable=True)  # e.g. "cs.AI,cs.LG"
    submitted_date = Column(String, nullable=True)  # "2025-11-19"
    pdf_url = Column(String, nullable=True)
    arxiv_url = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    __table_args__ = (
        Index('idx_submitted_date', 'submitted_date'),
    )

class Episode(Base):
    """Stores generated daily episodes"""
    __tablename__ = "episodes"
    
    episode_id = Column(String, primary_key=True, index=True)  # e.g. "ai-research-daily-2025-11-19"
    date_str = Column(String, nullable=False, index=True)  # "2025-11-19"
    total_submissions = Column(Integer, default=0)  # Total papers fetched
    selected_count = Column(Integer, default=0)  # Top K papers selected
    report_text = Column(Text, nullable=True)  # Full generated report
    episode_metadata = Column(JSON, nullable=True)  # Stats, categories, etc. (renamed from 'metadata')
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    __table_args__ = (
        Index('idx_date', 'date_str'),
    )
