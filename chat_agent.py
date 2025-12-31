class ChatAgent:
    def get_answer(self, user_id: str, text: str):
        return {
            "answer": "I am a general chat agent. I don't have specific episode context.",
            "metadata": {"agent": "chat"}
        }
