# How to Run Project Hunter - Complete Guide

**Simple answer: You DON'T need to run every 5 hours. Most things run continuously or just once!**

---

## Quick Overview

| Component | Run Once or Continuous? | When to Run |
|-----------|------------------------|-------------|
| **Chrome Extension** | Install once, runs always | One-time setup |
| **API Server** | Continuous (leave running) | Once at start |
| **Dashboard** | Continuous (leave running) | Once at start |
| **Discovery Script** | Once after browsing | After collecting 100+ domains |
| **Monitoring** | Continuous (24-48 hours) | Once after discovery |
| **Intelligence Report** | On-demand | When you want insights |

---

## Complete Workflow (Step-by-Step)

### 🔧 PHASE 1: ONE-TIME SETUP (Do this ONCE)

**Time: 10 minutes**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Chrome extension
# Open Chrome → chrome://extensions/
# Enable "Developer mode"
# Click "Load unpacked" → Select chrome_extension/ folder
```

**That's it for setup! Never need to do this again.**

---

### 📡 PHASE 2: DATA COLLECTION (Do once or whenever you want fresh data)

**Time: 30-60 minutes of casual browsing**

#### Step 1: Start API Server (Leave Running)

**Terminal 1:**
```bash
python api/discover_api.py
```

**What happens:**
- Server starts on localhost:8000
- Waits for extension to send data
- **LEAVE THIS RUNNING** - don't close terminal

**When to restart:**
- Never! Just leave it running
- Or restart if you close terminal by accident

---

#### Step 2: Start Dashboard (Optional but Recommended)

**Terminal 2:**
```bash
streamlit run dashboard.py
```

**What happens:**
- Opens browser at localhost:8501
- Shows real-time visualization
- **LEAVE THIS RUNNING** to watch progress

**When to restart:**
- Never! Just leave it running
- Or close if you don't want to watch

---

#### Step 3: Browse Google Discover (Normal Browsing)

**Chrome Browser:**
1. Go to `google.com` or `google.com/discover`
2. Scroll through your feed normally
3. Extension captures domains automatically
4. Watch dashboard or extension badge update

**How long?**
- 30-60 minutes total (can be split across days)
- Until you see 100-200 domains captured

**Can you stop and resume?**
- YES! Data is saved continuously
- Just keep API server running
- Browse whenever you want
- Accumulates over time

---

### 💾 PHASE 3: LOAD COMPETITORS (Run ONCE after browsing)

**Time: 10 seconds**

**Terminal 3 (or use Terminal 1 after stopping API):**
```bash
python scripts/run_discovery.py
```

**What happens:**
- Loads all captured domains from database
- Infers niches automatically
- Shows summary in terminal
- Saves to `data/competitors.json`

**Output:**
```
Total discovered: 127
By niche:
  technology: 45
  business: 32
  ...
```

**When to run:**
- ONCE after you finish browsing
- Or whenever you want to update competitor list
- NOT every 5 hours - only when you want to refresh

---

### 📊 PHASE 4: MONITORING (Run ONCE, Let it Run 24-48 Hours)

**Time: 24-48 hours continuous**

**Terminal:**
```bash
python scripts/run_monitor.py --cycles 100
```

Or for continuous (recommended):
```bash
python scripts/run_monitor.py
```

**What happens:**
- Finds RSS feeds for all competitors
- Monitors feeds every 60 seconds
- Extracts article DNA automatically
- Stores in database
- **RUNS CONTINUOUSLY** for 24-48 hours

**When to run:**
- ONCE after loading competitors
- Let it run for 24-48 hours to collect data
- Don't stop it! Leave it running

**Can you stop and restart?**
- Yes, but you'll miss articles published while stopped
- Best to let it run continuously
- Use `screen` or `tmux` to keep it running

---

### 📈 PHASE 5: INTELLIGENCE REPORT (Run When You Want Insights)

**Time: 10 seconds**

**Terminal:**
```bash
python scripts/generate_report.py
```

**What happens:**
- Analyzes all collected articles
- Identifies winning niche
- Shows structural patterns
- Displays title formulas
- Provides timing strategy

**When to run:**
- After monitoring has run for 24-48 hours
- Whenever you want updated insights
- Can run multiple times (gets better with more data)

---

## What Runs Continuously vs One-Time

### ✅ RUN ONCE (Never Again Unless You Want Fresh Data)

**1. Chrome Extension Install**
- Install once, works forever
- Automatically runs when you browse Google

**2. Discovery Script**
```bash
python scripts/run_discovery.py
```
- Run ONCE after browsing Discover
- Or run again if you collect more domains later

**3. Intelligence Report**
```bash
python scripts/generate_report.py
```
- Run whenever you want insights
- No need to run repeatedly

---

### 🔄 RUN CONTINUOUSLY (Leave Running)

**1. API Server**
```bash
python api/discover_api.py
```
- **Leave running** while browsing Discover
- Can stop after you're done browsing
- Restart when you want to browse again

**2. Dashboard (Optional)**
```bash
streamlit run dashboard.py
```
- **Leave running** if you want to watch progress
- Can close anytime, doesn't affect data

**3. Monitoring Script**
```bash
python scripts/run_monitor.py
```
- **Leave running** for 24-48 hours
- Continuously monitors RSS feeds
- Don't stop until you have enough articles (500+)

---

## Typical Usage Patterns

### Pattern 1: First Time Setup

**Day 1 - Morning (10 min setup + 60 min browsing):**
```bash
# Terminal 1: Start API (leave running)
python api/discover_api.py

# Terminal 2: Start Dashboard (leave running)
streamlit run dashboard.py

# Browser: Browse Google Discover for 60 minutes
# Extension captures 100-200 domains

# Terminal 3: Load competitors (once)
python scripts/run_discovery.py
```

**Day 1 - Afternoon (Start monitoring):**
```bash
# Terminal 1: Start monitoring (leave running 24-48 hours)
python scripts/run_monitor.py
```

**Day 3 - Morning (Get insights):**
```bash
# Terminal 1: Generate report
python scripts/generate_report.py
```

**DONE! You have everything you need.**

---

### Pattern 2: Daily Check-In

**You already have data, just want to check progress:**

```bash
# Start dashboard to view
streamlit run dashboard.py
```

**That's it! No need to run anything else.**

---

### Pattern 3: Fresh Data Collection

**You want to update competitor list (once a month):**

```bash
# Terminal 1: Start API
python api/discover_api.py

# Browser: Browse Discover for 30 min

# Terminal 2: Update competitors
python scripts/run_discovery.py
```

**Done! New competitors added.**

---

## Do You Need to Run Every 5 Hours? ❌ NO!

### What Runs Once:
- ✅ Chrome extension install
- ✅ Discovery script (after browsing)
- ✅ Intelligence report (when you want insights)

### What Runs Continuously (But NOT Every 5 Hours):
- ✅ API server - Only while actively browsing
- ✅ Monitoring - Once for 24-48 hours, then done
- ✅ Dashboard - Only when you want to view

### What You NEVER Need to Schedule:
- ❌ Nothing needs to run every 5 hours
- ❌ Nothing needs to run on a schedule
- ❌ Everything is either one-time or continuous

---

## How to Keep Things Running (If You Need To)

### If You Want Monitoring to Run for 48 Hours:

**Option 1: Keep Terminal Open**
```bash
python scripts/run_monitor.py
# Just don't close the terminal
```

**Option 2: Use Screen (Linux/Mac)**
```bash
screen -S monitor
python scripts/run_monitor.py
# Press Ctrl+A then D to detach
# Terminal can close, monitoring continues
```

**Option 3: Use tmux (Linux/Mac)**
```bash
tmux new -s monitor
python scripts/run_monitor.py
# Press Ctrl+B then D to detach
```

**Option 4: Use nohup (Linux/Mac)**
```bash
nohup python scripts/run_monitor.py > monitor.log 2>&1 &
```

**Option 5: Run in Background (Mac/Linux)**
```bash
python scripts/run_monitor.py &
```

---

## Common Questions

### Q: Do I need to browse Discover every day?
**A:** No! Browse once to collect 100-200 competitors, then you're done. Only browse again if you want to update your competitor list (maybe once a month).

### Q: Does monitoring need to run forever?
**A:** No! Just 24-48 hours to collect 500+ articles. After that, you have enough data for analysis. You can stop monitoring.

### Q: When do I run the intelligence report?
**A:** Whenever you want insights! After monitoring has collected enough articles (500+), run it once to see the analysis. You can run it again later to see updated patterns with more data.

### Q: Can I turn off my computer?
**A:**
- **While browsing Discover:** No - need API server running
- **During monitoring:** No - monitoring needs to run continuously for 24-48 hours
- **After collection:** Yes - all data is saved

### Q: What if I accidentally close something?
**A:** No problem! Just restart it:
- API server: Restart with `python api/discover_api.py`
- Dashboard: Restart with `streamlit run dashboard.py`
- Monitoring: Restart with `python scripts/run_monitor.py` (picks up where it left off)

---

## Minimal Daily Commands

**After initial setup, to just VIEW your data:**

```bash
streamlit run dashboard.py
```

**That's it!** Everything is already saved in the database.

---

## Summary: Simple Workflow

```
┌─────────────────────────────────────────────────┐
│ ONE-TIME SETUP (10 min)                         │
│ • Install dependencies                          │
│ • Install Chrome extension                      │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ DATA COLLECTION (60 min browsing)               │
│ 1. Start API server (leave running)            │
│ 2. Start dashboard (optional, leave running)   │
│ 3. Browse Google Discover normally              │
│ 4. Run discovery script (once)                  │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ MONITORING (24-48 hours continuous)             │
│ 1. Start monitoring script (leave running)     │
│ 2. Wait 24-48 hours for data collection        │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ ANALYSIS (10 seconds, anytime)                  │
│ 1. Generate intelligence report                 │
│ 2. View results in terminal or dashboard       │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ DONE! All data saved.                           │
│ View anytime with: streamlit run dashboard.py  │
└─────────────────────────────────────────────────┘
```

---

## What to Tell Hunter

**"Hunter, you only need to:**

1. **Setup once** (10 min) - Install extension
2. **Browse Discover once** (60 min) - Collect 100-200 competitors
3. **Run monitoring once** (24-48 hours continuous) - Let it collect articles
4. **Generate report** (anytime) - See the insights

**After that, all data is saved. No need to run every 5 hours or on any schedule. Just view the dashboard whenever you want!"**

---

## Quick Reference Card

**📋 Print This Out:**

```
PROJECT HUNTER - RUN COMMANDS

SETUP (Once):
  pip install -r requirements.txt
  [Install Chrome extension]

DATA COLLECTION (Once):
  Terminal 1: python api/discover_api.py
  Terminal 2: streamlit run dashboard.py
  Browser: Browse google.com/discover (60 min)
  Terminal 3: python scripts/run_discovery.py

MONITORING (Once, 24-48 hours):
  python scripts/run_monitor.py

ANALYSIS (Anytime):
  python scripts/generate_report.py

VIEW DATA (Anytime):
  streamlit run dashboard.py

THAT'S IT! No schedules needed.
```

---

**Bottom line: Set it up once, run monitoring for 48 hours, then you're done! All data is saved and you can view it anytime with the dashboard.** 🎯
