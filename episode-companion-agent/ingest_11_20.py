from ingest import parse_daily_report_gpk, ingest_bundle_gpk

# Raw data from user request
raw_report = """
Date: 2025-11-20

🎙️ AI Research Daily 11/20: Kandinsky 5.0, Reasoning via Video, VISPLAY

Listen: https://example.com/listen/11-20

Papers Covered in Today's Episode

Kandinsky 5.0: huggingface.co/papers/2511.14993
VRBench: huggingface.co/papers/2511.14994
VISPLAY: huggingface.co/papers/2511.14995

IN DEPTH

Executive Summary
Today's episode covers three major advancements in AI: Kandinsky 5.0 for image/video generation, VRBench for reasoning via video, and VISPLAY for self-evolving VLMs.

Noteworthy Researchers
- Researcher A (Kandinsky team)
- Researcher B (VRBench team)

🌟 Top Papers Today

1. ARC Is a Vision Problem! ⭐⭐⭐⭐⭐
2. Another Paper Title ⭐⭐⭐⭐
3. Yet Another Paper ⭐⭐⭐
4. Kandinsky 5.0 ⭐⭐⭐⭐⭐
5. VRBench ⭐⭐⭐⭐⭐
6. VISPLAY ⭐⭐⭐⭐⭐
7. Last Paper ⭐⭐⭐

📊 Report Metadata
Counts: 7 papers
Areas: Computer Vision, Generative AI
"""

audio_transcript = """
Welcome to AI Research Daily for November 20th, 2025.
Today we are discussing three exciting papers.
First up is Kandinsky 5.0, a new model for image and video generation that pushes the boundaries of quality and speed.
Next, we have VRBench, which explores reasoning via video. It's a benchmark that tests how well models can understand and reason about video content.
Finally, VISPLAY introduces self-evolving VLMs. This is a fascinating approach where visual language models improve themselves over time.
These are the top stories for today.
"""

def main():
    print("Parsing 11/20 Episode...")
    episode_id = "ai-research-daily-2025-11-20"
    bundle = parse_daily_report_gpk(episode_id, raw_report)
    
    print(f"Parsed Bundle: {bundle.episode_id}")
    print(f"Papers found: {len(bundle.papers)}")
    for p in bundle.papers:
        print(f" - {p.title} (Rank: {p.rank}, Audio: {p.in_audio})")

    print("\nIngesting Bundle...")
    result = ingest_bundle_gpk(bundle, audio_text=audio_transcript)
    print(f"Ingestion Result: {result}")

if __name__ == "__main__":
    main()
