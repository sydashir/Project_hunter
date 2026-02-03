// Listen for articles from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'NEW_DISCOVER_ARTICLE') {
    // Send to local API server
    fetch('http://localhost:8000/api/discover/article', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(message.data)
    })
    .then(response => response.json())
    .then(data => {
      console.log('[Discover Tracker] Sent to API:', message.data.domain);

      // Update badge with count
      chrome.storage.local.get(['totalDiscovered'], (result) => {
        const count = (result.totalDiscovered || 0) + 1;
        chrome.storage.local.set({totalDiscovered: count});
        chrome.action.setBadgeText({text: count.toString()});
        chrome.action.setBadgeBackgroundColor({color: '#4CAF50'});
      });
    })
    .catch(err => console.error('[Discover Tracker] API error:', err));
  }
});
