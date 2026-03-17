import asyncio
from utils.mcp_manager import YokTezMCPManager
import httpx
import json

async def manual_test(query):
    tr_query = query.replace('i', 'İ').replace('ı', 'I').upper()
    print(f"Testing for uppercase query: {tr_query}")
    
    url = "https://yoktezmcp.fastmcp.app/mcp/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Author only
        payload1 = {
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": "search_yok_tez_detailed", "arguments": {"author_name": tr_query, "results_per_page": 5}}
        }
        res1 = await client.post(url, json=payload1, headers=headers)
        print("Author only len:", len(res1.text))
        
        # Test 2: Advisor only
        payload2 = {
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": "search_yok_tez_detailed", "arguments": {"advisor_name": tr_query, "results_per_page": 5}}
        }
        res2 = await client.post(url, json=payload2, headers=headers)
        print("Advisor only len:", len(res2.text))

asyncio.run(manual_test("susantez"))
