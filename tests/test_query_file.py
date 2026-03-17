import asyncio
from utils.mcp_manager import YokTezMCPManager

import logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger('utils.mcp_manager').setLevel(logging.WARNING)

async def test():
    mcp = YokTezMCPManager()
    queries = ["Cem Çetinarslan", "Hilmi Kuşçu", "Çem Çetinarslan"]
    
    with open("test_query_out.txt", "w", encoding="utf-8") as f:
        for q in queries:
            f.write(f"\\n--- Testing Yazar Adı search for '{q}' ---\\n")
            res = await mcp.fetch(q, search_type="Yazar Adı")
            f.write(f"Results Count: {len(res['data'])}\\n")
            for d in res['data']:
                f.write(f"   - {d['Başlık'][:50]}... | {d['Yazarlar']}\\n")

asyncio.run(test())
