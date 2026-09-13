"""
Custom exceptions for the AI Job Recommender application.
"""


class JobRecommenderError(Exception):
    """Base exception for all job recommender errors."""


class ResumeParseError(JobRecommenderError):
    """Raised when a PDF resume cannot be read or parsed."""


class ProfileExtractionError(JobRecommenderError):
    """Raised when the LLM fails to extract a structured profile from resume text."""


class JobRecommendationError(JobRecommenderError):
    """Raised when the LLM fails to produce valid job recommendations."""


class VectorStoreError(JobRecommenderError):
    """Raised when a ChromaDB operation fails."""


class JobAPIError(JobRecommenderError):
    """Raised when a job API request fails unexpectedly."""
