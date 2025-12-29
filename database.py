"""
Database configuration and session management.
Production-ready with connection pooling, monitoring, and proper lifecycle.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, declarative_base
import time
import logging
import os

logger = logging.getLogger(__name__)

# ANTIGRAVITY: No server to install. It just creates a file.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./episode_companion.db")

# PRO FIX: Added connection timeout to prevent locking errors
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False, "timeout": 15},
    echo=os.getenv("SQL_ECHO", "false").lower() == "true"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================================
# Performance Monitoring
# ============================================================================

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track query start time"""
    conn.info.setdefault('query_start_time', []).append(time.time())
    logger.debug(f"Starting query: {statement[:100]}...")


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries"""
    total = time.time() - conn.info['query_start_time'].pop(-1)
    
    if total > 0.1:  # Queries slower than 100ms
        logger.warning(
            f"⚠️ Slow query detected ({total:.3f}s): {statement[:200]}...",
            extra={"duration": total, "statement": statement}
        )
    else:
        logger.debug(f"Query completed in {total:.3f}s")


# ============================================================================
# Dependency Injection for FastAPI
# ============================================================================

# PRO FIX: This Generator is crucial for FastAPI Dependency Injection
def get_db():
    """
    FastAPI dependency for database sessions.
    Ensures proper cleanup even on errors.
    
    Usage:
        @app.post("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db here
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# ============================================================================
# Database Initialization
# ============================================================================

def init_db():
    """
    Initialize database tables.
    NOTE: In production, use Alembic migrations instead.
    """
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def check_db_connection():
    """
    Verify database connectivity on startup.
    Returns True if successful, False otherwise.
    """
    from sqlalchemy import text
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection verified")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
