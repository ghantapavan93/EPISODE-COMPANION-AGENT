from ingest import get_vector_store

def debug_retrieval():
    episode_id = "ai-research-daily-2025-11-18"
    query = "What is Kandinsky 5.0?"
    
    print(f"Debugging retrieval for query: '{query}' in episode: {episode_id}")
    
    vs = get_vector_store()
    
    # 1. Simple Similarity Search (No filter)
    print("\n--- 1. Unfiltered Similarity Search ---")
    docs = vs.similarity_search_with_score(query, k=5)
    for doc, score in docs:
        print(f"Score: {score:.4f} | Episode: {doc.metadata.get('episode_id')} | Content: {doc.page_content[:100]}...")

    # 2. Filtered Search
    print(f"\n--- 2. Filtered Search (episode_id={episode_id}) ---")
    docs = vs.similarity_search_with_score(query, k=5, filter={"episode_id": episode_id})
    for doc, score in docs:
        print(f"Score: {score:.4f} | Content: {doc.page_content[:100]}...")
        
    if not docs:
        print("❌ No docs found with filter!")

if __name__ == "__main__":
    debug_retrieval()
