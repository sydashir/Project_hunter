# Project Hunter

**Autonomous Intelligence System for Google Discover**

Discovers the "secret sauce" of Google Discover by monitoring 100+ competitors, extracting article DNA, and identifying winning patterns.

---

## 🎯 What It Does

1. **Discovers** 100+ competitors from 7 seed URLs
2. **Monitors** RSS feeds every 60 seconds
3. **Extracts** 20+ DNA data points per article
4. **Analyzes** patterns to identify what works
5. **Reports** winning niche + actionable blueprint

---

## 📦 Installation & Setup

### **Prerequisites**

- Python 3.11 or higher
- Git
- API keys (Anthropic Claude, OpenAI optional)

---

### **Setup for Mac**

```bash
# 1. Clone or navigate to project
cd /path/to/project-hunter

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Install Playwright browsers
playwright install chromium

# 6. Create .env file (see API Keys section below)
touch .env
```

---

### **Setup for Windows**

```cmd
# 1. Clone or navigate to project
cd C:\path\to\project-hunter

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Install Playwright browsers
playwright install chromium

# 6. Create .env file (see API Keys section below)
# Create file manually or use: echo. > .env
```

---

### **API Keys Configuration**

Create a `.env` file in the project root:

```env
# Required
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Optional (for fallback/cross-verification)
OPENAI_API_KEY=sk-proj-xxxxx

# Optional (for social velocity tracking - future feature)
NETROWS_API_KEY=pk_live_xxxxx
```

**Where to get API keys:**
- **Anthropic Claude:** https://console.anthropic.com/
- **OpenAI:** https://platform.openai.com/api-keys
- **Netrows:** https://netrows.com/ (optional)

---

### **Verify Installation**

**Mac/Linux:**
```bash
python scripts/run_discovery.py --help
```

**Windows:**
```cmd
python scripts\run_discovery.py --help
```

If you see help text, you're good to go!

---

## 📊 NEW: Real-Time Dashboard

**Visualize everything in your browser!**

```bash
streamlit run dashboard.py
```

**Features:**
- 📊 Real-time domain capture visualization
- 🔍 Interactive competitor browser with filters
- 📈 Intelligence analysis with charts
- 📥 CSV export functionality
- ⚙️ System status monitoring

Opens automatically at: `http://localhost:8501`

See: [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) for full details

---

## 🚀 Quick Start

### **NEW: Chrome Extension Method (Recommended)**

**Uses passive monitoring - 100% legal, zero ban risk, most accurate**

1. **Install Chrome Extension** (see [SETUP_GUIDE.md](SETUP_GUIDE.md) for details):
   ```bash
   # Open chrome://extensions/
   # Enable Developer Mode
   # Load unpacked -> select chrome_extension/ folder
   ```

2. **Start API Server**:
   ```bash
   python api/discover_api.py
   ```

3. **Browse Google Discover** (30-60 minutes casual browsing):
   - Go to google.com or google.com/discover
   - Scroll through your feed naturally
   - Extension captures domains automatically
   - Target: 100-200 domains

4. **Load Discovered Competitors**:
   ```bash
   python scripts/run_discovery.py
   ```

**Why this method?**
- ✅ Discovers sites ACTUALLY in Google Discover (not random blogs)
- ✅ Zero ban risk (no automation, just observing your own feed)
- ✅ 100% legal (your own browsing data)
- ✅ Most accurate results

See full setup guide: [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

### **Alternative: BFS Crawler Method** (Original)

Discovers competitors by crawling from seed URLs.

**Mac/Linux:**
```bash
python scripts/run_discovery.py
```

**Windows:**
```cmd
python scripts\run_discovery.py
```

**What happens:**
- Crawls 7 seed URLs from `config/seed_urls.yaml`
- Discovers 100-150 competitor sites using BFS algorithm
- Auto-detects RSS feeds for all competitors
- Saves to `data/competitors/`

**Note:** This finds sites that link to each other, but doesn't guarantee they're in Google Discover.

---

### **Step 2: Start Monitoring** (24-48 hours recommended)

Monitors RSS feeds and extracts article DNA.

**Mac/Linux:**
```bash
# Test run (5 cycles)
python scripts/run_monitor.py --cycles 5

# Production (runs indefinitely)
python scripts/run_monitor.py
```

**Windows:**
```cmd
# Test run (5 cycles)
python scripts\run_monitor.py --cycles 5

# Production (runs indefinitely)
python scripts\run_monitor.py
```

**What happens:**
- Monitors 100+ RSS feeds every 60 seconds
- Detects new articles (GUID-based detection)
- Extracts DNA profiles (20+ data points per article)
- Runs intelligence analysis every 6 hours
- Saves to `data/articles/articles.db`

**Tip:** Let it run for 24-48 hours to collect sufficient data (500+ articles)

---

### **Step 3: Generate Intelligence Report**

Analyzes all data and identifies winning patterns.

**Mac/Linux:**
```bash
python scripts/generate_report.py
```

**Windows:**
```cmd
python scripts\generate_report.py
```

**What you get:**
- Niche velocity scores (0-100)
- Winning niche recommendation
- Structural blueprint (word count, images, schema)
- Title formulas (LLM-extracted patterns)
- Timing strategy (optimal publish windows)

---

## 📊 What You Get

✅ **Winning Niche** - Score 0-100, clear recommendation (HOT/WARM/MODERATE/COLD)
✅ **Structural Blueprint** - Word count, images, schema, HTML structure
✅ **Title Formulas** - LLM-extracted patterns that work
✅ **Timing Strategy** - When to publish for max velocity
✅ **Competitor Benchmarks** - Who's winning and why

---

## 📈 Expected Results (24-48 hours)

```
✓ Competitors: 100-150 sites
✓ RSS Feeds: 100-110 active
✓ Articles: 500-1000+
✓ DNA Profiles: 500+ complete (20+ data points each)
✓ Patterns: 6-10 structural patterns identified
✓ Winning Niche: Identified with 85+ confidence score
✓ Title Formulas: 10-20 proven patterns
✓ Timing Insights: 3+ optimal publish windows
```

**Cost:** $2-5 in API calls (LLM title analysis only)

---

## 📁 Project Structure

```
project-hunter/
├── chrome_extension/          # NEW: Chrome extension for passive monitoring
│   ├── manifest.json
│   ├── content.js
│   ├── background.js
│   ├── popup.html
│   └── popup.js
│
├── api/                       # NEW: FastAPI server
│   ├── discover_api.py
│   └── test_api.py
│
├── config/
│   ├── seed_urls.yaml        # 7 seed competitors + discovery settings
│   └── niches.yaml            # 6 niches with keywords
│
├── core/
│   ├── scout/                 # Discovery & Monitoring
│   │   ├── competitor_discovery.py
│   │   ├── rss_discovery.py
│   │   └── rss_monitor.py
│   ├── architect/             # DNA Extraction
│   │   └── dna_extractor.py
│   ├── intelligence/          # Pattern Recognition
│   │   ├── pattern_engine.py
│   │   ├── niche_scorer.py
│   │   ├── title_analyzer.py
│   │   └── timing_analyzer.py
│   ├── orchestrator/          # Coordination
│   │   ├── main_controller.py
│   │   ├── task_queue.py
│   │   └── rate_limiter.py
│   └── persistence/           # Data Layer
│       ├── database.py
│       └── models.py
│
├── scripts/
│   ├── run_discovery.py      # Step 1
│   ├── run_monitor.py         # Step 2
│   └── generate_report.py    # Step 3
│
├── data/                      # Auto-created during runtime
│   ├── competitors/
│   │   ├── discovered_sites.json
│   │   └── rss_feeds.json
│   ├── articles/
│   │   ├── articles.db       # SQLite database
│   │   └── dna_profiles/
│   └── intelligence/
│       ├── patterns.json
│       ├── niche_scores.json
│       ├── title_formulas.json
│       └── timing_insights.json
│
├── .env                       # API keys (create this)
├── .gitignore
├── requirements.txt
├── README.md
└── SETUP_GUIDE.md            # NEW: Detailed Chrome extension setup
```

---

## 🏗️ Architecture

```
Phase 1: Discovery (2-4 hours)
  ├─ BFS competitor crawler (7 seeds → 100+ sites)
  ├─ RSS feed auto-detection
  └─ Relevance scoring & filtering

Phase 2: Monitoring (continuous, 60s cycles)
  ├─ Async RSS polling (batches of 20)
  ├─ New article detection (GUID-based)
  ├─ DNA extraction queue (10 concurrent workers)
  └─ Intelligence analysis (every 6 hours)

Phase 3: Intelligence (on-demand)
  ├─ Pattern aggregation (word count, images, schema, structure)
  ├─ Niche velocity scoring (0-100)
  ├─ LLM title analysis (Claude/GPT)
  └─ Timing pattern analysis
```

**Tech Stack:**
- Python 3.11+ with asyncio
- Playwright (stealth mode for DNA extraction)
- feedparser (RSS parsing)
- aiohttp (async HTTP)
- SQLite (articles + DNA)
- Claude Sonnet 4.5 (title analysis)

---

## 💡 Key Features

- ✅ **BFS Competitor Discovery** - Relevance scoring, depth-limited crawl
- ✅ **Async RSS Monitoring** - Batches of 20 feeds, 60-second cycles
- ✅ **DNA Extraction** - 20+ data points (title, word count, images, schema, structure)
- ✅ **LLM Title Analysis** - Extract proven patterns from 500+ titles
- ✅ **Niche Velocity Scoring** - Article volume (20%) + social (25%) + timing (15%) + patterns (40%)
- ✅ **Anti-Ban Protection** - Playwright stealth mode + rate limiting + random delays
- ✅ **Production Ready** - Error handling, retry logic, state management

---

## 🔧 Configuration

### **Customize Seed URLs**

Edit `config/seed_urls.yaml`:
```yaml
seeds:
  - url: "https://your-competitor.com/"
    niche: "your-niche"

discovery:
  max_depth: 3              # Crawl depth (1-5)
  target_count: 150         # Target competitors
  min_relevance_score: 0.6  # Quality threshold
```

### **Customize Niches**

Edit `config/niches.yaml`:
```yaml
niches:
  your_niche:
    keywords: ["keyword1", "keyword2", "keyword3"]
    weight: 1.0
```

### **Adjust Performance**

**Monitoring speed** (edit `core/scout/rss_monitor.py`):
```python
RSSMonitor(
    batch_size=20,       # Feeds per batch (increase for faster)
    cycle_interval=60    # Seconds between cycles
)
```

**DNA workers** (edit `core/orchestrator/task_queue.py`):
```python
DNAExtractionQueue(max_workers=10)  # Concurrent extractions (5-20)
```

---

## 🐛 Troubleshooting

### **"ModuleNotFoundError: No module named 'feedparser'"**
```bash
pip install -r requirements.txt
```

### **Playwright errors**
```bash
playwright install chromium
```

### **"No competitors found"**
- Check `config/seed_urls.yaml` has valid URLs
- Verify internet connection
- Check logs in `data/logs/monitoring.log`

### **"API key not found"**
- Ensure `.env` file exists in project root
- Check API key format (starts with `sk-ant-` for Anthropic)

### **Rate limit errors**
- Built-in rate limiting handles this automatically
- System will retry with exponential backoff

---

## 📊 Monitoring Progress

### **View Real-Time Logs**

**Mac/Linux:**
```bash
tail -f data/logs/monitoring.log
```

**Windows:**
```cmd
powershell Get-Content data\logs\monitoring.log -Wait -Tail 50
```

### **Check Database Stats**

**Mac/Linux:**
```bash
sqlite3 data/articles/articles.db "SELECT COUNT(*) FROM articles;"
```

**Windows:**
```cmd
sqlite3 data\articles\articles.db "SELECT COUNT(*) FROM articles;"
```

### **View Discovered Competitors**

**Mac/Linux:**
```bash
cat data/competitors/discovered_sites.json | python -m json.tool
```

**Windows:**
```cmd
type data\competitors\discovered_sites.json
```

---

## ⚙️ Requirements

**Minimum:**
- Python 3.11+
- 4GB RAM
- 2GB disk space
- Internet connection

**APIs (get free tier):**
- Anthropic Claude API (required for title analysis)
- OpenAI API (optional, for cross-verification)
- Netrows API (optional, for social velocity tracking)

---

## 🎯 Use Cases

**1. Niche Research** - Discover which niche has highest velocity
**2. Content Strategy** - Copy winning structural patterns
**3. SEO Optimization** - Use proven title formulas
**4. Timing Strategy** - Publish during optimal windows
**5. Competitive Analysis** - Track what competitors are doing

---

## 📝 Notes

- **First run takes time:** Discovery phase may take 2-4 hours (crawling 100+ sites)
- **Let it run:** System needs 24-48 hours to collect sufficient data (500+ articles)
- **API costs:** Only title analysis uses LLM (~$1-2 per 500 titles), rest is free
- **Deterministic output:** No - output changes with real-time data (this is good!)
- **Patterns stabilize:** After 1000+ articles, core patterns become consistent

---

## 📄 License

Proprietary - Project Hunter

---

## 🚀 Next Steps After Intelligence Report

1. ✅ **Review winning niche** - Focus your content efforts
2. ✅ **Study structural blueprint** - Word count, images, schema requirements
3. ✅ **Apply title formulas** - Use proven headline patterns
4. ✅ **Follow timing strategy** - Publish during optimal windows
5. ✅ **Acquire domain** - Buy aged domain in winning niche
6. ✅ **Create content** - Use the blueprint to dominate Google Discover!

---

**Status:** Production Ready

**Get started:** `python scripts/run_discovery.py` 🚀
