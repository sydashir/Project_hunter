"""
Timing Pattern Analyzer

Analyzes publish timing patterns to identify optimal time windows
for publishing content.
"""

import statistics
from typing import Dict, List
from collections import defaultdict, Counter
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.persistence.database import Database


class TimingAnalyzer:
    """Analyze publish timing patterns"""

    def __init__(self):
        self.db = Database()

    def analyze_timing_patterns(self, niche: str = None) -> Dict:
        """
        Analyze timing patterns across articles

        Returns:
            Dictionary with timing insights
        """
        # Get articles
        if niche:
            articles = self.db.get_articles_by_niche(niche, limit=10000)
        else:
            # Get all articles
            articles = []
            with self.db.get_connection() as conn:
                rows = conn.execute("SELECT * FROM articles LIMIT 10000").fetchall()
                articles = [dict(row) for row in rows]

        if not articles:
            print("[Timing Analyzer] No articles found")
            return {"error": "No data"}

        print(f"[Timing Analyzer] Analyzing {len(articles)} articles...")

        # Extract timing data
        publish_hours = [a['publish_hour'] for a in articles if a.get('publish_hour') is not None]
        publish_days = [a['publish_day_of_week'] for a in articles if a.get('publish_day_of_week') is not None]

        # Analyze patterns
        result = {
            "niche": niche or "all",
            "sample_size": len(articles),
            "optimal_publish_hours": self._find_optimal_hours(publish_hours),
            "optimal_publish_days": self._find_optimal_days(publish_days),
            "hourly_distribution": self._get_hourly_distribution(publish_hours),
            "daily_distribution": self._get_daily_distribution(publish_days),
            "recommendations": self._generate_recommendations(publish_hours, publish_days)
        }

        # Save to intelligence folder
        import json
        timing_path = Path("data/intelligence/timing_insights.json")
        with open(timing_path, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"[Timing Analyzer] Complete! Insights saved to {timing_path}")

        return result

    def _find_optimal_hours(self, publish_hours: List[int]) -> List[str]:
        """Find optimal publish hours (UTC)"""
        if not publish_hours:
            return []

        # Count frequency
        hour_counts = Counter(publish_hours)

        # Get top 3 hours
        top_hours = hour_counts.most_common(3)

        # Format as time ranges
        optimal_windows = []
        for hour, count in top_hours:
            window = f"{hour:02d}:00-{(hour+1)%24:02d}:00 UTC"
            optimal_windows.append(window)

        return optimal_windows

    def _find_optimal_days(self, publish_days: List[int]) -> List[str]:
        """Find optimal publish days"""
        if not publish_days:
            return []

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Count frequency
        day_counts = Counter(publish_days)

        # Get top 3 days
        top_days = day_counts.most_common(3)

        return [day_names[day] for day, count in top_days]

    def _get_hourly_distribution(self, publish_hours: List[int]) -> Dict[str, int]:
        """Get distribution by hour"""
        if not publish_hours:
            return {}

        hour_counts = Counter(publish_hours)

        # Convert to readable format
        distribution = {}
        for hour in range(24):
            time_str = f"{hour:02d}:00"
            distribution[time_str] = hour_counts.get(hour, 0)

        return distribution

    def _get_daily_distribution(self, publish_days: List[int]) -> Dict[str, int]:
        """Get distribution by day of week"""
        if not publish_days:
            return {}

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_counts = Counter(publish_days)

        distribution = {}
        for i, day_name in enumerate(day_names):
            distribution[day_name] = day_counts.get(i, 0)

        return distribution

    def _generate_recommendations(self, publish_hours: List[int], publish_days: List[int]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Hour recommendations
        if publish_hours:
            hour_counts = Counter(publish_hours)
            peak_hour = hour_counts.most_common(1)[0][0]
            recommendations.append(f"Peak publishing hour: {peak_hour:02d}:00-{(peak_hour+1)%24:02d}:00 UTC")

            # Morning vs evening
            morning_count = sum(hour_counts.get(h, 0) for h in range(6, 12))
            afternoon_count = sum(hour_counts.get(h, 0) for h in range(12, 18))
            evening_count = sum(hour_counts.get(h, 0) for h in range(18, 24))

            if morning_count > afternoon_count and morning_count > evening_count:
                recommendations.append("Morning publishing (6-12 UTC) shows highest activity")
            elif afternoon_count > evening_count:
                recommendations.append("Afternoon publishing (12-18 UTC) shows highest activity")
            else:
                recommendations.append("Evening publishing (18-24 UTC) shows highest activity")

        # Day recommendations
        if publish_days:
            day_counts = Counter(publish_days)
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

            peak_day = day_names[day_counts.most_common(1)[0][0]]
            recommendations.append(f"Peak publishing day: {peak_day}")

            # Weekday vs weekend
            weekday_count = sum(day_counts.get(i, 0) for i in range(5))
            weekend_count = sum(day_counts.get(i, 0) for i in range(5, 7))

            if weekday_count > weekend_count * 2:
                recommendations.append("Weekday publishing dominates (Monday-Friday)")
            else:
                recommendations.append("Consistent publishing across week including weekends")

        return recommendations


def main():
    """Test timing analyzer"""
    analyzer = TimingAnalyzer()
    result = analyzer.analyze_timing_patterns()

    print(f"\n{'='*60}")
    print("TIMING ANALYSIS RESULT")
    print(f"{'='*60}")

    print(f"\nSample size: {result['sample_size']}")

    print(f"\nOptimal publish hours:")
    for hour in result.get('optimal_publish_hours', []):
        print(f"  - {hour}")

    print(f"\nOptimal publish days:")
    for day in result.get('optimal_publish_days', []):
        print(f"  - {day}")

    print(f"\nRecommendations:")
    for rec in result.get('recommendations', []):
        print(f"  • {rec}")


if __name__ == "__main__":
    main()
