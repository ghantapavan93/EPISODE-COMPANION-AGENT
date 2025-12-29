import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from agent import EpisodeCompanionAgent
from chat_agent import ChatAgent
from builder_agent import BuilderAgent
from conversation_manager import ConversationManager

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Layer B: Orchestrator / Brain
    Routes messages to the appropriate specialist agent based on intent and context.
    Now with SQLite persistence via Dependency Injection!
    """
    def __init__(self):
        self.episode_agent = EpisodeCompanionAgent()
        self.chat_agent = ChatAgent()
        self.builder_agent = BuilderAgent()
        logger.info("Orchestrator initialized with DB persistence.")

    def route_request(self, user_id: str, text: str, episode_id: Optional[str] = None, db: Session = None) -> Dict[str, Any]:
        """
        Decides which agent to call based on inputs.
        Uses SQLite database for persistent state management.
        PRO FIX: Now accepts DB session as parameter for proper dependency injection.
        """
        if db is None:
            raise ValueError("DB session is required")
            
        manager = ConversationManager(db)
        
        try:
            # 2. RESOLVE EPISODE ID
            if not episode_id:
                # Magic: Auto-resume last conversation
                episode_id = manager.get_last_episode_id(user_id)
                
            if not episode_id:
                # No episode context, check intent
                text_lower = text.lower()
                is_build_intent = any(k in text_lower for k in ["build", "create app", "scaffold", "generate code"])
                
                if is_build_intent:
                    return self.builder_agent.get_answer(user_id, text)
                else:
                    return self.chat_agent.get_answer(user_id, text)

            logger.info(f"Orchestrator routing for user={user_id}, episode_id={episode_id}, text='{text[:50]}...'")

            # 3. INTENT CLASSIFICATION
            text_lower = text.lower()
            is_build_intent = any(k in text_lower for k in ["build", "create app", "scaffold", "generate code"])
            
            if is_build_intent:
                return self.builder_agent.get_answer(user_id, text)
            
            # 4. EPISODE AGENT - Get mode and history
            mode = self.detect_intent(text)
            history_str = manager.get_conversation_context(user_id, episode_id)
            
            # 5. GENERATE ANSWER
            response = self.episode_agent.get_answer(
                episode_id, 
                mode, 
                text, 
                user_id=user_id, 
                conversation_history=history_str
            )
            
            # 6. SAVE STATE (Persistence!)
            manager.add_interaction(
                user_id=user_id,
                episode_id=episode_id,
                user_query=text,
                assistant_response=response["answer"],
                mode_used=response.get("mode", mode),
                metadata=response.get("metadata", {})
            )
            
            return response

        except SQLAlchemyError as e:
            logger.error(f"Database error in orchestrator: {e}")
            db.rollback()
            return {
                "answer": "I'm experiencing database issues. Please try again in a moment.",
                "metadata": {"error": "database_error", "details": str(e)}
            }
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return {
                "answer": "Something went wrong. Please try again.",
                "metadata": {"error": str(e)}
            }

    def detect_intent(self, text: str) -> str:
        """
        Smart intent detection to choose the best persona.
        """
        text_lower = text.lower()
        
        # Keywords for each mode
        founder_keywords = ["build", "startup", "market", "opportunity", "product", "business", "idea", "sell", "money", "cost"]
        engineer_keywords = ["implement", "code", "architecture", "train", "benchmark", "stack", "tech", "how to", "latency", "gpu"]
        explain_keywords = ["explain", "what is", "how does", "understand", "simple", "summary"]
        
        # Check for matches
        # Priority: Engineer > Founder > Plain English (default)
        
        if any(k in text_lower for k in engineer_keywords):
            return "engineer_angle"
        elif any(k in text_lower for k in founder_keywords):
            return "founder_takeaway"
        else:
            return "plain_english"
