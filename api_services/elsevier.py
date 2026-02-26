import asyncio
import aiohttp
from typing import List, Dict, Any
import streamlit as st
from utils.scraper_base import BaseScraper
import urllib.parse

class ElsevierScraper(BaseScraper):
    def __init__(self):
        super().__init__("Elsevier (ScienceDirect/Scopus)")
        self.base_url = "https://api.elsevier.com/content/search/scopus"
        
    async def fetch(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        try:
            # Check for API Key in Streamlit SECRETS
            api_key = self.get_config("elsevier", "api_key")
            if not api_key:
                return {
                    "source": self.name,
                    "status": "error",
                    "message": "Elsevier API Key (.streamlit/secrets.toml veya Environment Variable) tanımlanmamış. ScienceDirect araması yapılamıyor.",
                    "data": []
                }
            start_year = filters.get('start_year', 1990)
            end_year = filters.get('end_year', 2026)
            
            # Construct Scopus Advanced Query
            # Example: TITLE-ABS-KEY("machine learning") AND PUBYEAR > 2020 AND PUBYEAR < 2024
            scopus_query = f"TITLE-ABS-KEY({query}) AND PUBYEAR > {start_year - 1} AND PUBYEAR < {end_year + 1}"
            
            headers = {
                "X-ELS-APIKey": api_key,
                "Accept": "application/json"
            }
            
            params = {
                "query": scopus_query,
                "count": 25 # number of results per request
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(self.base_url, params=params, timeout=15) as response:
                    
                    if response.status == 429:
                        return {
                            "source": self.name,
                            "status": "error",
                            "message": "Elsevier API limitleriniz doldu (Rate Limit Exceeded).",
                            "data": []
                        }
                    elif response.status == 401:
                         return {
                            "source": self.name,
                            "status": "error",
                            "message": "Elsevier API Key geçersiz veya süresi dolmuş. Yetkilendirme hatası (401).",
                            "data": []
                        }
                        
                    response.raise_for_status()
                    data = await response.json()
                    
                    search_results = data.get("search-results", {})
                    entries = search_results.get("entry", [])
                    
                    if not entries:
                        # Empty results is not an error
                        pass
                    
                    for item in entries:
                        try:
                            if 'error' in item:
                                continue
                                
                            title = item.get('dc:title', 'Bilinmiyor')
                            
                            year = "Bilinmiyor"
                            cover_date = item.get('prism:coverDate') 
                            if cover_date and len(cover_date)>=4:
                                year = cover_date[:4]
                                
                            authors = item.get('dc:creator', 'Bilinmiyor')
                            doi = item.get('prism:doi', '-')
                            openaccess_flag = str(item.get('openaccessFlag', '0'))
                            if openaccess_flag == '0':
                                openaccess_flag = str(item.get('openaccess', '0')) # Fallback
                                
                            status = "Açık" if openaccess_flag.lower() in ['1', 'true'] else "Kilitli"
                            
                            abstract = item.get('dc:description', 'Özet bulunamadı.') 
                            
                            link = "-"
                            if item.get('link'):
                                for l in item['link']:
                                    if l.get('@ref') == 'scopus':
                                        link = l.get('@href', '-')
                                        break
                                    if l.get('@ref') == 'scidir' and link == '-':
                                        link = l.get('@href', '-')
                            if link == "-" and doi != "-":
                                link = f"https://doi.org/{doi}"
                                        
                            results.append({
                                "Kaynak": "Elsevier (Scopus)", "Yıl": year, "Başlık": title,
                                "Yazarlar": authors, "Erişim Durumu": status,
                                "DOI": doi, "Link": link, "Özet": abstract
                            })
                        except Exception as item_e:
                            self.logger.warning(f"Error parsing elsevier item: {item_e}")
                            continue

            return {
                "source": self.name,
                "status": "success",
                "message": "",
                "data": results
            }

        except aiohttp.ClientError as e:
            return {
                "source": self.name,
                "status": "error",
                "message": f"Bağlantı hatası: {str(e)}",
                "data": []
            }
        except asyncio.TimeoutError:
             return {
                "source": self.name,
                "status": "error",
                "message": "İstek zaman aşımına uğradı.",
                "data": []
            }
        except Exception as e:
            self.logger.error(f"Elsevier Error: {str(e)}")
            return {
                "source": self.name,
                "status": "error",
                "message": f"Beklenmeyen bir hata oluştu: {str(e)}",
                "data": []
            }
