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
    def _is_timeline_query(self, text: str) -> bool:
        """
        Detect whether the user is asking about MULTIPLE episodes.
        Only matches explicit multi-episode patterns, not within-episode comparisons.
        
        Examples that should match:
        - "compare today vs yesterday"
        - "what changed this week"
        - "show me the last 3 episodes"
        
        Examples that should NOT match:
        - "compare this paper to that one"  (within-episode)
        - "compare to the other big paper in this episode"  (within-episode)
        """
        t = text.lower()
        
        # Explicit multi-episode patterns
        multi_episode_patterns = [
            "yesterday",
            "last episode",
            "previous episode",
            "last few episodes",
            "this week",
            "past few days",
            "last 3 days",
            "across episodes",
            "over time",
            "this month",
            "timeline",
        ]
        
        # Check for explicit multi-episode keywords
        if any(pattern in t for pattern in multi_episode_patterns):
            return True
        
        # Explicitly exclude within-episode comparisons
        if "in this episode" in t or "in the episode" in t or "from this episode" in t:
            return False
        
        # Only match "compare" if it explicitly mentions episodes or time periods
        if "compare" in t and ("episode" in t or "today" in t or "week" in t):
            return True
        
        return False

    def _infer_mode_from_question(self, query: str, question_type: str) -> str:
        """
        Automatically infer the best persona mode based on question type.
        Used when mode is None or 'auto'.
        """
        MODE_MAP = {
            # Plain English
            "tldr": "plain_english",
            "explain_like_12": "plain_english",
            "analogy": "plain_english",
            "general": "plain_english",
            "summary": "plain_english",
            "relevance": "plain_english",

            # Learning Modes
            "quiz_me": "plain_english",
            "self_explain": "plain_english",

            # Founder
            "mvp": "founder_takeaway",
            "paid_product": "founder_takeaway",
            "market_fit": "founder_takeaway",
            "moat": "founder_takeaway",
            "risks": "founder_takeaway",
            "overhype_failure": "founder_takeaway",
            "role_solo_indie": "founder_takeaway",
            "role_pm_fintech": "founder_takeaway",

            # Engineer
            "prototype": "engineer_angle",
            "architecture": "engineer_angle",
            "pipeline": "engineer_angle",
            "api": "engineer_angle",
            "integration": "engineer_angle",
            "metrics": "engineer_angle",
            "experiment": "engineer_angle",
            "tradeoffs": "engineer_angle",
            "limitations": "engineer_angle",
            "role_backend_python_pg": "engineer_angle",
            "role_healthcare": "engineer_angle",
        }
        return MODE_MAP.get(question_type, "plain_english")

    def route_request(
        self,
        user_id: str,
        text: str,
        episode_id: Optional[str] = None,
        mode: Optional[str] = None,
        debug: bool = False,
        user_profile: Optional[Dict[str, str]] = None,
        db: Session = None,
    ) -> Dict[str, Any]:
        """
        Decides which agent to call based on inputs.
        Uses SQLite database for persistent state management.

        Args:
            user_id: stable user identifier
            text: user query
            episode_id: optional episode ID; if None, we auto-resume last
            mode: optional persona mode ("plain_english", "founder_takeaway", "engineer_angle")
            debug: if True, EpisodeCompanionAgent will include extra debug metadata
            user_profile: optional dict with role, domain, stack
            db: SQLAlchemy session (required)
        """
        if db is None:
            raise ValueError("DB session is required")

        manager = ConversationManager(db)

        try:
            # 1. Auto-infer mode if not provided or set to 'auto'
            if mode is None or mode == "auto":
                from behavior import classify_question
                question_type = classify_question(text)
                mode = self._infer_mode_from_question(text, question_type)
                logger.info(f"Auto-detected mode: {mode} for question_type: {question_type}")
            
            # 2. Resolve episode ID (auto-resume last if not provided)
            if not episode_id:
                episode_id = manager.get_last_episode_id(user_id)

            text_lower = text.lower()
            is_build_intent = any(
                k in text_lower for k in ["build", "create app", "scaffold", "generate code"]
            )

            # 2. Timeline / cross-episode queries (use last few episodes)
            if self._is_timeline_query(text):
                from repositories.episode_repository import EpisodeRepository
                repo = EpisodeRepository()
                recent_eps = repo.get_all_episodes(limit=5)  # latest 5 episodes
                episode_ids = [ep.episode_id for ep in recent_eps]
                if not episode_ids:
                    return {
                        "episode_id": "",
                        "mode": mode or "plain_english",
                        "answer": "I don't have enough past episodes stored to answer that yet.",
                        "metadata": {
                            "error": "no_recent_episodes",
                            "trace_id": "timeline-no-episodes",
                            "latency_ms": 0.0,
                            "stage_latency": {},
                            "used_chunks": 0,
                            "expanded_query": text,
                            "quality_checks": {},
                            "source_papers": [],
                            "tokens_in": 0,
                            "tokens_out": 0,
                            "model": "",
                            "question_type": "timeline",
                            "debug": None,
                            "suggested_followups": [],
                        },
                    }
                # default mode if not provided
                if mode is None:
                    mode = self.detect_intent(text)
                return self.episode_agent.get_timeline_answer(
                    episode_ids=episode_ids,
                    mode=mode,
                    query=text,
                    debug=debug,
                )

            # 3. No episode context → fall back to builder/chat agents
            if not episode_id:
                if is_build_intent:
                    return self.builder_agent.get_answer(user_id, text)
                else:
                    return self.chat_agent.get_answer(user_id, text)

            # 4. We DO have an episode_id → always use EpisodeCompanionAgent
            logger.info(
                f"Orchestrator routing for user={user_id}, episode_id={episode_id}, text='{text[:50]}...'"
            )

            # If mode is not explicitly provided (e.g. SMS), infer it from text
            if mode is None:
                mode = self.detect_intent(text)

            # Fetch conversation context for this user/episode
            history_str = manager.get_conversation_context(user_id, episode_id)

            # 5. Generate answer via episode companion agent
            response = self.episode_agent.get_answer(
                episode_id=episode_id,
                mode=mode,
                query=text,
                user_id=user_id,
                user_profile=user_profile,
                conversation_history=history_str,
                debug=debug,
            )

            # 6. Persist interaction
            try:
                manager.add_interaction(
                    user_id=user_id,
                    episode_id=episode_id,
                    user_query=text,
                    assistant_response=response["answer"],
                    mode_used=response.get("mode", mode),
                    metadata=response.get("metadata", {}),
                )
            except Exception as e:
                logger.error(f"Failed to persist interaction: {e}")

            return response

        except SQLAlchemyError as e:
            logger.error(f"Database error in orchestrator: {e}")
            db.rollback()
            return {
                "episode_id": episode_id or "",
                "mode": mode or "plain_english",
                "answer": "I'm experiencing database issues. Please try again in a moment.",
                "metadata": {
                    "error": "database_error",
                    "details": str(e),
                    "trace_id": "db-error",
                    "latency_ms": 0.0,
                    "stage_latency": {},
                    "used_chunks": 0,
                    "expanded_query": text,
                    "quality_checks": {},
                    "source_papers": [],
                    "tokens_in": 0,
                    "tokens_out": 0,
                    "model": "",
                    "question_type": "",
                    "debug": None,
                    "suggested_followups": [],
                },
            }
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return {
                "episode_id": episode_id or "",
                "mode": mode or "plain_english",
                "answer": "Something went wrong. Please try again.",
                "metadata": {
                    "error": str(e),
                    "trace_id": "orchestrator-error",
                    "latency_ms": 0.0,
                    "stage_latency": {},
                    "used_chunks": 0,
                    "expanded_query": text,
                    "quality_checks": {},
                    "source_papers": [],
                    "tokens_in": 0,
                    "tokens_out": 0,
                    "model": "",
                    "question_type": "",
                    "debug": None,
                    "suggested_followups": [],
                },
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
