import asyncio
import aiohttp
import urllib.parse
import json

async def test():
    query = "Hilmi Kuşçu"
    start_year = 2000
    end_year = 2026
    
    # Try the raw_author_name.search filter mentioned in OpenAlex error
    url = f"https://api.openalex.org/works?filter=raw_author_name.search:{urllib.parse.quote(query)}"
    url += f",publication_year:{start_year}-{end_year}&per-page=15"
    
    headers = {'User-Agent': 'mailto:engineering@example.com'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            print("Status:", response.status)
            text = await response.text()
            try:
                data = json.loads(text)
                print("Results Count:", len(data.get('results', [])))
            except:
                print(text)

asyncio.run(test())
