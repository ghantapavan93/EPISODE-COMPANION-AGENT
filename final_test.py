import logging
from agent import EpisodeCompanionAgent
from behavior import classify_question

# Simpler output
logging.basicConfig(level=logging.WARNING)

query = "explain this episode to me like I'm 12 years old"
episode_id = "ai-research-daily-2025-11-20"
mode = "plain_english"

print("Testing:", query[:50])

# Classify
question_type = classify_question(query)
print("Question type:", question_type)

# Get answer
agent = EpisodeCompanionAgent()
response = agent.get_answer(
    episode_id=episode_id,
    mode=mode,
    query=query,
    debug=False
)

print("Answer length:", len(response['answer']))

# Check for insufficient message
if "does not give enough detail" in response['answer']:
    print("FAIL - Returned INSUFFICIENT_MSG")
else:
    print("SUCCESS - Generated answer!")
    # Strip HTML to see text preview
    import re
    text_only = re.sub(r'<[^>]+>', '', response['answer'])
    print("Preview:", text_only[:200])
