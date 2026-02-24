import asyncio
from typing import List, Dict, Any

from api_services.openalex import OpenAlexScraper
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
    "OpenAlex (Global)": OpenAlexScraper,
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

async def fetch_all_sources(sources: List[str], query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Asynchronously fetch results from all selected sources.
    Returns a dictionary containing 'results' (the aggregated list of articles)
    and 'errors' (a list of error dictionaries for UI display).
    """
    tasks = []
    
    # Instantiate scrapers and create tasks
    for source_name in sources:
        scraper_class = scraper_map.get(source_name)
        if scraper_class:
            scraper = scraper_class()
            coro = scraper.fetch(query, filters)
            task = asyncio.wait_for(coro, timeout=40.0)
            tasks.append(task)
            
    # Gather all results concurrently
    gathered_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    aggregated_results = []
    errors = []
    
    for idx, result in enumerate(gathered_results):
        source_name = sources[idx] if idx < len(sources) else "Bilinmeyen Kaynak"
        if isinstance(result, Exception):
            # A timeout or unhandled exception directly from the scraper
            errors.append({
                "source": source_name,
                "status": "error",
                "message": f"Zaman aşımı veya beklenmeyen hata: {str(result)}"
            })
        elif isinstance(result, dict):
            # Standardized response
            if result.get("status") == "error":
                errors.append(result)
            elif result.get("status") == "success":
                data = result.get("data", [])
                if isinstance(data, list):
                    aggregated_results.extend(data)
        elif isinstance(result, list):
            # Backward compatibility for scrapers not yet updated
            aggregated_results.extend(result)
            
    return {"results": aggregated_results, "errors": errors}
