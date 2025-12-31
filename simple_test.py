import logging
import sys
from agent import EpisodeCompanionAgent
from behavior import classify_question

# Simpler output to avoid encoding issues
logging.basicConfig(level=logging.WARNING)

query = "explain this episode to me like I'm 12 years old"
episode_id = "ai-research-daily-2025-11-20"
mode = "plain_english"

print("Testing query:", query)
print()

# Classify
question_type = classify_question(query)
print("Question type:", question_type)

# Initialize agent
agent = EpisodeCompanionAgent()

# Expand query
expanded = agent._expand_query(query, episode_id)
print("Expanded query:", expanded)
print()

# Get answer
response = agent.get_answer(
    episode_id=episode_id,
    mode=mode,
    query=query,
    debug=False
)

print("Answer length:", len(response['answer']))
print()

# Check for insufficient message
if "does not give enough detail" in response['answer']:
    print("STATUS: FAILED - Returned INSUFFICIENT_MSG")
    checks = response['metadata'].get('quality_checks', {})
    print("Quality checks:", checks)
    
    # Print why it failed
    if checks.get('grounding_failed'):
        print("Reason: Grounding failed -", checks.get('reason'))
    if checks.get('hallucination_guardrail_triggered'):
        print("Reason: Hallucination guardrail triggered")
else:
    print("STATUS: SUCCESS - Generated valid answer")
    print()
    print("Answer preview:")
    print(response['answer'][:400])
