"""
CLI entry point for indexing/syncing job listings into the vector store.

Usage:
    python scripts/sync_jobs.py
    # or if installed as a package:
    sync-jobs
"""

import logging

from job_recommender.services.job_indexer import JobIndexer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("=" * 60)
    logger.info("AI Job Recommender — Job Sync")
    logger.info("=" * 60)

    result = JobIndexer().sync()

    logger.info("=" * 60)
    logger.info("SYNC COMPLETE")
    logger.info("  Fetched : %d", result.fetched)
    logger.info("  Added   : %d", result.added)
    logger.info("  Updated : %d", result.updated)
    logger.info("  Skipped : %d", result.skipped)
    logger.info("  DB total: %d", result.total_in_db)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
