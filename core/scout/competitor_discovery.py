"""
Competitor Discovery Engine

Implements recursive BFS crawler to discover 100+ competitors from seed URLs.
Uses relevance scoring to filter high-quality content sites in target niches.
"""

import asyncio
import yaml
from typing import List, Dict, Set, Tuple, Optional
from urllib.parse import urlparse, urljoin
from datetime import datetime
from collections import deque

import requests
from bs4 import BeautifulSoup

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.persistence.database import Database
from core.persistence.models import CompetitorSite, generate_id


class CompetitorDiscovery:
    """Discovers competitors using BFS crawl from seed URLs"""

    def __init__(self, config_path: str = "config"):
        self.config_path = Path(config_path)
        self.db = Database()

        # Load configuration
        self.seeds = self._load_seeds()
        self.niches = self._load_niches()
        self.exclude_domains = self._get_exclude_domains()

        # Discovery settings
        self.max_depth = 3
        self.target_count = 150
        self.min_relevance_score = 0.6

        # Tracking
        self.discovered: Dict[str, CompetitorSite] = {}
        self.visited: Set[str] = set()

    def _load_seeds(self) -> List[Dict]:
        """Load seed URLs from config"""
        with open(self.config_path / "seed_urls.yaml", 'r') as f:
            config = yaml.safe_load(f)
            return config['seeds']

    def _load_niches(self) -> Dict:
        """Load niche definitions and keywords"""
        with open(self.config_path / "niches.yaml", 'r') as f:
            config = yaml.safe_load(f)
            return config['niches']

    def _get_exclude_domains(self) -> Set[str]:
        """Get domains to exclude from discovery"""
        with open(self.config_path / "seed_urls.yaml", 'r') as f:
            config = yaml.safe_load(f)
            return set(config.get('exclude_domains', []))

    def run_discovery(self) -> List[CompetitorSite]:
        """
        Main discovery method - BFS crawl from seeds

        Returns:
            List of discovered competitor sites
        """
        print(f"[Discovery] Starting with {len(self.seeds)} seed URLs")
        print(f"[Discovery] Target: {self.target_count} competitors, Max depth: {self.max_depth}")

        # Initialize queue with seeds
        queue = deque()

        for seed in self.seeds:
            url = seed['url']
            domain = urlparse(url).netloc

            # Add seed as discovered site
            site = CompetitorSite(
                site_id=generate_id("site"),
                domain=domain,
                url=url,
                niche=seed['niche'],
                discovery_source="seed",
                authority_score=95.0,  # Seeds are high authority by definition
                crawl_depth=0
            )
            self.discovered[domain] = site
            queue.append((url, 0, None))  # (url, depth, parent_url)

        # BFS crawl
        while queue and len(self.discovered) < self.target_count:
            url, depth, parent_url = queue.popleft()

            if url in self.visited or depth > self.max_depth:
                continue

            self.visited.add(url)
            domain = urlparse(url).netloc

            print(f"[Discovery] Crawling: {url} (depth={depth}, discovered={len(self.discovered)})")

            try:
                # Fetch and parse page
                candidates = self._extract_candidate_links(url)

                # Score and filter candidates
                for candidate_url in candidates:
                    candidate_domain = urlparse(candidate_url).netloc

                    # Skip if already discovered or visited
                    if candidate_domain in self.discovered or candidate_url in self.visited:
                        continue

                    # Skip excluded domains
                    if self._is_excluded_domain(candidate_domain):
                        continue

                    # Calculate relevance score
                    score, niche = self._calculate_relevance_score(candidate_url, candidate_domain)

                    if score >= self.min_relevance_score:
                        # Add to discovered sites
                        site = CompetitorSite(
                            site_id=generate_id("site"),
                            domain=candidate_domain,
                            url=candidate_url,
                            niche=niche,
                            discovery_source="crawler",
                            discovered_from=domain,
                            authority_score=score * 100,
                            crawl_depth=depth + 1
                        )
                        self.discovered[candidate_domain] = site

                        print(f"  ✓ Discovered: {candidate_domain} (score={score:.2f}, niche={niche})")

                        # Add to queue for further crawling if not at max depth
                        if depth + 1 <= self.max_depth:
                            queue.append((candidate_url, depth + 1, url))

                # Respect rate limiting
                import time
                time.sleep(2)

            except Exception as e:
                print(f"  ✗ Error crawling {url}: {e}")
                continue

        print(f"\n[Discovery] Complete! Discovered {len(self.discovered)} competitors")

        # Save to database
        competitors_list = list(self.discovered.values())
        self.db.save_competitors(competitors_list)

        return competitors_list

    def _extract_candidate_links(self, url: str) -> List[str]:
        """
        Extract outbound links from a page

        Returns:
            List of candidate URLs
        """
        try:
            response = requests.get(
                url,
                timeout=15,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            candidates = []
            for link in soup.find_all('a', href=True):
                href = link['href']

                # Make absolute URL
                full_url = urljoin(url, href)

                # Only http/https links
                if not full_url.startswith(('http://', 'https://')):
                    continue

                parsed = urlparse(full_url)

                # Skip fragments and query strings for cleaner URLs
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
                if not clean_url.endswith('/'):
                    clean_url += '/'

                # Skip same domain
                if parsed.netloc == urlparse(url).netloc:
                    continue

                candidates.append(clean_url)

            # Deduplicate
            return list(set(candidates))

        except Exception as e:
            print(f"  Error extracting links from {url}: {e}")
            return []

    def _calculate_relevance_score(self, url: str, domain: str) -> Tuple[float, str]:
        """
        Calculate relevance score (0-1) for a candidate site

        Scoring components:
        - Niche keyword match (30%)
        - RSS feed exists (15%)
        - Content freshness (20%)
        - Domain authority (25%)
        - Mobile optimized (10%)

        Returns:
            (score, primary_niche)
        """
        scores = {}

        # 1. Niche keyword matching
        niche_scores = {}
        domain_and_url_lower = (domain + url).lower()

        for niche_name, niche_data in self.niches.items():
            keywords = niche_data.get('keywords', [])
            matches = sum(1 for kw in keywords if kw in domain_and_url_lower)
            niche_scores[niche_name] = matches

        best_niche = max(niche_scores, key=niche_scores.get)
        max_matches = niche_scores[best_niche]

        # Normalize: 3+ matches = full score
        niche_score = min(max_matches / 3.0, 1.0) * 0.30

        # 2. Check for RSS feed (simplified check)
        rss_score = self._check_rss_exists(domain) * 0.15

        # 3. Content freshness (simplified)
        freshness_score = 0.20  # Default assume fresh

        # 4. Domain authority (simplified - based on domain length and TLD)
        authority_score = self._estimate_authority(domain) * 0.25

        # 5. Mobile optimized (simplified)
        mobile_score = 0.10  # Default assume yes

        total_score = niche_score + rss_score + freshness_score + authority_score + mobile_score

        return (total_score, best_niche)

    def _check_rss_exists(self, domain: str) -> float:
        """
        Quick check if domain likely has RSS feed

        Returns:
            1.0 if likely has RSS, 0.0 otherwise
        """
        common_rss_paths = [
            f"https://{domain}/feed/",
            f"https://{domain}/rss/",
            f"https://{domain}/feed.xml",
            f"https://{domain}/rss.xml",
        ]

        for rss_url in common_rss_paths:
            try:
                response = requests.head(rss_url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    return 1.0
            except:
                continue

        return 0.0  # No RSS found (will be checked more thoroughly later)

    def _estimate_authority(self, domain: str) -> float:
        """
        Estimate domain authority based on heuristics

        Returns:
            Score between 0-1
        """
        score = 0.5  # Base score

        # Shorter domains often more authoritative
        if len(domain) < 15:
            score += 0.2

        # Common TLDs
        if domain.endswith(('.com', '.org', '.edu')):
            score += 0.2

        # Penalize very long domains or those with numbers
        if len(domain) > 25 or any(char.isdigit() for char in domain):
            score -= 0.2

        return max(0.0, min(1.0, score))

    def _is_excluded_domain(self, domain: str) -> bool:
        """Check if domain should be excluded"""
        # Check exact match
        if domain in self.exclude_domains:
            return True

        # Check if contains excluded domain (e.g., subdomain.facebook.com)
        for excluded in self.exclude_domains:
            if excluded in domain:
                return True

        # Exclude CDNs, ad networks, analytics
        excluded_patterns = [
            'cdn.', 'static.', 'img.', 'media.',
            'ads.', 'analytics.', 'tracking.',
            'doubleclick', 'googleadservices',
            'amazon-adsystem', 'googlesyndication'
        ]

        for pattern in excluded_patterns:
            if pattern in domain:
                return True

        return False


async def main():
    """Run competitor discovery"""
    discovery = CompetitorDiscovery()
    competitors = discovery.run_discovery()

    print(f"\n{'='*60}")
    print(f"DISCOVERY SUMMARY")
    print(f"{'='*60}")
    print(f"Total discovered: {len(competitors)}")

    # Group by niche
    by_niche = {}
    for comp in competitors:
        niche = comp.niche
        by_niche[niche] = by_niche.get(niche, 0) + 1

    print(f"\nBy niche:")
    for niche, count in sorted(by_niche.items(), key=lambda x: x[1], reverse=True):
        print(f"  {niche}: {count}")

    # Top performers
    top_10 = sorted(competitors, key=lambda x: x.authority_score, reverse=True)[:10]
    print(f"\nTop 10 by authority:")
    for comp in top_10:
        print(f"  {comp.domain} - {comp.niche} ({comp.authority_score:.0f})")


if __name__ == "__main__":
    # Note: This is sync version, async would be:
    # asyncio.run(main())
    discovery = CompetitorDiscovery()
    discovery.run_discovery()
