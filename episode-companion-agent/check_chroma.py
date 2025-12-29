import chromadb
from pathlib import Path

# Connect to ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

# Get all collections
collections = client.list_collections()
print(f"Collections: {[c.name for c in collections]}")

# Get the collection
if collections:
    collection = client.get_collection("episode_scripts")
    
    # Get all data
    data = collection.get()
    
    print(f"\nTotal documents: {collection.count()}")
    
    if data and 'metadatas' in data:
        # Get unique episode IDs
        episode_ids = set()
        for metadata in data['metadatas']:
            if metadata and 'episode_id' in metadata:
                episode_ids.add(metadata['episode_id'])
        
        print(f"\nEpisode IDs in ChromaDB:")
        for eid in sorted(episode_ids):
            print(f"  - {eid}")
    else:
        print("No metadata found")
else:
    print("No collections found!")
