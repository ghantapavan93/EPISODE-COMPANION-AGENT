"""
demo_kandinsky.py

Quick local harness to:
1) Ingest the AI Research Daily 11/20 Daily Report
2) Run a few canonical questions across modes
3) Print answers + tiny smell-check verdicts

Usage:
    python demo_kandinsky.py
"""

from __future__ import annotations

import textwrap
from typing import Any

# 🔧 ADJUST THESE IMPORTS to match your repo
from ingest import ingest_episode
from agent import EpisodeCompanionAgent as EpisodeAgent


EPISODE_ID = "ai-research-daily-2025-11-20"

DAILY_REPORT_1120 = textwrap.dedent(
    """
    AI Research Daily 11/20
    🎙️ AI Research Daily 11/20 — Discover the innovative concept of Kandinsky 5.0, a powerful family of foundation models for generating images and videos. Stay tuned for more groundbreaking AI research insights in today's AI Papers Daily!
    Listen: https://kochi.to/l/JMHm

    Papers Covered in Today's Episode
    Kandinsky 5.0: huggingface.co/papers/2511.14993
    Reasoning via Video: huggingface.co/papers/2511.15065
    VisPlay: huggingface.co/papers/2511.15661

    IN DEPTH: AI Research Papers from ARXIV
    AI Research Papers - Daily Curated Brief
    Date: 2025-11-19
    Curated: 7 papers from 871 submissions

    Executive Summary
    Kaiming He's team reframes abstract reasoning as vision with competitive human-level results on ARC. Notable cross-institutional efforts debut foundation models for fluid dynamics (Walrus, 11 institutions) and parametric human animation (MHR, 19 institutions). Safety evaluations dominate with autonomous driving and financial OCR benchmarks. Computer vision particularly active with 460 papers (53% of submissions).

    📚 Research Activity Overview
    Computer vision dominated with 460 papers (53% of all submissions), reflecting continued momentum in the area identified by graph analysis (828 papers this week). Strong convergence on safety-critical applications emerged across autonomous driving, financial document understanding, and multi-agent systems. The three major cross-institutional collaborations identified in graph data all published today, signaling coordinated research efforts on foundation models and human-centric applications.

    👥 Noteworthy Researchers Today
    Keze Wang - Sun Yat-sen University
    Why notable: Rising star with 4.0x publication acceleration (4 recent vs 1 earlier papers in graph database)
    Research areas: Computer vision, 3D object detection, multi-agent language systems
    Today's contributions: Two papers spanning monocular 3D detection and cost-effective language agent communication
    Publication velocity: Rapid acceleration identified in graph analysis, demonstrating unusual productivity burst

    Kaiming He - MIT (formerly Meta)
    Why notable: Legendary researcher (h-index 84, 520k+ citations), inventor of ResNet and He initialization
    Research areas: Computer vision, deep learning architectures, visual reasoning
    Today's contributions: Co-authored "ARC Is a Vision Problem!" achieving near-human performance on abstract reasoning benchmark
    Track record: One of the most influential researchers in modern deep learning, now exploring abstract reasoning challenges

    Yueru He, Xueqing Peng, Yupeng Cao - Multi-institutional Financial AI Team
    Why notable: Led FinCriticalED benchmark (12-institution collaboration identified in graph), with Yupeng Cao showing strong h-index (14) and Yan Wang (h-index 53) as senior collaborator
    Research areas: Financial document understanding, OCR evaluation, vision-language models
    Today's contributions: First fact-level evaluation benchmark for financial documents with 500 image-HTML pairs
    Collaboration strength: Exemplifies the type of large-scale cross-institutional research highlighted by graph analysis

    Jun Liu - Pacific Northwest National Laboratory
    Why notable: Highest h-index in today's dataset (127) with 72k citations, exceptional research impact
    Research areas: Robotics, AI applications in scientific domains
    Today's contributions: Robotics paper leveraging decades of domain expertise
    Research quality: Elite-tier researcher representing national lab contributions to AI/ML

    🌟 Top Papers Today
    1. ARC Is a Vision Problem! ⭐⭐⭐⭐⭐
    Authors: Keya Hu, Ali Cy, Linlu Qiu, Kaiming He, Xinlei Chen, Haoxiang Li
    Categories: cs.CV, cs.AI, cs.LG

    Why this matters: Co-authored by Kaiming He (h-index 84, 520k citations), one of deep learning's most influential figures. Challenges the dominant paradigm that treats abstract reasoning as a language problem, instead proposing a vision-centric approach. This represents a fundamental reframing of the ARC benchmark that has stumped most AI systems.

    Key Innovation: Formulates ARC as image-to-image translation using vanilla Vision Transformers trained from scratch on ARC data alone. Introduces "canvas" representation to incorporate visual priors, enabling standard vision architectures to tackle abstract reasoning without language intermediaries.

    Potential Impact: Achieves 60.4% accuracy on ARC-1 benchmark, competitive with leading LLMs while using far simpler architecture. Closes gap toward average human performance and suggests vision-native approaches may be more natural for spatial/geometric reasoning tasks. Could inspire new research direction for abstract reasoning beyond language models.

    2. Walrus: A Cross-Domain Foundation Model for Continuum Dynamics ⭐⭐⭐⭐⭐
    Authors: Multi-institutional team (11 institutions - identified in graph as notable collaboration)
    Categories: cs.CV, cs.CL

    Why this matters: One of three major cross-institutional collaborations identified by graph analysis (11 institutions). Addresses the critical challenge of generalizable fluid dynamics modeling, which impacts fields from climate science to engineering. Foundation models have transformed NLP/vision; this extends that paradigm to physics simulation.

    Key Innovation: First foundation model for continuum dynamics pretrained on 19 diverse scenarios (smoke, water, plasma, materials). Introduces harmonic-analysis stabilization for long-term predictions, distributed training framework, and compute-adaptive tokenization enabling efficient scaling.

    Potential Impact: Outperforms prior domain-specific models on prediction tasks while generalizing across fluid types. Could accelerate scientific computing, weather prediction, and engineering design by providing pre-trained physics understanding. Demonstrates foundation model approach extends beyond discrete tokens to continuous physical fields.

    3. MHR: Momentum Human Rig ⭐⭐⭐⭐⭐
    Authors: Multi-institutional team (19 institutions - largest collaboration in graph analysis)
    Categories: cs.CV

    Why this matters: Largest cross-institutional collaboration identified in graph data (19 institutions). Combines classical animation rigging (Momentum library) with modern parametric modeling (ATLAS skeleton/shape). Fills critical gap between research body models (SMPL) and production animation rigs used in film/games/VR.

    Key Innovation: First parametric human body model with non-linear pose correctives and anatomically plausible deformations designed for production pipelines. Bridges research and industry by providing expressive animation controls while maintaining statistical body shape modeling. Includes hand rig and production-ready export.

    Potential Impact: Enables AR/VR developers and animators to leverage statistical human body models without sacrificing animation control. Could accelerate adoption of learned body models in entertainment industry and democratize high-quality character animation. Released as open tool for graphics community.

    4. FinCriticalED: A Visual Benchmark for Financial Fact-Level OCR Evaluation ⭐⭐⭐⭐
    Authors: Yueru He, Xueqing Peng, Yupeng Cao (h-index 14), Yan Wang (h-index 53), multi-institutional team
    Categories: cs.AI, cs.LG

    Why this matters: Third major cross-institutional collaboration from graph analysis (12 institutions). Addresses critical need for reliable financial document understanding where errors have regulatory/fiduciary consequences. First benchmark to evaluate OCR at fact-level rather than character-level accuracy.

    Key Innovation: 500 image-HTML pairs with 700+ annotated financial facts spanning 10 document types (income statements, balance sheets, etc.). Introduces LLM-as-Judge evaluation pipeline for semantic fact extraction. Tests 10 OCR systems and 7 vision-language models on production financial documents.

    Potential Impact: Reveals that state-of-the-art VLMs still struggle with financial documents (fact-level accuracy gaps). Provides standardized benchmark for financial AI systems where accuracy is non-negotiable. Could drive improvements in automated financial reporting, compliance, and analysis tools used by millions of investors and analysts.

    5. DSBench: Is Your VLM for Autonomous Driving Safety-Ready? ⭐⭐⭐⭐
    Authors: Xianhui Meng, Zheng Lu (h-index 83, 33k citations), multi-author team from Chinese Academy of Sciences
    Categories: cs.CV, cs.AI

    Why this matters: Led by highly cited researcher Zheng Lu (h-index 83). Addresses the most critical question in autonomous driving deployment: can vision-language models reliably identify safety hazards? Previous VLM benchmarks focused on general perception, not safety-critical edge cases.

    Key Innovation: Comprehensive 98K-instance benchmark spanning 8 safety categories (collision risk, vulnerable road users, traffic violations, etc.). Multi-granularity evaluation from coarse hazard detection to fine-grained reasoning. Tests 24 leading VLMs including GPT-4V and Gemini across three difficulty levels.

    Potential Impact: Reveals significant gaps in current VLMs' safety reasoning capabilities, with even best models struggling on complex scenarios. Provides standardized safety evaluation before deploying VLMs in autonomous vehicles where failures cost lives. Could accelerate responsible development of vision-language systems for transportation.

    6. Cost-Effective Communication: An Auction-based Method for Language Agent Interaction ⭐⭐⭐⭐
    Authors: Soyul Lee, Seungmin Baek, Dongbo Min, Keze Wang (rising star - 4.0x acceleration)
    Categories: cs.AI, cs.LG

    Why this matters: Co-authored by Keze Wang, a rising star identified in graph analysis with 4.0x publication acceleration. Addresses the exploding token costs of multi-agent LLM systems by treating communication as scarce economic resource. Novel game-theoretic approach to agent coordination.

    Key Innovation: Dynamic Auction-based Language Agent (DALA) framework where agents bid for speaking opportunities based on message value density. Agents learn "strategic silence" - knowing when NOT to communicate. Achieves 84.32% on MMLU and 91.21% on HumanEval with only 6.25M tokens (fraction of SOTA methods).

    Potential Impact: Could make multi-agent LLM systems economically viable for production use by drastically reducing API costs. Emergent strategic behavior (silence as learned skill) suggests richer agent dynamics than forced communication. Applicable to any multi-agent scenario from coding assistants to research collaboration systems.

    7. Difficulty-Aware Label-Guided Denoising for Monocular 3D Object Detection ⭐⭐⭐
    Authors: Soyul Lee, Seungmin Baek, Dongbo Min, Keze Wang (rising star - 4.0x acceleration)
    Categories: cs.CV

    Why this matters: Second paper by rising star Keze Wang (4.0x acceleration), demonstrating breadth across vision and language domains. Tackles challenging monocular 3D detection where depth estimation from single images remains difficult. Introduces adaptive learning strategy based on sample difficulty.

    Key Innovation: MonoDLGD framework that dynamically adjusts label perturbation during training based on detection difficulty (occlusion, distance, truncation). Treats 3D detection as denoising problem where easy/hard samples require different noise levels. Geometry-aware representations leverage spatial relationships.

    Potential Impact: Advances single-camera 3D detection crucial for cost-effective autonomous systems and robotics. Adaptive difficulty-based training could generalize to other perception tasks with non-uniform sample complexity. Reduces sensor costs while maintaining robust 3D understanding.

    📊 Report Metadata
    Total papers reviewed: 871
    Papers featured: 7
    Notable authors highlighted: 4 researchers/teams
    Cross-institutional collaborations: 3 (all featured)
    Most active area: Computer Vision (460 papers, 53%)
    """
).strip()


def _extract_field(result: Any, key: str, default=None):
    """
    Helper to handle both dicts and NamedTuples from your agent.
    """
    if isinstance(result, dict):
        # Check in metadata for latency and chunks
        if key in ["latency_ms", "used_chunks"] and "metadata" in result:
            return result["metadata"].get(key, default)
        return result.get(key, default)
    if hasattr(result, key):
        return getattr(result, key)
    return default


def quick_verdict(test_label: str, answer: str) -> str:
    """
    Tiny, heuristic "smell check" so you can eyeball quality fast.
    Not strict, just hints.
    """
    a_lower = answer.lower()

    checks = []

    if "summary" in test_label:
        if all(name in a_lower for name in ["kandinsky", "video", "visplay"]):
            checks.append("covers all 3 focal papers ✅")
        else:
            checks.append("might be missing one of Kandinsky/Video/VisPlay ⚠️")

    if "kandinsky" in test_label:
        checks.append("mentions Kandinsky ✅" if "kandinsky" in a_lower else "no Kandinsky mention ❌")

    if "founder" in test_label:
        if any(word in a_lower for word in ["product", "startup", "app", "business", "market"]):
            checks.append("talks in product/market language ✅")
        else:
            checks.append("might be too generic / not product-y ⚠️")

    if "engineer" in test_label:
        if any(word in a_lower for word in ["implement", "architecture", "training", "pipeline", "code"]):
            checks.append("has implementation flavor ✅")
        else:
            checks.append("might be too high-level for engineer ⚠️")

    if not checks:
        checks.append("manual smell-check needed 👀")

    return " | ".join(checks)


def main() -> None:
    print("=" * 80)
    print("Kochi Episode Companion Agent – Demo for AI Research Daily 11/20 (Kandinsky/VRBench/VisPlay)")
    print("=" * 80)

    # 1) Ingest this episode into your vector store
    print("\n[1] Ingesting 11/20 Daily Report into vector store...")
    ingest_result = ingest_episode(EPISODE_ID, DAILY_REPORT_1120)
    print("Ingest result:", ingest_result)

    # 2) Initialize your agent
    print("\n[2] Initializing EpisodeAgent...")
    agent = EpisodeAgent()
    print("Agent ready.\n")

    # 3) Define canonical tests
    tests = [
        (
            "summary_plain",
            "plain_english",
            "What is today's AI Research Daily about in simple words?",
        ),
        (
            "kandinsky_plain",
            "plain_english",
            "Explain Kandinsky 5.0 like I'm new to AI.",
        ),
        (
            "founder_takeaway",
            "founder_takeaway",
            "If I'm a founder, what should I build or care about from today's episode?",
        ),
        (
            "engineer_angle",
            "engineer_angle",
            "As an engineer, what should I try implementing or experimenting with from Kandinsky 5.0, Reasoning via Video, and VisPlay?",
        ),
        (
            "bonus_walrus_mhr",
            "plain_english",
            "Briefly compare ARC Is a Vision Problem, Walrus, and MHR – what does each one contribute?",
        ),
    ]

    # 4) Run tests
    for label, mode, question in tests:
        print("\n" + "-" * 80)
        print(f"[TEST] {label}  |  mode={mode}")
        print(f"Q: {question}\n")

        try:
            result = agent.get_answer(
                episode_id=EPISODE_ID,
                query=question,
                mode=mode,
            )

            answer = _extract_field(result, "answer", "")
            latency_ms = _extract_field(result, "latency_ms", None)
            used_chunks = _extract_field(result, "used_chunks", None)

            print("Answer:\n")
            print(textwrap.fill(answer, width=90))

            print("\nMeta:")
            if latency_ms is not None:
                print(f"  - latency:     {latency_ms:.1f} ms")
            if used_chunks is not None:
                print(f"  - used_chunks: {used_chunks}")

            verdict = quick_verdict(label, answer)
            print(f"\nQuick smell-check: {verdict}")
        except Exception as e:
            print(f"Error running test {label}: {e}")

    print("\n" + "=" * 80)
    print("Demo complete. Read the answers above and decide where to tweak prompts / retrieval.")
    print("=" * 80)


if __name__ == "__main__":
    main()
