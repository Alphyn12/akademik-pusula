import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def fetch_dp():
    url = "https://dergipark.org.tr/tr/search?q=machine+learning"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            html = await response.text()
            with open("dp.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Wrote html")

asyncio.run(fetch_dp())
