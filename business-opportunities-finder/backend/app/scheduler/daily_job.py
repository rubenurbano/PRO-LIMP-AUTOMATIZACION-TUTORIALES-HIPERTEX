"""
Daily job scheduler and execution logic.
"""
import asyncio
import logging
from datetime import datetime, date
from typing import List, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.database import SessionLocal
from app.models import Source, RawOpportunity, Opportunity
from app.services.scrapers import RedditScraper, HackerNewsScraper, ProductHuntScraper
from app.services.gemini_analyzer import GeminiAnalyzer
from app.services.scorer import Scorer
from app.services.report_generator import ReportGenerator

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


async def run_daily_discovery():
    """
    Main daily discovery job.
    
    This function:
    1. Scrapes data from all sources
    2. Analyzes with Gemini
    3. Scores opportunities
    4. Generates top 10 report
    """
    logger.info("=" * 80)
    logger.info("Starting daily business opportunities discovery")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    db = SessionLocal()
    
    try:
        # Step 1: Scrape data from all sources
        logger.info("Step 1: Scraping data from sources...")
        raw_opportunities = await scrape_all_sources(db)
        logger.info(f"Collected {len(raw_opportunities)} raw opportunities")
        
        if not raw_opportunities:
            logger.warning("No raw opportunities found, skipping analysis")
            return
        
        # Step 2: Analyze and score with Gemini
        logger.info("Step 2: Analyzing opportunities with Gemini...")
        gemini_analyzer = GeminiAnalyzer()
        scorer = Scorer(db)
        
        scored_opportunities = []
        for raw_opp in raw_opportunities[:50]:  # Limit to avoid quota issues
            try:
                analysis = await analyze_opportunity(raw_opp, gemini_analyzer, scorer)
                if analysis:
                    scored_opportunities.append(analysis)
            except Exception as e:
                logger.error(f"Error analyzing opportunity {raw_opp.id}: {str(e)}")
                continue
        
        logger.info(f"Successfully analyzed {len(scored_opportunities)} opportunities")
        
        # Step 3: Deduplicate and rank
        logger.info("Step 3: Deduplicating and ranking...")
        deduplicated = scorer.deduplicate_opportunities(scored_opportunities)
        top_10 = scorer.get_top_n(deduplicated, n=10)
        
        # Step 4: Save opportunities to database
        logger.info("Step 4: Saving opportunities to database...")
        saved_opportunities = save_opportunities_to_db(db, top_10)
        
        # Step 5: Generate report
        logger.info("Step 5: Generating daily report...")
        execution_time = (datetime.now() - start_time).total_seconds() / 60
        metadata = {
            "sources_consulted": len(get_active_scrapers()),
            "total_analyzed": len(raw_opportunities),
            "execution_time_minutes": execution_time
        }
        
        report_gen = ReportGenerator(db)
        report = report_gen.generate_daily_report(saved_opportunities, metadata)
        
        logger.info(f"✅ Daily discovery completed successfully in {execution_time:.2f} minutes")
        logger.info(f"Top opportunity: {saved_opportunities[0].title if saved_opportunities else 'None'}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error in daily discovery: {str(e)}", exc_info=True)
    finally:
        db.close()


async def scrape_all_sources(db) -> List[RawOpportunity]:
    """Scrape data from all active sources."""
    scrapers = get_active_scrapers()
    all_raw_data = []
    
    # Run scrapers concurrently
    tasks = [scraper.scrape() for scraper in scrapers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for scraper, result in zip(scrapers, results):
        if isinstance(result, Exception):
            logger.error(f"Scraper {scraper.source_name} failed: {str(result)}")
            continue
        
        # Get or create source
        source = db.query(Source).filter(Source.name == scraper.source_name).first()
        if not source:
            source = Source(
                name=scraper.source_name,
                type=scraper.source_type,
                url=f"https://{scraper.source_type}.com",
                active=True
            )
            db.add(source)
            db.commit()
        
        # Save raw opportunities
        for item in result:
            normalized = scraper.normalize_data(item)
            
            # Check if already exists
            existing = db.query(RawOpportunity).filter(
                RawOpportunity.source_id == source.id,
                RawOpportunity.external_id == normalized["external_id"]
            ).first()
            
            if not existing:
                raw_opp = RawOpportunity(
                    source_id=source.id,
                    external_id=normalized["external_id"],
                    title=normalized["title"],
                    description=normalized["description"],
                    url=normalized["url"],
                    extra_data=normalized["metadata"],
                    processed=False
                )
                db.add(raw_opp)
                all_raw_data.append(raw_opp)
        
        db.commit()
        source.last_scraped_at = datetime.now()
        db.commit()
    
    return all_raw_data


async def analyze_opportunity(
    raw_opp: RawOpportunity,
    gemini_analyzer: GeminiAnalyzer,
    scorer: Scorer
) -> Dict[str, Any]:
    """Analyze a single opportunity with Gemini and calculate scores."""
    problem_text = f"{raw_opp.title}\n\n{raw_opp.description}"
    
    metadata = {
        "source": raw_opp.source_id,
        "upvotes": raw_opp.extra_data.get("upvotes", 0),
        "comments": raw_opp.extra_data.get("comments", 0),
        "url": raw_opp.url
    }
    
    # Get Gemini analysis
    analysis = await gemini_analyzer.score_opportunity(problem_text, metadata)
    
    # Calculate additional scores
    frequency_score = scorer.calculate_frequency_score(
        analysis.get("sector", ""),
        []  # Keywords would be extracted here
    )
    
    competition_score = scorer.calculate_competition_score(
        analysis.get("sector", ""),
        analysis.get("solution_type", "")
    )
    
    # Combine all scores
    all_scores = {
        **analysis["scores"],
        "frequency": frequency_score,
        "competition": competition_score
    }
    
    total_score = scorer.calculate_total_score(all_scores)
    
    return {
        "raw_opportunity_id": raw_opp.id,
        "title": raw_opp.title[:255],
        "problem_description": problem_text,
        "sector": analysis.get("sector"),
        "solution_type": analysis.get("solution_type"),
        "proposed_app": analysis.get("proposed_app"),
        "ideal_users": analysis.get("ideal_users"),
        "economic_benefit": {},  # Could be extracted from analysis
        "score_breakdown": all_scores,
        "score_total": total_score,
        "tags": analysis.get("tags", [])
    }


def save_opportunities_to_db(db, opportunities: List[Dict[str, Any]]) -> List[Opportunity]:
    """Save analyzed opportunities to database."""
    saved = []
    today = date.today().strftime("%Y%m%d")
    
    for idx, opp_data in enumerate(opportunities, 1):
        public_id = Opportunity.generate_public_id(today, idx)
        
        opportunity = Opportunity(
            public_id=public_id,
            title=opp_data["title"],
            problem_description=opp_data["problem_description"],
            sector=opp_data["sector"],
            solution_type=opp_data["solution_type"],
            proposed_app=opp_data["proposed_app"],
            ideal_users=opp_data["ideal_users"],
            economic_benefit=opp_data["economic_benefit"],
            score_breakdown=opp_data["score_breakdown"],
            score_total=opp_data["score_total"],
            tags=opp_data["tags"],
            status="new"
        )
        
        db.add(opportunity)
        saved.append(opportunity)
    
    db.commit()
    
    # Refresh to get IDs
    for opp in saved:
        db.refresh(opp)
    
    return saved


def get_active_scrapers():
    """Get list of active scraper instances."""
    return [
        RedditScraper(),
        HackerNewsScraper(),
        ProductHuntScraper(),
    ]


def start_scheduler():
    """Start the APScheduler for daily jobs."""
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already started")
        return
    
    scheduler = AsyncIOScheduler()
    
    # Schedule daily job
    scheduler.add_job(
        run_daily_discovery,
        trigger=CronTrigger(
            hour=settings.daily_run_hour,
            minute=settings.daily_run_minute,
            timezone=settings.timezone
        ),
        id='daily_discovery',
        replace_existing=True,
        max_instances=1
    )
    
    scheduler.start()
    logger.info(f"Scheduler started - Daily job will run at {settings.daily_run_hour}:{settings.daily_run_minute:02d} {settings.timezone}")


def stop_scheduler():
    """Stop the scheduler."""
    global scheduler
    
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    # For manual testing
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_daily_discovery())
