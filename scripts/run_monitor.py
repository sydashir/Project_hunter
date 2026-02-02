#!/usr/bin/env python3
"""
Run Monitoring Loop

Continuously monitors RSS feeds, extracts DNA, and runs periodic intelligence analysis.
This is the main production mode.
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.orchestrator.main_controller import MainController


async def main():
    parser = argparse.ArgumentParser(description="Project Hunter - RSS Monitoring")
    parser.add_argument("--cycles", type=int, default=None, help="Max monitoring cycles (default: infinite)")
    parser.add_argument("--intelligence-interval", type=int, default=6, help="Hours between intelligence runs (default: 6)")

    args = parser.parse_args()

    controller = MainController()

    print(f"Starting monitoring...")
    print(f"  Intelligence interval: {args.intelligence_interval} hours")
    print(f"  Max cycles: {args.cycles or 'Infinite'}")
    print(f"\nPress Ctrl+C to stop\n")

    try:
        await controller.run_full_pipeline(
            skip_discovery=True,  # Assume discovery already done
            monitoring_cycles=args.cycles,
            intelligence_interval_hours=args.intelligence_interval
        )
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")

    # Print final stats
    status = controller.get_system_status()
    print(f"\n{'='*70}")
    print("SESSION SUMMARY")
    print(f"{'='*70}")
    print(f"Total articles: {status['database_stats']['total_articles']}")
    print(f"Articles with DNA: {status['database_stats']['articles_with_dna']}")
    print(f"Pending DNA extraction: {status['database_stats']['pending_dna_extraction']}")


if __name__ == "__main__":
    asyncio.run(main())
