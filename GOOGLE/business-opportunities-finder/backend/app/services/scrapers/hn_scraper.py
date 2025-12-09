"""
HackerNews scraper using the official Firebase API.
"""
from typing import List, Dict, Any
import httpx
import asyncio
from datetime import datetime, timedelta
import logging

from app.services.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class HackerNewsScraper(BaseScraper):
    """Scraper for HackerNews stories."""
    
    def __init__(self):
        super().__init__(
            source_name="HackerNews",
            source_type="hackernews",
            config={
                "api_base": "https://hacker-news.firebaseio.com/v0",
                "limit": 100
            }
        )
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch 'Ask HN' posts and top stories."""
        opportunities = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Get Ask HN stories
                ask_stories = await self._fetch_ask_stories(client)
                opportunities.extend(ask_stories)
                
                # Get top stories (filter for relevant ones)
                top_stories = await self._fetch_top_stories(client)
                opportunities.extend(top_stories)
                
            except Exception as e:
                logger.error(f"Error fetching from HackerNews: {str(e)}", exc_info=True)
        
        return opportunities
    
    async def _fetch_ask_stories(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Fetch Ask HN stories."""
        try:
            # Get Ask HN story IDs
            response = await client.get(f"{self.config['api_base']}/askstories.json")
            response.raise_for_status()
            story_ids = response.json()[:self.config['limit']]
            
            # Fetch story details concurrently
            stories = []
            for story_id in story_ids[:20]:  # Limit to avoid too many requests
                story = await self._fetch_story_details(client, story_id)
                if story and self._is_relevant_story(story):
                    stories.append(story)
                await asyncio.sleep(0.1)  # Small delay to be respectful
            
            logger.info(f"Fetched {len(stories)} relevant Ask HN stories")
            return stories
            
        except Exception as e:
            logger.error(f"Error fetching Ask HN stories: {str(e)}")
            return []
    
    async def _fetch_top_stories(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Fetch top stories (with relevance filtering)."""
        try:
            response = await client.get(f"{self.config['api_base']}/topstories.json")
            response.raise_for_status()
            story_ids = response.json()[:50]
            
            stories = []
            for story_id in story_ids[:20]:
                story = await self._fetch_story_details(client, story_id)
                if story and self._is_relevant_story(story):
                    stories.append(story)
                await asyncio.sleep(0.1)
            
            logger.info(f"Fetched {len(stories)} relevant top stories from HN")
            return stories
            
        except Exception as e:
            logger.error(f"Error fetching top stories: {str(e)}")
            return []
    
    async def _fetch_story_details(self, client: httpx.AsyncClient, story_id: int) -> Dict[str, Any]:
        """Fetch details for a single story."""
        try:
            response = await client.get(f"{self.config['api_base']}/item/{story_id}.json")
            response.raise_for_status()
            item = response.json()
            
            if not item or item.get("type") != "story":
                return None
            
            return {
                "id": str(item.get("id")),
                "title": item.get("title", ""),
                "description": item.get("text", ""),
                "url": item.get("url", f"https://news.ycombinator.com/item?id={item.get('id')}"),
                "upvotes": item.get("score", 0),
                "comments": item.get("descendants", 0),
                "created_at": datetime.fromtimestamp(item.get("time", 0)).isoformat() if item.get("time") else None,
                "extra": {
                    "by": item.get("by", ""),
                    "hn_url": f"https://news.ycombinator.com/item?id={item.get('id')}"
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching story {story_id}: {str(e)}")
            return None
    
    def _is_relevant_story(self, story: Dict[str, Any]) -> bool:
        """Check if story is relevant for business opportunities."""
        if not story or story.get("upvotes", 0) < 10:
            return False
        
        title = story.get("title", "").lower()
        description = story.get("description", "").lower()
        text = title + " " + description
        
        # Keywords for Ask HN posts about problems
        relevant_keywords = [
            "ask hn", "problem", "issue", "frustrat", "need",
            "looking for", "how to", "help", "recommend",
            "better way", "automate", "tool for", "solution",
            "struggling", "inefficient", "manual"
        ]
        
        return any(keyword in text for keyword in relevant_keywords)
