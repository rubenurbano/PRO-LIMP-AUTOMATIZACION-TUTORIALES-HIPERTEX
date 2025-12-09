"""
ProductHunt scraper for trending products and discussions.
"""
from typing import List, Dict, Any
import httpx
import logging
from datetime import datetime

from app.services.scrapers.base_scraper import BaseScraper
from app.config import settings

logger = logging.getLogger(__name__)


class ProductHuntScraper(BaseScraper):
    """Scraper for ProductHunt."""
    
    def __init__(self):
        super().__init__(
            source_name="ProductHunt",
            source_type="producthunt",
            config={
                "api_base": "https://api.producthunt.com/v2/api/graphql",
                "limit": 20
            }
        )
        self.api_key = settings.producthunt_api_key
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch trending products and comments about unmet needs."""
        if not self.api_key:
            logger.warning("ProductHunt API key not configured, skipping")
            return []
        
        opportunities = []
        
        # GraphQL query for today's posts
        query = """
        {
          posts(first: 20, order: VOTES) {
            edges {
              node {
                id
                name
                tagline
                description
                url
                votesCount
                commentsCount
                createdAt
                topics {
                  edges {
                    node {
                      name
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.config["api_base"],
                    json={"query": query},
                    headers=headers
                )
                
                if response.status_code != 200:
                    logger.error(f"ProductHunt API error: {response.status_code} - {response.text}")
                    return []
                
                data = response.json()
                if "errors" in data:
                    logger.error(f"ProductHunt GraphQL errors: {data['errors']}")
                    return []
                
                posts = data.get("data", {}).get("posts", {}).get("edges", [])
                
                for edge in posts:
                    post = edge.get("node", {})
                    
                    # Extract topics
                    topics = [t["node"]["name"] for t in post.get("topics", {}).get("edges", [])]
                    
                    opportunities.append({
                        "id": post.get("id"),
                        "title": f"PH: {post.get('name')} - {post.get('tagline')}",
                        "description": post.get("description") or post.get("tagline"),
                        "url": post.get("url"),
                        "upvotes": post.get("votesCount"),
                        "comments": post.get("commentsCount"),
                        "created_at": post.get("createdAt"),
                        "extra": {
                            "topics": topics,
                            "source_type": "product_launch"
                        }
                    })
                
                logger.info(f"Fetched {len(opportunities)} posts from ProductHunt")
                
            except Exception as e:
                logger.error(f"Error fetching from ProductHunt: {str(e)}", exc_info=True)
        
        return opportunities
