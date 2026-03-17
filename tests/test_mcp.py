import asyncio
from utils.mcp_manager import YokTezMCPManager
import logging

logging.basicConfig(level=logging.DEBUG, filename='mcp_debug_final.log', filemode='w')

async def main():
    mcp = YokTezMCPManager()
    print("Testing Yazar Adı search for 'susantez'...")
    res = await mcp.fetch("susantez", search_type="Yazar Adı")
    print(f"Status: {res['status']}")
    print(f"Message: {res['message']}")
    print(f"Results Count: {len(res['data'])}")
    for d in res['data'][:3]:
        print(f"   - {d['Başlık']} | {d['Yazarlar']}")

asyncio.run(main())
