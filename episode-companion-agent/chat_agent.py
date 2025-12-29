import logging

logger = logging.getLogger(__name__)

class ChatAgent:
    """
    Placeholder for a General Chat Agent.
    Handles queries that are not specific to an episode or building.
    """
    def __init__(self):
        logger.info("ChatAgent initialized (Placeholder).")

    def get_answer(self, user_id: str, query: str):
        """
        Returns a placeholder response for general chat.
        """
        logger.info(f"ChatAgent received query from {user_id}: {query}")
        return {
            "answer": "I'm the General Chat Agent. I can help with general AI questions, but right now I'm just a placeholder. Try asking about the episode!",
            "metadata": {
                "agent": "chat_agent",
                "latency_ms": 10  # Fake latency
            }
        }
