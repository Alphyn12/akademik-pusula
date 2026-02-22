import asyncio
from typing import List, Dict, Any
from utils.scraper_base import BaseScraper
from scholarly import scholarly
import time

class ScholarScraper(BaseScraper):
    def __init__(self):
        super().__init__("Google Scholar")
        
    def _fetch_sync(self, query: str, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        results = []
        try:
            search_query = scholarly.search_pubs(query)
            for i in range(10):
                try:
                    pub = next(search_query)
                    bib = pub.get('bib', {})
                    title = bib.get('title', 'Bilinmiyor')
                    year = bib.get('pub_year', 'Bilinmiyor')
                    
                    if str(year).isdigit():
                        if not (start_year <= int(year) <= end_year):
                            continue
                    
                    authors = ', '.join(bib.get('author', ['Bilinmiyor']))
                    pub_url = pub.get('pub_url', '')
                    eprint_url = pub.get('eprint_url', '')
                    status = "Açık" if eprint_url else "Kilitli/Bilinmiyor"
                    abstract = bib.get('abstract', 'Özet bulunamadı.')
                    
                    results.append({
                        "Kaynak": "Google Scholar", "Yıl": year, "Başlık": title,
                        "Yazarlar": authors, "Erişim Durumu": status, "DOI": "-",
                        "Link": pub_url if pub_url else eprint_url, "Özet": abstract
                    })
                    time.sleep(1) # Be gentle with Google Scholar
                except StopIteration:
                    break
                except Exception as item_e:
                    self.logger.warning(f"Error parsing scholar item: {item_e}")
                    continue
        except Exception as e:
            self.logger.error(f"Scholar Error: {str(e)}")
        return results

    async def fetch(self, query: str, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self._fetch_sync, query, start_year, end_year)
