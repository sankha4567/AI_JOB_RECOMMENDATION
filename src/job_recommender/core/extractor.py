"""
Profile extractor — uses a Gemini LLM to parse resume text into a
structured CandidateProfile.
"""

import json
import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from job_recommender.config import get_settings
from job_recommender.exceptions import ProfileExtractionError
from job_recommender.models import CandidateProfile
from job_recommender.prompts.templates import PROFILE_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


class ProfileExtractor:
    """
    Extracts a structured CandidateProfile from raw resume text using an LLM.
    """

    def __init__(self) -> None:
        settings = get_settings()

        self._llm = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.google_api_key,
            temperature=0,
        )

        self._chain = (
            ChatPromptTemplate.from_template(PROFILE_EXTRACTION_PROMPT)
            | self._llm
            | StrOutputParser()
        )

    def extract(self, resume_text: str) -> CandidateProfile:
        """
        Extract candidate information from resume text.

        Args:
            resume_text: Plain text content of the resume.

        Returns:
            A validated CandidateProfile instance.

        Raises:
            ProfileExtractionError: If the LLM returns invalid or unparseable JSON.
        """
        logger.info("Extracting candidate profile from resume text.")

        try:
            raw: str = self._chain.invoke({"resume": resume_text})
            # Strip potential markdown fences that slip through
            clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            profile_dict: dict = json.loads(clean)
        except json.JSONDecodeError as exc:
            raise ProfileExtractionError(
                f"LLM returned non-JSON response: {exc}"
            ) from exc
        except Exception as exc:
            raise ProfileExtractionError(
                f"Profile extraction failed: {exc}"
            ) from exc

        try:
            profile = CandidateProfile.model_validate(profile_dict)
        except Exception as exc:
            raise ProfileExtractionError(
                f"Profile validation failed: {exc}"
            ) from exc

        logger.info("Profile extracted for candidate: %s", profile.name)
        return profile
