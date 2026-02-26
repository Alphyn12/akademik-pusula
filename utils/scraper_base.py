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
        
    def get_config(self, section: str, key: str, default: Any = None) -> Any:
        """
        Retrieves a configuration value from Streamlit secrets or environment variables.
        Falls back to environment variables if st.secrets is not available or the key is missing.
        
        Args:
            section (str): The section name (e.g., 'springer').
            key (str): The key name (e.g., 'api_key').
            default (Any): Optional default value if not found.
            
        Returns:
            Any: The configuration value or default.
        """
        import os
        import streamlit as st
        
        # 1. Try Streamlit Secrets (e.g., [section] key=val)
        try:
            # Check if secrets file exists/is loadable by streamlit before access
            if section and section in st.secrets:
                if key in st.secrets[section]:
                    return st.secrets[section][key]
            elif key in st.secrets:
                return st.secrets[key]
        except Exception:
            # st.secrets might raise StreamlitSecretNotFoundError if the file is missing
            pass
            
        # 2. Try Environment Variables (e.g., SECTION_KEY=val or KEY=val)
        env_key = f"{section.upper()}_{key.upper()}" if section else key.upper()
        return os.environ.get(env_key, os.environ.get(key.upper(), default))

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
