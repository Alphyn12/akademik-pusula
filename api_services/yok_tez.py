import asyncio
from typing import List, Dict, Any
from utils.scraper_base import BaseScraper
from utils.mcp_manager import YokTezMCPManager

class YokTezScraper(BaseScraper):
    def __init__(self):
        super().__init__("YÖK Tez / TR Üniversiteleri")
        self.mcp = YokTezMCPManager()
        
    async def fetch(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            search_type = filters.get('search_type', 'Kavram/Kelime Arama')
            
            # Delegate entirely to the MCP
            result = await self.mcp.fetch(query, search_type=search_type)
            
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
