import aiohttp
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from utils.scraper_base import BaseScraper
import asyncio

class ASMEScraper(BaseScraper):
    def __init__(self):
        super().__init__("ASME")
        
    async def fetch(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        try:
            start_year = filters.get('start_year', 1990)
            end_year = filters.get('end_year', 2026)
            
            url = f"https://api.crossref.org/works?query.title={urllib.parse.quote(query)}&filter=prefix:10.1115&rows=15"
            headers = {'User-Agent': 'MakalePusulas/3.0 (mailto:engineering@example.com)'}
            
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
                                        
                                if str(year).isdigit() and not (start_year <= int(year) <= end_year):
                                    continue
                                    
                                doi = item.get('DOI', '-')
                                is_oa = item.get('is-oa', False)
                                status = "Açık" if is_oa else "Kilitli"
                                
                                abstract = item.get('abstract', 'Özet bulunamadı.')
                                if abstract != 'Özet bulunamadı.':
                                    abstract = BeautifulSoup(abstract, 'html.parser').get_text()
                                
                                link = item.get('URL', '')
                                if link == "" and doi != "-":
                                    link = f"https://doi.org/{doi}"
                                    
                                results.append({
                                    "Kaynak": self.name, "Yıl": year, "Başlık": title,
                                    "Yazarlar": authors, "Erişim Durumu": status,
                                    "DOI": doi, "Link": link, "Özet": abstract
                                })
                            except Exception as item_e:
                                self.logger.warning(f"Error parsing asme item: {item_e}")
                                continue
            return {
                "source": self.name,
                "status": "success",
                "message": "",
                "data": results
            }
        except asyncio.TimeoutError:
            return {
                "source": self.name,
                "status": "error",
                "message": "İstek zaman aşımına uğradı.",
                "data": []
            }
        except Exception as e:
            self.logger.error(f"ASME Error: {str(e)}")
            return {
                "source": self.name,
                "status": "error",
                "message": f"Beklenmeyen bir hata oluştu: {str(e)}",
                "data": []
            }
