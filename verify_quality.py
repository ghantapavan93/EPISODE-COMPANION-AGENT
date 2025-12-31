import logging
import sys
import time
from agent import EpisodeCompanionAgent
from ingest import PaperEntryGpk, EpisodeBundleGpk, ingest_bundle_gpk

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("QualityCheck")

def print_separator(title):
    print(f"\n{'='*20} {title} {'='*20}\n")

def verify_quality():
    agent = EpisodeCompanionAgent()
    episode_id = "test-quality-episode"
    
    # 1. Ingest Dummy Data with Timestamps
    print_separator("1. Ingesting Test Episode")
    bundle = EpisodeBundleGpk(
        episode_id=episode_id,
        date_str="2025-11-23",
        hook="Test Hook",
        listen_url="http://test.com",
        full_report="Today we discuss the Transformer architecture. It uses self-attention to process sequences in parallel. This is crucial for LLMs. Another paper 'FlashAttention' optimizes this.",
        audio_transcript=None,
        papers=[
            PaperEntryGpk(
                title="Attention Is All You Need",
                text_content="The Transformer is the first transduction model relying entirely on self-attention to compute representations of its input and output without using sequence-aligned RNNs or convolution.",
                timestamp_start=60,
                timestamp_end=120
            ),
            PaperEntryGpk(
                title="FlashAttention",
                text_content="FlashAttention is an IO-aware exact attention algorithm that uses tiling to reduce memory accesses.",
                timestamp_start=180,
                timestamp_end=240
            )
        ]
    )
    ingest_bundle_gpk(bundle)
    print("✅ Ingestion complete.")

    # 2. Test Plain English Mode
    print_separator("2. Testing Plain English Mode")
    resp = agent.get_answer(episode_id, "plain_english", "What is the Transformer?")
    print(f"Answer:\n{resp['answer']}")
    if "Transformer" in resp['answer']:
        print("✅ Content check passed")
    
    # 3. Test Founder Mode with Profile
    print_separator("3. Testing Founder Mode (Profile: VC)")
    resp = agent.get_answer(
        episode_id, 
        "founder_takeaway", 
        "Why should I invest in this?", 
        user_profile={"role": "VC", "domain": "Deep Tech"}
    )
    print(f"Answer:\n{resp['answer']}")
    # We expect some business/investment language ideally, but at least a valid response
    
    # 4. Test Engineer Mode with Profile
    print_separator("4. Testing Engineer Mode (Profile: MLE)")
    resp = agent.get_answer(
        episode_id, 
        "engineer_angle", 
        "How do I implement this?", 
        user_profile={"role": "Machine Learning Engineer", "stack": "PyTorch"}
    )
    print(f"Answer:\n{resp['answer']}")

    # 5. Test Quiz Mode
    print_separator("5. Testing Quiz Mode")
    resp = agent.get_answer(episode_id, "plain_english", "Quiz me on this")
    print(f"Answer:\n{resp['answer']}")
    if "?" in resp['answer']:
        print("✅ Quiz format check passed")

    # 6. Test Critique Mode
    print_separator("6. Testing Critique Mode")
    resp = agent.get_answer(episode_id, "plain_english", "Let me explain: Transformers use RNNs.", user_profile=None)
    print(f"Answer:\n{resp['answer']}")
    # Should correct the user (Transformers do NOT use RNNs)

    # 7. Check Time Hints
    print_separator("7. Checking Time Hints")
    if resp['metadata'].get('episode_time_hint'):
        print(f"✅ Time Hint Found: {resp['metadata']['episode_time_hint']}")
    else:
        print("⚠️ No time hint found in critique response (might be expected if context wasn't retrieved or wide range)")

if __name__ == "__main__":
    try:
        verify_quality()
        print("\n🎉 All quality checks finished!")
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        sys.exit(1)
