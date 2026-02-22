import aiohttp
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from utils.scraper_base import BaseScraper

class CrossrefScraper(BaseScraper):
    def __init__(self):
        super().__init__("Crossref")
        
    async def fetch(self, query: str, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        results = []
        try:
            url = f"https://api.crossref.org/works?query.title={urllib.parse.quote(query)}&filter=from-pub-date:{start_year},until-pub-date:{end_year}&rows=20"
            headers = {'User-Agent': 'AkademikPusula/3.0 (mailto:engineering@example.com)'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get('message', {}).get('items', [])
                        for item in items:
                            try:
                                title = item.get('title', ['Bilinmiyor'])[0]
                                
                                query_words = set(query.lower().split())
                                title_words = set(title.lower().split())
                                if len(query_words) > 1 and not (query_words & title_words):
                                    continue
            
                                authors_list = [author.get('family', '') + " " + author.get('given', '') for author in item.get('author', [])]
                                authors = ", ".join(authors_list).strip() or "Bilinmiyor"
                                
                                year = "Bilinmiyor"
                                for df_ in ['published-print', 'published-online', 'created']:
                                    if df_ in item and 'date-parts' in item[df_]:
                                        year_val = item[df_]['date-parts'][0][0]
                                        if year_val:
                                            year = str(year_val)
                                        break
                                
                                doi = item.get('DOI', '-')
                                is_oa = item.get('is-oa', False)
                                status = "Açık" if is_oa else "Kilitli"
                                
                                abstract = item.get('abstract', 'Özet bulunamadı.')
                                if abstract != 'Özet bulunamadı.':
                                    abstract = BeautifulSoup(abstract, 'html.parser').get_text()
                                
                                results.append({
                                    "Kaynak": self.name, "Yıl": year, "Başlık": title,
                                    "Yazarlar": authors, "Erişim Durumu": status,
                                    "DOI": doi, "Link": item.get('URL', ''), "Özet": abstract
                                })
                            except Exception as item_e:
                                self.logger.warning(f"Error parsing crossref item: {item_e}")
                                continue
        except Exception as e:
            self.logger.error(f"Crossref Error: {str(e)}")
        return results
