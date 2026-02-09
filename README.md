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

## 🎯 NEW: Real Google Discover Scraper

**Access ACTUAL Google Discover feed - no workarounds!**

```bash
python scripts/discover_scraper.py
```

**How it works:**
1. Opens Chrome in **mobile mode** (where real Discover exists)
2. You log in to Google (60 seconds)
3. Automatically captures from **REAL Discover feed**
4. Runs for 30 minutes with auto-scrolling
5. Saves 100-200 verified competitors

**This IS the real Discover feed.** Mobile mode = actual Discover algorithm.

---

## 📊 Real-Time Dashboard

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

---

## 🚀 Quick Start - Step by Step

### **Prerequisites: Install Playwright Browsers**

```bash
playwright install chromium
```

**What this does:** Downloads Chrome browser for automation (100MB, one-time)

---

### **Method 1: Mobile Discover Scraper (Recommended - REAL Discover)**

#### **Step 1: Run the Scraper**

```bash
python scripts/discover_scraper.py
```

**What happens:**
- Asks: "How many minutes to scrape?"
- Type: `30` (recommended)
- Press Enter

#### **Step 2: Browser Opens in Mobile Mode**

**What you'll see:**
- Chrome opens showing a mobile phone screen
- This is **mobile mode** where real Discover exists

**What to do:**
1. **Log in to your Google account** (you have 60 seconds)
2. After login, **scroll down** to see Discover articles
3. Keep scrolling - scraper captures automatically

#### **Step 3: Automatic Capture**

**What happens:**
- Scraper runs for 30 minutes
- Auto-scrolls every 5 seconds
- Captures article domains automatically
- Shows: `✓ [1] techcrunch.com - Article title...`
- Terminal updates with each new domain found

**You can:**
- ✅ Let it run automatically
- ✅ Manually scroll if you want
- ✅ Close browser early (Ctrl+C) if you have enough domains

#### **Step 4: Load Competitors**

After scraper finishes:

```bash
python scripts/run_discovery.py
```

**What this does:**
- Loads captured domains from database
- Assigns niches automatically
- Shows summary: "Total discovered: 127"

**Expected output:**
```
Total discovered: 127
By niche:
  technology: 45
  business: 32
  health: 28
```

#### **Step 5: Start Monitoring**

```bash
python scripts/run_monitor.py
```

**What this does:**
- Finds RSS feeds for competitors
- Monitors for new articles (runs 24-48 hours)
- Extracts article DNA automatically

#### **Step 6: View Dashboard**

```bash
streamlit run dashboard.py
```

**What this does:**
- Opens visual dashboard in browser
- Shows competitors, charts, insights
- Updates in real-time

---

### **Complete Command Sequence**

```bash
# One-time setup
playwright install chromium

# Collect competitors (30 minutes)
python scripts/discover_scraper.py
# → Browser opens, log in, scroll
# → Captures from REAL Discover feed

# Load competitors
python scripts/run_discovery.py

# Monitor articles (24-48 hours)
python scripts/run_monitor.py

# Generate insights (anytime)
python scripts/generate_report.py

# View dashboard (anytime)
streamlit run dashboard.py
```

**Why this method?**
- ✅ Accesses **ACTUAL Google Discover feed** (mobile mode)
- ✅ 100% verified - these sites ARE in Discover
- ✅ Automatic scrolling and capture
- ✅ Most accurate results possible

---

### **Method 2: Chrome Extension (Alternative)**

Desktop passive monitoring:
```bash
python api/discover_api.py          # Start API
# Install extension in Chrome
# Browse google.com or news.google.com
python scripts/run_discovery.py     # Load
```

### **Method 3: API Interceptor (Advanced)**

```bash
python scripts/discover_api_interceptor.py
```

---

## ⚠️ Troubleshooting

### Error: "Executable doesn't exist" or "Playwright was just installed"

**Fix:**
```bash
playwright install chromium
```

This downloads the Chrome browser needed (100MB, one-time).

### Error: "No module named 'playwright'"

**Fix:**
```bash
pip install playwright
playwright install chromium
```

### Error: "No competitors found"

**Cause:** Haven't run scraper yet

**Fix:**
```bash
python scripts/discover_scraper.py  # Run this first
```

### Scraper runs but captures 0 domains

**Fix:**
1. Make sure you **logged in** to Google (wait full 60 seconds)
2. **Scroll down** in the browser to see Discover articles
3. Look for article cards on the page

### Want to stop scraper early?

Press `Ctrl+C` in terminal - captured data is already saved!

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
├── dashboard.py               # Streamlit dashboard
│
├── chrome_extension/          # Chrome extension for Discover capture
│   ├── manifest.json
│   ├── content.js
│   ├── background.js
│   ├── popup.html
│   ├── popup.js
│   └── icon.png
│
├── api/                       # FastAPI server
│   └── discover_api.py
│
├── core/
│   └── persistence/           # Data Layer
│       ├── database.py
│       └── models.py
│
├── scripts/
│   └── extract_discover_dna.py  # DNA extraction from captured articles
│
├── data/                      # Auto-created during runtime
│   ├── competitors/
│   │   └── discovered_sites.json
│   ├── articles/
│   └── dna_analysis/          # CSV output from DNA extraction
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🏗️ Architecture

```
Phase 1: Discovery
  ├─ Mobile Discover scraper (real feed → 100+ sites)
  ├─ OR Chrome extension (passive capture)
  └─ OR API interceptor (advanced)

Phase 2: Monitoring (24-48 hours)
  ├─ RSS feed detection
  ├─ Article polling (60s cycles)
  ├─ DNA extraction (concurrent)
  └─ Database storage

Phase 3: Intelligence (on-demand)
  ├─ Niche velocity scoring
  ├─ Pattern analysis
  ├─ Title formula extraction
  └─ Timing optimization
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

- ✅ **Real Discover Access** - Mobile scraper accesses actual Discover feed
- ✅ **Multiple Methods** - Mobile scraper, Chrome extension, API interceptor
- ✅ **Interactive Dashboard** - Real-time visualization with Streamlit
- ✅ **DNA Extraction** - 20+ data points per article
- ✅ **LLM Analysis** - Claude/GPT title pattern extraction
- ✅ **Niche Scoring** - Velocity-based scoring (0-100)
- ✅ **Production Ready** - Error handling, retry logic, auto-save

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
