"""
RSS Monitoring Engine

Real-time RSS feed monitoring with 60-second polling cycle.
Detects new articles by GUID comparison and queues for DNA extraction.
"""

import asyncio
import aiohttp
import feedparser
from typing import List, Dict, Set, Optional
from datetime import datetime
from collections import defaultdict
import time

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.persistence.database import Database
from core.persistence.models import Article, generate_id, parse_datetime


class RSSMonitor:
    """
    Monitors RSS feeds in 60-second cycles

    Features:
    - Async parallel fetching (batches of 20)
    - GUID-based new article detection
    - Automatic feed health tracking
    - Error handling and retry logic
    """

    def __init__(self, batch_size: int = 20, cycle_interval: int = 60):
        self.db = Database()
        self.batch_size = batch_size
        self.cycle_interval = cycle_interval

        # Tracking
        self.total_articles_detected = 0
        self.cycle_count = 0
        self.errors_by_feed = defaultdict(int)

        # Logging
        self.log_path = Path("data/logs")
        self.log_path.mkdir(parents=True, exist_ok=True)

    async def run_monitoring_loop(self, max_cycles: Optional[int] = None):
        """
        Main monitoring loop - runs indefinitely or for max_cycles

        Args:
            max_cycles: If set, stops after N cycles (for testing)
        """
        print(f"[RSS Monitor] Starting monitoring loop")
        print(f"[RSS Monitor] Cycle interval: {self.cycle_interval}s, Batch size: {self.batch_size}")

        while True:
            cycle_start = time.time()
            self.cycle_count += 1

            print(f"\n{'='*70}")
            print(f"CYCLE #{self.cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}")

            # Monitor all feeds
            new_articles = await self.monitor_all_feeds()

            # Stats
            cycle_duration = time.time() - cycle_start
            print(f"\n[Cycle #{self.cycle_count}] Complete in {cycle_duration:.1f}s")
            print(f"  New articles detected: {len(new_articles)}")
            print(f"  Total articles (session): {self.total_articles_detected}")

            # Check if we should stop
            if max_cycles and self.cycle_count >= max_cycles:
                print(f"\n[RSS Monitor] Reached max cycles ({max_cycles}). Stopping.")
                break

            # Wait for next cycle
            sleep_time = max(0, self.cycle_interval - cycle_duration)
            if sleep_time > 0:
                print(f"  Sleeping for {sleep_time:.1f}s until next cycle...")
                await asyncio.sleep(sleep_time)

    async def monitor_all_feeds(self) -> List[Article]:
        """
        Monitor all registered RSS feeds in parallel batches

        Returns:
            List of newly detected articles
        """
        # Load active feeds
        feeds = self.db.load_feeds()
        active_feeds = [f for f in feeds if f.get('status') in ['active', 'error']]

        if not active_feeds:
            print("[RSS Monitor] No active feeds found!")
            return []

        print(f"[RSS Monitor] Monitoring {len(active_feeds)} feeds...")

        all_new_articles = []

        # Process in batches
        for i in range(0, len(active_feeds), self.batch_size):
            batch = active_feeds[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(active_feeds) + self.batch_size - 1) // self.batch_size

            print(f"\n  Batch {batch_num}/{total_batches} ({len(batch)} feeds)")

            # Fetch batch in parallel
            results = await asyncio.gather(
                *[self.fetch_feed(feed) for feed in batch],
                return_exceptions=True
            )

            # Process results
            for feed, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"    ✗ {feed['feed_url'][:50]}: {result}")
                    self.db.update_feed_status(feed['feed_id'], error=str(result))
                elif result:
                    new_articles = result
                    all_new_articles.extend(new_articles)
                    print(f"    ✓ {feed['feed_url'][:50]}: {len(new_articles)} new")
                    # Update feed status with last GUID
                    if new_articles:
                        self.db.update_feed_status(feed['feed_id'], last_guid=new_articles[0].guid)
                else:
                    # No new articles
                    print(f"    - {feed['feed_url'][:50]}: 0 new")
                    self.db.update_feed_status(feed['feed_id'])

            # Small delay between batches
            if i + self.batch_size < len(active_feeds):
                await asyncio.sleep(2)

        self.total_articles_detected += len(all_new_articles)
        return all_new_articles

    async def fetch_feed(self, feed: Dict) -> List[Article]:
        """
        Fetch and parse a single RSS feed, detect new articles

        Args:
            feed: Feed dictionary with feed_url, feed_id, site_id, last_guid

        Returns:
            List of new Article objects
        """
        feed_url = feed['feed_url']
        feed_id = feed['feed_id']
        site_id = feed['site_id']
        last_seen_guid = feed.get('last_guid')

        try:
            # Fetch feed with timeout
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    feed_url,
                    timeout=aiohttp.ClientTimeout(total=10),
                    headers={'User-Agent': 'Mozilla/5.0 (compatible; ProjectHunter/1.0)'}
                ) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")

                    content = await response.read()

            # Parse feed
            parsed_feed = feedparser.parse(content)

            if parsed_feed.bozo and not parsed_feed.entries:
                raise Exception(f"Feed parse error: {parsed_feed.bozo_exception}")

            # Detect new articles
            new_articles = []
            entries = parsed_feed.entries

            for entry in entries:
                # Get GUID (unique identifier)
                guid = entry.get('id') or entry.get('link') or entry.get('guid')

                if not guid:
                    continue  # Skip if no ID

                # Stop when we hit the last seen GUID
                if guid == last_seen_guid:
                    break

                # Check if we've already seen this article
                if self.db.get_article_by_guid(guid):
                    continue  # Already in database

                # Extract article data
                title = entry.get('title', 'Untitled')
                url = entry.get('link', '')
                published = entry.get('published_parsed') or entry.get('updated_parsed')

                if published:
                    published_date = datetime(*published[:6]).isoformat()
                else:
                    published_date = datetime.now().isoformat()

                # Parse publish time components
                pub_dt = datetime.fromisoformat(published_date)
                publish_hour = pub_dt.hour
                publish_day_of_week = pub_dt.weekday()

                # Create Article object
                article = Article(
                    article_id=generate_id("article"),
                    feed_id=feed_id,
                    site_id=site_id,
                    guid=guid,
                    url=url,
                    title=title,
                    published_date=published_date,
                    publish_hour=publish_hour,
                    publish_day_of_week=publish_day_of_week
                )

                # Insert into database
                if self.db.insert_article(article):
                    # Add to DNA extraction queue
                    self.db.add_to_queue(article.article_id)
                    new_articles.append(article)

                    # Log the detection
                    self._log_article_detection(article)

            return new_articles

        except asyncio.TimeoutError:
            raise Exception("Timeout")
        except Exception as e:
            raise Exception(str(e))

    def _log_article_detection(self, article: Article):
        """Log article detection to file"""
        log_file = self.log_path / "monitoring.log"

        with open(log_file, 'a') as f:
            log_entry = f"[{datetime.now().isoformat()}] NEW: {article.title[:60]} | {article.url}\n"
            f.write(log_entry)

    def get_monitoring_stats(self) -> Dict:
        """Get monitoring statistics"""
        db_stats = self.db.get_stats()

        return {
            "cycle_count": self.cycle_count,
            "total_articles_detected": self.total_articles_detected,
            "database_stats": db_stats,
            "feed_health": self._get_feed_health()
        }

    def _get_feed_health(self) -> Dict:
        """Get feed health statistics"""
        feeds = self.db.load_feeds()

        total = len(feeds)
        if total == 0:
            return {"total": 0, "active": 0, "error": 0, "stale": 0, "dead": 0}

        by_status = defaultdict(int)
        for feed in feeds:
            status = feed.get('status', 'unknown')
            by_status[status] += 1

        return {
            "total": total,
            "active": by_status.get('active', 0),
            "error": by_status.get('error', 0),
            "stale": by_status.get('stale', 0),
            "dead": by_status.get('dead', 0)
        }


async def main():
    """Run RSS monitoring loop"""
    monitor = RSSMonitor()

    # Run for 5 cycles (for testing)
    # Remove max_cycles parameter for infinite monitoring
    await monitor.run_monitoring_loop(max_cycles=5)

    # Print final stats
    stats = monitor.get_monitoring_stats()

    print(f"\n{'='*70}")
    print(f"MONITORING SESSION SUMMARY")
    print(f"{'='*70}")
    print(f"Cycles completed: {stats['cycle_count']}")
    print(f"Articles detected: {stats['total_articles_detected']}")
    print(f"\nDatabase stats:")
    for key, value in stats['database_stats'].items():
        print(f"  {key}: {value}")
    print(f"\nFeed health:")
    for key, value in stats['feed_health'].items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
