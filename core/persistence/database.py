"""
Database layer for Project Hunter

Handles SQLite for articles and JSON for competitors/feeds.
Provides atomic writes, concurrent reads, and data integrity.
"""

import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from contextlib import contextmanager

from .models import (
    Article, ArticleDNA, CompetitorSite, RSSFeed,
    Pattern, NicheVelocity, generate_id
)


class Database:
    """Main database interface"""

    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "articles" / "articles.db"
        self.competitors_path = self.base_path / "competitors"
        self.intelligence_path = self.base_path / "intelligence"

        # Ensure directories exist
        self._init_directories()

        # Initialize SQLite database
        self._init_database()

    def _init_directories(self):
        """Create directory structure"""
        (self.base_path / "articles" / "dna_profiles").mkdir(parents=True, exist_ok=True)
        (self.base_path / "competitors").mkdir(parents=True, exist_ok=True)
        (self.base_path / "intelligence").mkdir(parents=True, exist_ok=True)
        (self.base_path / "logs").mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """Initialize SQLite schema with WAL mode for concurrent access"""
        with self.get_connection() as conn:
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")

            # Articles table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    article_id TEXT PRIMARY KEY,
                    feed_id TEXT NOT NULL,
                    site_id TEXT NOT NULL,
                    guid TEXT UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    published_date TEXT NOT NULL,
                    discovered_date TEXT NOT NULL,
                    niche TEXT,
                    dna_extracted INTEGER DEFAULT 0,
                    publish_hour INTEGER,
                    publish_day_of_week INTEGER,
                    social_velocity_score INTEGER DEFAULT 0,
                    reddit_mentions INTEGER DEFAULT 0,
                    x_mentions INTEGER DEFAULT 0,
                    last_updated TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # DNA profiles table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dna_profiles (
                    article_id TEXT PRIMARY KEY,
                    title TEXT,
                    title_length INTEGER,
                    title_has_number INTEGER,
                    title_has_question INTEGER,
                    title_has_superlative INTEGER,
                    title_pattern TEXT,
                    word_count INTEGER,
                    image_count INTEGER,
                    video_count INTEGER,
                    first_image_aspect_ratio TEXT,
                    first_image_format TEXT,
                    schema_types TEXT,
                    meta_description_length INTEGER,
                    h1_count INTEGER,
                    h2_count INTEGER,
                    h3_count INTEGER,
                    subheading_total INTEGER,
                    internal_links INTEGER,
                    external_links INTEGER,
                    page_speed_score INTEGER,
                    mobile_optimized INTEGER,
                    uses_webp INTEGER,
                    author TEXT,
                    category TEXT,
                    tags TEXT,
                    extracted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(article_id)
                )
            """)

            # Processing queue table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processing_queue (
                    article_id TEXT PRIMARY KEY,
                    status TEXT DEFAULT 'pending',
                    retry_count INTEGER DEFAULT 0,
                    last_error TEXT,
                    queued_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    processed_at TEXT,
                    FOREIGN KEY (article_id) REFERENCES articles(article_id)
                )
            """)

            # Indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_niche ON articles(niche)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_dna ON articles(dna_extracted)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_queue_status ON processing_queue(status)")

            conn.commit()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # ==================== ARTICLE OPERATIONS ====================

    def insert_article(self, article: Article) -> bool:
        """Insert new article (ignore if exists)"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO articles
                    (article_id, feed_id, site_id, guid, url, title, published_date,
                     discovered_date, niche, publish_hour, publish_day_of_week,
                     social_velocity_score, reddit_mentions, x_mentions, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article.article_id, article.feed_id, article.site_id,
                    article.guid, article.url, article.title,
                    article.published_date, article.discovered_date,
                    article.niche, article.publish_hour, article.publish_day_of_week,
                    article.social_velocity_score, article.reddit_mentions,
                    article.x_mentions, article.last_updated
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting article: {e}")
            return False

    def get_article_by_guid(self, guid: str) -> Optional[Dict]:
        """Check if article exists by GUID"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM articles WHERE guid = ?", (guid,)
            ).fetchone()
            return dict(row) if row else None

    def get_articles_by_niche(self, niche: str, limit: int = 100) -> List[Dict]:
        """Get recent articles for a niche"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM articles
                WHERE niche = ?
                ORDER BY published_date DESC
                LIMIT ?
            """, (niche, limit)).fetchall()
            return [dict(row) for row in rows]

    def get_articles_without_dna(self, limit: int = 50) -> List[Dict]:
        """Get articles pending DNA extraction"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM articles
                WHERE dna_extracted = 0
                ORDER BY discovered_date ASC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]

    def mark_dna_extracted(self, article_id: str):
        """Mark article as having DNA extracted"""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE articles SET dna_extracted = 1 WHERE article_id = ?",
                (article_id,)
            )
            conn.commit()

    # ==================== DNA OPERATIONS ====================

    def insert_dna_profile(self, article_id: str, dna: ArticleDNA) -> bool:
        """Insert DNA profile for an article"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO dna_profiles (
                        article_id, title, title_length, title_has_number,
                        title_has_question, title_has_superlative, title_pattern,
                        word_count, image_count, video_count,
                        first_image_aspect_ratio, first_image_format,
                        schema_types, meta_description_length,
                        h1_count, h2_count, h3_count, subheading_total,
                        internal_links, external_links, page_speed_score,
                        mobile_optimized, uses_webp, author, category, tags
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article_id, dna.title, dna.title_length,
                    int(dna.title_has_number), int(dna.title_has_question),
                    int(dna.title_has_superlative), dna.title_pattern,
                    dna.word_count, dna.image_count, dna.video_count,
                    dna.first_image_aspect_ratio, dna.first_image_format,
                    json.dumps(dna.schema_types), dna.meta_description_length,
                    dna.h1_count, dna.h2_count, dna.h3_count, dna.subheading_total,
                    dna.internal_links, dna.external_links, dna.page_speed_score,
                    int(dna.mobile_optimized), int(dna.uses_webp),
                    dna.author, dna.category, json.dumps(dna.tags)
                ))
                conn.commit()

                # Also save as JSON for detailed analysis
                self._save_dna_json(article_id, dna)
                return True
        except Exception as e:
            print(f"Error inserting DNA profile: {e}")
            return False

    def _save_dna_json(self, article_id: str, dna: ArticleDNA):
        """Save detailed DNA profile as JSON"""
        json_path = self.base_path / "articles" / "dna_profiles" / f"{article_id}.json"
        with open(json_path, 'w') as f:
            json.dump(dna.to_dict(), f, indent=2)

    def get_all_dna_profiles(self, niche: Optional[str] = None) -> List[Dict]:
        """Get all DNA profiles, optionally filtered by niche"""
        with self.get_connection() as conn:
            if niche:
                rows = conn.execute("""
                    SELECT d.* FROM dna_profiles d
                    JOIN articles a ON d.article_id = a.article_id
                    WHERE a.niche = ?
                """, (niche,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM dna_profiles").fetchall()

            return [dict(row) for row in rows]

    # ==================== QUEUE OPERATIONS ====================

    def add_to_queue(self, article_id: str):
        """Add article to processing queue"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO processing_queue (article_id, status)
                VALUES (?, 'pending')
            """, (article_id,))
            conn.commit()

    def get_pending_queue_items(self, limit: int = 10) -> List[str]:
        """Get pending article IDs from queue"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT article_id FROM processing_queue
                WHERE status = 'pending'
                ORDER BY queued_at ASC
                LIMIT ?
            """, (limit,)).fetchall()
            return [row['article_id'] for row in rows]

    def mark_queue_processed(self, article_id: str, success: bool = True, error: str = None):
        """Mark queue item as processed"""
        status = "completed" if success else "error"
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE processing_queue
                SET status = ?, processed_at = ?, last_error = ?, retry_count = retry_count + 1
                WHERE article_id = ?
            """, (status, datetime.now().isoformat(), error, article_id))
            conn.commit()

    # ==================== COMPETITORS & FEEDS (JSON) ====================

    def save_competitor(self, competitor: CompetitorSite):
        """Append a single competitor to JSON"""
        existing = self.load_competitors()
        existing.append(competitor.to_dict())
        path = self.competitors_path / "discovered_sites.json"
        with open(path, 'w') as f:
            json.dump(existing, f, indent=2)

    def save_competitors(self, competitors: List[CompetitorSite]):
        """Save discovered competitors to JSON"""
        path = self.competitors_path / "discovered_sites.json"
        data = [c.to_dict() for c in competitors]
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_competitors(self) -> List[Dict]:
        """Load competitors from JSON"""
        path = self.competitors_path / "discovered_sites.json"
        if not path.exists():
            return []
        with open(path, 'r') as f:
            return json.load(f)

    def save_feeds(self, feeds: List[RSSFeed]):
        """Save RSS feeds to JSON"""
        path = self.competitors_path / "rss_feeds.json"
        data = [f.to_dict() for f in feeds]
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_feeds(self) -> List[Dict]:
        """Load RSS feeds from JSON"""
        path = self.competitors_path / "rss_feeds.json"
        if not path.exists():
            return []
        with open(path, 'r') as f:
            return json.load(f)

    def update_feed_status(self, feed_id: str, last_guid: str = None, error: str = None):
        """Update feed last_guid and error status"""
        feeds = self.load_feeds()
        for feed in feeds:
            if feed['feed_id'] == feed_id:
                feed['last_fetched'] = datetime.now().isoformat()
                if last_guid:
                    feed['last_guid'] = last_guid
                    feed['error_count'] = 0
                if error:
                    feed['error_count'] = feed.get('error_count', 0) + 1
                    feed['last_error'] = error
                    # Update status based on error count
                    if feed['error_count'] >= 10:
                        feed['status'] = "dead"
                    elif feed['error_count'] >= 3:
                        feed['status'] = "error"
                break
        self.save_feeds([RSSFeed(**f) for f in feeds])

    # ==================== INTELLIGENCE (JSON) ====================

    def save_patterns(self, patterns: List[Pattern]):
        """Save discovered patterns"""
        path = self.intelligence_path / "patterns.json"
        data = [p.to_dict() for p in patterns]
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def save_niche_scores(self, scores: List[NicheVelocity]):
        """Save niche velocity scores"""
        path = self.intelligence_path / "niche_scores.json"
        data = [s.to_dict() for s in scores]
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def save_title_formulas(self, formulas: List[Dict]):
        """Save title formulas"""
        path = self.intelligence_path / "title_formulas.json"
        with open(path, 'w') as f:
            json.dump(formulas, f, indent=2)

    # ==================== STATS ====================

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_connection() as conn:
            total_articles = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
            articles_with_dna = conn.execute(
                "SELECT COUNT(*) FROM articles WHERE dna_extracted = 1"
            ).fetchone()[0]
            pending_queue = conn.execute(
                "SELECT COUNT(*) FROM processing_queue WHERE status = 'pending'"
            ).fetchone()[0]

            articles_by_niche = {}
            rows = conn.execute("""
                SELECT niche, COUNT(*) as count
                FROM articles
                GROUP BY niche
            """).fetchall()
            for row in rows:
                articles_by_niche[row['niche']] = row['count']

        competitors = len(self.load_competitors())
        feeds = len(self.load_feeds())

        return {
            "total_articles": total_articles,
            "articles_with_dna": articles_with_dna,
            "pending_dna_extraction": total_articles - articles_with_dna,
            "pending_queue": pending_queue,
            "competitors_discovered": competitors,
            "rss_feeds_registered": feeds,
            "articles_by_niche": articles_by_niche
        }
