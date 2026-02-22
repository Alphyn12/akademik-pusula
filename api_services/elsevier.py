import asyncio
from typing import List, Dict, Any
import streamlit as st
from utils.scraper_base import BaseScraper

class ElsevierScraper(BaseScraper):
    def __init__(self):
        super().__init__("Elsevier (ScienceDirect/Scopus)")
        
    def _fetch_sync(self, query: str, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        results = []
        try:
            if "elsevier" in st.secrets and "api_key" in st.secrets["elsevier"]:
                api_key = st.secrets["elsevier"]["api_key"]
            else:
                return results
                
            try:
                from elsapy.elsclient import ElsClient
                from elsapy.elssearch import ElsSearch
            except ImportError:
                self.logger.error("elsapy not installed")
                return results
                
            client = ElsClient(api_key)
            doc_srch = ElsSearch(query, 'scopus')
            try:
                doc_srch.execute(client, get_all=False)
            except Exception as e:
                self.logger.warning(f"ElsSearch execute failed: {str(e)}")
                return results

            if hasattr(doc_srch, 'results') and doc_srch.results:
                for item in doc_srch.results:
                    try:
                        if isinstance(item, dict) and 'error' in item:
                            continue
                            
                        title = item.get('dc:title', 'Bilinmiyor')
                        
                        year = "Bilinmiyor"
                        cover_date = item.get('prism:coverDate') 
                        if cover_date and len(cover_date)>=4:
                            year = cover_date[:4]
                            
                        if str(year).isdigit() and not (start_year <= int(year) <= end_year):
                            continue
                            
                        authors = item.get('dc:creator', 'Bilinmiyor')
                                
                        doi = item.get('prism:doi', '-')
                        openaccess_flag = str(item.get('openaccess', '0'))
                        status = "Açık" if openaccess_flag.lower() in ['1', 'true'] else "Kilitli"
                        
                        abstract = item.get('dc:description', 'Özet bulunamadı.')
                        
                        link = "-"
                        if item.get('link'):
                            for l in item['link']:
                                if l.get('@ref') == 'scopus':
                                    link = l.get('@href', '-')
                                    break
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
        except Exception as e:
            self.logger.error(f"Elsevier Error: {str(e)}")
        return results

    async def fetch(self, query: str, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self._fetch_sync, query, start_year, end_year)
