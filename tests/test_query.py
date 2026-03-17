import asyncio
from utils.mcp_manager import YokTezMCPManager

import logging
logging.basicConfig(level=logging.WARNING)
# also silence utils logger
logging.getLogger('utils.mcp_manager').setLevel(logging.WARNING)

async def test():
    mcp = YokTezMCPManager()
    queries = ["Cem Çetinarslan", "Hilmi Kuşçu", "Çem Çetinarslan"]
    for q in queries:
        print(f"\\n--- Testing Yazar Adı search for '{q}' ---")
        res = await mcp.fetch(q, search_type="Yazar Adı")
        print(f"Results Count: {len(res['data'])}")
        for d in res['data']:
            print(f"   - {d['Başlık'][:50]}... | {d['Yazarlar']}")

asyncio.run(test())
