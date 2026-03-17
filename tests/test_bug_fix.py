import asyncio
from utils.fetcher import fetch_all_sources
import logging

logging.basicConfig(level=logging.WARNING)

async def test():
    sources = ["arXiv", "YÖK Tez / TR Üniversiteleri"]
    query = "Hilmi Kuşçu"
    filters = {"search_type": "Yazar Adı", "start_year": 1990, "end_year": 2026}
    
    print("Fetching sources...")
    res = await fetch_all_sources(sources, query, filters)
    
    print("\\n--- ERRORS ---")
    for err in res.get("errors", []):
        print(f"{err.get('source')}: {err.get('message')}")
        
    print("\\n--- RESULTS ---")
    results = res.get("results", [])
    print(f"Total Results: {len(results)}")
    
    # Check distribution
    dist = {}
    for r in results:
        src = r.get("Kaynak", "Unknown")
        dist[src] = dist.get(src, 0) + 1
        
    for k, v in dist.items():
        print(f"{k}: {v} results")

asyncio.run(test())
