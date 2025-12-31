from ingest import ingest_episode

RICH_CONTENT = """
Date: 2025-11-18
🎙️ Welcome to AI Research Daily. Today we cover Denoising, Multi-Agent Communication, and Spatial Intelligence.

Papers Covered in Today's Episode:
1. Back to Basics: Let Denoising Generative Models Denoise: arxiv.org/abs/2511.12345
2. Cost-Effective Communication: arxiv.org/abs/2511.67890
3. Scaling Spatial Intelligence: arxiv.org/abs/2511.54321
4. Kandinsky 5.0: The New Standard in Image Generation: arxiv.org/abs/2511.99999

IN DEPTH

🌟 Top Papers Today

1. Back to Basics: Let Denoising Generative Models Denoise ⭐⭐⭐⭐⭐
Authors: Tianhong Li, Kaiming He
This paper challenges the complex "prediction of x0" paradigm in diffusion models. Kaiming He argues that we should simply predict the noise (epsilon) directly, as originally proposed.
Key insights:
- predicting clean data directly is unstable at high noise levels.
- predicting noise is numerically stable and aligns with the underlying physics of diffusion.
- They propose a simplified loss function that outperforms EDM and other state-of-the-art methods on ImageNet.
- This "Back to Basics" approach simplifies the architecture by removing the need for complex preconditioners.

2. Cost-Effective Communication in Multi-Agent Systems ⭐⭐⭐⭐
Authors: Yijia Fan, Keze Wang
Communication bandwidth is a scarce resource. This paper introduces a "market-based" mechanism where agents must "pay" to broadcast messages.
- Agents have a limited budget of tokens.
- They learn to only communicate when their information is critical for the team's success.
- Results show a 40% reduction in message traffic with no loss in cooperative performance in the StarCraft II benchmark.

3. Scaling Spatial Intelligence ⭐⭐⭐⭐⭐
Authors: Zhongang Cai et al.
Spatial reasoning is the next frontier. This paper introduces "SpatialBench", a massive dataset of 3D reasoning tasks.
- They find that current LLMs (even GPT-4) struggle with simple 3D rotations and perspective taking.
- They propose a new "Spatial-ViT" architecture that encodes 3D geometry natively.
- Training on this data improves performance on robot manipulation tasks by 25%.

4. Kandinsky 5.0: A New Era in Image Generation ⭐⭐⭐⭐⭐
Kandinsky 5.0 is a powerful foundation model for generating high-quality images and videos.
Key innovations:
- Real-time generation capabilities (under 1 second per image).
- Improved quality over previous versions (Kandinsky 4.0).
- Efficient architecture using a cascade of diffusion models.
- Can generate both images and short videos (up to 5 seconds).
- Uses a text-encoder that is 2x larger than Stable Diffusion XL for better prompt adherence.
- Training was done on a dataset of 2 billion image-text pairs.
"""

def run_ingest():
    print("Ingesting rich content for ai-research-daily-2025-11-18...")
    result = ingest_episode("ai-research-daily-2025-11-18", RICH_CONTENT)
    print(f"✅ Ingestion complete. Chunks: {result['chunks_count']}")
    print("You can now ask about 'Kandinsky 5.0' or 'Kaiming He's paper'.")

if __name__ == "__main__":
    run_ingest()
