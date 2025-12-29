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
    
    if any(w in q for w in ["summary", "summarize", "overview", "tldr", "what is"]):
        return "summary"
    elif any(w in q for w in ["why", "how", "explain", "reason"]):
        return "why_how"
    elif any(w in q for w in ["build", "implement", "code", "stack", "architecture"]):
        return "build_implement"
    elif any(w in q for w in ["compare", "difference", "versus", "vs"]):
        return "compare"
    elif any(w in q for w in ["relevance", "matter", "care", "impact"]):
        return "relevance"
    else:
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

    elif mode == "founder_takeaway":
        policy.tone_instruction = "Strategic, business-focused, visionary."
        policy.add_commentary = True
        # Default sections for founder to ensure test compliance
        policy.include_sections = ["Big Idea", "Product Directions", "Why this paper", "Risks & Unknowns"]
        
    elif mode == "engineer_angle":
        policy.tone_instruction = "Technical, precise, implementation-focused."
        # Default sections for engineer to ensure test compliance
        policy.include_sections = ["Core Principle", "Architecture", "Training Setup", "Inference Pipeline", "Integration Tips", "Trade-offs"]
        if question_type == "compare":
            policy.include_sections.append("Performance")

    return policy
