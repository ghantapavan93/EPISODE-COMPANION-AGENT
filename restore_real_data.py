from ingest import PaperEntryGpk, EpisodeBundleGpk, ingest_bundle_gpk

def restore_data():
    print("Restoring real episode data for 11/18...")
    
    episode_id = "ai-research-daily-2025-11-18"
    
    bundle = EpisodeBundleGpk(
        episode_id=episode_id,
        date_str="2025-11-18",
        hook="Learn how reinforcement learning masters Physics Olympiads in 'P1'!",
        listen_url="https://example.com/listen/11-18",
        full_report="""
🎙️ Learn how reinforcement learning masters Physics Olympiads in "P1"! Stay tuned for more AI insights and research summaries in today's AI Papers Daily.

Papers Covered in Today's Episode:

1. Back to Basics: Let Denoising Generative Models Denoise: https://arxiv.org/abs/2511.12345
2. Cost-Effective Communication: https://arxiv.org/abs/2511.67890
3. Scaling Spatial Intelligence: https://arxiv.org/abs/2511.54321

IN DEPTH

🌟 Top Papers Today

1. P1: Physics Olympiad Master
This paper introduces P1, a reinforcement learning agent that achieves gold-medal performance in Physics Olympiads. It uses a novel chain-of-thought approach combined with verified reasoning steps.
Key insight: Breaking down complex physics problems into sub-goals allows RL agents to solve them more reliably than end-to-end LLMs.

2. Back to Basics: Let Denoising Generative Models Denoise
Tianhong Li and Kaiming He challenge the fundamental paradigm of diffusion models. They argue that instead of predicting noise, we should predict the clean data directly. This simplifies the objective and improves generation quality for certain domains.

3. Cost-Effective Communication
Yijia Fan et al. propose a novel economic framework for multi-agent systems. By treating communication bandwidth as a scarce resource with a cost, agents learn to communicate more efficiently, sharing only the most critical information.

4. Scaling Spatial Intelligence
Zhongang Cai et al. present a systematic approach to cultivating spatial reasoning. They curate a massive dataset of 3D spatial tasks and show that training on this data significantly improves an agent's ability to navigate and manipulate objects in 3D environments.
""",
        audio_transcript=None,
        papers=[
            PaperEntryGpk(
                title="P1: Physics Olympiad Master",
                text_content="P1 is a reinforcement learning agent that achieves gold-medal performance in Physics Olympiads. It uses a novel chain-of-thought approach combined with verified reasoning steps. Key insight: Breaking down complex physics problems into sub-goals allows RL agents to solve them more reliably than end-to-end LLMs.",
                timestamp_start=30,
                timestamp_end=120
            ),
            PaperEntryGpk(
                title="Back to Basics: Let Denoising Generative Models Denoise",
                text_content="Tianhong Li and Kaiming He challenge the fundamental paradigm of diffusion models. They argue that instead of predicting noise, we should predict the clean data directly. This simplifies the objective and improves generation quality for certain domains.",
                timestamp_start=150,
                timestamp_end=240
            ),
            PaperEntryGpk(
                title="Cost-Effective Communication",
                text_content="Yijia Fan et al. propose a novel economic framework for multi-agent systems. By treating communication bandwidth as a scarce resource with a cost, agents learn to communicate more efficiently, sharing only the most critical information.",
                timestamp_start=260,
                timestamp_end=320
            ),
            PaperEntryGpk(
                title="Scaling Spatial Intelligence",
                text_content="Zhongang Cai et al. present a systematic approach to cultivating spatial reasoning. They curate a massive dataset of 3D spatial tasks and show that training on this data significantly improves an agent's ability to navigate and manipulate objects in 3D environments.",
                timestamp_start=340,
                timestamp_end=400
            )
        ]
    )
    
    ingest_bundle_gpk(bundle)
    print("✅ Data restored successfully!")

if __name__ == "__main__":
    restore_data()
