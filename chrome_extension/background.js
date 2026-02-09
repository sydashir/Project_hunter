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
    const response = await fetch(`${API_URL}/api/discover/article`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      console.error('[API] Bad response:', response.status);
      return;
    }
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
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    const count = data.total_domains || 0;

    chrome.action.setBadgeText({ text: count.toString() });
    chrome.action.setBadgeBackgroundColor({ color: '#10B981' });

    // Persist count so popup.js can read it
    chrome.storage.local.set({ totalDiscovered: count });
  } catch {
    chrome.action.setBadgeText({ text: '!' });
    chrome.action.setBadgeBackgroundColor({ color: '#EF4444' });
  }
}

// Update badge on startup
updateBadge();

// Refresh badge every 5 seconds
setInterval(updateBadge, 5000);
