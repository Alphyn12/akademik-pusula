import asyncio
import json
from utils.mcp_manager import YokTezMCPManager

async def test_mcp():
    mcp = YokTezMCPManager()
    
    res = await mcp.fetch("Hilmi Kuşçu", search_type="Yazar Adı")
    data = res.get("data", [])
    
    with open("test_yoktez_out.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("Done. Saved to test_yoktez_out.json")

asyncio.run(test_mcp())
