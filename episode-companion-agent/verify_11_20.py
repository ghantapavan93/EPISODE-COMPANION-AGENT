from agent import EpisodeCompanionAgent

def verify_agent():
    agent = EpisodeCompanionAgent()
    episode_id = "ai-research-daily-2025-11-20"

    print("Verifying Agent for 11/20 Episode...\n")

    # Test 1: Plain English
    print("--- Test 1: Plain English ---")
    query = "What is AI Research Daily 11/20 about in simple terms?"
    try:
        resp = agent.get_answer(episode_id, "plain_english", query)
        print(f"Answer: {resp['answer']}")
        print(f"Used Chunks: {resp['metadata']['used_chunks']}")
    except Exception as e:
        print(f"Error: {e}")
    print("\n")

    # Test 2: Founder Takeaway
    print("--- Test 2: Founder Takeaway ---")
    query = "If I’m a founder, what should I care about from today’s episode?"
    try:
        resp = agent.get_answer(episode_id, "founder_takeaway", query)
        print(f"Answer: {resp['answer']}")
        print(f"Used Chunks: {resp['metadata']['used_chunks']}")
    except Exception as e:
        print(f"Error: {e}")
    print("\n")

    # Test 3: Engineer Angle
    print("--- Test 3: Engineer Angle ---")
    query = "What should I try implementing from Kandinsky 5.0 or VISPLAY?"
    try:
        resp = agent.get_answer(episode_id, "engineer_angle", query)
        print(f"Answer: {resp['answer']}")
        print(f"Used Chunks: {resp['metadata']['used_chunks']}")
    except Exception as e:
        print(f"Error: {e}")
    print("\n")

if __name__ == "__main__":
    verify_agent()
