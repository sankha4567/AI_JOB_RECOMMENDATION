"""
Pydantic data models for the AI Job Recommender.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    """Candidate profile extracted from a resume."""

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
    Normalised job listing.

    Every external job API response must be converted into this schema
    before being stored in the vector store.
    """

    id: str
    title: str
    company: str
    location: str
    description: str
    skills: List[str] = Field(default_factory=list)
    url: str = ""


class JobRecommendation(BaseModel):
    """A single AI-ranked job recommendation."""

    title: str
    company: str
    location: str
    url: str = ""
    match_percentage: int = Field(ge=0, le=100)
    reason: str
    missing_skills: List[str] = Field(default_factory=list)
    learning_topics: List[str] = Field(default_factory=list)
    should_apply: bool = True


class RecommendationResponse(BaseModel):
    """Wrapper returned by the recommender containing all ranked jobs."""

    recommendations: List[JobRecommendation] = Field(default_factory=list)