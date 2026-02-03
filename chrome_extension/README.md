# Google Discover Competitor Tracker - Chrome Extension

This Chrome extension passively captures articles you see in your Google Discover feed to help identify competitors that are already successful in Google Discover.

## Features

- **Passive Monitoring**: No automation, just observes what you naturally see
- **Zero Ban Risk**: Uses normal browsing behavior, no ToS violation
- **Real-time Capture**: Extracts domains as you scroll through Discover
- **Badge Counter**: Shows how many domains discovered in extension icon
- **Local API Integration**: Sends data to local FastAPI server for processing

## Installation

1. **Install the extension in Chrome**:
   ```
   - Open Chrome
   - Go to chrome://extensions/
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select the chrome_extension/ folder
   ```

2. **Start the API server**:
   ```bash
   python api/discover_api.py
   ```

   The API will start on http://localhost:8000

3. **Browse Google Discover**:
   ```
   - Open Chrome
   - Go to google.com or google.com/discover
   - Scroll through your Discover feed naturally
   - Extension will automatically capture article domains
   - Watch the badge counter on the extension icon increase
   ```

## How It Works

### Content Script (content.js)
- Runs on Google.com pages
- Uses MutationObserver to watch for new Discover articles
- Extracts domain, URL, title, and position
- Sends to background script

### Background Script (background.js)
- Receives data from content script
- Sends to local API server at http://localhost:8000
- Updates badge counter

### Popup (popup.html)
- Shows total domains discovered
- Provides reset button

## Data Flow

```
Google Discover Page
    ↓ (DOM observation)
Content Script
    ↓ (chrome.runtime.sendMessage)
Background Script
    ↓ (HTTP POST)
Local API Server (http://localhost:8000/api/discover/article)
    ↓ (saves to database)
Database (data/competitors.json)
```

## Usage Tips

1. **Leave it running**: Browse Discover normally while working, extension runs passively
2. **Scroll regularly**: More scrolling = more domains discovered
3. **Target 100+ domains**: Aim for 100-200 domains before running discovery script
4. **Check progress**: Click extension icon to see current count

## Legal & Privacy

- ✅ **100% Legal**: You're capturing your own browsing data
- ✅ **No ToS violation**: Uses normal browsing behavior, no automation
- ✅ **Zero ban risk**: Just observing DOM like browser dev tools
- ✅ **Privacy-friendly**: Data stays on your local machine

## Troubleshooting

### Extension not capturing domains
- Make sure you're on google.com (not google.com/search)
- Check browser console (F12) for "[Discover Tracker]" messages
- Verify API server is running on localhost:8000

### API server not receiving data
- Check if API server is running: http://localhost:8000/docs
- Look for CORS errors in browser console
- Verify fetch URL in background.js matches API server address

### Badge not updating
- Click extension icon to see if counter is incrementing
- Check background script console for errors (chrome://extensions/ → Details → Inspect views: background page)

## Icon Note

The extension uses a placeholder SVG icon. For production, replace `icon.png` with a proper 128x128 PNG icon.

## Next Steps

After collecting 100+ domains:

1. **Load discovered competitors**:
   ```bash
   python scripts/run_discovery.py
   ```

2. **Find RSS feeds**:
   ```bash
   python scripts/run_monitor.py --cycles 1
   ```

3. **Start monitoring**:
   ```bash
   python scripts/run_monitor.py --cycles 5
   ```
