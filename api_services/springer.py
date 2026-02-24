import aiohttp
import urllib.parse
from typing import List, Dict, Any
import streamlit as st
from utils.scraper_base import BaseScraper
import asyncio

class SpringerScraper(BaseScraper):
    def __init__(self):
        super().__init__("Springer")
        
    async def fetch(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        try:
            start_year = filters.get('start_year', 1990)
            end_year = filters.get('end_year', 2026)
            
            if "springer" in st.secrets and "api_key" in st.secrets["springer"]:
                api_key = st.secrets["springer"]["api_key"]
            else:
                return {
                    "source": self.name,
                    "status": "error",
                    "message": "Springer API Key (.streamlit/secrets.toml) dosyasına tanımlanmamış.",
                    "data": []
                }
                
            url = f"http://api.springernature.com/meta/v2/json?q={urllib.parse.quote(query)}&api_key={api_key}&p=15"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        records = data.get('records', [])
                        for record in records:
                            try:
                                title = record.get('title', 'Bilinmiyor')
                                
                                pub_date = record.get('publicationDate', '')
                                year = pub_date[:4] if len(pub_date) >= 4 and pub_date[:4].isdigit() else "Bilinmiyor"
                                
                                if str(year).isdigit() and not (start_year <= int(year) <= end_year):
                                    continue
                                    
                                creators_list = record.get('creators', [])
                                authors = ", ".join([c.get('creator', '') for c in creators_list]) if creators_list else "Bilinmiyor"
                                
                                doi = record.get('doi', '-')
                                
                                open_access_str = str(record.get('openaccess', 'false')).lower()
                                status = "Açık" if open_access_str == 'true' else "Kilitli"
                                
                                abstract = record.get('abstract', 'Özet bulunamadı.')
                                
                                url_links = record.get('url', [])
                                link = url_links[0].get('value', '') if url_links else ""
                                
                                results.append({
                                    "Kaynak": self.name, "Yıl": year, "Başlık": title,
                                    "Yazarlar": authors, "Erişim Durumu": status,
                                    "DOI": doi, "Link": link, "Özet": abstract
                                })
                            except Exception as item_e:
                                self.logger.warning(f"Error parsing springer item: {item_e}")
                                continue
                    elif response.status == 401 or response.status == 403:
                         return {
                            "source": self.name,
                            "status": "error",
                            "message": "Springer API Key geçersiz veya süresi dolmuş. Yetkilendirme hatası.",
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
            self.logger.error(f"Springer Error: {str(e)}")
            return {
                "source": self.name,
                "status": "error",
                "message": f"Beklenmeyen bir hata oluştu: {str(e)}",
                "data": []
            }
