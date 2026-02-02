#!/usr/bin/env python3
"""
Run Discovery Phase

Discovers competitors and RSS feeds from seed URLs.
Run this once at the beginning.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.orchestrator.main_controller import MainController


async def main():
    controller = MainController()
    await controller.run_discovery_phase()

    # Print results
    print(f"\n{'='*70}")
    print("DISCOVERY RESULTS")
    print(f"{'='*70}")

    status = controller.get_system_status()
    print(f"\nCompetitors discovered: {status['database_stats']['competitors_discovered']}")
    print(f"RSS feeds registered: {status['database_stats']['rss_feeds_registered']}")

    print(f"\nDiscovery phase complete!")
    print(f"Next step: Run 'python scripts/run_monitor.py' to start monitoring")


if __name__ == "__main__":
    asyncio.run(main())
