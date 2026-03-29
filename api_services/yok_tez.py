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
            start_year = filters.get('start_year', 1990)
            end_year = filters.get('end_year', 2026)

            # Delegate entirely to the MCP
            result = await self.mcp.fetch(query, search_type=search_type)

            # Rewrite metadata to match YokTez
            if result.get("status") == "success":
                result["source"] = self.name
                filtered_data = []
                for item in result.get("data", []):
                    item["Kaynak"] = self.name
                    year_str = str(item.get("Yıl", ""))
                    if year_str.isdigit() and not (start_year <= int(year_str) <= end_year):
                        continue
                    filtered_data.append(item)
                result["data"] = filtered_data

            elif result.get("status") == "error":
                result["source"] = self.name

            return result
            
        except Exception as e:
            self.logger.error(f"YÖK Tez Error: {str(e)}")
            return {
                "source": self.name,
                "status": "error",
                "message": f"Beklenmeyen bir hata oluştu: {str(e)}",
                "data": []
            }
