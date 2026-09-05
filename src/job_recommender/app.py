from job_recommender.config import RESUME_PATH
from job_recommender.pdf_utils import PDFReader
from job_recommender.profile_extractor import ProfileExtractor
from job_recommender.recommender import JobRecommender


class Application:

    def __init__(self):

        self.extractor = ProfileExtractor()

        self.recommender = JobRecommender()

    def run(self):

        print("=" * 70)
        print("AI JOB RECOMMENDER")
        print("=" * 70)

        print("\nReading Resume...\n")

        resume_text = PDFReader.extract_text(
            RESUME_PATH
        )

        print("Extracting Candidate Profile...\n")

        profile = self.extractor.extract(
            resume_text
        )

        print("=" * 70)
        print("Candidate Profile")
        print("=" * 70)

        print(f"Name            : {profile.name}")
        print(f"Email           : {profile.email}")
        print(f"Phone           : {profile.phone}")
        print(f"Preferred Role  : {profile.preferred_role}")
        print(f"Experience      : {profile.experience} Years")
        print(f"Education       : {profile.education}")
        print(f"Location        : {profile.location}")

        print("\nSkills")

        for skill in profile.skills:
            print(f"  • {skill}")

        print("\nSearching Similar Jobs...\n")

        response = self.recommender.recommend(
            profile
        )

        print("=" * 70)
        print("TOP JOB RECOMMENDATIONS")
        print("=" * 70)

        for index, job in enumerate(
                response.recommendations,
                start=1
        ):

            print(f"\n{index}. {job.title}")

            print(f"Company : {job.company}")

            print(f"Location: {job.location}")

            print(f"Match   : {job.match_percentage}%")

            print(f"Reason  : {job.reason}")

            print("\nMissing Skills")

            if job.missing_skills:

                for skill in job.missing_skills:

                    print(f"   - {skill}")

            else:

                print("   None")

            print("-" * 70)


def main():

    app = Application()

    app.run()


if __name__ == "__main__":

    main()