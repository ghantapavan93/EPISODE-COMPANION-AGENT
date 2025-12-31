from ingest import get_vector_store

def check_data():
    print("Checking vector store content...")
    vs = get_vector_store()
    
    # Query for the episode ID
    results = vs.similarity_search("physics olympiad", k=3, filter={"episode_id": "ai-research-daily-2025-11-18"})
    
    print(f"Found {len(results)} results for 'physics olympiad' in episode 11/18:")
    for doc in results:
        print(f"- {doc.page_content[:100]}...")

if __name__ == "__main__":
    check_data()
