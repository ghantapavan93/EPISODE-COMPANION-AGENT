import os
from ingest import ingest_episode

def ingest_sample():
    file_path = "data/daily_report_11_18.txt"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    episode_id = "ai-research-daily-2025-11-18"
    print(f"Ingesting episode: {episode_id}")
    
    try:
        result = ingest_episode(episode_id, text)
        print(f"Ingestion successful: {result}")
    except Exception as e:
        print(f"Ingestion failed: {e}")

if __name__ == "__main__":
    ingest_sample()
