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

## 🚀 Quick Start

```bash
# 1. Setup
pip install -r requirements.txt
playwright install chromium
python check_api.py

# 2. Discover competitors (2-4 hours)
python scripts/run_discovery.py

# 3. Monitor & analyze (24-48 hours)
python scripts/run_monitor.py

# 4. Generate intelligence report
python scripts/generate_report.py
```

---

## 📊 What You Get

✅ **Winning Niche** - Score 0-100, clear recommendation
✅ **Structural Blueprint** - Word count, images, schema, structure
✅ **Title Formulas** - LLM-extracted patterns that work
✅ **Timing Strategy** - When to publish for max velocity
✅ **Competitor Benchmarks** - Who's winning and why

---

## 📁 Documentation

- **QUICK_START.md** - Get started in 3 steps
- **PROJECT_STATUS.md** - Complete documentation
- **config/** - Seed URLs and niche settings

---

## 🏗️ Architecture

```
Phase 1: Discovery → 100+ competitors + RSS feeds
Phase 2: Monitoring → Articles + DNA profiles (60s cycle)
Phase 3: Intelligence → Patterns + niche scores (6h cycle)
```

Built with Python, Playwright, Claude AI, asyncio, SQLite.

---

## 💡 Key Features

- ✅ BFS competitor discovery with relevance scoring
- ✅ Async RSS monitoring (batches of 20, 60s cycle)
- ✅ DNA extraction with 20+ data points
- ✅ LLM-powered title pattern analysis
- ✅ Niche velocity scoring (article volume + social + timing + patterns)
- ✅ Anti-ban protection (stealth mode + rate limiting)
- ✅ Production-ready with error handling

---

## 📈 Expected Results (24-48 hours)

```
Competitors: 100-150 sites
Articles: 500-1000+
DNA Profiles: 500+ complete
Patterns: 6-10 structural
Winning Niche: Identified with 85+ score
```

---

## ⚙️ Requirements

- Python 3.11+
- Playwright (Chromium)
- Anthropic API (Claude)
- OpenAI API (optional)
- Netrows API (optional)

---

## 📄 License

Proprietary - Project Hunter

---

**Status:** Production Ready (93% Complete)

**Read QUICK_START.md to begin!** 🚀
