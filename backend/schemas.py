from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class CompanionQueryRequest(BaseModel):
    """
    Request payload for the episode companion agent.
    """
    user_id: str = Field(
        ...,
        description="Stable user identifier (phone hash, user UUID, etc.)"
    )
    message: str = Field(
        ...,
        description="User's natural language query."
    )
    episode_id: Optional[str] = Field(
        default=None,
        description="Episode ID like 'ai-research-daily-2025-11-22'. "
                    "If omitted, we'll auto-resume last episode."
    )
    mode: Optional[str] = Field(
        default=None,
        description="Persona mode: 'plain_english', 'founder_takeaway', or 'engineer_angle'. "
                    "If omitted, backend infers."
    )
    debug: bool = Field(
        default=False,
        description="If true, include extra debug info in metadata (context preview, etc.)."
    )


class CompanionAnswerMetadata(BaseModel):
    trace_id: str
    latency_ms: float
    stage_latency: Dict[str, float]
    used_chunks: int
    expanded_query: str
    quality_checks: Dict[str, Any]
    source_papers: List[str]
    tokens_in: int
    tokens_out: int
    model: str
    question_type: str

    # Optional debug fields; we keep them flexible
    debug: Optional[Dict[str, Any]] = None

    # New: optional follow-up suggestions from EpisodeCompanionAgent / timeline answers
    suggested_followups: Optional[List[str]] = None

    # Optional error info (used in orchestrator error responses)
    error: Optional[str] = None
    details: Optional[str] = None


class CompanionQueryResponse(BaseModel):
    """
    Response payload from the episode companion agent.
    """
    episode_id: str
    mode: str
    answer: str
    metadata: CompanionAnswerMetadata
