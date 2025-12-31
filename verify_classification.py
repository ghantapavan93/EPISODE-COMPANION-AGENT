import sys
import os

# Add current directory to path so we can import modules
sys.path.append(os.getcwd())

from behavior import classify_question
from orchestrator import Orchestrator

def test_classification():
    print("Testing classification logic...")
    
    test_cases = [
        # Founder
        ("If I only had a weekend to build an MVP", "mvp"),
        ("What is one 4-hour project I could build?", "prototype"),
        ("What customer segment would pay right now?", "paid_product"),
        ("What is the realistic moat here?", "moat"),
        ("What are the top 3 risks?", "risks"),
        ("Is this over-hyped?", "overhype_failure"),
        ("I am a solo indie dev", "role_solo_indie"),
        ("I'm a PM at a SaaS startup in fintech", "role_pm_fintech"),
        
        # Engineer
        ("Describe a minimal data pipeline", "pipeline"),
        ("Sketch a minimal API", "api"),
        ("Implement this with Python + FastAPI + PostgreSQL", "architecture"),
        ("How to integrate this paper into an existing microservice", "integration"),
        ("What metrics and logs should I track?", "metrics"),
        ("How to run a small-scale experiment?", "experiment"),
        ("What are the trade-offs between this approach?", "tradeoffs"),
        ("What are the limitations or weak points?", "limitations"),
        ("I'm a backend engineer working mostly with Python + Postgres", "role_backend_python_pg"),
        ("I'm at a healthcare startup", "role_healthcare"),
        
        # Plain English / General
        ("Give me a summary", "summary"),
        ("Explain why this matters", "why_how"),
        ("TL;DR please", "tldr"),
    ]
    
    failed = 0
    for query, expected in test_cases:
        result = classify_question(query)
        if result != expected:
            print(f"❌ Failed: '{query}' -> Got '{result}', expected '{expected}'")
            failed += 1
        else:
            print(f"✅ Passed: '{query}' -> '{result}'")
            
    if failed == 0:
        print("\nAll classification tests passed!")
    else:
        print(f"\n{failed} classification tests failed.")

def test_orchestrator_mode_inference():
    print("\nTesting Orchestrator mode inference...")
    orch = Orchestrator()
    
    test_cases = [
        ("mvp", "founder_takeaway"),
        ("moat", "founder_takeaway"),
        ("risks", "founder_takeaway"),
        ("role_solo_indie", "founder_takeaway"),
        
        ("pipeline", "engineer_angle"),
        ("api", "engineer_angle"),
        ("metrics", "engineer_angle"),
        ("tradeoffs", "engineer_angle"),
        
        ("tldr", "plain_english"),
        ("summary", "plain_english"),
    ]
    
    failed = 0
    for q_type, expected_mode in test_cases:
        # We can pass a dummy query since we are testing the mapping logic which uses question_type
        # But _infer_mode_from_question takes query and question_type
        mode = orch._infer_mode_from_question("dummy query", q_type)
        if mode != expected_mode:
            print(f"❌ Failed: Type '{q_type}' -> Got '{mode}', expected '{expected_mode}'")
            failed += 1
        else:
            print(f"✅ Passed: Type '{q_type}' -> '{mode}'")

    if failed == 0:
        print("\nAll orchestrator mode inference tests passed!")
    else:
        print(f"\n{failed} orchestrator mode inference tests failed.")

if __name__ == "__main__":
    test_classification()
    test_orchestrator_mode_inference()
