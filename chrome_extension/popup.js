// Show stats
chrome.storage.local.get(['totalDiscovered'], (result) => {
  document.getElementById('count').innerText = result.totalDiscovered || 0;
});

// Reset button
document.getElementById('reset').addEventListener('click', async () => {
  try {
    const response = await fetch('http://localhost:8000/api/discover/reset', { method: 'POST' });
    if (!response.ok) {
      console.error('[Reset] API returned', response.status);
    }
  } catch (err) {
    console.error('[Reset] API unreachable:', err);
  }
  chrome.storage.local.set({totalDiscovered: 0});
  chrome.action.setBadgeText({text: ''});
  document.getElementById('count').innerText = '0';
});
