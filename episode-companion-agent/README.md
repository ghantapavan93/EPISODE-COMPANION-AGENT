# Episode Companion Agent

A focused microservice that gives a single "AI Research Daily" episode its own mini-agent. It allows users to ask questions about an episode in structured modes (Plain English, Founder Takeaway, Engineer Angle).

## Features

*   **Ingestion Pipeline**: Chunks and embeds episode scripts into a local ChromaDB vector store.
*   **RAG Architecture**: Retrieves relevant context before generating answers.
*   **Structured Modes**:
    *   `/plain_english`: Simple explanations.
    *   `/founder_takeaway`: Business and product implications.
    *   `/engineer_angle`: Technical details and architecture.
*   **Clean API**: FastAPI endpoints for easy integration.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file with your OpenAI API key:
    ```
    OPENAI_API_KEY=sk-...
    ```

## Usage

### 1. Ingest an Episode
You can ingest a script via the Python script or the API.

**Via Script:**
```bash
python ingest.py
```
(This ingests `data/sample_episode.txt` by default)

**Via API:**
```bash
curl -X POST "http://localhost:8000/ingest" \
     -H "Content-Type: application/json" \
     -d '{"episode_id": "test_ep", "text": "..."}'
```

### 2. Run the Server
```bash
uvicorn main:app --reload
```

### 3. Ask Questions
Query the agent using one of the specific modes:

**Founder Takeaway:**
```bash
curl -X POST "http://localhost:8000/episodes/ai_daily_2025_11_18/founder_takeaway" \
     -H "Content-Type: application/json" \
     -d '{"query": "What can I build with this?"}'
```

**Engineer Angle:**
```bash
curl -X POST "http://localhost:8000/episodes/ai_daily_2025_11_18/engineer_angle" \
     -H "Content-Type: application/json" \
     -d '{"query": "How does the architecture work?"}'
```

## Project Structure

*   `ingest.py`: Handles text splitting and vector storage.
*   `agent.py`: Core logic for retrieval and LLM generation.
*   `prompts.py`: Centralized prompt templates for different personas.
*   `main.py`: FastAPI application entry point.
*   `data/`: Stores sample data.
*   `chroma_db/`: Local vector database persistence.

## ArXiv Paper Fetching

**NEW:** Generate daily research episodes automatically from arXiv!

### Quick Start

Generate an episode for a specific date:
```bash
python fetch_and_ingest.py --date 2025-11-19
```

This will:
1. Fetch papers from arXiv for that date
2. Score and rank them using heuristics
3. Generate a daily report with LLM
4. Save to database
5. Ingest into RAG for querying

### Manual Workflow

```python
from episode_generator import generate_episode

# Generate episode
bundle = generate_episode("2025-11-19", top_k=7)

# Ingest into RAG
from ingest import ingest_bundle_gpk
ingest_bundle_gpk(bundle)

# Query the companion agent
from agent import EpisodeCompanionAgent
agent = EpisodeCompanionAgent()
response = agent.get_answer(
    episode_id=bundle.episode_id,
    mode="plain_english",
    query="What are the main papers from this episode?"
)
```

### Key Modules

*   `arxiv_fetcher.py`: Fetches papers from arXiv by date/category
*   `paper_scorer.py`: Scores and ranks papers using heuristics
*   `episode_generator.py`: Generates daily reports with LLM
*   `fetch_and_ingest.py`: CLI tool for complete workflow
*   `repositories/`: Database access layer for papers and episodes

See [`demo_arxiv_fetcher.py`](demo_arxiv_fetcher.py) for a complete demonstration.

### Upstream Pipeline - API Endpoint

**NEW:** Generate episodes directly from arXiv via API!

This implementation uses:
- `feedparser` for arXiv XML parsing
- Google Gemini for report generation
- Admin API endpoint for web integration

#### Quick Example

```bash
# Generate episode (requires API key)
curl -X POST "http://localhost:8000/admin/generate-episode?target_date=2025-11-19" \
     -H "X-API-Key: my-secret-antigravity-password"

# Returns generated report ready for ingestion
```

#### Interactive Test

```bash
python test_upstream_pipeline.py
```

This will:
1. Call the API to generate a report from arXiv
2. Show you the report preview  
3. Optionally ingest it into the system
4. Optionally query the agent to verify

#### Key Modules (Upstream Pipeline)

*   `arxiv_loader.py`: Fetches papers from arXiv using feedparser
*   `report_generator.py`: Generates reports with Google Gemini
*   `/admin/generate-episode`: Admin API endpoint (requires API key)

See [`upstream_pipeline_docs.md`](.gemini/antigravity/brain/.../upstream_pipeline_docs.md) for complete documentation.

## API Endpoint Summary

### Episode Generation
- `POST /admin/generate-episode` - Generate episode from arXiv (API key required)
- `POST /episodes/{episode_id}/ingest` - Ingest episode content
- `POST /query` - Query with smart routing (API key required)
- `POST /episodes/{episode_id}/query` - Query specific episode

### Admin Endpoints (Require API Key)
- `DELETE /history/clear` - Clear user history
- `POST /cleanup` - Cleanup old conversations
- `POST /admin/generate-episode` - Generate from arXiv

