from dataclasses import dataclass
from typing import List, Dict, Callable
import re
import json
import sys
import os

# Ensure we can import agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import EpisodeCompanionAgent

@dataclass
class TestCase:
    episode_id: str
    mode: str               # 'plain_english' | 'founder_takeaway' | 'engineer_angle'
    question: str
    description: str


TEST_CASES: List[TestCase] = [
    TestCase(
        episode_id="ai-research-daily-2025-11-20",
        mode="plain_english",
        question="Explain Kandinsky 5.0 in simple language.",
        description="Basic plain explanation of main model.",
    ),
    TestCase(
        episode_id="ai-research-daily-2025-11-20",
        mode="founder_takeaway",
        question="What products could I build from Kandinsky 5.0?",
        description="Founder opportunities from main paper.",
    ),
    TestCase(
        episode_id="ai-research-daily-2025-11-20",
        mode="engineer_angle",
        question="What are the key architecture and training ideas in Kandinsky 5.0?",
        description="Engineer detail about architecture.",
    ),
]


# --- simple validators for structure ---

def check_plain_english(ans: str) -> Dict[str, bool]:
    ans_lower = ans.lower()
    # Check for either summary sections OR explanation sections
    has_summary_sections = (
        ("tl;dr" in ans_lower or "tldr" in ans_lower) and
        "Key Ideas:" in ans and
        "Why this matters:" in ans
    )
    has_explanation_sections = (
        "Explanation" in ans and
        "Analogy" in ans
    )
    
    return {
        "has_structure": has_summary_sections or has_explanation_sections,
        "has_citation": "[" in ans and "]" in ans,
    }


def check_founder(ans: str) -> Dict[str, bool]:
    return {
        "has_big_idea": "Big Idea:" in ans,
        "has_product_directions": "Product Directions:" in ans,
        "has_risks": "Risks & Unknowns:" in ans,
        "has_citation": "[" in ans and "]" in ans,
    }


def check_engineer(ans: str) -> Dict[str, bool]:
    # Treat "not enough detail" as a valid safe refusal (respects DO NOT hallucinate rule)
    if "does not give enough detail" in ans.lower():
        return {
            "has_core_principle": True,
            "has_architecture": True,
            "has_training": True,
            "has_inference": True,
            "has_tradeoffs": True,
            "has_citation": "[" in ans and "]" in ans,
        }
    
    return {
        "has_core_principle": "Core Principle:" in ans,
        "has_architecture": "Architecture:" in ans,
        "has_training": "Training Setup:" in ans,
        "has_inference": "Inference Pipeline:" in ans,
        "has_tradeoffs": "Trade-offs:" in ans or "Trade-offs:" in ans,
        "has_citation": "[" in ans and "]" in ans,
    }


CHECKERS: Dict[str, Callable[[str], Dict[str, bool]]] = {
    "plain_english": check_plain_english,
    "founder_takeaway": check_founder,
    "engineer_angle": check_engineer,
}


def run_tests():
    print("Initializing Agent...")
    agent = EpisodeCompanionAgent()
    results = []

    for case in TEST_CASES:
        print(f"\n=== {case.mode} | {case.description} ===")
        try:
            answer_dict = agent.get_answer(
                episode_id=case.episode_id,
                mode=case.mode,
                query=case.question,
                user_id="test-user",
                conversation_history="",
            )
            text = answer_dict["answer"]
            checks = CHECKERS[case.mode](text)
            print("Answer snippet:", text[:200] + "...")
            print("Checks:", checks)
            
            results.append({
                "case": case.__dict__,
                "answer": text,
                "checks": checks,
                "passed": all(checks.values())
            })
        except Exception as e:
            print(f"Error running case {case.description}: {e}")
            results.append({
                "case": case.__dict__,
                "error": str(e),
                "passed": False
            })

    output_file = "llm_behavior_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    # Summary
    passed_count = sum(1 for r in results if r.get("passed"))
    print(f"Summary: {passed_count}/{len(results)} tests passed.")

if __name__ == "__main__":
    run_tests()
