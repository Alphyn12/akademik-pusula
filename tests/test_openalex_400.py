import asyncio
import aiohttp
import urllib.parse
import json

async def test():
    query = "Hilmi Kuşçu dergipark"
    start_year = 2000
    end_year = 2026
    
    url = f"https://api.openalex.org/works?filter=author.display_name.search:{urllib.parse.quote(query)}"
    url += f",publication_year:{start_year}-{end_year}&per-page=15"
    
    headers = {'User-Agent': 'mailto:engineering@example.com'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            text = await response.text()
            with open("test_openalex_400.json", "w", encoding="utf-8") as f:
                try:
                    data = json.loads(text)
                    json.dump(data, f, indent=2)
                except:
                    f.write(text)

asyncio.run(test())
