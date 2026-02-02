"""
Niche Velocity Scorer

Calculates velocity scores for each niche to identify the winning niche.
Combines article volume, social velocity, timing, and structural patterns.
"""

import statistics
from typing import Dict, List
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.persistence.database import Database
from core.persistence.models import NicheVelocity


class NicheScorer:
    """Calculate niche velocity scores"""

    def __init__(self):
        self.db = Database()

        # Niche list
        self.niches = ["space", "astronomy", "science", "health", "physics", "technology"]

    def score_all_niches(self, time_window_hours: int = 24) -> List[NicheVelocity]:
        """
        Calculate velocity scores for all niches

        Args:
            time_window_hours: Time window for analysis (default 24h)

        Returns:
            List of NicheVelocity objects, sorted by score
        """
        print(f"[Niche Scorer] Scoring niches based on last {time_window_hours} hours...")

        scores = []

        for niche in self.niches:
            score = self._score_niche(niche, time_window_hours)
            scores.append(score)

        # Sort by velocity score
        scores.sort(key=lambda x: x.velocity_score, reverse=True)

        # Save scores
        self.db.save_niche_scores(scores)

        # Print summary
        print(f"\n[Niche Scorer] Results:")
        for i, score in enumerate(scores, 1):
            print(f"  #{i}. {score.niche}: {score.velocity_score:.1f} ({score.recommendation})")

        return scores

    def _score_niche(self, niche: str, time_window_hours: int) -> NicheVelocity:
        """
        Calculate velocity score for a single niche

        Scoring formula:
        - Article volume (20%)
        - Social velocity (25%)
        - Publish speed (15%)
        - Pattern strength (40%)
        """
        # Get articles in time window
        cutoff = datetime.now() - timedelta(hours=time_window_hours)
        articles = self.db.get_articles_by_niche(niche, limit=10000)

        # Filter to time window
        recent_articles = [
            a for a in articles
            if datetime.fromisoformat(a.get('published_date', '')) > cutoff
        ]

        # Component 1: Article Volume (0-100)
        volume_score = min(len(recent_articles) / 2.0, 100)  # 200+ articles = max score

        # Component 2: Social Velocity (0-100)
        # Average social velocity score from articles
        social_scores = [a.get('social_velocity_score', 0) for a in recent_articles]
        social_score = statistics.mean(social_scores) if social_scores else 0

        # Component 3: Publish Speed (0-100)
        # How quickly are articles being published
        if len(recent_articles) >= 2:
            # Calculate average time between articles
            publish_times = sorted([datetime.fromisoformat(a['published_date']) for a in recent_articles])
            intervals = [(publish_times[i+1] - publish_times[i]).total_seconds() / 3600
                        for i in range(len(publish_times) - 1)]
            avg_interval = statistics.mean(intervals)

            # Faster publishing = higher score (1 hour between = 100, 12 hours = 50, 24+ = 0)
            speed_score = max(0, 100 - (avg_interval / 24 * 100))
        else:
            speed_score = 0

        # Component 4: Pattern Strength (0-100)
        # How many articles have DNA extracted and match patterns
        articles_with_dna = [a for a in recent_articles if a.get('dna_extracted', 0) == 1]
        dna_extraction_rate = len(articles_with_dna) / len(recent_articles) if recent_articles else 0
        pattern_score = dna_extraction_rate * 100

        # Calculate composite score (weighted)
        velocity_score = (
            volume_score * 0.20 +
            social_score * 0.25 +
            speed_score * 0.15 +
            pattern_score * 0.40
        )

        # Get top performers
        top_performers = self._get_top_performers(niche, recent_articles)

        # Generate recommendation
        recommendation = self._get_recommendation(velocity_score)

        # Count competitors
        competitors = len(set(a['site_id'] for a in recent_articles))

        return NicheVelocity(
            niche=niche,
            articles_published_24h=len(recent_articles),
            social_velocity=int(social_score),
            avg_time_to_publish=int(statistics.mean([abs(datetime.now() - datetime.fromisoformat(a['discovered_date'])).total_seconds()
                                                     for a in recent_articles])) if recent_articles else 0,
            structural_pattern_strength=pattern_score / 100,
            velocity_score=velocity_score,
            competitors_tracked=competitors,
            top_performers=top_performers,
            recommendation=recommendation
        )

    def _get_top_performers(self, niche: str, articles: List[Dict]) -> List[Dict]:
        """Get top performing sites in niche"""
        # Group by site
        by_site = {}
        for article in articles:
            site_id = article['site_id']
            if site_id not in by_site:
                by_site[site_id] = []
            by_site[site_id].append(article)

        # Calculate performance per site
        site_scores = []
        for site_id, site_articles in by_site.items():
            score = {
                "site_id": site_id,
                "article_count": len(site_articles),
                "avg_social_score": statistics.mean([a.get('social_velocity_score', 0) for a in site_articles])
            }
            site_scores.append(score)

        # Sort by article count
        site_scores.sort(key=lambda x: x['article_count'], reverse=True)

        return site_scores[:5]  # Top 5

    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on velocity score"""
        if score >= 80:
            return "HOT - Prime target niche"
        elif score >= 60:
            return "WARM - Strong opportunity"
        elif score >= 40:
            return "MODERATE - Consider testing"
        else:
            return "COLD - Not recommended"


def main():
    """Test niche scorer"""
    scorer = NicheScorer()
    scores = scorer.score_all_niches(time_window_hours=24)

    print(f"\n{'='*60}")
    print("NICHE VELOCITY RANKING")
    print(f"{'='*60}")

    for i, score in enumerate(scores, 1):
        print(f"\n#{i}. {score.niche.upper()}")
        print(f"   Velocity Score: {score.velocity_score:.1f}/100")
        print(f"   Articles (24h): {score.articles_published_24h}")
        print(f"   Social Velocity: {score.social_velocity}/100")
        print(f"   Recommendation: {score.recommendation}")


if __name__ == "__main__":
    main()
