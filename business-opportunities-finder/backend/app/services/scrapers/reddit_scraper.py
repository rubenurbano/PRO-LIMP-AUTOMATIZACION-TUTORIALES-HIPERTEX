"""
Reddit scraper using PRAW (Python Reddit API Wrapper).
"""
from typing import List, Dict, Any
import praw
import asyncio
from datetime import datetime, timedelta
import logging

from app.services.scrapers.base_scraper import BaseScraper
from app.config import settings

logger = logging.getLogger(__name__)


class RedditScraper(BaseScraper):
    """Scraper for Reddit posts."""
    
    def __init__(self):
        super().__init__(
            source_name="Reddit",
            source_type="reddit",
            config={
                "subreddits": ["Entrepreneur", "smallbusiness", "SaaS", "nocode", "Automation"],
                "time_filter": "day",
                "limit": 100
            }
        )
        
        # Initialize Reddit client
        if settings.reddit_client_id and settings.reddit_client_secret:
            self.reddit = praw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent=settings.reddit_user_agent
            )
        else:
            self.reddit = None
            logger.warning("Reddit API credentials not configured")
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch posts from configured subreddits."""
        if not self.reddit:
            logger.warning("Reddit client not initialized, skipping")
            return []
        
        opportunities = []
        
        try:
            # Run in thread pool since PRAW is synchronous
            loop = asyncio.get_event_loop()
            opportunities = await loop.run_in_executor(None, self._fetch_sync)
            
        except Exception as e:
            logger.error(f"Error fetching from Reddit: {str(e)}", exc_info=True)
        
        return opportunities
    
    def _fetch_sync(self) -> List[Dict[str, Any]]:
        """Synchronous fetch method for PRAW."""
        opportunities = []
        
        for subreddit_name in self.config["subreddits"]:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Get top posts from last day
                for submission in subreddit.top(
                    time_filter=self.config["time_filter"],
                    limit=self.config["limit"]
                ):
                    # Filter for problem/pain point posts
                    if self._is_relevant_post(submission):
                        opportunities.append({
                            "id": submission.id,
                            "title": submission.title,
                            "description": submission.selftext,
                            "url": f"https://reddit.com{submission.permalink}",
                            "upvotes": submission.score,
                            "comments": submission.num_comments,
                            "created_at": datetime.fromtimestamp(submission.created_utc).isoformat(),
                            "extra": {
                                "subreddit": subreddit_name,
                                "author": str(submission.author) if submission.author else "[deleted]"
                            }
                        })
                
                logger.info(f"Fetched {len([o for o in opportunities if o['extra']['subreddit'] == subreddit_name])} posts from r/{subreddit_name}")
                
            except Exception as e:
                logger.error(f"Error fetching from r/{subreddit_name}: {str(e)}")
                continue
        
        return opportunities
    
    def _is_relevant_post(self, submission) -> bool:
        """
        Determine if a post is relevant (contains problem/pain point).
        
        Basic heuristics:
        - Title or text contains keywords like "problem", "frustrating", "need", "wish", "how to"
        - Has reasonable engagement (score > 5)
        - Not too old
        """
        if submission.score < 5:
            return False
        
        # Check age (not older than 2 days)
        created = datetime.fromtimestamp(submission.created_utc)
        if datetime.now() - created > timedelta(days=2):
            return False
        
        # Keyword matching (simple approach)
        text = (submission.title + " " + submission.selftext).lower()
        
        problem_keywords = [
            "problem", "issue", "frustrat", "annoying", "pain",
            "need", "wish", "looking for", "how to", "help",
            "expensive", "inefficient", "manual", "waste time",
            "automate", "difficult", "hard to", "struggle"
        ]
        
        return any(keyword in text for keyword in problem_keywords)
