import asyncio
from typing import List, Dict, Any

from api_services.scholar import ScholarScraper
from api_services.crossref import CrossrefScraper
from api_services.arxiv import ArxivScraper
from api_services.dergipark import DergiParkScraper
from api_services.yok_tez import YokTezScraper
from api_services.tr_dizin import TRDizinScraper
from api_services.ieee import IEEEScraper
from api_services.elsevier import ElsevierScraper
from api_services.springer import SpringerScraper
from api_services.asme import ASMEScraper

# Mapping of source names to their respective scraper classes
scraper_map = {
    "Google Scholar": ScholarScraper,
    "Crossref": CrossrefScraper,
    "arXiv": ArxivScraper,
    "DergiPark": DergiParkScraper,
    "YÖK Tez / TR Üniversiteleri": YokTezScraper,
    "TR Kaynaklı / TR Dizin": TRDizinScraper,
    "IEEE Xplore": IEEEScraper,
    "Elsevier (ScienceDirect)": ElsevierScraper,
    "Springer": SpringerScraper,
    "ASME": ASMEScraper
}

async def fetch_all_sources(sources: List[str], query: str, start_year: int, end_year: int) -> List[Dict[str, Any]]:
    """
    Asynchronously fetch results from all selected sources.
    """
    tasks = []
    
    # Instantiate scrapers and create tasks
    for source_name in sources:
        scraper_class = scraper_map.get(source_name)
        if scraper_class:
            scraper = scraper_class()
            coro = scraper.fetch(query, start_year, end_year)
            task = asyncio.wait_for(coro, timeout=40.0)
            tasks.append(task)
            
    # Gather all results concurrently
    gathered_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_results = []
    for result in gathered_results:
        # Ignore exceptions from failed scrapers (they log themselves)
        if isinstance(result, list):
            all_results.extend(result)
            
    return all_results
