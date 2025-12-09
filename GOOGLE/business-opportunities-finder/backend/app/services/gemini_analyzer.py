"""
Gemini AI Analyzer for scoring and analyzing business opportunities.
"""
from typing import Dict, Any, List
import json
import logging
import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """Analyzer using Google Gemini for opportunity scoring and analysis."""
    
    def __init__(self):
        """Initialize Gemini client."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            generation_config={
                "temperature": settings.gemini_temperature,
                "response_mime_type": "application/json"
            }
        )
    
    async def score_opportunity(
        self,
        problem_text: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score a business opportunity using Gemini.
        
        Args:
            problem_text: The problem description from the source
            metadata: Additional context (source, engagement, etc.)
            
        Returns:
            Dictionary with scores, analysis, and proposed app details
        """
        try:
            prompt = self._build_scoring_prompt(problem_text, metadata)
            
            # Generate response
            response = await self.model.generate_content_async(prompt)
            
            # Parse JSON response
            result = json.loads(response.text)
            
            logger.info(f"Scored opportunity with total estimated score: {self._calculate_total_score(result['scores']):.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error scoring opportunity with Gemini: {str(e)}", exc_info=True)
            return self._get_default_score()
    
    def _build_scoring_prompt(self, problem_text: str, metadata: Dict[str, Any]) -> str:
        """Build the prompt for Gemini to score an opportunity."""
        return f"""
You are a business opportunity analyst for SaaS and automation products.

**Task:** Analyze the following business problem and score it across multiple dimensions.

**Problem Description:**
{problem_text}

**Source Context:**
- Platform: {metadata.get('source', 'Unknown')}
- Engagement: {metadata.get('upvotes', 0)} upvotes, {metadata.get('comments', 0)} comments
- URL: {metadata.get('url', 'N/A')}

**Scoring Criteria (0-10 for each):**

1. **Pain & Urgency** (0-10)
   - 10: Critical problem with direct economic impact, immediate need
   - 7-9: Significant frustration, clear pain points
   - 4-6: Noticeable inconvenience but not blocking
   - 1-3: "Nice to have" without urgency
   - 0: No real pain detected
   
   Look for: urgency words, cost quantification, emotional tone

2. **Willingness to Pay** (0-10)
   - 10: Clear budget mentioned, high-value sector (fintech, healthcare, legal)
   - 7-9: B2B sector with known purchasing power
   - 4-6: Mention of budget or willingness to pay
   - 1-3: Low-budget sector
   - 0: Non-monetizable segment
   
   Consider: industry sector, company size mentions, ROI discussions

3. **Technical Feasibility** (0-10)
   - 10: MVP possible in 1-2 weeks with existing APIs and tools
   - 7-9: MVP in 1 month with standard stack
   - 4-6: Requires learning 1-2 new technologies
   - 1-3: Requires specialized expertise
   - 0: Not feasible for solo developer
   
   Consider: availability of APIs, data model complexity, infrastructure needs

4. **AI/Automation Synergy** (0-10)
   - 10: Perfect fit for AI/automation (text processing, data analysis, prediction)
   - 7-9: Core features can be automated with AI
   - 4-6: AI can enhance the experience
   - 1-3: Mostly manual solution
   - 0: Not applicable for AI
   
   Consider: nature of the task, data availability, automation potential

**Additional Analysis:**

5. **Sector Identification:** What industry/niche is this problem in? (e.g., "Healthcare - Dental Clinics", "E-commerce", "Legal Services")

6. **Solution Type:** What type of solution would work best? Choose one: "SaaS Web App", "Mobile App", "Automation Workflow", "AI Agent", "API Service", "Browser Extension"

7. **Proposed App:**
   - Suggested name (creative, professional, related to the problem)
   - Brief description (2-3 sentences explaining the solution)
   - 3-5 key features
   - Pricing model suggestion (e.g., "$49-199/month based on usage")
   - MVP timeline estimate (e.g., "3-4 weeks")

8. **Ideal Users:**
   - Who would pay for this? (specific user profile)
   - Estimated market size (if inferable, otherwise "Unknown")
   - Buying capacity: "Low", "Medium", or "High"

**Output Format (JSON):**

{{
  "scores": {{
    "pain": <0-10 as number>,
    "willingness_to_pay": <0-10 as number>,
    "technical_feasibility": <0-10 as number>,
    "ai_synergy": <0-10 as number>
  }},
  "justifications": {{
    "pain": "<1-2 sentence explanation>",
    "willingness_to_pay": "<1-2 sentence explanation>",
    "technical_feasibility": "<1-2 sentence explanation>",
    "ai_synergy": "<1-2 sentence explanation>"
  }},
  "sector": "<identified sector>",
  "solution_type": "<type of solution>",
  "proposed_app": {{
    "name": "<suggested app name>",
    "description": "<2-3 sentence description>",
    "key_features": [
      "<feature 1>",
      "<feature 2>",
      "<feature 3>"
    ],
    "pricing_model": "<pricing suggestion with range>",
    "mvp_estimate": "<time estimate>"
  }},
  "ideal_users": {{
    "profile": "<user profile description>",
    "market_size": "<estimated size or 'Unknown'>",
    "buying_capacity": "<Low|Medium|High>"
  }},
  "tags": ["<tag1>", "<tag2>", "<tag3>"]
}}

Be analytical, specific, and justify your scores based on evidence from the problem description.
Return ONLY valid JSON, no additional text.
"""
    
    def _calculate_total_score(self, scores: Dict[str, float]) -> float:
        """Calculate estimated total score (frequency and competition will be added later)."""
        weights = {
            "pain": 0.30,
            "willingness_to_pay": 0.20,
            "technical_feasibility": 0.10,
            "ai_synergy": 0.05
        }
        
        total = sum(scores.get(key, 0) * weight for key, weight in weights.items())
        return total
    
    def _get_default_score(self) -> Dict[str, Any]:
        """Return default scores when Gemini fails."""
        return {
            "scores": {
                "pain": 5.0,
                "willingness_to_pay": 5.0,
                "technical_feasibility": 5.0,
                "ai_synergy": 5.0
            },
            "justifications": {
                "pain": "Unable to analyze",
                "willingness_to_pay": "Unable to analyze",
                "technical_feasibility": "Unable to analyze",
                "ai_synergy": "Unable to analyze"
            },
            "sector": "Unknown",
            "solution_type": "Unknown",
            "proposed_app": {
                "name": "Unknown",
                "description": "Analysis failed",
                "key_features": [],
                "pricing_model": "Unknown",
                "mvp_estimate": "Unknown"
            },
            "ideal_users": {
                "profile": "Unknown",
                "market_size": "Unknown",
                "buying_capacity": "Medium"
            },
            "tags": []
        }
    
    async def cluster_similar_problems(self, problems: List[str]) -> List[List[int]]:
        """
        Group similar problems using embeddings.
        
        Args:
            problems: List of problem descriptions
            
        Returns:
            List of clusters (each cluster is a list of indices)
        """
        # For MVP, we'll use simple text similarity
        # In production, you'd use embeddings and clustering algorithms
        logger.info(f"Clustering {len(problems)} problems (simplified implementation)")
        
        # For now, return each problem in its own cluster
        # TODO: Implement proper clustering with embeddings
        return [[i] for i in range(len(problems))]
