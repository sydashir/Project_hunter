# Project Hunter - Output Guide

**What You'll Get, When, and In What Format**

---

## Stage 1: Chrome Extension (While Browsing)

### Visual Output in Browser

**Extension Badge (Real-time):**
```
Chrome toolbar icon shows: [127]
↑ Number of domains captured
```

**Extension Popup (Click icon):**
```
┌──────────────────────────────┐
│  🎯 Discover Tracker         │
├──────────────────────────────┤
│  Domains Discovered:         │
│         127                  │
├──────────────────────────────┤
│  [Reset Counter]             │
└──────────────────────────────┘
```

**Browser Console (F12 → Console tab):**
```
[Discover Tracker] Monitoring active
[Discover Tracker] Found: techcrunch.com
[Discover Tracker] Found: forbes.com
[Discover Tracker] Found: healthline.com
[Discover Tracker] Sent to API: techcrunch.com
[Discover Tracker] Sent to API: forbes.com
...
```

---

## Stage 2: API Server (Terminal)

### Terminal Output (While Running)

**When you start:**
```bash
$ python api/discover_api.py

[Discover API] Starting on http://localhost:8000
[Discover API] Install Chrome extension and browse Google Discover
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**While browsing (as extension sends data):**
```
[API] New domain: techcrunch.com (position 0)
[API] New domain: theverge.com (position 1)
[API] New domain: wired.com (position 2)
[API] New domain: forbes.com (position 3)
[API] New domain: businessinsider.com (position 4)
...
INFO:     127.0.0.1:54321 - "POST /api/discover/article HTTP/1.1" 200 OK
INFO:     127.0.0.1:54322 - "POST /api/discover/article HTTP/1.1" 200 OK
...
```

### API Web Interface

**Visit in browser:** `http://localhost:8000/docs`

**You'll see:**
```
FastAPI - Swagger UI
════════════════════════════════════════

Endpoints:
  POST /api/discover/article
  GET  /api/discover/stats
  POST /api/discover/reset

Try it out → Test endpoints interactively
```

**Stats Endpoint:** `http://localhost:8000/api/discover/stats`

**JSON Response:**
```json
{
  "total_domains": 127,
  "domains": [
    "techcrunch.com",
    "theverge.com",
    "wired.com",
    "forbes.com",
    "businessinsider.com",
    "healthline.com",
    "medicalnewstoday.com",
    "space.com",
    "phys.org",
    "sciencedaily.com",
    ... (117 more)
  ]
}
```

---

## Stage 3: Discovery Script (Terminal)

### Terminal Output

**Command:**
```bash
$ python scripts/run_discovery.py
```

**Full Output:**
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
  [1] theverge.com - technology
  [2] wired.com - technology
  [3] forbes.com - business
  [4] businessinsider.com - business
  [5] healthline.com - health
  [6] medicalnewstoday.com - health
  [7] space.com - science
  [8] phys.org - science
  [9] sciencedaily.com - science
```

---

## Stage 4: Database Files (JSON)

### File Location: `data/competitors.json`

**Format:** JSON array of competitor objects

**File Contents:**
```json
[
  {
    "site_id": "site_abc123",
    "domain": "techcrunch.com",
    "url": "https://techcrunch.com/2024/02/03/article-title",
    "niche": "technology",
    "sub_niches": [],
    "discovery_source": "chrome_extension",
    "discovered_from": null,
    "discovery_date": "2024-02-03T10:30:45.123456",
    "authority_score": 100.0,
    "rss_feeds": [],
    "last_crawled": null,
    "crawl_depth": 0,
    "status": "active",
    "metadata": {
      "discover_position": 0,
      "discovered_at": "2024-02-03T10:30:45.123456",
      "sample_title": "Breaking: AI Makes Major Breakthrough"
    }
  },
  {
    "site_id": "site_def456",
    "domain": "forbes.com",
    "url": "https://forbes.com/sites/article",
    "niche": "business",
    "sub_niches": [],
    "discovery_source": "chrome_extension",
    "discovered_from": null,
    "discovery_date": "2024-02-03T10:31:12.789012",
    "authority_score": 97.0,
    "rss_feeds": [],
    "last_crawled": null,
    "crawl_depth": 0,
    "status": "active",
    "metadata": {
      "discover_position": 3,
      "discovered_at": "2024-02-03T10:31:12.789012",
      "sample_title": "Top Business Trends for 2024"
    }
  }
  ... (125 more competitors)
]
```

**File Size:** ~50-150KB (for 100-200 competitors)

---

## Stage 5: RSS Discovery (Terminal)

### Output After Running RSS Discovery

**Command:**
```bash
$ python scripts/run_monitor.py --cycles 1
```

**Terminal Output:**
```
[Monitor] Starting RSS discovery for 127 competitors...
[RSS] Checking techcrunch.com...
  ✓ Found: https://techcrunch.com/feed/
[RSS] Checking forbes.com...
  ✓ Found: https://www.forbes.com/feed/
[RSS] Checking healthline.com...
  ✓ Found: https://www.healthline.com/rss
...

[Monitor] RSS Discovery Complete
  Total competitors: 127
  RSS feeds found: 112
  No RSS: 15

[Monitor] Starting monitoring cycle 1/1...
[Monitor] Fetching 112 feeds...
  New articles: 47

[Monitor] Cycle complete. Waiting 60s...
```

---

## Stage 6: Monitoring Results (Terminal + Database)

### Terminal Output (Continuous)

```
[Monitor] Cycle 1: Fetched 112 feeds, found 47 new articles
[DNA] Extracting DNA for: "AI Breakthrough in Neural Networks"
[DNA] Extracting DNA for: "Top 10 Health Tips for 2024"
...
[DNA] Queue: 45 pending

[Monitor] Cycle 2: Fetched 112 feeds, found 12 new articles
[DNA] Completed: 32 extractions
[DNA] Queue: 25 pending

[Monitor] Cycle 3: Fetched 112 feeds, found 8 new articles
...
```

### Database Output

**File:** `data/articles/articles.db` (SQLite database)

**Query to see articles:**
```bash
$ sqlite3 data/articles/articles.db "SELECT title, domain, publish_date FROM articles LIMIT 5;"
```

**Output:**
```
AI Breakthrough in Neural Networks|techcrunch.com|2024-02-03 10:30:00
Top 10 Health Tips for 2024|healthline.com|2024-02-03 10:45:00
SpaceX Launches New Mission|space.com|2024-02-03 11:00:00
Business Trends Analysis|forbes.com|2024-02-03 11:15:00
Latest Physics Discovery|phys.org|2024-02-03 11:30:00
```

---

## Stage 7: Intelligence Report (Terminal + JSON)

### Terminal Output

**Command:**
```bash
$ python scripts/generate_report.py
```

**Output:**
```
╔══════════════════════════════════════════════════════════╗
║         PROJECT HUNTER - INTELLIGENCE REPORT             ║
╚══════════════════════════════════════════════════════════╝

ANALYSIS PERIOD: 2024-02-01 to 2024-02-03
TOTAL ARTICLES ANALYZED: 487

┌─────────────────────────────────────────────────────────┐
│ WINNING NICHE                                           │
└─────────────────────────────────────────────────────────┘

🔥 TECHNOLOGY (Score: 92/100) - HOT
   Articles: 178 (36.5%)
   Avg Velocity: 8.3 articles/day
   Top Performers: TechCrunch, The Verge, Wired

📊 BUSINESS (Score: 78/100) - WARM
   Articles: 134 (27.5%)
   Avg Velocity: 5.8 articles/day
   Top Performers: Forbes, Business Insider

💊 HEALTH (Score: 65/100) - MODERATE
   Articles: 112 (23.0%)
   Avg Velocity: 4.2 articles/day
   Top Performers: Healthline, Medical News Today

┌─────────────────────────────────────────────────────────┐
│ STRUCTURAL BLUEPRINT                                    │
└─────────────────────────────────────────────────────────┘

Word Count:      800-1200 (optimal)
Images:          3-5 per article
Schema Markup:   95% use Article schema
HTML Structure:  H1 → H2 (3-4) → H3 (2-3 each)
Meta Description: 140-160 characters

┌─────────────────────────────────────────────────────────┐
│ TITLE FORMULAS (Top 10)                                 │
└─────────────────────────────────────────────────────────┘

1. [Number] + [Topic] + "That" + [Benefit]
   Example: "7 AI Tools That Will Transform Your Workflow"

2. "How" + [Subject] + [Action] + [Timeframe]
   Example: "How Scientists Discovered Dark Matter in 2024"

3. [Superlative] + [Topic] + "You" + [Action]
   Example: "Best Productivity Apps You Should Try Today"

... (7 more formulas)

┌─────────────────────────────────────────────────────────┐
│ TIMING STRATEGY                                         │
└─────────────────────────────────────────────────────────┘

Best Publishing Times:
  1. 7:00-9:00 AM EST (Morning commute)
  2. 12:00-1:00 PM EST (Lunch break)
  3. 6:00-8:00 PM EST (Evening wind-down)

Best Days: Tuesday, Wednesday (mid-week peaks)
Worst Days: Saturday (lowest engagement)

┌─────────────────────────────────────────────────────────┐
│ RECOMMENDATION                                          │
└─────────────────────────────────────────────────────────┘

✓ Focus on: TECHNOLOGY niche
✓ Target length: 900-1100 words
✓ Include: 4 images + Article schema
✓ Publish: Tuesday/Wednesday, 7-9 AM EST
✓ Use: Title formula #1 (Number + Benefit)

Expected Discover Performance: HIGH (92/100)
```

### JSON Files Created

**1. Niche Scores:** `data/intelligence/niche_scores.json`
```json
{
  "technology": {
    "score": 92,
    "article_count": 178,
    "velocity": 8.3,
    "rating": "HOT",
    "top_performers": ["techcrunch.com", "theverge.com", "wired.com"]
  },
  "business": {
    "score": 78,
    "article_count": 134,
    "velocity": 5.8,
    "rating": "WARM",
    "top_performers": ["forbes.com", "businessinsider.com"]
  }
}
```

**2. Patterns:** `data/intelligence/patterns.json`
```json
{
  "word_count": {
    "min": 800,
    "max": 1200,
    "average": 980,
    "optimal": "900-1100"
  },
  "images": {
    "min": 3,
    "max": 5,
    "average": 4.2,
    "optimal": 4
  },
  "schema_usage": {
    "article": 0.95,
    "newsarticle": 0.78,
    "blogposting": 0.45
  }
}
```

**3. Title Formulas:** `data/intelligence/title_formulas.json`
```json
[
  {
    "formula": "[Number] + [Topic] + 'That' + [Benefit]",
    "examples": [
      "7 AI Tools That Will Transform Your Workflow",
      "5 Health Tips That Actually Work"
    ],
    "frequency": 89,
    "success_rate": 0.87
  },
  {
    "formula": "'How' + [Subject] + [Action] + [Timeframe]",
    "examples": [
      "How Scientists Discovered Dark Matter in 2024"
    ],
    "frequency": 67,
    "success_rate": 0.82
  }
]
```

**4. Timing Insights:** `data/intelligence/timing_insights.json`
```json
{
  "best_hours": [7, 8, 12, 19],
  "best_days": ["Tuesday", "Wednesday"],
  "worst_days": ["Saturday"],
  "average_publish_time": "08:30",
  "peak_engagement_window": "07:00-09:00"
}
```

---

## Complete Output Summary

### Terminal Outputs (What You See)

| Stage | Command | Output Format | What You Get |
|-------|---------|---------------|--------------|
| Extension | Browse Discover | Badge counter | Real-time domain count |
| API Server | `python api/discover_api.py` | Terminal logs | "New domain: X" messages |
| Discovery | `python scripts/run_discovery.py` | Terminal summary | Niche breakdown + top 10 |
| Monitoring | `python scripts/run_monitor.py` | Terminal logs | Articles found, DNA extracted |
| Report | `python scripts/generate_report.py` | Formatted report | Complete intelligence analysis |

### File Outputs (What's Saved)

| File | Format | Size | Contains |
|------|--------|------|----------|
| `data/competitors.json` | JSON | 50-150KB | All discovered competitors |
| `data/articles/articles.db` | SQLite | 5-50MB | All monitored articles |
| `data/intelligence/niche_scores.json` | JSON | 5-10KB | Niche velocity scores |
| `data/intelligence/patterns.json` | JSON | 10-20KB | Structural patterns |
| `data/intelligence/title_formulas.json` | JSON | 15-30KB | Title formulas |
| `data/intelligence/timing_insights.json` | JSON | 2-5KB | Publishing times |

### Web Outputs (Browser Access)

| URL | What You See |
|-----|--------------|
| `http://localhost:8000/docs` | Interactive API documentation |
| `http://localhost:8000/api/discover/stats` | JSON stats of captured domains |
| Extension popup | Domain counter and reset button |
| Browser console (F12) | Real-time capture logs |

---

## Visual Flow of All Outputs

```
1. BROWSING (You see)
   ↓
   Extension Badge: [127]
   Browser Console: "Found: techcrunch.com"

2. API SERVER (Terminal shows)
   ↓
   "[API] New domain: techcrunch.com (position 0)"

3. DISCOVERY SCRIPT (Terminal shows)
   ↓
   "Total discovered: 127"
   "By niche: technology: 45..."

4. DATABASE (File created)
   ↓
   data/competitors.json (JSON with 127 objects)

5. MONITORING (Terminal shows)
   ↓
   "Cycle 1: Found 47 new articles"
   "DNA extracted: 32 complete"

6. DATABASE (Files updated)
   ↓
   data/articles/articles.db (SQLite with articles)

7. INTELLIGENCE (Terminal + Files)
   ↓
   Terminal: Formatted report
   Files: 4 JSON files with insights
```

---

## Example: Complete Output Sequence

**You run these commands in order:**

```bash
# 1. Start API (keep running)
$ python api/discover_api.py
> [Discover API] Starting on http://localhost:8000

# 2. Browse Discover for 30-60 min
# (Extension shows badge incrementing: 1, 2, 3... 127)

# 3. Load competitors
$ python scripts/run_discovery.py
> Total discovered: 127
> By niche: technology: 45, business: 32...

# 4. Start monitoring (let run 24-48 hours)
$ python scripts/run_monitor.py
> Cycle 1: Found 47 new articles...

# 5. Generate intelligence report
$ python scripts/generate_report.py
> WINNING NICHE: TECHNOLOGY (92/100)
> Word Count: 800-1200 optimal...
```

**You get these files:**
- `data/competitors.json` (127 competitors)
- `data/articles/articles.db` (500+ articles)
- `data/intelligence/*.json` (4 insight files)

**Plus terminal output showing progress at each step!**

---

## Quick Reference: "Where's My Data?"

**Live/Real-time:**
- Extension badge (domain count)
- API terminal (log messages)
- Browser at localhost:8000/api/discover/stats

**Saved to Disk:**
- Competitors: `data/competitors.json`
- Articles: `data/articles/articles.db`
- Insights: `data/intelligence/*.json`

**Reports/Analysis:**
- Terminal: `python scripts/generate_report.py`
- Files: JSON files in `data/intelligence/`

---

## Output Format Summary

✅ **Terminal** - Progress messages, summaries, reports
✅ **JSON** - Structured data (competitors, patterns, insights)
✅ **SQLite** - Article database (queryable)
✅ **Web API** - Real-time stats (JSON via HTTP)
✅ **Browser UI** - Extension popup and console

You get **multiple formats** so you can:
- View progress (terminal)
- Access data programmatically (JSON/SQLite)
- Monitor live (API/extension)
- Read reports (formatted terminal output)
