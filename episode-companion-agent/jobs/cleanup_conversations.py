"""
Background job to clean up old conversations.
Can be run as a cron job or scheduled task.
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_db, SessionLocal
from conversation_manager import ConversationManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cleanup_old_conversations(days_old: int = 30):
    """Delete conversations older than specified days"""
    logger.info(f"Starting conversation cleanup (>{days_old} days old)...")
    
    try:
        db = SessionLocal()
        try:
            manager = ConversationManager(db)
            deleted_count = manager.cleanup_old_conversations(days_old=days_old)
            logger.info(f"✅ Cleanup completed: {deleted_count} conversations deleted")
            return deleted_count
        finally:
            db.close()
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}", exc_info=True)
        return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up old conversations")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Delete conversations older than this many days (default: 30)"
    )
    
    args = parser.parse_args()
    
    # Run cleanup
    deleted = cleanup_old_conversations(days_old=args.days)
    print(f"Deleted {deleted} old conversations")
