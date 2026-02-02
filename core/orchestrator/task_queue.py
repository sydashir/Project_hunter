"""
Task Queue

Async task queue for DNA extraction with concurrency control.
Processes articles in parallel with rate limiting and error handling.
"""

import asyncio
from typing import List, Optional, Callable
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.persistence.database import Database
from core.architect.dna_extractor import DNAExtractor
from core.orchestrator.rate_limiter import get_rate_limiter


class DNAExtractionQueue:
    """
    Async queue for processing DNA extraction tasks

    Features:
    - Concurrent processing (default 10 workers)
    - Rate limiting (Playwright requests)
    - Error handling and retry logic
    - Progress tracking
    """

    def __init__(self, max_workers: int = 10):
        self.db = Database()
        self.extractor = DNAExtractor()
        self.rate_limiter = get_rate_limiter()

        self.max_workers = max_workers
        self.queue = asyncio.Queue()

        # Statistics
        self.processed_count = 0
        self.error_count = 0
        self.start_time = None

    async def process_pending_articles(self, limit: Optional[int] = None):
        """
        Process all pending articles from database queue

        Args:
            limit: Max articles to process (None = all)
        """
        # Get pending articles
        pending_article_ids = self.db.get_pending_queue_items(limit or 999999)

        if not pending_article_ids:
            print("[DNA Queue] No pending articles")
            return

        print(f"[DNA Queue] Processing {len(pending_article_ids)} articles with {self.max_workers} workers")

        # Add to queue
        for article_id in pending_article_ids:
            await self.queue.put(article_id)

        # Start workers
        self.start_time = datetime.now()

        workers = [
            asyncio.create_task(self._worker(i))
            for i in range(self.max_workers)
        ]

        # Wait for queue to be empty
        await self.queue.join()

        # Cancel workers
        for worker in workers:
            worker.cancel()

        # Print summary
        duration = (datetime.now() - self.start_time).total_seconds()
        print(f"\n[DNA Queue] Complete!")
        print(f"  Processed: {self.processed_count}")
        print(f"  Errors: {self.error_count}")
        print(f"  Duration: {duration:.1f}s")
        print(f"  Rate: {self.processed_count/duration:.2f} articles/sec")

    async def _worker(self, worker_id: int):
        """
        Worker coroutine - processes articles from queue

        Args:
            worker_id: Worker identifier
        """
        while True:
            try:
                # Get article ID from queue
                article_id = await self.queue.get()

                # Get article details from database
                article = await self._get_article_details(article_id)

                if not article:
                    print(f"  [Worker {worker_id}] Article {article_id} not found")
                    self.queue.task_done()
                    continue

                print(f"  [Worker {worker_id}] Processing: {article['title'][:50]}")

                # Acquire rate limit
                await self.rate_limiter.acquire("playwright")

                # Extract DNA
                success = await self._extract_dna(article_id, article['url'], article['title'])

                # Mark as processed in queue
                if success:
                    self.db.mark_queue_processed(article_id, success=True)
                    self.processed_count += 1
                else:
                    self.db.mark_queue_processed(article_id, success=False, error="Extraction failed")
                    self.error_count += 1

                # Mark task as done
                self.queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"  [Worker {worker_id}] Error: {e}")
                self.error_count += 1
                self.queue.task_done()

    async def _get_article_details(self, article_id: str) -> Optional[dict]:
        """Get article details from database"""
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._get_article_sync,
            article_id
        )

    def _get_article_sync(self, article_id: str) -> Optional[dict]:
        """Sync version of get article"""
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM articles WHERE article_id = ?",
                (article_id,)
            ).fetchone()
            return dict(row) if row else None

    async def _extract_dna(self, article_id: str, url: str, title: str) -> bool:
        """
        Extract DNA for an article

        Returns:
            True if successful, False otherwise
        """
        try:
            dna = await self.extractor.extract_article_dna(article_id, url, title)
            return dna is not None
        except Exception as e:
            print(f"    DNA extraction error: {e}")
            return False

    def get_stats(self) -> dict:
        """Get processing statistics"""
        return {
            "processed": self.processed_count,
            "errors": self.error_count,
            "queue_size": self.queue.qsize()
        }


async def main():
    """Test DNA extraction queue"""
    queue = DNAExtractionQueue(max_workers=5)

    # Process pending articles (limit to 10 for testing)
    await queue.process_pending_articles(limit=10)


if __name__ == "__main__":
    asyncio.run(main())
