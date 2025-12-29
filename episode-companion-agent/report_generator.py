"""
Report Generator - Upstream Pipeline

Uses Google Gemini to write the "Executive Summary" 
so the report feels human-written.
"""

from langchain_ollama import ChatOllama
from arxiv_loader import Paper
from typing import List

REPORT_TEMPLATE = """
You are the editor of 'AI Research Daily'. 
Write a daily briefing based on these 7 papers.

Structure the response exactly like this:

# 🎙️ Today's Deep Dive
[Write a 2-sentence hook about the most interesting paper here]

# 📊 Research Activity
Total submissions today: {total_count}
Primary focus: Computer Vision and LLMs.

# 🌟 Top Papers Today
{paper_sections}

---
INSTRUCTIONS:
1. For the "Deep Dive", pick the paper that seems most "consumer-facing" or "product-ready".
2. Keep the tone professional but excited (like a tech founder).
3. Do not output markdown for the whole block, just the content.
"""

class ReportGenerator:
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:7b-instruct", temperature=0.7)

    def generate_markdown(self, date_str: str, total_count: int, papers: List[Paper]) -> str:
        # 1. Prepare the context
        paper_text = "\n\n".join([
            f"{i+1}. {p.title}\nID: {p.arxiv_id}\nAbstract: {p.abstract[:400]}..." 
            for i, p in enumerate(papers)
        ])

        # 2. Generate the summary using LLM
        # Note: We pass the raw data to LLM to write the "fluff" (hooks/summary)
        prompt = REPORT_TEMPLATE.format(
            total_count=total_count,
            paper_sections=paper_text
        )
        
        response = self.llm.invoke(prompt)
        generated_content = response.content

        # 3. Append the FULL technical details for the Agent to ingest later
        full_report = f"Episode Date: {date_str}\n\n" + generated_content + "\n\n# 📚 Full Paper Details\n"
        
        for p in papers:
            full_report += p.markdown_section + "\n---\n"
            
        return full_report
