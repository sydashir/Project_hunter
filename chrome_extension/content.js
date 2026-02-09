// Fast Discover Article Tracker - Optimized for speed
let discoveredDomains = new Set();
let articleCount = 0;

// Excluded domains (Google, social, etc.)
const EXCLUDED = [
  'google.com', 'google.co', 'gstatic.com', 'googleapis.com',
  'youtube.com', 'youtu.be', 'facebook.com', 'fb.com',
  'twitter.com', 'x.com', 'instagram.com', 'tiktok.com',
  'reddit.com', 'linkedin.com', 'pinterest.com',
  'apple.com', 'apps.apple.com', 'play.google.com',
  'wikipedia.org', 'spotify.com', 'amazon.com'
];

function isExcluded(domain) {
  return EXCLUDED.some(ex => domain.includes(ex));
}

function extractDomain(url) {
  try {
    return new URL(url).hostname;
  } catch {
    return null;
  }
}

function processLink(link) {
  if (!link.href || !link.href.startsWith('http')) return;

  const domain = extractDomain(link.href);
  if (!domain || isExcluded(domain) || discoveredDomains.has(domain)) return;

  discoveredDomains.add(domain);
  articleCount++;

  // Get title from nearby text
  const title = link.innerText?.trim().substring(0, 150) ||
                link.querySelector('span, div, h3, h2')?.innerText?.trim().substring(0, 150) || '';

  const data = {
    domain: domain,
    url: link.href,
    title: title,
    position: articleCount,
    timestamp: new Date().toISOString()
  };

  // Send immediately
  chrome.runtime.sendMessage({ type: 'NEW_DISCOVER_ARTICLE', data: data });
  console.log(`[Discover] #${articleCount}: ${domain}`);
}

function scanPage() {
  // Method 1: Images with dimg_ prefix (mobile Discover)
  document.querySelectorAll('img[id^="dimg_"]').forEach(img => {
    const link = img.closest('a');
    if (link) processLink(link);
  });

  // Method 2: All external article links
  document.querySelectorAll('a[href^="http"]').forEach(link => {
    // Skip Google internal links
    if (link.href.includes('google.com/search') ||
        link.href.includes('google.com/url') ||
        link.href.includes('accounts.google')) return;

    // Must have image or substantial content
    const hasImage = link.querySelector('img');
    const hasText = link.innerText?.length > 15;

    if (hasImage || hasText) {
      processLink(link);
    }
  });

  // Method 3: Data attribute cards
  document.querySelectorAll('[data-hveid] a[href^="http"], [jsname] a[href^="http"]').forEach(el => {
    const link = el.tagName === 'A' ? el : el.querySelector('a');
    if (link) processLink(link);
  });
}

// Run on Google pages
if (window.location.hostname.includes('google.com')) {
  console.log('[Discover Tracker] Active on:', window.location.href);

  // Initial scans
  setTimeout(scanPage, 500);
  setTimeout(scanPage, 1500);
  setTimeout(scanPage, 3000);

  // Watch for DOM changes (infinite scroll)
  const observer = new MutationObserver(() => scanPage());
  observer.observe(document.body, { childList: true, subtree: true });

  // Scan on scroll (throttled to 200ms)
  let scrollTimeout;
  window.addEventListener('scroll', () => {
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(scanPage, 200);
  }, { passive: true });

  // Periodic scan every 2 seconds
  setInterval(scanPage, 2000);
}
