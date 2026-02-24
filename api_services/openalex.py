import aiohttp
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from utils.scraper_base import BaseScraper
import asyncio

class OpenAlexScraper(BaseScraper):
    def __init__(self):
        super().__init__("OpenAlex (Global)")
        
    async def fetch(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        try:
            start_year = filters.get('start_year', 1990)
            end_year = filters.get('end_year', 2026)
            
            # Using OpenAlex API
            # Search by title/abstract/full text. Format: https://api.openalex.org/works?search=query
            # Filter by year. 
            # OpenAlex provides up to 100k free requests per day without API key.
            # Using polite pool by providing an email in User-Agent is recommended.

            url = f"https://api.openalex.org/works?search={urllib.parse.quote(query)}"
            url += f"&filter=publication_year:{start_year}-{end_year}"
            
            # Limit to 15 results
            url += "&per-page=15"
            
            headers = {'User-Agent': 'mailto:engineering@example.com'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=12) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get('results', [])
                        
                        for item in items:
                            try:
                                title = item.get('title', 'Bilinmiyor')
                                if not title:
                                    title = "Bilinmiyor"
                                    
                                year = str(item.get('publication_year', 'Bilinmiyor'))
                                
                                authorships = item.get('authorships', [])
                                authors_list = []
                                for auth in authorships:
                                    author_info = auth.get('author', {})
                                    display_name = author_info.get('display_name')
                                    if display_name:
                                        authors_list.append(display_name)
                                        
                                authors = ", ".join(authors_list).strip() or "Bilinmiyor"
                                
                                doi = item.get('doi', '-')
                                
                                open_access = item.get('open_access', {})
                                is_oa = open_access.get('is_oa', False)
                                status = "Açık" if is_oa else "Kilitli"
                                
                                abstract = "Özet bulunamadı."
                                
                                # OpenAlex returns abstract via inverted index, we need to reconstruct it if we want it,
                                # but usually simple searches just want the title/link first. Let's try to reconstruct.
                                abstract_inverted = item.get('abstract_inverted_index', {})
                                if abstract_inverted:
                                    word_index = []
                                    for word, positions in abstract_inverted.items():
                                        for pos in positions:
                                            word_index.append((pos, word))
                                    word_index.sort(key=lambda x: x[0])
                                    abstract = " ".join([w[1] for w in word_index])
                                
                                link = doi if doi != "-" else ""
                                if not link:
                                    primary_location = item.get('primary_location', {})
                                    if primary_location:
                                        link = primary_location.get('pdf_url') or primary_location.get('landing_page_url') or ""
                                    
                                results.append({
                                    "Kaynak": self.name, "Yıl": year, "Başlık": title,
                                    "Yazarlar": authors, "Erişim Durumu": status,
                                    "DOI": doi, "Link": link, "Özet": abstract
                                })
                            except Exception as item_e:
                                self.logger.warning(f"Error parsing OpenAlex item: {item_e}")
                                continue
                    elif response.status == 429:
                         return {
                            "source": self.name,
                            "status": "error",
                            "message": "OpenAlex günlük istek limitleri (Rate Limit) aşıldı.",
                            "data": []
                        }
                    else:
                         return {
                            "source": self.name,
                            "status": "error",
                            "message": f"OpenAlex sunucu hatası: HTTP {response.status}",
                            "data": []
                        }

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
            self.logger.error(f"OpenAlex Error: {str(e)}")
            return {
                "source": self.name,
                "status": "error",
                "message": f"Beklenmeyen bir hata oluştu: {str(e)}",
                "data": []
            }
