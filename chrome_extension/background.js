// Background service worker - handles API communication
const API_URL = 'http://localhost:8000';

// Listen for articles from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'NEW_DISCOVER_ARTICLE') {
    sendToAPI(message.data);
  }
});

// Send article to API
async function sendToAPI(data) {
  try {
    await fetch(`${API_URL}/api/discover/article`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    console.log('[API] Sent:', data.domain);
    updateBadge();
  } catch (err) {
    console.error('[API] Error:', err);
  }
}

// Update badge with API count
async function updateBadge() {
  try {
    const response = await fetch(`${API_URL}/api/discover/stats`);
    const data = await response.json();
    const count = data.total_domains || 0;

    chrome.action.setBadgeText({ text: count.toString() });
    chrome.action.setBadgeBackgroundColor({ color: '#10B981' });
  } catch {
    chrome.action.setBadgeText({ text: '!' });
    chrome.action.setBadgeBackgroundColor({ color: '#EF4444' });
  }
}

// Update badge on startup
updateBadge();

// Refresh badge every 5 seconds
setInterval(updateBadge, 5000);
