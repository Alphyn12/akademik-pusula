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
    async def fetch(self, query: str, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        """
        Asynchronously fetches academic data from the target source.
        
        Args:
            query (str): The search term.
            start_year (int): Minimum publication year.
            end_year (int): Maximum publication year.
            
        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing article metadata.
        """
        pass
