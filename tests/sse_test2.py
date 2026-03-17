import asyncio
import httpx
import json

async def test_fastmcp():
    url = "https://yoktezmcp.fastmcp.app/mcp/"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Step 1: Subscribe to SSE stream
        print(f"Connecting to SSE: {url}")
        req = client.build_request("GET", url, headers={"Accept": "text/event-stream"})
        resp = await client.send(req, stream=True)
        print(f"Status: {resp.status_code}")
        
        async for line in resp.aiter_lines():
            line = line.strip()
            print("SSE:", line)
            
            if line.startswith("data: "):
                data = json.loads(line[6:])
                # Try to parse EndpointEvent
                print("DATA", data)
        
        print("SSE closed")

asyncio.run(test_fastmcp())
