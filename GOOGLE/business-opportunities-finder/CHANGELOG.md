# Changelog

All notable changes to the Business Opportunities Finder project will be documented in this file.

## [1.0.0] - 2025-12-01

### 🎉 Initial Release

#### Added

**Backend**
- FastAPI application with async support
- PostgreSQL database with SQLAlchemy ORM
- Complete data models (Source, Opportunity, RawOpportunity, DailyReport, ScoringConfig)
- Reddit scraper using PRAW
- HackerNews scraper using Firebase API
- ProductHunt scraper (skeleton, requires API key)
- Google Gemini 3 integration for AI analysis
- Multi-criteria scoring engine with configurable weights
- Daily job scheduler using APScheduler (runs at 7 AM)
- Report generator (JSON + HTML email format)
- REST API with filtering, pagination, and search
- Comprehensive API documentation (Swagger/OpenAPI)

**Frontend**
- Modern dark-themed dashboard with glassmorphism effects
- Real-time statistics display
- Advanced filtering (sector, status, score, search)
- Responsive opportunity cards with scores breakdown
- Beautiful animations and transitions
- Mobile-responsive design

**Infrastructure**
- Docker and Docker Compose setup
- Environment-based configuration
- Automated database migrations
- Health check endpoints
- CORS support

**Scoring Model**
- Pain & Urgency (30%)
- Frequency (20%)
- Willingness to Pay (20%)
- Low Competition (15%)
- Technical Feasibility (10%)
- AI Synergy (5%)

#### Features

- ✅ Automated daily discovery (scheduled at 7 AM)
- ✅ Multi-source scraping (Reddit, HackerNews)
- ✅ AI-powered analysis with Gemini 3
- ✅ Intelligent scoring and ranking
- ✅ Opportunity deduplication
- ✅ Status tracking (new, selected, in progress, discarded)
- ✅ User notes for each opportunity
- ✅ Historical reports storage
- ✅ Analytics dashboard
- ✅ Full-text search
- ✅ Export to JSON

#### Documentation

- README with project overview
- SETUP_GUIDE with installation instructions
- API_KEYS guide for configuration
- API documentation (auto-generated)
- Inline code documentation

---

## Future Enhancements (Roadmap)

### Version 1.1 (Planned)

- [ ] Email notifications for daily reports
- [ ] Opportunity detail modal in frontend
- [ ] Historical trends visualization (Chart.js)
- [ ] PDF export for opportunities
- [ ] Enhanced clustering using embeddings
- [ ] Twitter/X integration (if API access available)

### Version 1.2 (Planned)

- [ ] User authentication and multi-user support
- [ ] Favorites and collections
- [ ] Custom scoring weights per user
- [ ] Webhooks for Slack/Discord
- [ ] Browser extension for quick save
- [ ] Mobile app (React Native)

### Version 2.0 (Future)

- [ ] Machine learning for better scoring
- [ ] Automatic market research for each opportunity
- [ ] Competition analysis with web scraping
- [ ] Revenue projection calculator
- [ ] Integration with Make.com for automation
- [ ] Notion/Obsidian sync

---

## Contributing

To suggest features or report bugs, please create an issue in the repository.

## License

MIT License - See LICENSE file for details
