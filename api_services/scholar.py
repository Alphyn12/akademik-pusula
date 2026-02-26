import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from utils.scraper_base import BaseScraper
from utils.proxy_manager import ProxyManager
import urllib.parse
import re
import random
import streamlit as st

# Global lock for all Scholar-derived searches to prevent IP ban / CAPTCHA limits
# from concurrent concurrent scraping bursts (like Google + DergiPark + YokTez at once)
_SCHOLAR_LOCK = asyncio.Lock()
# Global state to fast-fail subsequent scraping requests if CAPTCHA is hit
_CAPTCHA_TRIGGERED = False

class ScholarScraper(BaseScraper):
    def __init__(self):
        super().__init__("Google Scholar")
        self.base_url = "https://scholar.google.com/scholar"

    async def fetch(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        global _CAPTCHA_TRIGGERED
        results = []
        try:
            # Check if user has provided a ScraperAPI key
            scraper_api_key = self.get_config("scraper_api", "api_key")

            # Fast-Fail if a previous Scholar request within this run already hit CAPTCHA
            # (Only applies if NOT using a third-party paid/free-tier rotating scraper API)
            if _CAPTCHA_TRIGGERED and not scraper_api_key:
                return {
                    "source": self.name,
                    "status": "error",
                    "message": "Google Scholar araması CAPTCHA engeline takıldı. (ScraperAPI Key ekleyerek bu engeli tamamen aşabilirsiniz).",
                    "data": []
                }
                
            start_year = filters.get('start_year', 1990)
            end_year = filters.get('end_year', 2026)
            languages = filters.get('language', [])
            
            params = {
                "q": query,
                "as_ylo": start_year,
                "as_yhi": end_year,
            }
            
            # Apply language filters if required. 
            if "Türkçe" in languages and "İngilizce" not in languages:
                params["hl"] = "tr"
                params["lr"] = "lang_tr"
            elif "İngilizce" in languages and "Türkçe" not in languages:
                params["hl"] = "en"
                params["lr"] = "lang_en"
            else:
                params["hl"] = "tr"

            headers = ProxyManager.get_random_headers()
            
            # Serialize Scholar requests to prevent instant CAPTCHA triggers
            async with _SCHOLAR_LOCK:
                # Add a natural human-like delay before each request 
                await asyncio.sleep(random.uniform(1.5, 3.5))
                
                # Determine URL based on ScraperAPI presence
                target_url = self.base_url
                req_params = params
                
                if scraper_api_key:
                    # Route through ScraperAPI
                    # Form URL encoding for the target Google Scholar Page
                    target_url_encoded = urllib.parse.urlencode({"url": self.base_url})
                    for k,v in params.items():
                        target_url_encoded += f"&url={k}={v}" # Not perfect encoding but close enough for query
                        
                    url_to_scrape = self.base_url + "?" + urllib.parse.urlencode(params)
                    
                    req_params = {
                        "api_key": scraper_api_key,
                        "url": url_to_scrape,
                        "render": "false",
                        "premium": "true", # Important for Google Scholar routing
                    }
                    target_url = "http://api.scraperapi.com"
                
                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get(target_url, params=req_params, timeout=30 if scraper_api_key else 12) as response:
                        
                        if response.status == 429:
                            if not scraper_api_key: _CAPTCHA_TRIGGERED = True
                            return {
                                "source": self.name,
                                "status": "error",
                                "message": "IP Adresi Google Scholar tarafından engellendi. Scraping için güçlü bir proxy/ScraperAPI girin.",
                                "data": []
                            }
                            
                        response.raise_for_status()
                        html = await response.text()
                        
                        soup = BeautifulSoup(html, "html.parser")
                        
                        # Detect CAPTCHA via form structure
                        if soup.find(id="gs_captcha_ccl") or "Recaptcha" in html or "g-recaptcha" in html:
                            if not scraper_api_key: _CAPTCHA_TRIGGERED = True
                            return {
                                "source": self.name,
                                "status": "error",
                                "message": "Google Scholar CAPTCHA istiyor. Tarama durduruldu. Limitleri aşmak için lütfen .streamlit/secrets.toml içine scraper_api anahtarı ekleyin.",
                                "data": []
                            }

                        # Parse results
                        articles = soup.select(".gs_r.gs_or.gs_scl")
                        
                        for item in articles:
                            try:
                                title_el = item.select_one(".gs_rt a")
                                if not title_el:
                                    title_el = item.select_one(".gs_rt") # Some citations don't have links
                                
                                title = title_el.text.strip() if title_el else "Bilinmiyor"
                                pub_url = title_el['href'] if title_el and title_el.has_attr('href') else ""
                                
                                # Author and Year parsing
                                meta_div = item.select_one(".gs_a")
                                meta_text = meta_div.text if meta_div else ""
                                authors = ""
                                year = "Bilinmiyor"
                                
                                if meta_text:
                                    parts = meta_text.split("-")
                                    if len(parts) > 0:
                                        authors = parts[0].strip()
                                    if len(parts) > 1:
                                        venue_year_part = parts[1].strip()
                                        year_match = re.search(r'\b(19|20)\d{2}\b', venue_year_part)
                                        if year_match:
                                            year = year_match.group(0)

                                abstract_div = item.select_one(".gs_rs")
                                abstract = abstract_div.text.strip() if abstract_div else "Özet bulunamadı."
                                
                                # OAX / Eprint
                                eprint_el = item.select_one(".gs_ggs.gs_fl a")
                                eprint_url = eprint_el['href'] if eprint_el and eprint_el.has_attr('href') else ""
                                
                                status = "Açık" if eprint_url else "Kilitli/Bilinmiyor"
                                
                                results.append({
                                    "Kaynak": self.name,
                                    "Yıl": year,
                                    "Başlık": title,
                                    "Yazarlar": authors,
                                    "Erişim Durumu": status,
                                    "DOI": "-",
                                    "Link": pub_url if pub_url else eprint_url,
                                    "Özet": abstract
                                })
                            except Exception as item_e:
                                self.logger.warning(f"Error parsing specific scholar item: {item_e}")
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
            self.logger.error(f"Scholar Error: {str(e)}")
            return {
                "source": self.name,
                "status": "error",
                "message": f"Beklenmeyen bir hata oluştu: {str(e)}",
                "data": []
            }
