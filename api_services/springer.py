import aiohttp
import urllib.parse
from typing import List, Dict, Any
import streamlit as st
from utils.scraper_base import BaseScraper

class SpringerScraper(BaseScraper):
    def __init__(self):
        super().__init__("Springer")
        
    async def fetch(self, query: str, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        results = []
        try:
            if "springer" in st.secrets and "api_key" in st.secrets["springer"]:
                api_key = st.secrets["springer"]["api_key"]
            else:
                return results
                
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
        except asyncio.TimeoutError:
            self.logger.warning("Springer request timed out.")
        except Exception as e:
            self.logger.error(f"Springer Error: {str(e)}")
            
        return results
