import asyncio
from typing import List, Dict, Any
from utils.scraper_base import BaseScraper
from api_services.openalex import OpenAlexScraper

class YokTezScraper(BaseScraper):
    def __init__(self):
        super().__init__("YÖK Tez / TR Üniversiteleri")
        self.oa_scraper = OpenAlexScraper()
        
    async def fetch(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            yok_query = f"{query} thesis turkey university"
            
            # Delegate entirely to the async OpenAlexScraper
            result = await self.oa_scraper.fetch(yok_query, filters)
            
            # Rewrite metadata to match YokTez
            if result.get("status") == "success":
                result["source"] = self.name
                for item in result.get("data", []):
                    item["Kaynak"] = self.name
                    
            elif result.get("status") == "error":
                result["source"] = self.name # Make sure error source is correct
                
            return result
            
        except Exception as e:
            self.logger.error(f"YÖK Tez Error: {str(e)}")
            return {
                "source": self.name,
                "status": "error",
                "message": f"Beklenmeyen bir hata oluştu: {str(e)}",
                "data": []
            }
