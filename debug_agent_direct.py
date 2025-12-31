import sys
import os
import logging

# Add current directory to path
sys.path.append(os.getcwd())

logging.basicConfig(level=logging.INFO)

try:
    from agent import EpisodeCompanionAgent
    print("✅ Successfully imported EpisodeCompanionAgent")
    
    agent = EpisodeCompanionAgent()
    print(f"✅ Agent initialized. LLM: {agent.llm}")
    
    print("\n--- Testing _safe_llm_call_gpk ---")
    res = agent._safe_llm_call_gpk("Say hello")
    print(f"Result: '{res}'")
    
    print("\n--- Testing _generate_quiz_questions_gpk ---")
    quiz = agent._generate_quiz_questions_gpk("This is a test context about AI.", "Quiz me", 3)
    print(f"Quiz Result: {quiz[:100]}...")
    
except Exception as e:
    print(f"\n❌ CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
