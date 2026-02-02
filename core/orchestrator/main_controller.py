"""
Main Orchestration Controller

Coordinates all agents (Scout, Architect, Intelligence) in an integrated loop.
This is the heart of Project Hunter's autonomous operation.
"""

import asyncio
import time
from datetime import datetime
from typing import Optional

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.scout.competitor_discovery import CompetitorDiscovery
from core.scout.rss_discovery import RSSDiscovery
from core.scout.rss_monitor import RSSMonitor
from core.orchestrator.task_queue import DNAExtractionQueue
from core.intelligence.pattern_engine import PatternEngine
from core.intelligence.niche_scorer import NicheScorer
from core.intelligence.title_analyzer import TitleAnalyzer
from core.intelligence.timing_analyzer import TimingAnalyzer
from core.persistence.database import Database


class MainController:
    """
    Main orchestration controller

    Phases:
    1. Discovery - Find competitors and RSS feeds (run once)
    2. Monitoring - Continuous RSS monitoring + DNA extraction
    3. Intelligence - Periodic pattern analysis and scoring
    """

    def __init__(self):
        self.db = Database()

        # Components
        self.discovery = CompetitorDiscovery()
        self.rss_discovery = RSSDiscovery()
        self.rss_monitor = RSSMonitor()
        self.dna_queue = DNAExtractionQueue(max_workers=10)
        self.pattern_engine = PatternEngine()
        self.niche_scorer = NicheScorer()
        self.title_analyzer = TitleAnalyzer(use_claude=True)
        self.timing_analyzer = TimingAnalyzer()

        # State
        self.discovery_complete = False
        self.monitoring_active = False

    async def run_full_pipeline(
        self,
        skip_discovery: bool = False,
        monitoring_cycles: Optional[int] = None,
        intelligence_interval_hours: int = 6
    ):
        """
        Run the complete Project Hunter pipeline

        Args:
            skip_discovery: Skip initial discovery if already done
            monitoring_cycles: Number of monitoring cycles (None = infinite)
            intelligence_interval_hours: How often to run intelligence analysis
        """
        print(f"\n{'='*70}")
        print(" PROJECT HUNTER - MAIN CONTROLLER")
        print(f"{'='*70}\n")

        # Phase 1: Discovery (if needed)
        if not skip_discovery:
            await self.run_discovery_phase()
        else:
            print("[Controller] Skipping discovery phase...")

        # Phase 2 & 3: Monitoring + Intelligence (continuous)
        await self.run_monitoring_and_intelligence(
            monitoring_cycles=monitoring_cycles,
            intelligence_interval_hours=intelligence_interval_hours
        )

    async def run_discovery_phase(self):
        """
        Phase 1: Discover competitors and RSS feeds

        This runs once at the beginning.
        """
        print(f"\n{'='*70}")
        print(" PHASE 1: DISCOVERY")
        print(f"{'='*70}\n")

        # Step 1: Discover competitors
        print("[1/2] Discovering competitors...")
        competitors = self.discovery.run_discovery()
        print(f"✓ Discovered {len(competitors)} competitors\n")

        # Step 2: Discover RSS feeds
        print("[2/2] Discovering RSS feeds...")
        feeds = self.rss_discovery.discover_all_feeds()
        print(f"✓ Discovered {len(feeds)} RSS feeds\n")

        self.discovery_complete = True

        print(" PHASE 1 COMPLETE")
        print(f"{'='*70}\n")

    async def run_monitoring_and_intelligence(
        self,
        monitoring_cycles: Optional[int] = None,
        intelligence_interval_hours: int = 6
    ):
        """
        Phases 2 & 3: Continuous monitoring + periodic intelligence

        Args:
            monitoring_cycles: Max monitoring cycles (None = infinite)
            intelligence_interval_hours: How often to run intelligence analysis
        """
        print(f"\n{'='*70}")
        print(" PHASES 2 & 3: MONITORING + INTELLIGENCE")
        print(f"{'='*70}\n")

        self.monitoring_active = True

        # Track last intelligence run
        last_intelligence_run = 0
        intelligence_interval_seconds = intelligence_interval_hours * 3600

        # Monitoring loop
        cycle = 0

        while True:
            cycle += 1
            cycle_start = time.time()

            print(f"\n{'-'*70}")
            print(f" CYCLE #{cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'-'*70}\n")

            # Task 1: Monitor RSS feeds
            print("[1/2] Monitoring RSS feeds...")
            new_articles = await self.rss_monitor.monitor_all_feeds()
            print(f"✓ Detected {len(new_articles)} new articles\n")

            # Task 2: Process DNA extraction queue
            print("[2/2] Processing DNA extraction queue...")
            await self.dna_queue.process_pending_articles(limit=50)  # Process up to 50 per cycle

            # Periodic intelligence analysis
            current_time = time.time()
            if current_time - last_intelligence_run >= intelligence_interval_seconds:
                print(f"\n[Intelligence] Running periodic analysis...")
                await self.run_intelligence_analysis()
                last_intelligence_run = current_time

            # Cycle complete
            cycle_duration = time.time() - cycle_start
            print(f"\n Cycle #{cycle} complete in {cycle_duration:.1f}s")

            # Check if we should stop
            if monitoring_cycles and cycle >= monitoring_cycles:
                print(f"\n[Controller] Reached max cycles ({monitoring_cycles}). Stopping.")
                break

            # Wait for next cycle
            sleep_time = max(0, 60 - cycle_duration)  # 60-second cycle
            if sleep_time > 0:
                print(f" Sleeping for {sleep_time:.1f}s until next cycle...\n")
                await asyncio.sleep(sleep_time)

        self.monitoring_active = False

        print(f"\n{'='*70}")
        print(" MONITORING COMPLETE")
        print(f"{'='*70}\n")

    async def run_intelligence_analysis(self):
        """
        Phase 3: Run full intelligence analysis

        This runs periodically (e.g., every 6 hours) during monitoring.
        """
        print(f"\n{'='*70}")
        print(f" INTELLIGENCE ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

        # Step 1: Pattern extraction
        print("[1/4] Extracting structural patterns...")
        patterns = self.pattern_engine.analyze_all_patterns()
        print(f"✓ Identified {len(patterns)} patterns\n")

        # Step 2: Niche velocity scoring
        print("[2/4] Calculating niche velocity scores...")
        niche_scores = self.niche_scorer.score_all_niches()
        print(f"✓ Scored {len(niche_scores)} niches\n")

        # Step 3: Title formula analysis (every other run to save API costs)
        # print("[3/4] Analyzing title formulas with LLM...")
        # title_analysis = self.title_analyzer.analyze_titles(limit=200)
        # print(f"✓ Extracted title formulas\n")

        # Step 4: Timing analysis
        print("[4/4] Analyzing publish timing patterns...")
        timing_insights = self.timing_analyzer.analyze_timing_patterns()
        print(f"✓ Generated timing insights\n")

        print(" INTELLIGENCE ANALYSIS COMPLETE")
        print(f"{'='*70}\n")

        # Print winning niche
        if niche_scores:
            winner = niche_scores[0]
            print(f" WINNING NICHE: {winner.niche.upper()}")
            print(f"   Velocity Score: {winner.velocity_score:.1f}/100")
            print(f"   {winner.recommendation}")
            print()

    def get_system_status(self) -> dict:
        """Get current system status"""
        db_stats = self.db.get_stats()

        return {
            "discovery_complete": self.discovery_complete,
            "monitoring_active": self.monitoring_active,
            "database_stats": db_stats,
            "rss_monitor_stats": self.rss_monitor.get_monitoring_stats() if self.monitoring_active else {},
            "dna_queue_stats": self.dna_queue.get_stats()
        }


async def main():
    """
    Main entry point for Project Hunter

    Running modes:
    1. Full pipeline: Discovery + Monitoring + Intelligence
    2. Monitoring only: Skip discovery if already done
    3. Intelligence only: Run analysis on existing data
    """
    controller = MainController()

    # Run full pipeline for testing (5 monitoring cycles)
    # For production: Remove monitoring_cycles parameter to run indefinitely
    await controller.run_full_pipeline(
        skip_discovery=False,  # Set to True if discovery already done
        monitoring_cycles=5,  # Remove for infinite monitoring
        intelligence_interval_hours=1  # Run intelligence every hour (for testing)
    )

    # Print final status
    status = controller.get_system_status()
    print(f"\n{'='*70}")
    print(" FINAL SYSTEM STATUS")
    print(f"{'='*70}")
    print(f"Discovery complete: {status['discovery_complete']}")
    print(f"Monitoring active: {status['monitoring_active']}")
    print(f"\nDatabase stats:")
    for key, value in status['database_stats'].items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
