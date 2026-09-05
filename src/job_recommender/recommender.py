import json

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from job_recommender.config import (
    GOOGLE_API_KEY,
    LLM_MODEL
)

from job_recommender.models import (
    CandidateProfile,
    RecommendationResponse
)

from job_recommender.prompts import JOB_RANKING_PROMPT
from job_recommender.vector_store import VectorStore


class JobRecommender:

    def __init__(self):

        self.vector_store = VectorStore()

        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0
        )

        self.prompt = ChatPromptTemplate.from_template(
            JOB_RANKING_PROMPT
        )

        self.parser = StrOutputParser()

        self.chain = (
            self.prompt
            | self.llm
            | self.parser
        )

    def build_query(
        self,
        profile: CandidateProfile
    ) -> str:
        """
        Builds a semantic search query from the candidate profile.
        """

        skills = ", ".join(profile.skills)

        return f"""
Preferred Role:
{profile.preferred_role}

Skills:
{skills}

Experience:
{profile.experience} years

Education:
{profile.education}

Location:
{profile.location}
"""

    def retrieve_jobs(
        self,
        profile: CandidateProfile
    ):

        query = self.build_query(profile)

        jobs = self.vector_store.mmr_search(
            query=query
        )

        return jobs

    def recommend(
        self,
        profile: CandidateProfile
    ) -> RecommendationResponse:

        jobs = self.retrieve_jobs(profile)

        jobs_text = "\n\n".join(

            job.page_content

            for job in jobs

        )

        response = self.chain.invoke(
            {
                "candidate": profile.model_dump_json(
                    indent=2
                ),
                "jobs": jobs_text
            }
        )

        response_dict = json.loads(
            response
        )

        return RecommendationResponse.model_validate(
            response_dict
        )