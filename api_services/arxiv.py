import aiohttp
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from utils.scraper_base import BaseScraper

class ArxivScraper(BaseScraper):
    def __init__(self):
        super().__init__("arXiv")
        
    async def fetch(self, query: str, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        results = []
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"http://export.arxiv.org/api/query?search_query=ti:{encoded_query}+OR+abs:{encoded_query}&start=0&max_results=20"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        text = await response.text()
                        soup = BeautifulSoup(text, 'xml')
                        entries = soup.find_all('entry')
                        for entry in entries:
                            try:
                                title = entry.title.text.strip().replace('\n', ' ')
                                year = entry.published.text[:4] if entry.published else "Bilinmiyor"
                                
                                if year.isdigit() and not (start_year <= int(year) <= end_year):
                                    continue
                                    
                                authors = ", ".join([author.find('name').text for author in entry.find_all('author')])
                                doi = entry.find('arxiv:doi')
                                doi_val = doi.text if doi else "-"
                                
                                abstract = entry.summary.text.strip().replace('\n', ' ') if entry.summary else "Özet bulunamadı."
                                
                                results.append({
                                    "Kaynak": self.name, "Yıl": year, "Başlık": title,
                                    "Yazarlar": authors, "Erişim Durumu": "Açık",
                                    "DOI": doi_val, "Link": entry.id.text, "Özet": abstract
                                })
                            except Exception as item_e:
                                self.logger.warning(f"Error parsing arxiv item: {item_e}")
                                continue
        except Exception as e:
            self.logger.error(f"arXiv Error: {str(e)}")
        return results
