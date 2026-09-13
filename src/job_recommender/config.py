"""
Application configuration using pydantic-settings.

Priority order for secrets:
  1. Streamlit Cloud  → st.secrets   (injected into os.environ at startup)
  2. Local / CI       → os.environ / .env file

Use `get_settings()` to obtain a cached singleton instance.
"""

import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _inject_streamlit_secrets() -> None:
    """
    Bridge Streamlit Cloud secrets into os.environ so pydantic-settings
    can read them like regular environment variables.

    On Streamlit Cloud, secrets defined in the dashboard are accessible via
    ``st.secrets`` but are NOT automatically placed in ``os.environ``.
    This function does that mapping once at startup.

    When running locally (where ``streamlit`` may not be imported or
    ``st.secrets`` is empty / unavailable), this is a silent no-op.
    """
    try:
        import streamlit as st  # noqa: PLC0415

        for key, value in st.secrets.items():
            if key not in os.environ:
                os.environ[key] = str(value)
    except Exception:  # noqa: BLE001
        # Not running on Streamlit, or secrets not configured — that's fine.
        pass


class Settings(BaseSettings):
    """
    Validated, type-safe application settings.

    Values are resolved in priority order:
    Streamlit secrets → environment variables → .env file → field defaults.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Gemini / LLM
    # ------------------------------------------------------------------
    google_api_key: str = Field(..., alias="GOOGLE_API_KEY")

    llm_model: str = Field(
        default="gemini-3.5-flash-lite",
        alias="LLM_MODEL",
    )

    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL",
    )

    # ------------------------------------------------------------------
    # ChromaDB
    # ------------------------------------------------------------------
    chroma_path: str = Field(default="chroma_db", alias="CHROMA_PATH")

    collection_name: str = Field(default="ai_jobs", alias="COLLECTION_NAME")

    top_k_results: int = Field(default=20, alias="TOP_K_RESULTS")

    fetch_k_results: int = Field(default=50, alias="FETCH_K_RESULTS")

    # ------------------------------------------------------------------
    # File paths
    # ------------------------------------------------------------------
    upload_folder: str = Field(default="uploads", alias="UPLOAD_FOLDER")

    cache_folder: str = Field(default="jobs_cache", alias="CACHE_FOLDER")

    # ------------------------------------------------------------------
    # Job API
    # ------------------------------------------------------------------
    jobs_per_page: int = Field(default=100, alias="JOBS_PER_PAGE")

    max_pages: int = Field(default=10, alias="MAX_PAGES")

    request_timeout: int = Field(default=30, alias="REQUEST_TIMEOUT")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached singleton Settings instance.

    Streamlit secrets are injected into os.environ before the first
    Settings() call so pydantic-settings can resolve them correctly.
    """
    _inject_streamlit_secrets()
    return Settings()