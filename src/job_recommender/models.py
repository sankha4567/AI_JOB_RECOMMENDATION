from typing import List

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    """
    Candidate profile extracted from the resume.
    """

    name: str = ""

    email: str = ""

    phone: str = ""

    location: str = ""

    preferred_role: str = ""

    experience: int = 0

    education: str = ""

    skills: List[str] = Field(default_factory=list)


class Job(BaseModel):
    """
    Standard Job model.

    Every Job API should be converted into this format.
    """

    id: str

    title: str

    company: str

    location: str

    description: str

    skills: List[str]

    url: str


class JobRecommendation(BaseModel):
    """
    Recommendation returned by Gemini.
    """

    title: str

    company: str

    location: str

    match_percentage: int

    reason: str

    missing_skills: List[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    """
    Final response returned by recommender.
    """

    recommendations: List[JobRecommendation]