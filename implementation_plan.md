# Implementation Plan - Episode Companion Agent

## Goal
Build a "Episode Companion Agent" microservice for Kochi that ingests episode scripts and provides structured, persona-based answers (Plain English, Founder, Engineer) via an API.

## User Review Required
> [!IMPORTANT]
> **API Keys**: This solution requires an OpenAI API Key for Embeddings and Chat. Please ensure `OPENAI_API_KEY` is set in your environment.
> **Local Storage**: ChromaDB will create a local `chroma_db` folder to store vectors.

## Design Discussion (Brainstorming)
The user requested a "brainstorm" phase. Here are the key design decisions:

1.  **Ingestion Strategy**:
    *   We will use `RecursiveCharacterTextSplitter` from LangChain.
    *   Chunk size: ~1000 characters with ~200 overlap seems appropriate for capturing context without being too large for retrieval.
    *   Metadata: Every chunk MUST have `episode_id` in metadata to allow filtering later (crucial for the "Multi-episode" future extension).

2.  **Agent Architecture**:
    *   Instead of a complex agent loop, a **RAG (Retrieval-Augmented Generation)** pipeline is sufficient and faster.
    *   We will use a "Router" pattern where the API endpoint determines the "Mode" (Prompt Template) to use.
    *   **Future Proofing**: The `EpisodeCompanionAgent` class will be designed to accept `episode_id` for every operation, enabling multi-episode support from day one, even if we only test with one.

3.  **API Design**:
    *   RESTful endpoints: `POST /episodes/{episode_id}/{mode}`.
    *   This is cleaner than `GET` with query params because we might want to send user context in the body later.
    *   For the POC, we'll also add a helper `POST /ingest` endpoint to easily load a script.

## Proposed Changes

### Project Structure
We will create a flat structure for simplicity, as requested:
```
metallic-kilonova/
├── main.py           # FastAPI app & endpoints
├── agent.py          # EpisodeCompanionAgent class
├── ingest.py         # Ingestion logic
├── prompts.py        # Prompt templates
├── requirements.txt  # Dependencies
└── data/             # Folder for sample scripts
```

### [NEW] requirements.txt
Dependencies: `fastapi`, `uvicorn`, `langchain`, `langchain-openai`, `chromadb`, `python-dotenv`.

### [NEW] prompts.py
Defines `PROMPT_TEMPLATES` dictionary mapping modes to LangChain `ChatPromptTemplate`s.
*   `plain_english`: Focus on simplicity, analogies.
*   `founder_takeaway`: Focus on market, product, opportunities.
*   `engineer_angle`: Focus on stack, implementation, trade-offs.

### [NEW] ingest.py
Functions:
*   `ingest_episode(episode_id: str, text: str)`:
    1.  Init ChromaDB client.
    2.  Split text.
    3.  Embed and add to collection with `ids` and `metadatas=[{"episode_id": ...}]`.

### [NEW] agent.py
Class `EpisodeCompanionAgent`:
*   `__init__`: Connects to ChromaDB.
*   `get_answer(episode_id: str, mode: str, query: str)`:
    1.  Select prompt based on `mode`.
    2.  `vector_store.similarity_search(query, filter={"episode_id": episode_id})`.
    3.  Format context.
    4.  Call LLM.
    5.  Return structured response.

### [NEW] main.py
*   `POST /ingest`: Accepts JSON `{episode_id, text}`.
*   `POST /episodes/{episode_id}/{mode}`: Accepts JSON `{query}` (optional, defaults to generic "tell me about this").
    *   Modes: `plain_english`, `founder_takeaway`, `engineer_angle`.

## Verification Plan

### Automated Tests
We will create a simple test script `test_flow.py` to verify the pipeline end-to-end.
1.  **Ingest**: Send a sample script to `/ingest`.
2.  **Query**: Call each mode endpoint and assert valid JSON response.

### Manual Verification
1.  **Setup**: Run `uvicorn main:app --reload`.
2.  **Ingest**: Use `curl` to ingest the "Kaiming He" sample text (I will create this based on the user's prompt).
3.  **Interact**:
    *   Ask for "Founder Takeaway" and check if it mentions "Direct Denoising" opportunities.
    *   Ask for "Engineer Angle" and check if it mentions "Transformers" or "Architecture".
