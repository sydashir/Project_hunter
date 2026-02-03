# Project Hunter - Chrome Extension Setup Guide

This guide walks you through setting up the Chrome extension-based competitor discovery system.

## Overview

Instead of automated web scraping, Project Hunter uses a **Chrome extension that passively monitors your Google Discover feed**. This approach:

- ✅ **100% Legal** - You're capturing your own browsing data
- ✅ **Zero Ban Risk** - No automation, just normal browsing
- ✅ **No ToS Violation** - Uses passive DOM observation
- ✅ **Most Accurate** - Discovers sites ACTUALLY in Google Discover

## Architecture

```
┌─────────────────────┐
│  Google Discover    │
│  (Your Feed)        │
└──────────┬──────────┘
           │ Passive observation
           ↓
┌─────────────────────┐
│  Chrome Extension   │
│  - content.js       │
│  - background.js    │
└──────────┬──────────┘
           │ HTTP POST
           ↓
┌─────────────────────┐
│  FastAPI Server     │
│  localhost:8000     │
└──────────┬──────────┘
           │ Saves to DB
           ↓
┌─────────────────────┐
│  Database           │
│  competitors.json   │
└─────────────────────┘
```

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This includes:
- `fastapi` - API server
- `uvicorn` - ASGI server
- Other existing dependencies

## Step 2: Install Chrome Extension

1. **Open Chrome Extensions page**:
   ```
   chrome://extensions/
   ```

2. **Enable Developer Mode**:
   - Toggle "Developer mode" in the top right corner

3. **Load the extension**:
   - Click "Load unpacked"
   - Navigate to and select: `chrome_extension/` folder
   - Extension should appear in your extensions list

4. **Pin the extension** (optional):
   - Click the puzzle icon in Chrome toolbar
   - Find "Discover Competitor Tracker"
   - Click the pin icon to keep it visible

## Step 3: Start the API Server

Open a terminal and run:

```bash
python api/discover_api.py
```

You should see:
```
[Discover API] Starting on http://localhost:8000
[Discover API] Install Chrome extension and browse Google Discover
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Keep this terminal open** while browsing.

### Verify API is working:

Visit: http://localhost:8000/docs

You should see FastAPI's automatic API documentation.

## Step 4: Browse Google Discover

1. **Open Chrome** (with extension installed)

2. **Go to Google Discover**:
   - Visit `google.com` or `google.com/discover`
   - You can also access it from the Google app homepage

3. **Scroll through your feed**:
   - Browse naturally for 30-60 minutes
   - Don't need to click articles, just scroll past them
   - Extension will capture domains automatically

4. **Watch the counter**:
   - Extension badge shows number of domains discovered
   - Click extension icon to see detailed count

5. **Target**: Collect 100-200 domains (2-3 hours of casual browsing)

### Tips for Effective Collection:

- **Leave it running**: Browse Discover while working on other tasks
- **Scroll regularly**: More scrolling = more domains
- **Multiple sessions**: Don't need to do all at once
- **Diverse content**: Scroll through different topics in your feed

## Step 5: Load Discovered Competitors

After collecting 100+ domains, run:

```bash
python scripts/run_discovery.py
```

This will:
- Load competitors from the database
- Infer niches based on domain/title keywords
- Show summary by niche
- List top performers by position

Expected output:
```
============================================================
PROJECT HUNTER - Competitor Discovery (Chrome Extension)
============================================================

Make sure:
1. Chrome extension is installed
2. API server is running (python api/discover_api.py)
3. You've browsed Google Discover for 30+ minutes

[Discovery] Loading competitors from Chrome extension data...
[Discovery] Loaded 127 competitors from extension

============================================================
DISCOVERY COMPLETE
============================================================
Total discovered: 127

By niche:
  technology: 45
  business: 32
  health: 28
  finance: 22

Top 10 by Discover position:
  [0] techcrunch.com - technology
  [1] forbes.com - business
  [2] healthline.com - health
  ...
```

## Step 6: Find RSS Feeds

The system will automatically discover RSS feeds for captured competitors.

This happens as part of the monitoring phase (unchanged from before).

## Step 7: Start Monitoring

```bash
python scripts/run_monitor.py --cycles 5
```

This will:
- Find RSS feeds for discovered competitors
- Monitor feeds for new articles
- Extract article DNA profiles
- Store in database

## Verification Checklist

### Chrome Extension
- [ ] Extension installed and visible in chrome://extensions/
- [ ] Badge shows count when browsing Discover
- [ ] Popup shows domain count
- [ ] Console shows "[Discover Tracker] Found: example.com"

### API Server
- [ ] Server starts without errors
- [ ] http://localhost:8000/docs loads
- [ ] Console shows "[API] New domain: example.com" when browsing
- [ ] http://localhost:8000/api/discover/stats returns JSON

### Discovery Script
- [ ] Loads competitors from database
- [ ] Shows summary by niche
- [ ] Lists top performers
- [ ] Competitors have `discovery_source: "chrome_extension"`

### Database
- [ ] File exists: `data/competitors.json`
- [ ] Contains sites with `discovery_source: "chrome_extension"`
- [ ] Metadata includes `discover_position`, `discovered_at`, `sample_title`

## Troubleshooting

### Extension not capturing domains

**Symptoms**: Badge not incrementing, no domains captured

**Solutions**:
1. Make sure you're on `google.com`, not `google.com/search`
2. Check browser console (F12) for errors
3. Look for "[Discover Tracker]" messages in console
4. Try reloading the page

### API not receiving data

**Symptoms**: Extension captures domains but API shows no data

**Solutions**:
1. Verify API server is running: `curl http://localhost:8000/api/discover/stats`
2. Check browser console for CORS errors
3. Verify fetch URL in `background.js` is `http://localhost:8000`
4. Check API server terminal for error messages

### No competitors loaded

**Symptoms**: `run_discovery.py` shows 0 competitors

**Solutions**:
1. Make sure you browsed Discover with extension installed
2. Check if API server received data: http://localhost:8000/api/discover/stats
3. Verify `data/competitors.json` exists and has entries
4. Look for entries with `"discovery_source": "chrome_extension"`

### Port already in use

**Symptoms**: API server fails to start with "Address already in use"

**Solutions**:
1. Kill existing process: `lsof -ti:8000 | xargs kill -9`
2. Or use different port in `api/discover_api.py` and `background.js`

## API Endpoints

### POST /api/discover/article
Receives article data from Chrome extension

**Request body**:
```json
{
  "domain": "example.com",
  "url": "https://example.com/article",
  "title": "Article Title",
  "position": 0,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Response**:
```json
{
  "status": "success",
  "domain": "example.com",
  "total_discovered": 127
}
```

### GET /api/discover/stats
Get discovery statistics

**Response**:
```json
{
  "total_domains": 127,
  "domains": ["example.com", "another.com", ...]
}
```

### POST /api/discover/reset
Reset discovered domains counter (for testing)

**Response**:
```json
{
  "status": "reset",
  "total_domains": 0
}
```

## Files Structure

```
project-hunter/
├── chrome_extension/
│   ├── manifest.json       # Extension config
│   ├── content.js         # DOM observer
│   ├── background.js      # API communication
│   ├── popup.html         # UI
│   ├── popup.js           # UI logic
│   └── icon.svg           # Extension icon
├── api/
│   ├── __init__.py
│   └── discover_api.py    # FastAPI server
├── core/
│   └── scout/
│       └── competitor_discovery.py  # Updated with load_from_extension()
├── scripts/
│   └── run_discovery.py   # Updated to load extension data
└── data/
    └── competitors.json   # Stored competitors
```

## Next Steps

After collecting and loading competitors:

1. **RSS Discovery** - System finds RSS feeds for competitors
2. **Monitoring** - Monitors feeds for new articles
3. **DNA Extraction** - Analyzes what makes articles successful
4. **Intelligence Reports** - Generates insights on winning patterns

## Legal & Privacy Notes

### Why This Approach is Legal

1. **Your Own Data**: You're capturing your own browsing activity
2. **No Automation**: Extension just observes, doesn't automate
3. **No Scraping**: Only captures what you naturally see
4. **Passive Observation**: Similar to browser dev tools (legal)
5. **No ToS Violation**: Normal browsing behavior

### Precedent

Similar tools that are legal:
- Ad blockers (uBlock Origin)
- Privacy tools (Privacy Badger)
- Developer tools (React DevTools)
- All use similar DOM observation techniques

### What's NOT Allowed

The extension does NOT:
- ❌ Automate scrolling or clicking
- ❌ Scrape content or full HTML
- ❌ Bypass authentication
- ❌ Access non-public data
- ❌ Violate rate limits (no limits on human browsing)

## Support

For issues:
1. Check console logs (browser and API server)
2. Verify all steps in checklist
3. Review troubleshooting section
4. Check extension permissions in chrome://extensions/

## Performance Tips

- **Casual browsing**: Leave extension running during normal Discover browsing
- **No rush**: Collect domains over multiple sessions
- **Quality over speed**: 100-200 high-quality domains better than 500 random ones
- **Diverse niches**: Scroll through different topics for broader coverage
