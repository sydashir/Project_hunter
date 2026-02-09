"""
Data models for Project Hunter

Defines the structure for competitors, RSS feeds, articles, and DNA profiles.
"""

from dataclasses import dataclass, field, asdict, fields
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class FeedStatus(Enum):
    """RSS feed health status"""
    ACTIVE = "active"
    STALE = "stale"
    ERROR = "error"
    DEAD = "dead"


class SiteStatus(Enum):
    """Competitor site status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


@dataclass
class CompetitorSite:
    """Represents a discovered competitor website"""
    site_id: str
    domain: str
    url: str
    niche: str
    sub_niches: List[str] = field(default_factory=list)
    discovery_source: str = "seed"  # "seed", "crawler", or "chrome_extension"
    discovered_from: Optional[str] = None  # parent URL
    discovery_date: str = field(default_factory=lambda: datetime.now().isoformat())
    authority_score: float = 0.0  # 0-100
    rss_feeds: List[str] = field(default_factory=list)
    last_crawled: Optional[str] = None
    crawl_depth: int = 0
    status: str = SiteStatus.ACTIVE.value
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CompetitorSite':
        """Create CompetitorSite from dictionary"""
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class RSSFeed:
    """Represents an RSS/Atom feed"""
    feed_id: str
    feed_url: str
    site_id: str
    feed_type: str = "rss"  # "rss" or "atom"
    discovered_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_fetched: Optional[str] = None
    fetch_interval: int = 60  # seconds
    status: str = FeedStatus.ACTIVE.value
    last_guid: Optional[str] = None  # Last seen article GUID
    error_count: int = 0
    last_error: Optional[str] = None
    health_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RSSFeed':
        """Create RSSFeed from dictionary"""
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class ArticleDNA:
    """DNA profile of an article - structural and content patterns"""
    # Required fields first (no defaults)
    title: str
    title_length: int
    title_has_number: bool
    title_has_question: bool
    title_has_superlative: bool
    word_count: int
    image_count: int

    # Optional fields with defaults
    title_pattern: Optional[str] = None
    video_count: int = 0
    first_image_aspect_ratio: Optional[str] = None
    first_image_format: Optional[str] = None

    # Schema and meta
    schema_types: List[str] = field(default_factory=list)
    meta_description_length: int = 0
    meta_keywords_count: int = 0

    # HTML structure
    h1_count: int = 0
    h2_count: int = 0
    h3_count: int = 0
    subheading_total: int = 0
    internal_links: int = 0
    external_links: int = 0

    # Performance
    page_speed_score: Optional[int] = None
    mobile_optimized: bool = False
    uses_webp: bool = False

    # Additional metadata
    author: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Article:
    """Represents a detected article from RSS feed"""
    article_id: str
    feed_id: str
    site_id: str
    guid: str
    url: str
    title: str
    published_date: str
    discovered_date: str = field(default_factory=lambda: datetime.now().isoformat())
    niche: str = ""

    # DNA extraction status
    dna_extracted: bool = False
    dna_profile: Optional[Dict] = None

    # Publish timing
    publish_hour: Optional[int] = None  # 0-23
    publish_day_of_week: Optional[int] = None  # 0-6

    # Social signals
    social_velocity_score: int = 0
    reddit_mentions: int = 0
    x_mentions: int = 0

    # Processing metadata
    processing_errors: List[str] = field(default_factory=list)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Pattern:
    """Represents a discovered content pattern"""
    pattern_id: str
    niche: str
    pattern_type: str  # "title_formula", "timing", "structure", "topic"
    confidence: float  # 0-1
    sample_size: int  # Number of articles analyzed
    discovered_date: str = field(default_factory=lambda: datetime.now().isoformat())
    pattern_data: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class NicheVelocity:
    """Velocity score for a niche"""
    niche: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Metrics
    articles_published_24h: int = 0
    social_velocity: int = 0
    avg_time_to_publish: int = 0  # seconds
    structural_pattern_strength: float = 0.0  # 0-1

    # Composite score (0-100)
    velocity_score: float = 0.0

    # Supporting data
    competitors_tracked: int = 0
    top_performers: List[Dict[str, Any]] = field(default_factory=list)
    recommendation: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


# Helper functions
def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix"""
    import uuid
    uid = str(uuid.uuid4())[:8]
    return f"{prefix}_{uid}" if prefix else uid


def parse_datetime(dt_string: str) -> datetime:
    """Parse ISO format datetime string"""
    return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
