"""
RSS Feed Discovery

Auto-detects RSS/Atom feeds from competitor websites.
Validates feed health and registers them for monitoring.
"""

import requests
import feedparser
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.persistence.database import Database
from core.persistence.models import RSSFeed, generate_id


class RSSDiscovery:
    """Discovers and validates RSS/Atom feeds from competitor sites"""

    def __init__(self):
        self.db = Database()

        # Common RSS feed patterns
        self.common_paths = [
            '/feed/',
            '/rss/',
            '/feed.xml',
            '/rss.xml',
            '/atom.xml',
            '/index.xml',
            '/?feed=rss',
            '/?feed=rss2',
            '/?feed=atom',
        ]

    def discover_all_feeds(self) -> List[RSSFeed]:
        """
        Discover RSS feeds for all registered competitors

        Returns:
            List of discovered and validated RSS feeds
        """
        competitors = self.db.load_competitors()

        if not competitors:
            print("[RSS Discovery] No competitors found. Run competitor discovery first.")
            return []

        print(f"[RSS Discovery] Discovering feeds for {len(competitors)} competitors...")

        all_feeds = []

        for comp in competitors:
            site_id = comp['site_id']
            domain = comp['domain']
            url = comp['url']

            print(f"\n[RSS Discovery] Checking: {domain}")

            feeds = self._discover_feeds_for_site(url, site_id)

            if feeds:
                print(f"  ✓ Found {len(feeds)} feed(s)")
                all_feeds.extend(feeds)
                # Update competitor with feed URLs
                comp['rss_feeds'] = [f.feed_url for f in feeds]
            else:
                print(f"  ✗ No feeds found")

        # Save all discovered feeds
        if all_feeds:
            self.db.save_feeds(all_feeds)

            # Update competitors with feed info
            from core.persistence.models import CompetitorSite
            competitors_obj = [CompetitorSite(**c) for c in competitors]
            self.db.save_competitors(competitors_obj)

        print(f"\n[RSS Discovery] Complete! Discovered {len(all_feeds)} feeds total")
        return all_feeds

    def _discover_feeds_for_site(self, site_url: str, site_id: str) -> List[RSSFeed]:
        """
        Discover RSS feeds for a single site

        Strategy:
        1. Check HTML <link> tags for RSS/Atom feeds
        2. Try common feed paths
        3. Validate each found feed

        Returns:
            List of valid RSS feeds
        """
        discovered_feeds = []

        # Method 1: Parse HTML for feed links
        feeds_from_html = self._parse_html_for_feeds(site_url)

        # Method 2: Try common paths
        feeds_from_paths = self._try_common_paths(site_url)

        # Combine and deduplicate
        all_feed_urls = list(set(feeds_from_html + feeds_from_paths))

        # Validate each feed
        for feed_url in all_feed_urls:
            if self._validate_feed(feed_url):
                feed_type = "atom" if "atom" in feed_url.lower() else "rss"

                feed = RSSFeed(
                    feed_id=generate_id("feed"),
                    feed_url=feed_url,
                    site_id=site_id,
                    feed_type=feed_type,
                    status="active"
                )

                discovered_feeds.append(feed)

        return discovered_feeds

    def _parse_html_for_feeds(self, url: str) -> List[str]:
        """
        Parse HTML page for <link> tags pointing to RSS/Atom feeds

        Returns:
            List of feed URLs
        """
        try:
            response = requests.get(
                url,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )

            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            feeds = []

            # Look for <link rel="alternate" type="application/rss+xml">
            for link in soup.find_all('link', rel='alternate'):
                feed_type = link.get('type', '')
                href = link.get('href', '')

                if any(t in feed_type for t in ['rss', 'atom', 'xml']):
                    # Make absolute URL
                    feed_url = urljoin(url, href)
                    feeds.append(feed_url)

            return feeds

        except Exception as e:
            print(f"    Error parsing HTML: {e}")
            return []

    def _try_common_paths(self, url: str) -> List[str]:
        """
        Try common RSS feed path patterns

        Returns:
            List of valid feed URLs found
        """
        feeds = []

        for path in self.common_paths:
            feed_url = urljoin(url, path)

            try:
                response = requests.head(
                    feed_url,
                    timeout=5,
                    allow_redirects=True,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )

                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    if any(t in content_type for t in ['xml', 'rss', 'atom']):
                        feeds.append(feed_url)

            except:
                continue

        return feeds

    def _validate_feed(self, feed_url: str) -> bool:
        """
        Validate that a feed URL is valid and active

        Checks:
        1. Feed is parseable
        2. Has at least 1 entry
        3. Latest entry is recent (within 60 days)

        Returns:
            True if valid, False otherwise
        """
        try:
            # Fetch feed
            response = requests.get(
                feed_url,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0'}
            )

            if response.status_code != 200:
                return False

            # Parse with feedparser
            feed = feedparser.parse(response.content)

            # Check for errors
            if feed.bozo and not feed.entries:
                return False

            # Must have at least one entry
            if not feed.entries:
                print(f"    No entries in feed")
                return False

            # Check freshness - latest entry should be within 60 days
            latest_entry = feed.entries[0]
            if hasattr(latest_entry, 'published_parsed') and latest_entry.published_parsed:
                pub_date = datetime(*latest_entry.published_parsed[:6])
                days_old = (datetime.now() - pub_date).days

                if days_old > 60:
                    print(f"    Feed is stale (last post {days_old} days ago)")
                    return False

            print(f"    ✓ Valid feed with {len(feed.entries)} entries")
            return True

        except Exception as e:
            print(f"    Error validating feed: {e}")
            return False

    def get_feed_health_report(self) -> Dict:
        """
        Generate health report for all registered feeds

        Returns:
            Dictionary with feed health statistics
        """
        feeds = self.db.load_feeds()

        total = len(feeds)
        active = sum(1 for f in feeds if f.get('status') == 'active')
        error = sum(1 for f in feeds if f.get('status') == 'error')
        stale = sum(1 for f in feeds if f.get('status') == 'stale')
        dead = sum(1 for f in feeds if f.get('status') == 'dead')

        return {
            "total_feeds": total,
            "active": active,
            "error": error,
            "stale": stale,
            "dead": dead,
            "health_rate": f"{(active/total*100):.1f}%" if total > 0 else "0%"
        }


def main():
    """Run RSS feed discovery"""
    discovery = RSSDiscovery()
    feeds = discovery.discover_all_feeds()

    # Generate health report
    health = discovery.get_feed_health_report()

    print(f"\n{'='*60}")
    print(f"FEED DISCOVERY SUMMARY")
    print(f"{'='*60}")
    print(f"Total feeds discovered: {health['total_feeds']}")
    print(f"Active feeds: {health['active']}")
    print(f"Health rate: {health['health_rate']}")


if __name__ == "__main__":
    main()
