from ingest import get_vector_store

def check_episode_content(episode_id):
    print(f"Checking content for episode: {episode_id}")
    vs = get_vector_store()
    
    # Get all data
    data = vs._collection.get(where={"episode_id": episode_id})
    
    ids = data['ids']
    metadatas = data['metadatas']
    documents = data['documents']
    
    print(f"Found {len(ids)} chunks.")
    
    if len(ids) == 0:
        print("⚠️ No content found! This is why you get 'insufficient detail'.")
        return

    print("\n--- Searching for 'Kandinsky' ---")
    found = False
    for i, (doc, meta) in enumerate(zip(documents, metadatas)):
        if "Kandinsky" in doc:
            print(f"\nMatch found in Chunk {i+1}:")
            print(f"Metadata: {meta}")
            print(f"Content: {doc[:300]}...")
            found = True
            
    if not found:
        print("❌ 'Kandinsky' not found in any chunk text.")

if __name__ == "__main__":
    check_episode_content("ai-research-daily-2025-11-18")
