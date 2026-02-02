#!/usr/bin/env python3
"""
Generate Intelligence Report

Runs all intelligence analysis and generates a comprehensive report
showing the "secret sauce" of Google Discover.
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.intelligence.pattern_engine import PatternEngine
from core.intelligence.niche_scorer import NicheScorer
from core.intelligence.title_analyzer import TitleAnalyzer
from core.intelligence.timing_analyzer import TimingAnalyzer
from core.persistence.database import Database


async def main():
    print(f"\n{'='*70}")
    print(" PROJECT HUNTER - INTELLIGENCE REPORT")
    print(f" Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    db = Database()
    stats = db.get_stats()

    # Overview
    print("SYSTEM OVERVIEW")
    print(f"{'-'*70}")
    print(f"Competitors tracked: {stats['competitors_discovered']}")
    print(f"RSS feeds monitored: {stats['rss_feeds_registered']}")
    print(f"Total articles analyzed: {stats['total_articles']}")
    print(f"Articles with DNA: {stats['articles_with_dna']}")
    print(f"\nArticles by niche:")
    for niche, count in stats['articles_by_niche'].items():
        print(f"  {niche}: {count}")

    # 1. Niche Velocity Scores
    print(f"\n{'='*70}")
    print("1. NICHE VELOCITY RANKING")
    print(f"{'='*70}\n")

    scorer = NicheScorer()
    niche_scores = scorer.score_all_niches()

    for i, score in enumerate(niche_scores, 1):
        print(f"#{i}. {score.niche.upper()}")
        print(f"   Velocity Score: {score.velocity_score:.1f}/100")
        print(f"   Articles (24h): {score.articles_published_24h}")
        print(f"   Social Velocity: {score.social_velocity}/100")
        print(f"   Competitors: {score.competitors_tracked}")
        print(f"   Recommendation: {score.recommendation}\n")

    # Winner
    if niche_scores:
        winner = niche_scores[0]
        print(f"🏆 WINNING NICHE: {winner.niche.upper()}")
        print(f"   → Focus your efforts here for maximum Discover velocity\n")

    # 2. Structural Patterns
    print(f"\n{'='*70}")
    print("2. STRUCTURAL PATTERNS")
    print(f"{'='*70}\n")

    pattern_engine = PatternEngine()
    patterns = pattern_engine.analyze_all_patterns()

    for pattern in patterns:
        if pattern.sample_size > 0:
            print(f"{pattern.pattern_type.upper()} (confidence: {pattern.confidence:.2f})")
            print(f"  Sample size: {pattern.sample_size}")

            if pattern.pattern_type == "word_count":
                print(f"  Optimal range: {pattern.pattern_data.get('sweet_spot', 'N/A')}")
                print(f"  Median: {pattern.pattern_data.get('median', 0):.0f} words")

            elif pattern.pattern_type == "images":
                print(f"  Optimal count: {pattern.pattern_data.get('optimal_image_count', 'N/A')}")
                print(f"  Preferred ratio: {pattern.pattern_data.get('most_common_aspect_ratio', 'N/A')}")
                print(f"  WebP adoption: {pattern.pattern_data.get('webp_adoption_rate', 0)*100:.0f}%")

            elif pattern.pattern_type == "schema":
                print(f"  Usage rate: {pattern.pattern_data.get('schema_usage_rate', 0)*100:.0f}%")
                print(f"  Required types: {', '.join(pattern.pattern_data.get('required_types', []))}")

            elif pattern.pattern_type == "structure":
                print(f"  Subheadings: {pattern.pattern_data.get('total_subheadings_range', 'N/A')}")
                print(f"  Internal links: {pattern.pattern_data.get('internal_links_range', 'N/A')}")

            print()

    # 3. Timing Insights
    print(f"\n{'='*70}")
    print("3. TIMING INSIGHTS")
    print(f"{'='*70}\n")

    timing_analyzer = TimingAnalyzer()
    timing = timing_analyzer.analyze_timing_patterns()

    print(f"Sample size: {timing['sample_size']} articles")
    print(f"\nOptimal publish hours (UTC):")
    for hour in timing.get('optimal_publish_hours', [])[:3]:
        print(f"  • {hour}")

    print(f"\nOptimal publish days:")
    for day in timing.get('optimal_publish_days', [])[:3]:
        print(f"  • {day}")

    print(f"\nRecommendations:")
    for rec in timing.get('recommendations', []):
        print(f"  → {rec}")

    # 4. Title Analysis (if available)
    print(f"\n{'='*70}")
    print("4. TITLE FORMULAS")
    print(f"{'='*70}\n")

    # Check if title analysis exists
    title_path = Path("data/intelligence/title_formulas.json")
    if title_path.exists():
        with open(title_path, 'r') as f:
            title_data = json.load(f)

        if title_data:
            latest = title_data[0]
            print(f"Model used: {latest.get('model_used', 'N/A')}")
            print(f"Sample size: {latest.get('sample_size', 'N/A')}")
            print(f"\nAnalysis:")
            analysis = latest.get('analysis', {})
            if isinstance(analysis, dict):
                print(json.dumps(analysis, indent=2))
            else:
                print(analysis)
    else:
        print("Title analysis not yet run.")
        print("Run: python scripts/analyze_titles.py")

    # Summary
    print(f"\n{'='*70}")
    print("ACTIONABLE SUMMARY")
    print(f"{'='*70}\n")

    if niche_scores:
        winner = niche_scores[0]
        print(f"1. FOCUS ON: {winner.niche.upper()} (Velocity: {winner.velocity_score:.0f}/100)")

    word_pattern = next((p for p in patterns if p.pattern_type == "word_count"), None)
    if word_pattern and word_pattern.sample_size > 0:
        print(f"2. WORD COUNT: {word_pattern.pattern_data.get('sweet_spot', '800-1200')} words")

    image_pattern = next((p for p in patterns if p.pattern_type == "images"), None)
    if image_pattern and image_pattern.sample_size > 0:
        print(f"3. IMAGES: {image_pattern.pattern_data.get('optimal_image_count', '2-4')} images, 16:9 ratio, WebP format")

    schema_pattern = next((p for p in patterns if p.pattern_type == "schema"), None)
    if schema_pattern and schema_pattern.sample_size > 0:
        print(f"4. SCHEMA: NewsArticle + Organization (required)")

    if timing.get('optimal_publish_hours'):
        print(f"5. TIMING: {timing['optimal_publish_hours'][0]} ({timing['optimal_publish_days'][0]})")

    print(f"\n{'='*70}\n")

    print("Report saved to data/intelligence/")
    print("Next step: Use these insights to create your content strategy!")


if __name__ == "__main__":
    asyncio.run(main())
