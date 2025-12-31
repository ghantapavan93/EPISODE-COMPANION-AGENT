from dataclasses import dataclass
from typing import List, Optional
import re

@dataclass
class AnswerPolicy:
    min_words: int
    max_words: int
    include_sections: List[str]
    tone_instruction: str
    add_commentary: bool

def classify_question(query: str) -> str:
    """Classify the user query into a specific type."""
    q = query.lower()

    # --- Learning modes -------------------------------------------------
    quiz_triggers = [
        "quiz me",
        "test me",
        "ask me questions",
        "questions to test if i understood",
        "multiple-choice questions",
        "multiple choice questions",
        "mcq",
        "spaced-repetition",
        "spaced repetition",
        "mix easy and hard questions",
    ]
    if any(t in q for t in quiz_triggers):
        return "quiz_me"

    self_explain_triggers = [
        "let me explain",
        "did i get this right",
        "tell me if i understood",
        "grade my explanation",
        "give me feedback on my explanation",
        "what i got right and wrong",
        "rewrite it and highlight what i missed",
        "highlight what i missed",
        "give me feedback and a better version",
    ]
    if any(t in q for t in self_explain_triggers):
        return "self_explain"

    # TL;DR requests (before generic summary)
    if "tldr" in q or "tl;dr" in q or ("3" in q and "bullet" in q):
        return "tldr"

    # Episode-native flavor questions
    if "builder-friendly insight" in q:
        return "episode_builder_insight"
    if "half paying attention" in q:
        return "episode_half_attention"
    if "crazy but plausible side-project" in q or "crazy but plausible side project" in q:
        return "episode_side_project"
    if "age the best" in q or "look silly in 2 years" in q:
        return "episode_aging"

    # Core idea with example
    if "core idea" in q and "example" in q:
        return "core_idea"

    # 🆕 Founder-mode canonical prompts
    if "if i only had a weekend" in q and "mvp" in q:
        return "mvp"
    if "one 4-hour project" in q or "one 4 hour project" in q:
        return "prototype"
    if "next thing you'd build in a month" in q or "build in a month" in q:
        return "month"
    if "paid product" in q or "turn this episode into a paid product" in q:
        return "paid_product"
    if "customer segment would pay right now" in q:
        return "paid_product"
    if "pricing model" in q and "go-to-market" in q:
        return "paid_product"
    if "realistic moat" in q or "closest existing products" in q or "differentiate using this research" in q:
        return "moat"
    if "top 3 risks" in q or "top three risks" in q or "unknowns" in q:
        return "risks"
    if "over-hyped" in q or "overhyped" in q:
        return "overhype_failure"
    if "solo indie dev" in q:
        return "role_solo_indie"
    if "pm at a saas startup in fintech" in q or "i'm a pm at a saas startup in fintech" in q:
        return "role_pm_fintech"

    # 🆕 Engineer-mode canonical prompts
    if "one simple prototype" in q:
        return "prototype"
    if "describe a minimal data pipeline" in q or "minimal data pipeline" in q:
        return "pipeline"
    if "sketch a minimal api" in q:
        return "api"
    if "implement this with python + fastapi + postgresql" in q:
        return "architecture"
    if "integrate this paper into an existing microservice" in q:
        return "integration"
    if "metrics and logs should i track" in q:
        return "metrics"
    if "bottlenecks or failure modes" in q:
        return "risks"
    if "small-scale experiment" in q:
        return "experiment"
    if "trade-offs between this approach" in q:
        return "tradeoffs"
    if "limitations or weak points" in q:
        return "limitations"
    if "backend engineer working mostly with python + postgres" in q:
        return "role_backend_python_pg"
    if "i'm at a healthcare startup" in q:
        return "role_healthcare"

    # Brainstorm / ideation
    if any(w in q for w in ["brainstorm", "idea", "project", "prototype", "4 hour", "4-hour"]):
        return "brainstorm"

    # Summary requests
    if any(w in q for w in ["summary", "summarize", "overview", "what is"]):
        return "summary"

    # Why/how explanations
    if any(w in q for w in ["why", "how", "explain", "reason"]):
        return "why_how"

    # Build/implement queries
    if any(w in q for w in ["build", "implement", "code", "stack", "architecture"]):
        return "build_implement"

    # Comparison queries
    if any(w in q for w in ["compare", "difference", "versus", "vs"]):
        return "compare"

    # Relevance / one thing to remember
    if any(w in q for w in ["relevance", "matter", "care", "impact", "remember one thing"]):
        return "relevance"

    # Fallback
    return "general"

def get_policy(mode: str, question_type: str) -> AnswerPolicy:
    """Return the answer policy based on persona mode and question type."""
    # Default base policy
    policy = AnswerPolicy(
        min_words=50,
        max_words=300,
        include_sections=[],
        tone_instruction="Helpful and concise.",
        add_commentary=False
    )

    if mode == "plain_english":
        policy.tone_instruction = "Simple, accessible, radio-host style."
        # Default sections for plain English to ensure test compliance
        policy.include_sections = ["TL;DR", "Key Ideas", "Why this matters"]
        if question_type == "why_how":
            # Relaxed sections for explanation
            policy.include_sections = ["Explanation", "Analogy"]
            policy.max_words = 300
        elif question_type == "brainstorm":
            policy.include_sections = ["Explanation", "Ideas"]
            policy.max_words = 400
    elif mode == "founder_takeaway":
        policy.tone_instruction = "Strategic, business-focused, visionary."
        policy.add_commentary = True
        policy.include_sections = ["Big Idea", "Product Directions", "Why this paper", "Risks & Unknowns"]
        if question_type == "brainstorm":
            policy.max_words = 500
    elif mode == "engineer_angle":
        policy.tone_instruction = "Technical, precise, implementation-focused."
        policy.include_sections = ["Core Principle", "Architecture", "Training Setup", "Inference Pipeline", "Integration Tips", "Trade-offs"]
        if question_type == "compare":
            policy.include_sections.append("Performance")
        if question_type == "brainstorm":
            policy.max_words = 500
    return policy
