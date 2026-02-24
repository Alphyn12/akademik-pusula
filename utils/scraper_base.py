from abc import ABC, abstractmethod
from typing import List, Dict, Any
from utils.logger import logger

class BaseScraper(ABC):
    """
    Abstract base class for all Akademik Pusula API scrapers.
    Forces implementation of the asynchronous `fetch` method.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logger
        
    @abstractmethod
    async def fetch(self, query: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronously fetches academic data from the target source.
        
        Args:
            query (str): The search term.
            filters (Dict[str, Any]): Dictionary containing filters like start_year, end_year, language, max_results.
            
        Returns:
            Dict[str, Any]: Standardized response dictionary containing status, message, and data.
        """
        pass
