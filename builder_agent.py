class BuilderAgent:
    def get_answer(self, user_id: str, text: str):
        return {
            "answer": "I am a builder agent. I can help you scaffold apps.",
            "metadata": {"agent": "builder"}
        }
