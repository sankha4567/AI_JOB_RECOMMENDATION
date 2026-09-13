"""
Job indexer — fetches jobs from the API and upserts them into the vector store.
"""

import hashlib
import logging

from langchain_core.documents import Document

from job_recommender.core.vector_store import VectorStore
from job_recommender.models import Job
from job_recommender.services.job_api import JobAPIClient

logger = logging.getLogger(__name__)


class SyncResult:
    """Summary statistics from a completed sync run."""

    def __init__(self) -> None:
        self.fetched: int = 0
        self.added: int = 0
        self.updated: int = 0
        self.skipped: int = 0
        self.total_in_db: int = 0

    def __str__(self) -> str:
        return (
            f"Fetched={self.fetched}  Added={self.added}  "
            f"Updated={self.updated}  Skipped={self.skipped}  "
            f"DB total={self.total_in_db}"
        )


class JobIndexer:
    """
    Orchestrates fetching job listings from the API and indexing them
    into the vector store with content-hash-based deduplication.
    """

    def __init__(self) -> None:
        self._job_api = JobAPIClient()
        self._vector_store = VectorStore()

    def sync(self) -> SyncResult:
        """
        Fetch all jobs and upsert changed ones into the vector store.

        Returns:
            A SyncResult with summary statistics.
        """
        logger.info("Starting job sync…")

        jobs = self._job_api.fetch_jobs()
        result = SyncResult()
        result.fetched = len(jobs)

        for job in jobs:
            document, content_hash = self._build_document(job)

            if not self._vector_store.job_exists(job.id):
                self._vector_store.add_job(document, job.id)
                result.added += 1
                continue

            metadata = self._vector_store.get_metadata(job.id)
            if metadata and metadata.get("content_hash") == content_hash:
                result.skipped += 1
                continue

            self._vector_store.update_job(document, job.id)
            result.updated += 1

        result.total_in_db = self._vector_store.count()

        logger.info("Sync complete — %s", result)
        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_document(job: Job) -> tuple[Document, str]:
        """
        Convert a Job into a LangChain Document and compute its content hash.

        Returns:
            (Document, sha256_hex_hash)
        """
        content = (
            f"Title: {job.title}\n\n"
            f"Company: {job.company}\n\n"
            f"Location: {job.location}\n\n"
            f"Skills:\n{', '.join(job.skills)}\n\n"
            f"Description:\n{job.description}"
        )

        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        document = Document(
            page_content=content,
            metadata={
                "job_id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "url": job.url,
                "content_hash": content_hash,
            },
        )

        return document, content_hash
