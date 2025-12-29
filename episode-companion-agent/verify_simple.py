from agent import EpisodeCompanionAgent

def verify_agent_simple():
    agent = EpisodeCompanionAgent()
    episode_id = "ai-research-daily-2025-11-20"

    print("Verifying Agent (Simple)...")
    query = "What is AI Research Daily 11/20 about?"
    try:
        resp = agent.get_answer(episode_id, "plain_english", query)
        print(f"Answer: {resp['answer']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_agent_simple()
