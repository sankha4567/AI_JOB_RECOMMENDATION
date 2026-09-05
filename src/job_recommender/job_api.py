import time

import requests

from job_recommender.config import (
    MAX_PAGES,
    REQUEST_TIMEOUT
)

from job_recommender.models import Job


class JobAPI:

    BASE_URL = "https://www.arbeitnow.com/api/job-board-api"

    def fetch_jobs(self):

        jobs = []

        for page in range(1, MAX_PAGES + 1):

            print(f"Fetching Page {page}")

            try:

                response = requests.get(
                    self.BASE_URL,
                    params={
                        "page": page
                    },
                    timeout=REQUEST_TIMEOUT
                )

                # Rate limited
                if response.status_code == 429:

                    print(
                        "Rate limit reached. "
                        "Waiting 10 seconds..."
                    )

                    time.sleep(10)

                    # Retry the same page
                    response = requests.get(
                        self.BASE_URL,
                        params={
                            "page": page
                        },
                        timeout=REQUEST_TIMEOUT
                    )

                response.raise_for_status()

                data = response.json()

                api_jobs = data.get(
                    "data",
                    []
                )

                if not api_jobs:
                    break

                for job in api_jobs:

                    jobs.append(
                        self.normalize_job(job)
                    )

                # Small delay between requests
                time.sleep(2)

            except requests.RequestException as e:

                print(
                    f"Failed to fetch page {page}: {e}"
                )

                break

        return jobs

    def normalize_job(self, job):

        skills = job.get(
            "tags",
            []
        )

        return Job(
            id=str(
                job.get("slug")
            ),

            title=job.get(
                "title",
                ""
            ),

            company=job.get(
                "company_name",
                ""
            ),

            location=job.get(
                "location",
                ""
            ),

            description=job.get(
                "description",
                ""
            ),

            skills=skills,

            url=job.get(
                "url",
                ""
            )
        )