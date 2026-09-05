import hashlib

from langchain_core.documents import Document

from job_recommender.job_api import JobAPI
from job_recommender.vector_store import VectorStore


class JobIndexer:

    def __init__(self):

        self.job_api = JobAPI()

        self.vector_store = VectorStore()

    def generate_hash(self, content: str) -> str:

        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

    def create_document(self, job):

        content = f"""
Title: {job.title}

Company: {job.company}

Location: {job.location}

Skills:
{", ".join(job.skills)}

Description:

{job.description}
"""

        content_hash = self.generate_hash(content)

        document = Document(
            page_content=content,
            metadata={
                "job_id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "url": job.url,
                "content_hash": content_hash
            }
        )

        return document, content_hash

    def sync(self):

        print("\nFetching Jobs...\n")

        jobs = self.job_api.fetch_jobs()

        print(f"Fetched {len(jobs)} jobs.\n")

        added = 0
        updated = 0
        skipped = 0

        for job in jobs:

            document, content_hash = self.create_document(
                job
            )

            if not self.vector_store.job_exists(job.id):

                self.vector_store.add_job(
                    document,
                    job.id
                )

                added += 1

                continue

            metadata = self.vector_store.get_metadata(
                job.id
            )

            old_hash = metadata.get(
                "content_hash"
            )

            if old_hash == content_hash:

                skipped += 1

                continue

            self.vector_store.update_job(
                document,
                job.id
            )

            updated += 1

        print("=" * 50)
        print("SYNC SUMMARY")
        print("=" * 50)
        print(f"Fetched : {len(jobs)}")
        print(f"Added   : {added}")
        print(f"Updated : {updated}")
        print(f"Skipped : {skipped}")
        print(f"Database: {self.vector_store.count()}")
        print("=" * 50)


def main():

    JobIndexer().sync()


if __name__ == "__main__":

    main()