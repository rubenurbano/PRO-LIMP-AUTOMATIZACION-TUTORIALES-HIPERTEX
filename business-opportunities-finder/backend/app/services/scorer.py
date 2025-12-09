"""
Scoring engine for calculating opportunity scores.
"""
from typing import Dict, Any, List
import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.config import get_scoring_weights
from app.models import RawOpportunity

logger = logging.getLogger(__name__)


class Scorer:
    """Scoring engine for business opportunities."""
    
    def __init__(self, db: Session):
        self.db = db
        self.weights = get_scoring_weights()
    
    def calculate_frequency_score(self, sector: str, problem_keywords: List[str]) -> float:
        """
        Calculate frequency score based on how often similar problems appear.
        
        Args:
            sector: Identified sector
            problem_keywords: Key terms from the problem
            
        Returns:
            Frequency score (0-10)
        """
        # Count similar problems in last 7 days
        one_week_ago = datetime.now() - timedelta(days=7)
        
        # Simple approach: Count raw opportunities with similar keywords
        # In production, you'd use embeddings for better similarity matching
        count = self.db.query(RawOpportunity).filter(
            RawOpportunity.detected_at >= one_week_ago
        ).count()
        
        # Map count to score (simplified)
        # 50+ mentions = 10, 20-49 = 8, 10-19 = 6, 3-9 = 4, 1-2 = 2
        if count >= 50:
            return 10.0
        elif count >= 20:
            return 8.5
        elif count >= 10:
            return 6.5
        elif count >= 3:
            return 4.5
        elif count >= 1:
            return 2.5
        else:
            return 1.0
    
    def calculate_competition_score(self, sector: str, solution_type: str) -> float:
        """
        Calculate competition score (inverted - lower competition = higher score).
        
        Args:
            sector: Identified sector
            solution_type: Type of solution
            
        Returns:
            Competition score (0-10, where 10 = low competition)
        """
        # For MVP, use heuristics based on sector
        # In production, you'd search for existing solutions
        
        low_competition_sectors = [
            "construction", "manufacturing", "agriculture",
            "government", "education", "non-profit"
        ]
        
        high_competition_sectors = [
            "e-commerce", "marketing", "crm", "project management"
        ]
        
        sector_lower = sector.lower()
        
        if any(kw in sector_lower for kw in low_competition_sectors):
            return 8.5
        elif any(kw in sector_lower for kw in high_competition_sectors):
            return 4.0
        else:
            return 6.5  # Default medium competition
    
    def calculate_total_score(self, gemini_scores: Dict[str, float]) -> float:
        """
        Calculate total weighted score.
        
        Args:
            gemini_scores: Dictionary with all dimension scores including frequency and competition
            
        Returns:
            Total score (0-10)
        """
        total = (
            self.weights["pain"] * gemini_scores.get("pain", 0) +
            self.weights["frequency"] * gemini_scores.get("frequency", 0) +
            self.weights["willingness_to_pay"] * gemini_scores.get("willingness_to_pay", 0) +
            self.weights["low_competition"] * gemini_scores.get("competition", 0) +
            self.weights["technical_feasibility"] * gemini_scores.get("technical_feasibility", 0) +
            self.weights["ai_synergy"] * gemini_scores.get("ai_synergy", 0)
        )
        
        return round(total, 2)
    
    def rank_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank opportunities by total score.
        
        Args:
            opportunities: List of opportunity dictionaries with scores
            
        Returns:
            Sorted list of opportunities (highest score first)
        """
        return sorted(
            opportunities,
            key=lambda opp: opp.get("score_total", 0),
            reverse=True
        )
    
    def get_top_n(self, opportunities: List[Dict[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top N opportunities.
        
        Args:
            opportunities: List of opportunities
            n: Number of top opportunities to return
            
        Returns:
            Top N opportunities
        """
        ranked = self.rank_opportunities(opportunities)
        return ranked[:n]
    
    def deduplicate_opportunities(
        self,
        opportunities: List[Dict[str, Any]],
        similarity_threshold: float = 0.85
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate opportunities based on similarity.
        
        Args:
            opportunities: List of opportunities
            similarity_threshold: Threshold for considering two opportunities as duplicates
            
        Returns:
            Deduplicated list of opportunities
        """
        # For MVP, use simple title + sector matching
        # In production, use embeddings for better deduplication
        
        seen = set()
        deduplicated = []
        
        for opp in opportunities:
            key = (opp.get("sector", "").lower(), opp.get("title", "").lower()[:50])
            
            if key not in seen:
                seen.add(key)
                deduplicated.append(opp)
            else:
                logger.debug(f"Skipping duplicate: {opp.get('title', '')[:50]}")
        
        return deduplicated
