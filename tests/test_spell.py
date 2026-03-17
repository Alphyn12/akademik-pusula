import asyncio
from utils.mcp_manager import YokTezMCPManager

import logging
logging.basicConfig(level=logging.WARNING)

async def test():
    mcp = YokTezMCPManager()
    queries = ["Hilmi Kuşcu", "HİLMİ KUŞCU", "Cem Çetinarslan ", "Cem Cetinarslan"]
    for q in queries:
        print(f"\\n--- Testing Yazar Adı search for '{q}' ---")
        res = await mcp.fetch(q, search_type="Yazar Adı")
        print(f"Results Count: {len(res['data'])}")

asyncio.run(test())
