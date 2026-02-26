import aiohttp
import urllib.parse
from typing import List, Dict, Any
import streamlit as st
from utils.scraper_base import BaseScraper
import asyncio

class IEEEScraper(BaseScraper):
    def __init__(self):
        super().__init__("IEEE Xplore")
        
    async def fetch(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        try:
            start_year = filters.get('start_year', 1990)
            end_year = filters.get('end_year', 2026)
            
            api_key = self.get_config("ieee", "api_key")
            if not api_key:
                return {
                    "source": self.name,
                    "status": "error",
                    "message": "IEEE API Key (.streamlit/secrets.toml veya Environment Variable) tanımlanmamış.",
                    "data": []
                }
                
            url = f"http://ieeexploreapi.ieee.org/api/v1/search/articles?querytext={urllib.parse.quote(query)}&apikey={api_key}&max_records=15"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get('articles', [])
                        for article in articles:
                            try:
                                title = article.get('title', 'Bilinmiyor')
                                
                                year = "Bilinmiyor"
                                pub_year = str(article.get('publication_year', ''))
                                if pub_year.isdigit():
                                    year = pub_year
                                    
                                if str(year).isdigit() and not (start_year <= int(year) <= end_year):
                                    continue
                                    
                                authors_dict = article.get('authors', {})
                                authors_list = authors_dict.get('authors', []) if isinstance(authors_dict, dict) else []
                                authors = ", ".join([a.get('full_name', '') for a in authors_list]) if authors_list else "Bilinmiyor"
                                
                                doi = article.get('doi', '-')
                                is_oa = article.get('is_open_access', False)
                                status = "Açık" if is_oa else "Kilitli"
                                
                                abstract = article.get('abstract', 'Özet bulunamadı.')
                                
                                link = article.get('html_url', article.get('pdf_url', '-'))
                                if link == "-" and doi != "-":
                                    link = f"https://doi.org/{doi}"
                                    
                                results.append({
                                    "Kaynak": self.name, "Yıl": year, "Başlık": title,
                                    "Yazarlar": authors, "Erişim Durumu": status,
                                    "DOI": doi, "Link": link, "Özet": abstract
                                })
                            except Exception as item_e:
                                self.logger.warning(f"Error parsing ieee item: {item_e}")
                                continue
                    elif response.status == 401 or response.status == 403:
                         return {
                            "source": self.name,
                            "status": "error",
                            "message": "IEEE API Key geçersiz veya süresi dolmuş. Yetkilendirme hatası.",
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
            self.logger.error(f"IEEE Error: {str(e)}")
            return {
                "source": self.name,
                "status": "error",
                "message": f"Beklenmeyen bir hata oluştu: {str(e)}",
                "data": []
            }
