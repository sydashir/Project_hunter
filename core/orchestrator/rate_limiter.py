"""
Rate Limiter

Protects against API rate limits and bot detection.
Manages request quotas for Playwright, LLM APIs, and external services.
"""

import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, Tuple
from datetime import datetime


class RateLimiter:
    """
    Token-bucket based rate limiter for multiple resources

    Limits:
    - Playwright requests: 50/hour (avoid bot detection)
    - Anthropic API: 1000/hour (API limit)
    - OpenAI API: 500/hour
    - Netrows API: 5000/day
    - RSS fetches: 200/minute
    """

    def __init__(self):
        # Define limits: (max_requests, window_seconds)
        self.limits: Dict[str, Tuple[int, int]] = {
            "playwright": (50, 3600),  # 50 per hour
            "anthropic_api": (1000, 3600),
            "openai_api": (500, 3600),
            "netrows_api": (5000, 86400),  # per day
            "rss_fetch": (200, 60),  # per minute
        }

        # Track timestamps of requests
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque())

        # Statistics
        self.stats = defaultdict(int)

    async def acquire(self, resource: str, weight: int = 1):
        """
        Acquire permission to make a request

        Blocks until we're under the rate limit.

        Args:
            resource: Resource type (e.g., "playwright", "anthropic_api")
            weight: Request weight (default 1)
        """
        if resource not in self.limits:
            # Unknown resource, allow by default
            return

        max_requests, window = self.limits[resource]
        now = time.time()

        while True:
            # Clean old timestamps outside the window
            history = self.request_history[resource]
            while history and now - history[0] >= window:
                history.popleft()

            # Check if under limit
            if len(history) + weight <= max_requests:
                # Add current request timestamp(s)
                for _ in range(weight):
                    history.append(now)

                # Update stats
                self.stats[f"{resource}_requests"] += weight
                return

            # Over limit - wait until oldest request expires
            wait_time = window - (now - history[0])
            print(f"  [Rate Limit] {resource}: waiting {wait_time:.1f}s...")
            await asyncio.sleep(min(wait_time + 0.1, 5))  # Cap wait at 5s chunks
            now = time.time()

    def get_remaining(self, resource: str) -> int:
        """Get remaining quota for a resource"""
        if resource not in self.limits:
            return 999999

        max_requests, window = self.limits[resource]
        now = time.time()

        # Clean old timestamps
        history = self.request_history[resource]
        while history and now - history[0] >= window:
            history.popleft()

        return max(0, max_requests - len(history))

    def get_stats(self) -> Dict:
        """Get usage statistics"""
        stats = dict(self.stats)

        # Add current quotas
        for resource in self.limits:
            stats[f"{resource}_remaining"] = self.get_remaining(resource)

        return stats

    def reset_stats(self):
        """Reset statistics counters"""
        self.stats.clear()


# Global singleton instance
_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
