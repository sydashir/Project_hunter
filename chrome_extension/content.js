// Passive observer - no automation, just watches DOM
let discoveredDomains = new Set();
let articlePosition = 0;

// Observer watches for Discover articles
const observer = new MutationObserver(() => {
  // Multiple selectors for Discover cards
  const selectors = [
    '[data-test-id="discover-card"]',
    '[role="article"]',
    'article a[href*="http"]',
    '[data-hveid] a[href]'
  ];

  selectors.forEach(selector => {
    document.querySelectorAll(selector).forEach(element => {
      const link = element.querySelector('a') || element;
      const url = link.href;

      if (!url || !url.startsWith('http')) return;

      // Extract domain
      const domain = new URL(url).hostname;

      // Skip Google/social domains
      const excluded = ['google.com', 'youtube.com', 'facebook.com', 'twitter.com', 'instagram.com'];
      if (excluded.some(ex => domain.includes(ex))) return;

      // New domain found!
      if (!discoveredDomains.has(domain)) {
        discoveredDomains.add(domain);

        const articleData = {
          domain: domain,
          url: url,
          title: element.querySelector('h3, h2')?.innerText || '',
          position: articlePosition++,
          timestamp: new Date().toISOString()
        };

        // Send to background script
        chrome.runtime.sendMessage({
          type: 'NEW_DISCOVER_ARTICLE',
          data: articleData
        });

        console.log('[Discover Tracker] Found:', domain);
      }
    });
  });
});

// Start observing when on Google Discover
if (window.location.href.includes('google.com')) {
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
  console.log('[Discover Tracker] Monitoring active');
}
