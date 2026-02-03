# Project Hunter - Dashboard Guide

**Real-time visualization of competitor discovery and intelligence analysis**

---

## What is the Dashboard?

A **Streamlit-powered web dashboard** that provides:

- 📊 **Real-time monitoring** of domain capture
- 🔍 **Competitor browser** with filtering and sorting
- 📈 **Intelligence visualization** (niche scores, patterns, formulas)
- ⚙️ **System status** and configuration

---

## Quick Start

### 1. Install Dependencies

```bash
pip install streamlit plotly
```

(Or run: `pip install -r requirements.txt`)

### 2. Start the Dashboard

```bash
streamlit run dashboard.py
```

**The dashboard will open in your browser automatically!**

Default URL: `http://localhost:8501`

---

## Dashboard Features

### 📊 Overview Page

**What you see:**
- **Top Metrics**
  - Domains captured (from extension)
  - Competitors stored
  - Articles monitored
  - Niches discovered

- **Real-time Domain Capture**
  - Bar chart of recently captured domains
  - Live count from extension
  - Progress to target (150 domains)

- **Competitor Overview**
  - Pie chart by niche
  - Bar chart by discovery source

- **Article Timeline**
  - Line chart showing articles over time

**Best for:** Quick system health check

---

### 🔍 Competitor Discovery Page

**What you see:**
- **Filters**
  - By niche (multi-select)
  - By discovery source
  - By minimum authority score

- **Sortable Table**
  - Domain, niche, authority score
  - Discover position
  - RSS feed count
  - Sample article title

- **Top 10 Performers**
  - Horizontal bar chart
  - Metrics for each competitor

- **Export**
  - Download as CSV

**Best for:** Exploring discovered competitors

---

### 📈 Intelligence Analysis Page

**What you see:**
- **Niche Performance**
  - Winning niche with score
  - Bar chart of all niche scores
  - Scatter plot: articles vs velocity

- **Structural Blueprint**
  - Word count (optimal range)
  - Image count
  - Schema usage percentage
  - HTML structure

- **Title Formulas**
  - Top 5 formulas with examples
  - Success rate and frequency
  - Expandable cards

- **Timing Strategy**
  - Best publishing times
  - Best days of week
  - Days to avoid

**Best for:** Understanding winning patterns

---

### ⚙️ Settings Page

**What you see:**
- **API Configuration**
  - Connection test
  - Host and port settings

- **Database Status**
  - File listing
  - Size information

- **Chrome Extension**
  - Installation instructions
  - File verification

- **Data Management**
  - Reload data
  - Clear cache
  - Export (coming soon)

**Best for:** System configuration and troubleshooting

---

## Usage Workflow

### Scenario 1: Active Browsing

**You're browsing Google Discover right now:**

1. **Start API server:**
   ```bash
   python api/discover_api.py
   ```

2. **Start dashboard:**
   ```bash
   streamlit run dashboard.py
   ```

3. **Browse Discover** (keep both running)

4. **Watch Overview page:**
   - See domains appear in real-time
   - Progress bar fills up
   - Charts update automatically

**Auto-refresh:** Dashboard updates every 5-10 seconds

---

### Scenario 2: After Data Collection

**You've collected 100+ competitors:**

1. **Start dashboard:**
   ```bash
   streamlit run dashboard.py
   ```

2. **Go to Competitor Discovery:**
   - Browse all competitors
   - Filter by niche
   - Export to CSV

3. **Check Intelligence Analysis:**
   - View niche scores
   - Review winning patterns
   - Read title formulas

---

### Scenario 3: Monitoring Progress

**You're running 24-hour monitoring:**

1. **Start monitoring:**
   ```bash
   python scripts/run_monitor.py
   ```

2. **Start dashboard:**
   ```bash
   streamlit run dashboard.py
   ```

3. **Keep Overview page open:**
   - Watch article count grow
   - See timeline update
   - Monitor system status

---

## Dashboard Screenshots (What You'll See)

### Overview Page
```
┌─────────────────────────────────────────────────────┐
│  🎯 Project Hunter Dashboard                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [127]          [127]         [487]         [6]    │
│  Domains      Competitors    Articles     Niches   │
│  Captured       Stored      Monitored   Discovered │
│                                                     │
├─────────────────────────────────────────────────────┤
│  📡 Real-Time Domain Capture                        │
│  ┌───────────────────────────────────────────────┐ │
│  │ [Bar chart showing recent domains]            │ │
│  │ techcrunch.com, forbes.com, wired.com...      │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
├─────────────────────────────────────────────────────┤
│  🏆 Competitor Overview                             │
│  ┌──────────────┐  ┌──────────────┐               │
│  │ [Pie chart]  │  │ [Bar chart]  │               │
│  │ By Niche     │  │ By Source    │               │
│  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────┘
```

### Competitor Discovery Page
```
┌─────────────────────────────────────────────────────┐
│  🔍 Competitor Discovery                            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Filter: [Technology] [Business] [Health]          │
│  Source: [chrome_extension] [crawler]              │
│  Min Score: [──────●─────] 50                      │
│                                                     │
├─────────────────────────────────────────────────────┤
│  📋 Competitors (127)                               │
│  ┌─────────────────────────────────────────────┐   │
│  │ Domain          Niche      Score  Position  │   │
│  │ techcrunch.com  technology  100     0       │   │
│  │ theverge.com    technology   99     1       │   │
│  │ forbes.com      business     97     3       │   │
│  │ ...                                         │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  [📥 Download as CSV]                               │
└─────────────────────────────────────────────────────┘
```

### Intelligence Analysis Page
```
┌─────────────────────────────────────────────────────┐
│  📈 Intelligence Analysis                           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  🏆 Winning Niche     📰 Total Articles  ⚡ Velocity│
│  TECHNOLOGY           487                8.3/day   │
│  Score: 92/100        178 in winner     Winner     │
│                                                     │
├─────────────────────────────────────────────────────┤
│  🔥 Niche Performance                               │
│  ┌──────────────┐  ┌──────────────┐               │
│  │ [Bar chart]  │  │ [Scatter]    │               │
│  │ Scores       │  │ Art vs Vel   │               │
│  └──────────────┘  └──────────────┘               │
│                                                     │
├─────────────────────────────────────────────────────┤
│  📐 Structural Blueprint                            │
│  [900-1100]  [4]      [95%]     [H1→H2→H3]        │
│  Word Count  Images  Schema    Structure          │
│                                                     │
├─────────────────────────────────────────────────────┤
│  💡 Title Formulas                                  │
│  ▼ Formula 1: [Number] + [Topic] + "That" + ...   │
│  ▼ Formula 2: "How" + [Subject] + [Action] + ...  │
│  ▼ Formula 3: [Superlative] + [Topic] + ...       │
└─────────────────────────────────────────────────────┘
```

---

## Real-Time Features

### Auto-Refresh
- **API stats**: Every 5 seconds
- **Competitor data**: Every 10 seconds
- **Article data**: Every 10 seconds

### Manual Refresh
- Click "🔄 Refresh Data" in sidebar
- Or press `R` in browser

### Live Status Indicators
- 🟢 **Green** = API server online
- 🟡 **Yellow** = API server offline
- 🔴 **Red** = API server error

---

## Customization

### Change Refresh Rate

Edit `dashboard.py`:

```python
@st.cache_data(ttl=5)  # Change 5 to desired seconds
def get_api_stats():
    ...
```

### Change Dashboard Port

```bash
streamlit run dashboard.py --server.port 8502
```

### Disable Auto-Refresh

```bash
streamlit run dashboard.py --server.runOnSave false
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `R` | Refresh dashboard |
| `C` | Clear cache |
| `/` | Focus search (in tables) |
| `?` | Show help |

---

## Troubleshooting

### Dashboard won't start

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Fix:**
```bash
pip install streamlit plotly
```

---

### No data showing

**Error:** "No competitors discovered yet"

**Possible causes:**
1. Haven't browsed Discover yet
2. Haven't run discovery script
3. API server not running

**Fix:**
1. Start API: `python api/discover_api.py`
2. Browse Discover with extension
3. Run: `python scripts/run_discovery.py`
4. Refresh dashboard

---

### API status shows offline

**Error:** "⚠ API Server Offline" in sidebar

**Fix:**
```bash
python api/discover_api.py
```

Keep this running in a separate terminal.

---

### Charts not loading

**Error:** Blank charts or loading spinners

**Fix:**
1. Check if data files exist: `ls data/`
2. Reload data: Click "🔄 Reload All Data" in Settings
3. Clear browser cache: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)

---

## Performance Tips

### For Large Datasets (1000+ articles)

**Limit query results:**

Edit `dashboard.py`:

```python
query = "SELECT * FROM articles ORDER BY publish_date DESC LIMIT 1000"
# Change 1000 to lower number for faster loading
```

### Reduce Refresh Rate

```python
@st.cache_data(ttl=30)  # Refresh every 30 seconds instead of 5
```

### Disable Real-Time Mode

Comment out auto-refresh in sidebar:

```python
# st.markdown("---")
# if st.button("🔄 Refresh Data"):
#     st.rerun()
```

---

## Integration with Other Tools

### Export Data from Dashboard

**CSV Export:**
1. Go to Competitor Discovery page
2. Filter competitors as needed
3. Click "📥 Download as CSV"

**Use exported CSV:**
```python
import pandas as pd

df = pd.read_csv('competitors_20240203.csv')
print(df.head())
```

### API Integration

**Get real-time stats programmatically:**

```python
import requests

response = requests.get('http://localhost:8000/api/discover/stats')
stats = response.json()
print(f"Total domains: {stats['total_domains']}")
```

---

## Advanced Features (Coming Soon)

- 🔔 **Alerts** - Notify when target reached
- 📊 **Custom Charts** - Build your own visualizations
- 📤 **Auto-Export** - Schedule CSV exports
- 🔐 **Authentication** - Password-protect dashboard
- 📱 **Mobile View** - Responsive design

---

## FAQ

### Q: Can I run dashboard on a different port?
**A:** Yes: `streamlit run dashboard.py --server.port 8502`

### Q: Can I access dashboard from another computer?
**A:** Yes: `streamlit run dashboard.py --server.address 0.0.0.0`
Then visit: `http://YOUR_IP:8501`

### Q: Does dashboard use a lot of resources?
**A:** No, very lightweight:
- Memory: ~100MB
- CPU: <5% (when idle)
- Network: Minimal (only API calls)

### Q: Can I keep dashboard running 24/7?
**A:** Yes! It's designed for continuous monitoring.
Use `screen` or `tmux` to keep it running in background.

### Q: Will dashboard work without API server?
**A:** Partially. You'll see stored data but no real-time capture.

---

## Comparison: Dashboard vs Terminal

| Feature | Terminal | Dashboard |
|---------|----------|-----------|
| **Real-time** | ✓ Logs | ✓ Charts + Logs |
| **Visual** | ✗ Text only | ✓ Charts + Graphs |
| **Filtering** | ✗ Manual | ✓ Interactive |
| **Export** | ✗ Copy/paste | ✓ CSV download |
| **Mobile** | ✗ | ✓ (responsive) |
| **Ease of use** | Technical | User-friendly |

**Recommendation:** Use BOTH
- Terminal for running scripts
- Dashboard for monitoring and analysis

---

## Quick Commands

**Start everything:**
```bash
# Terminal 1: API server
python api/discover_api.py

# Terminal 2: Dashboard
streamlit run dashboard.py

# Terminal 3: Monitoring (optional)
python scripts/run_monitor.py
```

**Stop everything:**
```bash
# Press Ctrl+C in each terminal
# Or close terminal windows
```

---

## Summary

The dashboard provides:
- ✅ Real-time visualization
- ✅ Interactive exploration
- ✅ Easy data export
- ✅ Professional presentation
- ✅ No coding required (after setup)

**Perfect for:**
- Monitoring during browsing
- Presenting results to stakeholders
- Quick data exploration
- System health checks

**Run with:**
```bash
streamlit run dashboard.py
```

Then open browser at: `http://localhost:8501`

---

**Enjoy your real-time intelligence dashboard!** 🎯📊
