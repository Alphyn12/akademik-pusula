import asyncio
import aiohttp
import time
from api_services.arxiv import ArxivScraper

async def test_arxiv():
    scraper = ArxivScraper()
    start_time = time.time()
    res = await scraper.fetch("Hilmi Kuşçu", {"search_type": "Yazar Adı", "start_year": 1990, "end_year": 2026})
    print(f"Time taken: {time.time() - start_time:.2f}s")
    print("arxiv:", res)

asyncio.run(test_arxiv())
