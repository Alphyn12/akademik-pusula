import asyncio
import httpx
import json

async def test_fastmcp():
    url = "https://yoktezmcp.fastmcp.app/mcp/"
    post_url = None
    
    async with httpx.AsyncClient() as client:
        # Step 1: Subscribe to SSE stream
        print(f"Connecting to SSE: {url}")
        req = client.build_request("GET", url, headers={"Accept": "text/event-stream"})
        resp = await client.send(req, stream=True)
        
        async for line in resp.aiter_lines():
            line = line.strip()
            print("SSE:", line)
            
            if line.startswith("data: "):
                data = line[6:]
                # Try to parse EndpointEvent
                if "endpoint" in line.lower() or "post" in line.lower():
                    # We might get an endpoint url here
                    pass
            
            if "endpoint" in line:
                    pass
        
        print("SSE closed")

asyncio.run(test_fastmcp())
