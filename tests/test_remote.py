import asyncio
import httpx

async def main():
    try:
        async with httpx.AsyncClient() as client:
            print("Connecting to SSE...")
            async with client.stream('GET', 'https://yoktezmcp.fastmcp.app/mcp/sse') as resp:
                print(f"Status: {resp.status_code}")
                async for line in resp.aiter_lines():
                    print("SSE Line:", line)
                    if line.startswith("data:"):
                        break
    except Exception as e:
        print("Error:", e)

asyncio.run(main())
