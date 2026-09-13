"""
Job API client — fetches job listings from the Arbeitnow public board API
and normalises them into the application's Job model.
"""

import logging
import time

import requests

from job_recommender.config import get_settings
from job_recommender.exceptions import JobAPIError
from job_recommender.models import Job

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.arbeitnow.com/api/job-board-api"
_RATE_LIMIT_BACKOFF_SECONDS = 10
_REQUEST_DELAY_SECONDS = 2


class JobAPIClient:
    """
    Client for the Arbeitnow public job board API.

    Fetches paginated job listings and normalises each entry into a Job model.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._max_pages = settings.max_pages
        self._timeout = settings.request_timeout

    def fetch_jobs(self) -> list[Job]:
        """
        Fetch all available jobs up to ``max_pages`` pages.

        Returns:
            A list of normalised Job instances.

        Raises:
            JobAPIError: If an unrecoverable request error occurs.
        """
        jobs: list[Job] = []

        for page in range(1, self._max_pages + 1):
            logger.info("Fetching job listings — page %d / %d", page, self._max_pages)

            response = self._get_page(page)
            if response is None:
                break  # Unrecoverable error; abort early

            api_jobs: list[dict] = response.get("data", [])

            if not api_jobs:
                logger.info("No more jobs returned — stopping at page %d.", page)
                break

            for raw_job in api_jobs:
                jobs.append(self._normalise(raw_job))

            time.sleep(_REQUEST_DELAY_SECONDS)

        logger.info("Fetched %d total jobs.", len(jobs))
        return jobs

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_page(self, page: int) -> dict | None:
        """
        Perform a single paginated GET request.

        Handles 429 rate-limit responses with one automatic retry.
        Returns None on a fatal error so the caller can stop iteration.
        """
        params = {"page": page}

        try:
            response = requests.get(_BASE_URL, params=params, timeout=self._timeout)

            if response.status_code == 429:
                logger.warning(
                    "Rate limit hit on page %d. Retrying in %ds…",
                    page,
                    _RATE_LIMIT_BACKOFF_SECONDS,
                )
                time.sleep(_RATE_LIMIT_BACKOFF_SECONDS)
                response = requests.get(_BASE_URL, params=params, timeout=self._timeout)

            response.raise_for_status()
            return response.json()

        except requests.RequestException as exc:
            logger.error("Failed to fetch page %d: %s", page, exc)
            return None

    @staticmethod
    def _normalise(raw: dict) -> Job:
        """Map a raw API job dict into a normalised Job model."""
        return Job(
            id=str(raw.get("slug", "")),
            title=raw.get("title", ""),
            company=raw.get("company_name", ""),
            location=raw.get("location", ""),
            description=raw.get("description", ""),
            skills=raw.get("tags", []),
            url=raw.get("url", ""),
        )
