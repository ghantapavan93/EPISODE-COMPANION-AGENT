"""
Episode Generator Module

Generates daily episodes by:
1. Fetching papers from arXiv
2. Scoring and ranking papers
3. Generating report text with LLM
4. Building EpisodeBundleGpk objects
"""

import logging
from typing import List, Optional
from datetime import datetime
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

from arxiv_fetcher import ArxivPaper, fetch_papers_by_date
from paper_scorer import rank_papers
from ingest import EpisodeBundleGpk, PaperEntryGpk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EpisodeGenerator:
    """Generates daily research episodes"""
    
    def __init__(self, model_name: str = "qwen2.5:7b-instruct"):
        """
        Initialize generator with LLM.
        
        Args:
            model_name: Ollama model to use for report generation
        """
        self.llm = ChatOllama(
            model=model_name,
            temperature=0.7,
            num_ctx=4096
        )
        self.parser = StrOutputParser()
    
    def _build_report_prompt(
        self, 
        papers: List[ArxivPaper], 
        date: str, 
        total_submissions: int
    ) -> str:
        """Build prompt for LLM report generation"""
        
        # Format papers for prompt
        papers_text = ""
        for i, paper in enumerate(papers, 1):
            papers_text += f"\n{i}. **{paper.title}**\n"
            papers_text += f"   - Authors: {paper.authors}\n"
            papers_text += f"   - Categories: {paper.categories}\n"
            papers_text += f"   - Abstract: {paper.abstract[:300]}...\n"
            papers_text += f"   - arXiv ID: {paper.arxiv_id}\n"
        
        # Parse date for display
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            display_date = dt.strftime("%m/%d")
        except:
            display_date = date
        
        prompt = f"""You are writing a daily research report for AI researchers and practitioners.

Date: {date}
Total papers submitted: {total_submissions}
Top papers selected: {len(papers)}

Here are the top {len(papers)} papers for today:
{papers_text}

Generate a comprehensive daily research report in this exact format:

Date: {date}

🎙️ AI Research Daily {display_date}: [Create an engaging hook mentioning 2-3 key papers]

Listen: https://example.com/listen/{display_date.replace('/', '-')}

Papers Covered in Today's Episode

[List each paper as: Title: huggingface.co/papers/ARXIV_ID]

IN DEPTH

Executive Summary
[Write 2-3 sentences summarizing the key themes and advancements from today's papers]

Research Activity Overview
- Total Submissions: {total_submissions}
- Featured Papers: {len(papers)}
- Primary Fields: [List main categories]

Noteworthy Researchers Today
[List 2-3 notable researchers/teams from the papers with a brief note about their contribution]

🌟 Top Papers Today

[For each paper, write:]
[Number]. [Title] ⭐⭐⭐⭐⭐ (or ⭐⭐⭐⭐ or ⭐⭐⭐)

Why this matters:
[1-2 sentences on significance]

Key Innovation:
[1-2 sentences on the main contribution]

Potential Impact:
[1-2 sentences on how this could affect the field]

---

📊 Report Metadata
Curated: {len(papers)} papers from {total_submissions} submissions
Primary Areas: [List categories]
Generation Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}

Write the complete report now:"""
        
        return prompt
    
    def generate_report_text(
        self, 
        papers: List[ArxivPaper], 
        date: str, 
        total_submissions: int
    ) -> str:
        """
        Generate report text using LLM.
        
        Args:
            papers: List of top papers
            date: Date string "YYYY-MM-DD"
            total_submissions: Total number of papers fetched
            
        Returns:
            Generated report text
        """
        logger.info(f"Generating report for {date} with {len(papers)} papers")
        
        prompt = self._build_report_prompt(papers, date, total_submissions)
        
        chain = self.llm | self.parser
        report = chain.invoke(prompt)
        
        logger.info("Report generated successfully")
        return report
    
    def generate_episode(
        self,
        date: str,
        categories: Optional[List[str]] = None,
        top_k: int = 7,
        max_results: int = 1000
    ) -> EpisodeBundleGpk:
        """
        Generate a complete episode bundle.
        
        Args:
            date: Date string "YYYY-MM-DD"
            categories: arXiv categories to fetch
            top_k: Number of top papers to select
            max_results: Max papers to fetch from arXiv
            
        Returns:
            EpisodeBundleGpk object ready for ingestion
        """
        logger.info(f"Generating episode for {date}")
        
        # 1. Fetch papers
        logger.info("Step 1: Fetching papers from arXiv...")
        all_papers = fetch_papers_by_date(date, categories, max_results)
        total_submissions = len(all_papers)
        logger.info(f"Fetched {total_submissions} papers")
        
        if not all_papers:
            logger.warning(f"No papers found for {date}")
            raise ValueError(f"No papers found for {date}")
        
        # 2. Rank papers
        logger.info(f"Step 2: Ranking papers, selecting top {top_k}...")
        top_papers = rank_papers(all_papers, top_k)
        logger.info(f"Selected {len(top_papers)} top papers")
        
        # 3. Generate report
        logger.info("Step 3: Generating report with LLM...")
        report_text = self.generate_report_text(top_papers, date, total_submissions)
        
        # 4. Build episode bundle
        logger.info("Step 4: Building episode bundle...")
        
        # Create episode ID
        episode_id = f"ai-research-daily-{date}"
        
        # Build paper entries
        paper_entries = []
        for i, paper in enumerate(top_papers, 1):
            paper_entries.append(PaperEntryGpk(
                title=paper.title,
                url=f"https://huggingface.co/papers/{paper.arxiv_id}",
                rank=i,
                in_audio=True,  # All top papers are considered "in audio"
                text_content=None  # Will be populated from report if needed
            ))
        
        # Create hook (extract from report if available)
        hook_line = f"AI Research Daily {date}: {top_papers[0].title[:50]}..."
        if "🎙️" in report_text:
            # Try to extract hook from report
            lines = report_text.split("\n")
            for line in lines:
                if "🎙️" in line:
                    hook_line = line.strip()
                    break
        
        # Create bundle
        bundle = EpisodeBundleGpk(
            episode_id=episode_id,
            date_str=date,
            hook=hook_line,
            listen_url=f"https://example.com/listen/{date}",
            full_report=report_text,
            audio_transcript=None,  # Can be added later with TTS
            papers=paper_entries
        )
        
        logger.info(f"✅ Episode {episode_id} generated successfully")
        
        return bundle


def generate_episode(
    date: str,
    categories: Optional[List[str]] = None,
    top_k: int = 7,
    max_results: int = 1000
) -> EpisodeBundleGpk:
    """
    Convenience function to generate an episode.
    
    Args:
        date: Date string "YYYY-MM-DD"
        categories: arXiv categories to fetch
        top_k: Number of top papers to select
        max_results: Max papers to fetch from arXiv
        
    Returns:
        EpisodeBundleGpk object
    """
    generator = EpisodeGenerator()
    return generator.generate_episode(date, categories, top_k, max_results)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_date = sys.argv[1]
    else:
        test_date = "2025-11-19"
    
    print(f"Generating episode for {test_date}...\n")
    
    try:
        bundle = generate_episode(test_date, top_k=7)
        
        print(f"✅ Episode Generated: {bundle.episode_id}")
        print(f"Date: {bundle.date_str}")
        print(f"Papers: {len(bundle.papers)}")
        print(f"\nHook: {bundle.hook}")
        print(f"\n{'='*60}")
        print(bundle.full_report[:500])
        print("...")
        print(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"Error generating episode: {e}")
        import traceback
        traceback.print_exc()
