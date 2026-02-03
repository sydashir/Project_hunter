"""
FastAPI server to receive Google Discover data from Chrome extension
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Set
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from core.persistence.database import Database
from core.persistence.models import CompetitorSite, generate_id

app = FastAPI(title="Project Hunter - Discover API")

# Enable CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track discovered domains
discovered_domains: Set[str] = set()
db = Database()

class DiscoverArticle(BaseModel):
    domain: str
    url: str
    title: str
    position: int
    timestamp: str

@app.post("/api/discover/article")
async def receive_article(article: DiscoverArticle) -> Dict:
    """Receive article data from Chrome extension"""

    # Skip if already discovered
    if article.domain in discovered_domains:
        return {"status": "duplicate", "domain": article.domain}

    discovered_domains.add(article.domain)

    # Create CompetitorSite object
    site = CompetitorSite(
        site_id=generate_id("site"),
        domain=article.domain,
        url=article.url,
        niche="unknown",  # Will be inferred later
        discovery_source="chrome_extension",
        discovered_from=None,
        authority_score=100.0 - article.position,  # Higher position = higher score
        crawl_depth=0,
        metadata={
            'discover_position': article.position,
            'discovered_at': article.timestamp,
            'sample_title': article.title
        }
    )

    # Save to database
    db.save_competitor(site)

    print(f"[API] New domain: {article.domain} (position {article.position})")

    return {
        "status": "success",
        "domain": article.domain,
        "total_discovered": len(discovered_domains)
    }

@app.get("/api/discover/stats")
async def get_stats() -> Dict:
    """Get discovery statistics"""
    return {
        "total_domains": len(discovered_domains),
        "domains": list(discovered_domains)
    }

@app.post("/api/discover/reset")
async def reset() -> Dict:
    """Reset discovered domains (for testing)"""
    discovered_domains.clear()
    return {"status": "reset", "total_domains": 0}

if __name__ == "__main__":
    import uvicorn
    print("[Discover API] Starting on http://localhost:8000")
    print("[Discover API] Install Chrome extension and browse Google Discover")
    uvicorn.run(app, host="127.0.0.1", port=8000)
