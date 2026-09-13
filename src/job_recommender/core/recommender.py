"""
Job recommender — retrieves semantically similar jobs from the vector store
and asks the LLM to rank and explain them for a given candidate.
"""

import json
import logging

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from job_recommender.config import get_settings
from job_recommender.core.vector_store import VectorStore
from job_recommender.exceptions import JobRecommendationError
from job_recommender.models import CandidateProfile, RecommendationResponse
from job_recommender.prompts.templates import JOB_RANKING_PROMPT

logger = logging.getLogger(__name__)


class JobRecommender:
    """
    Retrieves candidate-relevant jobs from the vector store and uses an
    LLM to rank and explain them.
    """

    def __init__(self) -> None:
        settings = get_settings()

        self._vector_store = VectorStore()

        self._chain = (
            ChatPromptTemplate.from_template(JOB_RANKING_PROMPT)
            | ChatGoogleGenerativeAI(
                model=settings.llm_model,
                google_api_key=settings.google_api_key,
                temperature=0,
            )
            | StrOutputParser()
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def recommend(self, profile: CandidateProfile) -> RecommendationResponse:
        """
        Return ranked job recommendations for the given candidate profile.

        Args:
            profile: Extracted candidate profile.

        Returns:
            A RecommendationResponse with the top-ranked jobs.

        Raises:
            JobRecommendationError: If retrieval or ranking fails.
        """
        logger.info("Retrieving candidate-relevant jobs from vector store.")
        jobs: list[Document] = self._retrieve_jobs(profile)

        if not jobs:
            logger.warning("No jobs found in vector store.")
            return RecommendationResponse(recommendations=[])

        jobs_text = "\n\n".join(job.page_content for job in jobs)

        logger.info("Invoking LLM to rank %d jobs.", len(jobs))

        try:
            raw: str = self._chain.invoke(
                {
                    "candidate": profile.model_dump_json(indent=2),
                    "jobs": jobs_text,
                }
            )
            clean = (
                raw.strip()
                .removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
            response_dict: dict = json.loads(clean)
        except json.JSONDecodeError as exc:
            raise JobRecommendationError(
                f"LLM returned non-JSON response: {exc}"
            ) from exc
        except Exception as exc:
            raise JobRecommendationError(
                f"Job ranking failed: {exc}"
            ) from exc

        try:
            response = RecommendationResponse.model_validate(response_dict)
        except Exception as exc:
            raise JobRecommendationError(
                f"Recommendation response validation failed: {exc}"
            ) from exc

        logger.info("Ranked %d recommendations.", len(response.recommendations))
        return response

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_query(self, profile: CandidateProfile) -> str:
        """Build a semantic search query string from the candidate profile."""
        skills = ", ".join(profile.skills)
        return (
            f"Preferred Role:\n{profile.preferred_role}\n\n"
            f"Skills:\n{skills}\n\n"
            f"Experience:\n{profile.experience} years\n\n"
            f"Education:\n{profile.education}\n\n"
            f"Location:\n{profile.location}"
        )

    def _retrieve_jobs(self, profile: CandidateProfile) -> list[Document]:
        """Query the vector store with MMR search using the candidate profile."""
        query = self._build_query(profile)
        return self._vector_store.mmr_search(query=query)
