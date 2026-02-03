#!/usr/bin/env python3
"""
Run Discovery Phase

Loads competitors discovered via Chrome extension.
Run this after browsing Google Discover with the extension installed.
"""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from core.scout.competitor_discovery import CompetitorDiscovery

def main():
    """Load competitors discovered via Chrome extension"""
    print("="*60)
    print("PROJECT HUNTER - Competitor Discovery (Chrome Extension)")
    print("="*60)
    print("\nMake sure:")
    print("1. Chrome extension is installed")
    print("2. API server is running (python api/discover_api.py)")
    print("3. You've browsed Google Discover for 30+ minutes")
    print("")

    discovery = CompetitorDiscovery()
    competitors = discovery.load_from_extension()

    if not competitors:
        print("\n⚠️  No competitors found!")
        print("Browse Google Discover with the extension installed to collect data.")
        return

    print(f"\n{'='*60}")
    print(f"DISCOVERY COMPLETE")
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

    print(f"\nTop 10 by Discover position:")
    top_10 = sorted(competitors, key=lambda x: x.authority_score, reverse=True)[:10]
    for comp in top_10:
        pos = comp.metadata.get('discover_position', 'N/A')
        print(f"  [{pos}] {comp.domain} - {comp.niche}")

if __name__ == "__main__":
    main()
