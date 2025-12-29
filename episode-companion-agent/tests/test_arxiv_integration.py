"""
Test ArXiv Fetcher Integration

Tests for arxiv_fetcher.py, paper_scorer.py, and episode_generator.py
"""

import pytest
from datetime import datetime, timedelta
from arxiv_fetcher import ArxivFetcher, fetch_papers_by_date
from paper_scorer import PaperScorer, rank_papers
from episode_generator import EpisodeGenerator


class TestArxivFetcher:
    """Test arXiv fetching functionality"""
    
    def test_fetch_papers_by_date(self):
        """Test fetching papers for a specific date"""
        # Use a recent date that should have papers
        test_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        papers = fetch_papers_by_date(test_date, max_results=10)
        
        assert isinstance(papers, list)
        # Note: May be 0 if no papers that day, but function should still work
        print(f"Fetched {len(papers)} papers for {test_date}")
        
        if papers:
            paper = papers[0]
            assert hasattr(paper, 'arxiv_id')
            assert hasattr(paper, 'title')
            assert hasattr(paper, 'authors')
            assert hasattr(paper, 'abstract')
            assert hasattr(paper, 'categories')
            assert paper.submitted_date == test_date
    
    def test_fetcher_rate_limiting(self):
        """Test that rate limiting is working"""
        import time
        fetcher = ArxivFetcher(delay_seconds=1.0)
        
        start = time.time()
        # Make two calls
        fetcher._throttle()
        fetcher._throttle()
        elapsed = time.time() - start
        
        # Should take at least 1 second due to rate limiting
        assert elapsed >= 1.0


class TestPaperScorer:
    """Test paper scoring and ranking"""
    
    def test_score_paper(self):
        """Test scoring a single paper"""
        from arxiv_fetcher import ArxivPaper
        
        paper = ArxivPaper(
            arxiv_id="2511.14993",
            title="Test Paper",
            authors="Author A, Author B, Author C",
            abstract="This is a test abstract. " * 50,  # Long abstract
            categories="cs.CV, cs.AI",
            submitted_date="2025-11-19",
            pdf_url="https://arxiv.org/pdf/2511.14993.pdf",
            arxiv_url="https://arxiv.org/abs/2511.14993"
        )
        
        scorer = PaperScorer()
        score = scorer.score_paper(paper)
        
        assert isinstance(score, float)
        assert score > 0
        print(f"Paper score: {score:.2f}")
    
    def test_rank_papers(self):
        """Test ranking multiple papers"""
        from arxiv_fetcher import ArxivPaper
        
        papers = [
            ArxivPaper(
                arxiv_id=f"2511.{14990+i}",
                title=f"Paper {i}",
                authors=", ".join([f"Author {j}" for j in range(i+1)]),
                abstract="Abstract. " * (50 + i*10),
                categories="cs.CV" if i % 2 == 0 else "cs.CL",
                submitted_date="2025-11-19",
                pdf_url=f"https://arxiv.org/pdf/2511.{14990+i}.pdf",
                arxiv_url=f"https://arxiv.org/abs/2511.{14990+i}"
            )
            for i in range(10)
        ]
        
        top_papers = rank_papers(papers, top_k=5)
        
        assert len(top_papers) == 5
        print(f"Top papers: {[p.title for p in top_papers]}")


class TestEpisodeGenerator:
    """Test episode generation"""
    
    @pytest.mark.slow
    def test_generate_episode(self):
        """Test full episode generation (slow, requires arXiv + LLM)"""
        # Use a date that should have papers
        test_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        generator = EpisodeGenerator()
        
        try:
            bundle = generator.generate_episode(
                date=test_date,
                top_k=3,  # Small number for test
                max_results=20  # Limit results
            )
            
            assert bundle.episode_id == f"ai-research-daily-{test_date}"
            assert bundle.date_str == test_date
            assert len(bundle.papers) <= 3
            assert bundle.full_report
            
            print(f"Generated episode: {bundle.episode_id}")
            print(f"Papers: {len(bundle.papers)}")
            
        except ValueError as e:
            # If no papers found, that's okay for this test
            print(f"No papers found for {test_date}: {e}")
            pytest.skip(f"No papers found for {test_date}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
