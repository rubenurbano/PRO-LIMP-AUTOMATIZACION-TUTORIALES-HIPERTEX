# API Keys Configuration

## 🎯 Minimum Setup (Only 1 Required!)

### 1. Google Gemini API Key ⭐ (REQUIRED)

**Purpose**: AI analysis and scoring of opportunities

**How to get it**:
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

**Add to `.env`**:
```env
GEMINI_API_KEY=AIzaSy...your-key-here
```

**Free tier**: 60 requests per minute (sufficient for daily runs)

---

### 2. HackerNews 🎉 (NO API KEY NEEDED!)

**Purpose**: Scrape "Ask HN" posts and top stories from HackerNews

**How to use it**:
- Already configured! No setup needed ✅
- Works out of the box
- Uses the official HackerNews Firebase API (free, no authentication)

**Free tier**: Unlimited (reasonable use)

---

## 🔧 Optional Additional Sources

### 3. Reddit API Credentials (Optional)

**How to get it**:
1. Go to https://www.reddit.com/prefs/apps
2. Scroll to bottom and click "create another app..."
3. Fill in:
   - Name: "Business Opportunities Finder"
   - Type: Select "script"
   - Description: "Discover business opportunities"
   - Redirect URI: http://localhost:8000
4. Click "create app"
5. Copy your credentials:
   - **Client ID**: The string under "personal use script"
   - **Client Secret**: The "secret" field

**Add to `.env`**:
```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USER_AGENT=BusinessOpportunitiesFinder/1.0
```

**Free tier**: 60 requests per minute

**Note**: The system works perfectly with just HackerNews. Reddit is optional for additional data diversity.

---

### 4. ProductHunt API Key (Optional)

**Purpose**: Discover trending products and comments

**How to get it**:
1. Go to https://www.producthunt.com/v2/oauth/applications
2. Sign in
3. Create a new application
4. Copy the API token

**Add to `.env`**:
```env
PRODUCTHUNT_API_KEY=your_token_here
```

**Note**: ProductHunt scraper is disabled by default in the code. Uncomment in `daily_job.py` after adding key.

---

### 5. Twitter API Bearer Token (Optional)

**Purpose**: Track problem discussions on Twitter

**How to get it**:
1. Go to https://developer.twitter.com/
2. Apply for developer access
3. Create a project and app
4. Copy the Bearer Token

**Add to `.env`**:
```env
TWITTER_BEARER_TOKEN=your_bearer_token
```

**Warning**: Twitter API has very limited free tier (1,500 tweets/month). Not recommended unless you have paid plan.

---

## Email Configuration (Optional)

To receive daily reports by email:

**Gmail Setup** (recommended):
1. Enable 2-factor authentication on your Google account
2. Generate an App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy the 16-character password

**Add to `.env`**:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your_app_password_here
EMAIL_TO=your.email@gmail.com
```

---

## Testing Your API Keys

After adding keys to `.env`, test them:

```powershell
# Restart backend
docker-compose restart backend

# Check logs for errors
docker-compose logs backend | Select-String "error"

# Run a manual test
docker-compose exec backend python -c "from app.config import settings; print(f'Gemini key: {settings.gemini_api_key[:20]}...')"
```

---

## API Quota Limits Summary

| Service | Free Tier | Upgrade Needed? | Status |
|---------|-----------|-----------------|--------|
| **Gemini** | 60 req/min | No (sufficient) | ⭐ **REQUIRED** |
| **HackerNews** | No limit (reasonable use) | No | ✅ **Free, no API key!** |
| Reddit | 60 req/min | No (sufficient) | 🔧 Optional |
| ProductHunt | 1000 req/day | Maybe | 🔧 Optional |
| Twitter | 1,500 tweets/month | Yes (very limited) | 🔧 Optional |

**Recommendation**: Start with just **Gemini + HackerNews**. This is enough for MVP and requires only ONE API key!

---

## Security Best Practices

1. **Never commit `.env`** to git (already in `.gitignore`)
2. **Store API keys securely** (use password manager)
3. **Rotate keys** periodically
4. **Monitor usage** in each platform's dashboard
5. **Set up billing alerts** if using paid tiers

---

## Need Help?

- **Gemini API**: https://ai.google.dev/docs
- **Reddit API**: https://www.reddit.com/dev/api/
- **ProductHunt API**: https://api.producthunt.com/v2/docs
- **Twitter API**: https://developer.twitter.com/en/docs
