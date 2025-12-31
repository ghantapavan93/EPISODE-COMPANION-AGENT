"""
ArXiv Loader - Upstream Pipeline

This handles the dirty work of talking to arXiv, cleaning dates, 
and generating the HuggingFace links.
"""

import feedparser
import urllib.parse
from datetime import datetime, date
from typing import List, Optional
from dataclasses import dataclass

# The categories we care about (same as the report)
TARGET_CATEGORIES = ["cs.AI", "cs.CV", "cs.LG", "cs.CL", "cs.RO"]

@dataclass
class Paper:
    arxiv_id: str
    title: str
    abstract: str
    authors: List[str]
    primary_category: str
    published_date: date
    pdf_url: str
    
    @property
    def huggingface_url(self):
        # HuggingFace just wraps the ID
        return f"https://huggingface.co/papers/{self.arxiv_id}"

    @property
    def markdown_section(self):
        # Formats the paper for the report body
        return f"""
### {self.title}
**Authors:** {', '.join(self.authors[:3])}{' et al.' if len(self.authors) > 3 else ''}
**Links:** [arXiv]({self.pdf_url}) | [HuggingFace]({self.huggingface_url})

**Abstract:**
{self.abstract}
"""

class ArxivLoader:
    def get_papers_for_date(self, target_date: date, max_results: int = 100) -> List[Paper]:
        """
        Fetches papers submitted on a specific date.
        Note: arXiv API 'submittedDate' is tricky, so we fetch a buffer and filter.
        """
        # Construct query: cat:cs.AI OR cat:cs.CV ...
        cat_query = " OR ".join([f"cat:{c}" for c in TARGET_CATEGORIES])
        
        # Query parameters
        params = {
            "search_query": cat_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        url = f"http://export.arxiv.org/api/query?{urllib.parse.urlencode(params)}"
        feed = feedparser.parse(url)
        
        valid_papers = []
        
        for entry in feed.entries:
            # Parse date (Format: 2025-11-20T14:00:00Z)
            pub_dt = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ").date()
            
            # Filter strictly by date
            if pub_dt == target_date:
                # Clean ID (http://arxiv.org/abs/2101.12345v1 -> 2101.12345)
                raw_id = entry.id.split("/abs/")[-1].split("v")[0]
                
                paper = Paper(
                    arxiv_id=raw_id,
                    title=entry.title.replace("\n", " "),
                    abstract=entry.summary.replace("\n", " "),
                    authors=[a.name for a in entry.authors],
                    primary_category=entry.tags[0]['term'] if entry.tags else "cs.AI",
                    published_date=pub_dt,
                    pdf_url=entry.link
                )
                valid_papers.append(paper)
        
        return valid_papers

    def select_top_papers(self, papers: List[Paper], top_n: int = 7) -> List[Paper]:
        """
        The 'Curator' Logic.
        Real logic would use citations/graph. 
        Antigravity logic: Prioritize specific hot topics and abstract length (proxy for depth).
        """
        # Priority mapping
        priority = {"cs.CV": 5, "cs.LG": 4, "cs.CL": 3, "cs.AI": 2}
        
        def score(p: Paper):
            cat_score = priority.get(p.primary_category, 1)
            # Prefer shorter titles (often punchier) and longer abstracts (more detail)
            return (cat_score, len(p.abstract) - len(p.title))

        # Sort descending by score
        return sorted(papers, key=score, reverse=True)[:top_n]
