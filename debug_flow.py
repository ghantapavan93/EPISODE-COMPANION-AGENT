import logging
from agent import EpisodeCompanionAgent
from behavior import classify_question, get_policy

# Configure logging to see what's happening
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_query_flow():
    """Debug the full flow for the problematic query."""
    
    query = "explain this episode to me like I'm 12 years old"
    episode_id = "ai-research-daily-2025-11-20"
    mode = "plain_english"
    
    print("=" * 80)
    print(f"DEBUGGING QUERY: '{query}'")
    print("=" * 80)
    
    # Step 1: Classify question
    question_type = classify_question(query)
    print(f"\n1. Question Classification: {question_type}")
    
    # Step 2: Get policy
    policy = get_policy(mode, question_type)
    print(f"\n2. Policy for mode '{mode}' and type '{question_type}':")
    print(f"   - Min words: {policy.min_words}, Max words: {policy.max_words}")
    print(f"   - Sections: {policy.include_sections}")
    print(f"   - Tone: {policy.tone_instruction}")
    
    # Step 3: Initialize agent and check query expansion
    agent = EpisodeCompanionAgent()
    expanded = agent._expand_query(query, episode_id)
    print(f"\n3. Query Expansion:")
    print(f"   - Original: {query}")
    print(f"   - Expanded: {expanded}")
    
    # Step 4: Try retrieval
    print(f"\n4. Testing Retrieval...")
    docs = agent._retrieve_gpk(episode_id, expanded, k=5)
    print(f"   - Retrieved {len(docs)} documents")
    if docs:
        print(f"   - First doc preview: {docs[0].page_content[:200]}...")
        print(f"   - First doc metadata: {docs[0].metadata}")
    
    # Step 5: Run full answer generation
    print(f"\n5. Running Full Answer Generation...")
    response = agent.get_answer(
        episode_id=episode_id,
        mode=mode,
        query=query,
        debug=True
    )
    
    print(f"\n6. RESPONSE:")
    print(f"   - Answer length: {len(response['answer'])}")
    print(f"   - Quality checks: {response['metadata'].get('quality_checks', {})}")
    print(f"   - Question type in metadata: {response['metadata'].get('question_type')}")
    
    # Check for insufficient message
    if "does not give enough detail" in response['answer']:
        print(f"\n   ⚠️ PROBLEM: Returned INSUFFICIENT_MSG")
        print(f"   - Checking why...")
        
        # Check if grounding failed
        checks = response['metadata'].get('quality_checks', {})
        if checks.get('grounding_failed'):
            print(f"   - Grounding failed: {checks.get('reason')}")
        if checks.get('hallucination_guardrail_triggered'):
            print(f"   - Hallucination guardrail triggered")
    else:
        print(f"\n   ✅ SUCCESS: Generated valid answer")
        print(f"   - Answer preview:\n{response['answer'][:500]}...")

if __name__ == "__main__":
    debug_query_flow()
