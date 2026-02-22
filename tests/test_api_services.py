import pytest
import asyncio
from api_services.crossref import CrossrefScraper
from api_services.arxiv import ArxivScraper

@pytest.mark.asyncio
async def test_crossref_scraper():
    scraper = CrossrefScraper()
    results = await scraper.fetch(query="machine learning", start_year=2020, end_year=2023)
    
    # Check if results is a list
    assert isinstance(results, list)
    
    # If it returns something, check the shape
    if results:
        first = results[0]
        assert "Başlık" in first
        assert "Yıl" in first
        assert "Erişim Durumu" in first

@pytest.mark.asyncio
async def test_arxiv_scraper():
    scraper = ArxivScraper()
    results = await scraper.fetch(query="quantum computing", start_year=2021, end_year=2022)
    
    assert isinstance(results, list)
    
    if results:
        first = results[0]
        assert "Kaynak" in first
        assert first["Kaynak"] == "arXiv"
        
