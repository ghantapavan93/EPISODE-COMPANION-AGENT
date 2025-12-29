from fastapi import FastAPI, HTTPException, status, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from sqlalchemy import text
from sqlalchemy.orm import Session
import logging
import os
import time
import uuid
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from ingest import ingest_episode, get_vector_store
from agent import EpisodeCompanionAgent
from orchestrator import Orchestrator
from conversation_manager import ConversationManager

# Upstream Pipeline imports
from arxiv_loader import ArxivLoader
from report_generator import ReportGenerator

# Database imports
from database import engine, Base, get_db, init_db, check_db_connection
import models  # Important: registers the models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Key Security (Antigravity: Simple but effective)
API_KEY = os.getenv("API_KEY", "my-secret-antigravity-password")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key. Please provide a valid X-API-Key header.",
        )
    return api_key

# Initialize Database with health check
logger.info("Checking database connection...")
if not check_db_connection():
    logger.error("Failed to connect to database!")
    raise Exception("Database connection failed")

init_db()

# Initialize FastAPI with enhanced metadata
app = FastAPI(
    title="Episode Companion Agent",
    description="Microservice for querying Kochi AI Research Daily episodes with three personas: Plain English, Founder Takeaway, and Engineer Angle",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware for Trace IDs and Logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    
    start_time = time.time()
    logger.info(f"[{trace_id}] Request started: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Trace-ID"] = trace_id
        logger.info(f"[{trace_id}] Request completed: {response.status_code} in {process_time:.2f}ms")
        return response
    except Exception as e:
        logger.error(f"[{trace_id}] Request failed: {e}")
        raise

# CORS Configuration for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Orchestrator (which initializes the agents)
try:
    orchestrator = Orchestrator()
    # We can still keep a direct reference to the episode agent if needed for legacy endpoints,
    # or just access it via orchestrator.episode_agent
    agent = orchestrator.episode_agent
    logger.info("Orchestrator and Agents initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize orchestrator: {e}")
    raise

# ============================================================================
# Pydantic Models with Validation
# ============================================================================

class IngestRequest(BaseModel):
    """Request model for episode ingestion"""
    text: str = Field(..., min_length=100, description="Episode content (Daily Report text)")
    title: Optional[str] = Field(None, description="Episode title")
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Text content cannot be empty')
        return v

class QueryRequest(BaseModel):
    """Request model for episode queries"""
    query: str = Field(..., min_length=3, max_length=500, description="User question about the episode")
    user_id: Optional[str] = Field(None, description="Unique user identifier (phone or session)")
    
    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    agent_ready: bool
    vector_store_ready: bool

class EpisodeInfo(BaseModel):
    """Episode metadata"""
    episode_id: str
    chunks_count: Optional[int] = None
    title: Optional[str] = None

class FeedbackPayload(BaseModel):
    """Feedback submission"""
    message_id: int = Field(..., description="ID of the assistant message to rate")
    rating: int = Field(..., ge=-1, le=1, description="Rating: -1 (bad), 0 (neutral), 1 (good)")
    comment: Optional[str] = Field(None, max_length=500, description="Optional feedback comment")

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def read_root():
    """Serve the main web UI"""
    return FileResponse('static/index.html')

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns system status, version, and component readiness.
    """
    try:
        vector_store = get_vector_store()
        vector_store_ready = vector_store is not None
    except Exception as e:
        logger.warning(f"Vector store health check failed: {e}")
        vector_store_ready = False
    
    return HealthResponse(
        status="ok",
        version="1.0.0",
        agent_ready=agent is not None,
        vector_store_ready=vector_store_ready
    )

@app.get("/episodes", response_model=List[str], tags=["Episodes"])
def list_episodes():
    """
    List all available episode IDs.
    
    Returns a list of episode_id strings that have been ingested.
    """
    try:
        vector_store = get_vector_store()
        # Get all unique episode IDs from the collection
        # Note: This is a simplified version; in production, you'd maintain a separate index
        collection = vector_store._collection
        all_metadata = collection.get()
        
        if not all_metadata or 'metadatas' not in all_metadata:
            return []
        
        episode_ids = set()
        for metadata in all_metadata['metadatas']:
            if metadata and 'episode_id' in metadata:
                episode_ids.add(metadata['episode_id'])
        
        return sorted(list(episode_ids))
    
    except Exception as e:
        logger.error(f"Failed to list episodes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve episode list: {str(e)}"
        )

@app.post("/episodes/{episode_id}/ingest", tags=["Episodes"])
def ingest_episode_endpoint(episode_id: str, request: IngestRequest):
    """
    Dynamically ingest a new episode.
    
    This endpoint allows runtime ingestion of episode content without restarting the service.
    Perfect for integrating with Kochi's Daily Report generation pipeline.
    
    Args:
        episode_id: Unique identifier for the episode (e.g., "ai-research-daily-2025-11-18")
        request: Episode content and optional metadata
    
    Returns:
        Ingestion result with chunk count and IDs
    """
    try:
        logger.info(f"Starting ingestion for episode_id={episode_id}")
        
        # Validate episode_id format
        if not episode_id or len(episode_id) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="episode_id must be at least 3 characters"
            )
        
        result = ingest_episode(episode_id, request.text)
        
        logger.info(f"Successfully ingested episode_id={episode_id}, chunks={result['chunks_count']}")
        
        return {
            "status": "success",
            "episode_id": episode_id,
            "title": request.title,
            "data": result
        }
    
    except ValueError as e:
        logger.warning(f"Validation error for episode_id={episode_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        logger.error(f"Ingestion failed for episode_id={episode_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )

@app.post("/episodes/{episode_id}/query", tags=["Episodes"])
def query_episode(episode_id: str, mode: str, request: QueryRequest, req: Request):
    """
    Query an episode with a specific persona mode.
    """
    try:
        trace_id = getattr(req.state, "trace_id", "unknown")
        logger.info(f"[{trace_id}] Query received: episode_id={episode_id}, mode={mode}, query_length={len(request.query)}")
        
        response = agent.get_answer(episode_id, mode, request.query)
        
        # Attach trace_id to response
        response["trace_id"] = trace_id
        
        logger.info(f"[{trace_id}] Query completed: latency={response['metadata']['latency_ms']}ms")
        
        return response
    
    except ValueError as e:
        logger.warning(f"Validation error: episode_id={episode_id}, mode={mode}, error={e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        logger.error(f"Query failed: episode_id={episode_id}, mode={mode}, error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}"
        )

@app.post("/query", tags=["Orchestrator"])
def orchestrator_query(
    request: QueryRequest, 
    req: Request, 
    episode_id: Optional[str] = None,
    api_key: str = Depends(get_api_key),  # API Key protection
    db: Session = Depends(get_db)  # PRO FIX: Dependency Injection
):
    """
    Smart routing endpoint (API key protected).
    PRO FIX: Now uses FastAPI Dependency Injection for DB session.
    """
    try:
        trace_id = getattr(req.state, "trace_id", "unknown")
        user_id = request.user_id or "anonymous"
        logger.info(f"[{trace_id}] Orchestrator query: user_id={user_id}, episode_id={episode_id}")
        
        # PRO FIX: Pass DB session to orchestrator
        response = orchestrator.route_request(
            user_id=user_id,
            text=request.query,
            episode_id=episode_id,
            db=db  # Inject DB session
        )
        
        # Attach trace_id if response is a dict
        if isinstance(response, dict):
            response["trace_id"] = trace_id
        
        return response
        
    except Exception as e:
        logger.error(f"Orchestrator failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Orchestration failed: {str(e)}"
        )

@app.delete("/history/clear", tags=["Admin"], dependencies=[Depends(get_api_key)])
def clear_history(user_id: str, db: Session = Depends(get_db)):
    """
    Wipes conversation history for a specific user.
    ADMIN ONLY - Requires API Key authentication.
    """
    try:
        # The "Janitor" - User data hygiene
        # Delete all messages first (due to FK constraint)
        db.execute(
            text("DELETE FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = :user_id)"),
            {"user_id": user_id}
        )
        # Then delete conversations
        result = db.execute(
            text("DELETE FROM conversations WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        db.commit()
        
        return {
            "success": True,
            "message": f"Cleared all conversation history for user {user_id}",
            "rows_affected": result.rowcount
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to clear history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear history: {str(e)}"
        )

@app.post("/history", tags=["History"])
def get_user_history(user_id: str, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get user's conversation history across all episodes.
    Returns recent conversations with metadata.
    """
    try:
        from repositories.conversation_repository import ConversationRepository
        
        repo = ConversationRepository(db)
        conversations = repo.get_user_conversations(user_id, limit)
        
        history = [
            {
                "episode_id": conv.episode_id,
                "last_mode": conv.last_mode,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            }
            for conv in conversations
        ]
        
        return {
            "success": True,
            "user_id": user_id,
            "history": history
        }
        
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )

@app.post("/cleanup", tags=["Admin"], dependencies=[Depends(get_api_key)])
def cleanup_old_conversations(days_old: int = 30, db: Session = Depends(get_db)):
    """
    Delete conversations older than specified days.
    ADMIN ONLY - Requires API Key authentication.
    Should be called periodically (e.g., daily cron job).
    """
    try:
        manager = ConversationManager(db)
        deleted_count = manager.cleanup_old_conversations(days_old)
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "days_old": days_old
        }
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cleanup failed: {str(e)}"
        )

@app.post("/feedback", tags=["Feedback"])
def submit_feedback(payload: FeedbackPayload, db: Session = Depends(get_db)):
    """
    Submit user feedback for a specific assistant message.
    
    Allows users to rate answers and provide comments for quality improvement.
    """
    try:
        from models import Message
        
        manager = ConversationManager(db)
        manager.submit_feedback(
            message_id=payload.message_id,
            rating=payload.rating,
            comment=payload.comment
        )
        
        return {
            "success": True,
            "message": "Feedback submitted successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Feedback submission failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store feedback"
        )

@app.post("/admin/generate-episode", tags=["Admin"], dependencies=[Depends(get_api_key)])
async def generate_episode_from_arxiv(
    target_date: str,
    max_results: int = 100,
    db: Session = Depends(get_db)
):
    """
    Upstream Pipeline: Generate an episode from arXiv automatically.
    
    This endpoint:
    1. Scrapes arXiv for the specified date
    2. Picks top 7 papers using heuristics
    3. Writes the report using Gemini
    4. Returns the generated report text
    
    ADMIN ONLY - Requires API Key authentication.
    
    Args:
        target_date: Date string in format "YYYY-MM-DD"
        max_results: Maximum papers to fetch from arXiv (default: 100)
    
    Returns:
        Generated report markdown ready for ingestion
    """
    try:
        from datetime import datetime
        
        # Parse date
        try:
            parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
        
        logger.info(f"Generating episode for {target_date}")
        
        loader = ArxivLoader()
        generator = ReportGenerator()
        
        # 1. Fetch papers from arXiv
        logger.info(f"Fetching papers from arXiv for {target_date}...")
        raw_papers = loader.get_papers_for_date(parsed_date, max_results)
        
        if not raw_papers:
            return {
                "success": False,
                "message": f"No papers found for {target_date} yet. Try yesterday.",
                "date": target_date,
                "papers_found": 0
            }
        
        logger.info(f"Found {len(raw_papers)} papers")
        
        # 2. Curate - pick top papers
        logger.info("Selecting top papers...")
        top_papers = loader.select_top_papers(raw_papers, top_n=7)
        logger.info(f"Selected {len(top_papers)} top papers")
        
        # 3. Write report using Gemini
        logger.info("Generating report with Gemini...")
        report_markdown = generator.generate_markdown(
            date_str=str(parsed_date),
            total_count=len(raw_papers),
            papers=top_papers
        )
        
        logger.info("Report generated successfully")
        
        # 4. Return (you can then paste this into /ingest)
        return {
            "success": True,
            "date": target_date,
            "papers_found": len(raw_papers),
            "top_papers_selected": len(top_papers),
            "generated_report": report_markdown,
            "paper_titles": [p.title for p in top_papers],
            "message": "Report generated successfully. You can now ingest this using the /episodes/{episode_id}/ingest endpoint."
        }
        
    except Exception as e:
        logger.error(f"Failed to generate episode: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Episode generation failed: {str(e)}"
        )

# Legacy endpoint for backward compatibility
@app.post("/episodes/{episode_id}/{mode}", tags=["Episodes (Legacy)"])
def get_answer_endpoint(episode_id: str, mode: str, request: QueryRequest):
    """
    Legacy query endpoint for backward compatibility.
    
    Note: Use /episodes/{episode_id}/query with mode in query params for new integrations.
    """
    return agent.get_answer(
        episode_id=episode_id,
        mode=mode,
        query=request.query,
        user_id=request.user_id
    )

# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors gracefully"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Validation Error", "detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all error handler for unexpected errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal Server Error", "detail": "An unexpected error occurred"}
    )

# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("=" * 70)
    logger.info("Episode Companion Agent - Starting Up")
    logger.info("=" * 70)
    logger.info(f"Version: 1.0.0")
    logger.info(f"Docs: http://localhost:8000/docs")
    logger.info(f"ReDoc: http://localhost:8000/redoc")
    logger.info("=" * 70)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Episode Companion Agent - Shutting Down")

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
