import json

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from job_recommender.config import (
    GOOGLE_API_KEY,
    LLM_MODEL
)

from job_recommender.models import CandidateProfile
from job_recommender.prompts import PROFILE_EXTRACTION_PROMPT


class ProfileExtractor:

    def __init__(self):

        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0
        )

        self.prompt = ChatPromptTemplate.from_template(
            PROFILE_EXTRACTION_PROMPT
        )

        self.parser = StrOutputParser()

        self.chain = (
            self.prompt
            | self.llm
            | self.parser
        )

    def extract(self, resume_text: str) -> CandidateProfile:
        """
        Extract candidate information from resume.
        """

        response = self.chain.invoke(
            {
                "resume": resume_text
            }
        )

        profile_dict = json.loads(response)

        return CandidateProfile.model_validate(
            profile_dict
        )