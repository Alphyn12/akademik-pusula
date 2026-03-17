import asyncio
from utils.mcp_manager import YokTezMCPManager
import logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger('utils.mcp_manager').setLevel(logging.WARNING)

async def test():
    mcp = YokTezMCPManager()
    q = "Hilmi Kuşçu " # Notice trailing space
    print(f"\\n--- Testing trailing space for '{q}' ---")
    res = await mcp.fetch(q, search_type="Yazar Adı")
    print(f"Results Count: {len(res['data'])}")

asyncio.run(test())
