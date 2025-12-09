"""
Base scraper class that all scrapers inherit from.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""
    
    def __init__(self, source_name: str, source_type: str, config: Dict[str, Any] = None):
        self.source_name = source_name
        self.source_type = source_type
        self.config = config or {}
        self.rate_limiter = None
        
    @abstractmethod
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch raw data from the source.
        
        Returns:
            List of dictionaries with raw opportunity data.
            Each dict should have: external_id, title, description, url, metadata
        """
        pass
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scrape method that handles rate limiting and error handling.
        
        Returns:
            List of raw opportunities
        """
        try:
            logger.info(f"Starting scrape for {self.source_name} ({self.source_type})")
            start_time = datetime.now()
            
            # Fetch data
            data = await self.fetch_data()
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Scraped {len(data)} items from {self.source_name} in {elapsed:.2f}s")
            
            return data
            
        except Exception as e:
            logger.error(f"Error scraping {self.source_name}: {str(e)}", exc_info=True)
            return []
    
    def normalize_data(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw data into standard format.
        
        Args:
            raw_item: Raw data from source
            
        Returns:
            Normalized dictionary with standard fields
        """
        return {
            "external_id": str(raw_item.get("id", "")),
            "title": raw_item.get("title", ""),
            "description": raw_item.get("description", ""),
            "url": raw_item.get("url", ""),
            "metadata": {
                "upvotes": raw_item.get("upvotes", 0),
                "comments": raw_item.get("comments", 0),
                "created_at": raw_item.get("created_at", None),
                **raw_item.get("extra", {})
            }
        }
