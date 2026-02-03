# Quick Start: Chrome Extension Method

**5-minute setup for discovering Google Discover competitors**

## What You Need

- Chrome browser
- Python 3.11+
- 30-60 minutes of casual Google Discover browsing

## Setup (One Time)

### 1. Install Chrome Extension

```bash
# Open Chrome
# Go to: chrome://extensions/
# Toggle "Developer mode" (top right)
# Click "Load unpacked"
# Select folder: chrome_extension/
```

### 2. Start API Server

```bash
python api/discover_api.py
```

Leave this terminal open. You should see:
```
[Discover API] Starting on http://localhost:8000
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 3. Test Setup (Optional but Recommended)

In a new terminal:
```bash
python api/test_api.py
```

If you see "✓ API is running", you're good to go!

## Usage

### Step 1: Collect Domains (30-60 minutes)

1. **Open Chrome** with extension installed
2. **Go to** `google.com` or `google.com/discover`
3. **Scroll through your feed** naturally
4. **Watch the badge** on the extension icon increment
5. **Target**: 100-200 domains

**Tips**:
- No need to click articles, just scroll past them
- Can browse casually while working
- Collect over multiple sessions
- More domains = better data

### Step 2: Load Competitors

```bash
python scripts/run_discovery.py
```

Output:
```
============================================================
PROJECT HUNTER - Competitor Discovery (Chrome Extension)
============================================================

[Discovery] Loaded 127 competitors from extension

============================================================
DISCOVERY COMPLETE
============================================================
Total discovered: 127

By niche:
  technology: 45
  business: 32
  health: 28
  ...

Top 10 by Discover position:
  [0] techcrunch.com - technology
  [1] forbes.com - business
  ...
```

### Step 3: Start Monitoring

```bash
python scripts/run_monitor.py --cycles 5
```

This will:
- Find RSS feeds for discovered competitors
- Monitor feeds for new articles
- Extract article DNA profiles
- Generate intelligence reports

## Verification Checklist

- [ ] Extension installed and visible in Chrome
- [ ] API server running on localhost:8000
- [ ] Extension badge shows count when browsing Discover
- [ ] `run_discovery.py` loads 100+ competitors
- [ ] `data/competitors.json` file created

## Troubleshooting

### Extension not capturing
- Make sure you're on `google.com` (not search results)
- Check browser console (F12) for "[Discover Tracker]" messages
- Reload the page

### API not receiving data
- Verify API is running: visit http://localhost:8000/docs
- Check browser console for CORS errors
- Restart API server

### No competitors found
- Make sure you've browsed Discover with extension installed
- Check API stats: http://localhost:8000/api/discover/stats
- Verify API server was running while browsing

## What's Next?

After loading 100+ competitors:

1. **RSS Discovery** - Automatically finds RSS feeds
2. **Monitoring** - Monitors feeds for new articles (24-48 hours)
3. **DNA Extraction** - Analyzes what makes articles successful
4. **Intelligence Reports** - Identifies winning patterns

## Why This Method?

✅ **Accurate** - Finds sites ACTUALLY in Google Discover
✅ **Legal** - Your own browsing data, no ToS violation
✅ **Safe** - Zero ban risk, no automation
✅ **Simple** - Just browse normally, extension does the rest

## Full Documentation

- **Detailed Setup**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Extension Details**: [chrome_extension/README.md](chrome_extension/README.md)
- **Main README**: [README.md](README.md)

## Support

If you encounter issues:
1. Run test script: `python api/test_api.py`
2. Check API logs in terminal
3. Check browser console (F12)
4. Review [SETUP_GUIDE.md](SETUP_GUIDE.md) troubleshooting section
