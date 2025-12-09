# Business Opportunities Finder - Setup Guide

## Prerequisites

Before starting, make sure you have:

1. **Docker Desktop** installed (for Windows 11)
   - Download from: https://www.docker.com/products/docker-desktop

2. **API Keys**:
   - **Google Gemini API key** (REQUIRED) ⭐
     - Get it from: https://makersuite.google.com/app/apikey
   - **HackerNews** - No API key needed! Works out of the box ✅
   - **Reddit API credentials** (optional, for additional sources)
     - Create an app at: https://www.reddit.com/prefs/apps
   - **ProductHunt API key** (optional)
   - **Twitter API** (optional)

## Quick Start (5 minutes)

### Step 1: Configure Environment

1. Navigate to the project directory:
   ```powershell
   cd C:\Users\rubenurbano\HIPERTEX\business-opportunities-finder
   ```

2. Copy the environment template:
   ```powershell
   Copy-Item .env.example .env
   ```

3. Edit `.env` file with your API keys:
   ```powershell
   notepad .env
   ```

   **Minimum required configuration:**
   ```env
   # REQUIRED: Get from https://makersuite.google.com/app/apikey
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # HackerNews works automatically - no API key needed!
   
   # Optional: Reddit (for additional data sources)
   # REDDIT_CLIENT_ID=your_client_id
   # REDDIT_CLIENT_SECRET=your_client_secret
   ```

### Step 2: Start the Application

```powershell
docker-compose up -d
```

This will:
- Start PostgreSQL database
- Build and start the FastAPI backend
- Automatically run database migrations

### Step 3: Access the Dashboard

Open your browser and go to:
```
http://localhost:8000
```

You should see the Business Opportunities Finder dashboard!

### Step 4: Run First Discovery (Manual)

To test the system manually before waiting for the scheduled run:

```powershell
docker-compose exec backend python -m app.scheduler.daily_job
```

This will:
1. Scrape HackerNews (and Reddit if configured)
2. Analyze problems with Gemini AI
3. Generate the top 10 opportunities
4. Create a daily report

The process takes approximately 5-15 minutes depending on API quotas.

## How It Works

### Automatic Daily Execution

The system automatically runs every day at **7:00 AM** (configurable in `.env`):

1. **Scrapes** HackerNews (+ Reddit if configured)
2. **Analyzes** each problem with Gemini AI
3. **Scores** based on 6 criteria (pain, frequency, willingness to pay, competition, technical feasibility, AI synergy)
4. **Ranks** and selects top 10
5. **Generates** JSON and HTML reports
6. **Stores** in database

### Using the Dashboard

**Filters:**
- **Sector**: Filter by industry (e.g., Healthcare, E-commerce)
- **Status**: Filter by your workflow (New, Selected, In Progress, Discarded)
- **Min Score**: Show only high-scoring opportunities (7+, 8+, 9+)
- **Search**: Full-text search in titles and descriptions

**Card Actions:**
- Click any card to view details (coming soon: full modal)
- Update status to track your progress
- Add notes for each opportunity

## Troubleshooting

### "Connection refused" error

Make sure Docker Desktop is running:
```powershell
docker ps
```

You should see two containers: `oppfinder_db` and `oppfinder_backend`.

### "API key invalid" error

Check your `.env` file has valid API keys. Restart the container after updating:
```powershell
docker-compose restart backend
```

### No opportunities showing

1. Check if the daily job has run:
   ```powershell
   docker-compose logs backend | Select-String "daily discovery"
   ```

2. Run manually (see Step 4 above)

3. Check API quotas (especially Reddit and Gemini)

### Database errors

Reset the database:
```powershell
docker-compose down -v
docker-compose up -d
```

**Warning**: This deletes all stored opportunities!

## Configuration

### Change Daily Run Time

Edit `.env`:
```env
DAILY_RUN_HOUR=7
DAILY_RUN_MINUTE=0
TIMEZONE=Europe/Madrid
```

Restart backend:
```powershell
docker-compose restart backend
```

### Adjust Scoring Weights

Edit `.env` to change how opportunities are scored:
```env
SCORE_WEIGHT_PAIN=0.30
SCORE_WEIGHT_FREQUENCY=0.20
SCORE_WEIGHT_WILLINGNESS_TO_PAY=0.20
SCORE_WEIGHT_LOW_COMPETITION=0.15
SCORE_WEIGHT_TECHNICAL_FEASIBILITY=0.10
SCORE_WEIGHT_AI_SYNERGY=0.05
```

### Add More Sources

To enable ProductHunt scraping, add your API key to `.env`:
```env
PRODUCTHUNT_API_KEY=your_key_here
```

Then uncomment ProductHuntScraper in `backend/app/scheduler/daily_job.py`:
```python
def get_active_scrapers():
    return [
        RedditScraper(),
        HackerNewsScraper(),
        ProductHuntScraper(),  # Uncomment this line
    ]
```

## API Documentation

Access the interactive API docs:
```
http://localhost:8000/docs
```

### Key Endpoints

- `GET /api/opportunities` - List opportunities with filters
- `GET /api/opportunities/{id}` - Get single opportunity
- `PATCH /api/opportunities/{id}` - Update status/notes
- `GET /api/analytics` - Get statistics
- `GET /api/reports/latest` - Get latest daily report

## Viewing Reports

Reports are saved in the container at `/app/reports/`:
```powershell
docker-compose exec backend ls -la /app/reports
```

Copy a report to your local machine:
```powershell
docker cp oppfinder_backend:/app/reports/report_2025-12-01.json ./
```

## Development

### View Logs

```powershell
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Access Database

```powershell
docker-compose exec db psql -U oppfinder -d opportunities_db
```

Useful queries:
```sql
-- Count opportunities
SELECT COUNT(*) FROM opportunities;

-- View top 5 by score
SELECT public_id, title, score_total FROM opportunities ORDER BY score_total DESC LIMIT 5;

-- View sources
SELECT * FROM sources;
```

### Rebuild After Code Changes

```powershell
docker-compose down
docker-compose build
docker-compose up -d
```

## Next Steps

1. **Configure Email Notifications** (optional)
   - Add SMTP settings to `.env`
   - Daily reports will be emailed automatically

2. **Customize Prompts**
   - Edit `backend/app/services/gemini_analyzer.py`
   - Adjust the scoring prompt for your specific needs

3. **Add Custom Sources**
   - Create a new scraper in `backend/app/services/scrapers/`
   - Follow the pattern from `reddit_scraper.py`

4. **Export Data**
   - Use API endpoints to export opportunities
   - Download JSON reports from `/app/reports`

## Support

For issues or questions:
1. Check the logs: `docker-compose logs backend`
2. Review this guide
3. Check the API docs: http://localhost:8000/docs

---

**Enjoy discovering your next SaaS idea! 🚀**
