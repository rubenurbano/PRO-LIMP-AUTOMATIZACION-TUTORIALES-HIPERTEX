"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging

from app.config import settings, get_cors_origins
from app.database import init_db
from app.api import opportunities, reports, analytics, sources
from app.scheduler.daily_job import start_scheduler

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Business Opportunities Finder...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Start scheduler
    start_scheduler()
    logger.info("Scheduler started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Business Opportunities Finder",
    description="Automated system to discover and analyze daily business opportunities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(opportunities.router, prefix="/api", tags=["opportunities"])
app.include_router(reports.router, prefix="/api", tags=["reports"])
app.include_router(analytics.router, prefix="/api", tags=["analytics"])
app.include_router(sources.router, prefix="/api", tags=["sources"])

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def root():
    """Serve the main frontend page."""
    return FileResponse("frontend/index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "debug": settings.debug
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
