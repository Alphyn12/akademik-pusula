import asyncio
from typing import List, Dict, Any
from utils.scraper_base import BaseScraper
from api_services.openalex import OpenAlexScraper

class DergiParkScraper(BaseScraper):
    def __init__(self):
        super().__init__("DergiPark (Kapsamlı)")
        self.oa_scraper = OpenAlexScraper()
        
    async def fetch(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            dp_query = f"{query} dergipark"
            
            # Delegate entirely to the async OpenAlexScraper
            result = await self.oa_scraper.fetch(dp_query, filters)
            
            # Rewrite metadata to match DergiPark
            if result.get("status") == "success":
                result["source"] = self.name
                for item in result.get("data", []):
                    item["Kaynak"] = self.name
                    
            elif result.get("status") == "error":
                result["source"] = self.name # Make sure error source is correct
                
            return result
            
        except Exception as e:
            self.logger.error(f"DergiPark Error: {str(e)}")
            return {
                "source": self.name,
                "status": "error",
                "message": f"Beklenmeyen bir hata oluştu: {str(e)}",
                "data": []
            }
