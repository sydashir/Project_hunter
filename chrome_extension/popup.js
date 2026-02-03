// Show stats
chrome.storage.local.get(['totalDiscovered'], (result) => {
  document.getElementById('count').innerText = result.totalDiscovered || 0;
});

// Reset button
document.getElementById('reset').addEventListener('click', () => {
  chrome.storage.local.set({totalDiscovered: 0});
  chrome.action.setBadgeText({text: ''});
  document.getElementById('count').innerText = '0';
});
