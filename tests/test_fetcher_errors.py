import asyncio
from utils.fetcher import fetch_all_sources

async def test():
    # Test sources
    sources = ["OpenAlex (Global)", "DergiPark", "YÖK Tez / TR Üniversiteleri"]
    query = "test"
    filters = {"search_type": "Kavram/Kelime Arama", "start_year": 2000, "end_year": 2024}
    
    print("Fetching sources...")
    res = await fetch_all_sources(sources, query, filters)
    
    print("--- ERRORS ---")
    for err in res.get("errors", []):
        print(f"{err.get('source')}: {err.get('message')}")
        
    print("--- RESULTS COUNT ---")
    print(len(res.get("results", [])))

asyncio.run(test())
