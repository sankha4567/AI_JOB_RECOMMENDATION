"""
Vector store wrapper around ChromaDB using LangChain.
"""

import logging
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from job_recommender.config import get_settings
from job_recommender.exceptions import VectorStoreError

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Thin wrapper around a ChromaDB collection that handles embedding
    and CRUD operations for job documents.
    """

    def __init__(self) -> None:
        settings = get_settings()

        logger.info(
            "Initialising VectorStore (collection=%s, path=%s)",
            settings.collection_name,
            settings.chroma_path,
        )

        self._top_k = settings.top_k_results
        self._fetch_k = settings.fetch_k_results

        embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        self._db = Chroma(
            collection_name=settings.collection_name,
            persist_directory=settings.chroma_path,
            embedding_function=embeddings,
        )

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def add_job(self, document: Document, job_id: str) -> None:
        """Add a single job document to the store."""
        try:
            self._db.add_documents(documents=[document], ids=[job_id])
            logger.debug("Added job: %s", job_id)
        except Exception as exc:
            raise VectorStoreError(f"Failed to add job '{job_id}': {exc}") from exc

    def add_jobs(self, documents: list[Document], ids: list[str]) -> None:
        """Batch-add multiple job documents."""
        try:
            self._db.add_documents(documents=documents, ids=ids)
            logger.info("Batch-added %d jobs.", len(ids))
        except Exception as exc:
            raise VectorStoreError(f"Batch add failed: {exc}") from exc

    def update_job(self, document: Document, job_id: str) -> None:
        """Replace an existing job document (delete + re-add)."""
        self.delete_job(job_id)
        self.add_job(document, job_id)
        logger.debug("Updated job: %s", job_id)

    def delete_job(self, job_id: str) -> None:
        """Remove a job document from the store."""
        try:
            self._db.delete(ids=[job_id])
        except Exception as exc:
            raise VectorStoreError(f"Failed to delete job '{job_id}': {exc}") from exc

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def job_exists(self, job_id: str) -> bool:
        """Return True if a document with the given ID already exists."""
        result = self._db.get(ids=[job_id])
        return len(result["ids"]) > 0

    def get_metadata(self, job_id: str) -> dict[str, Any] | None:
        """Return the metadata dict for a job, or None if not found."""
        result = self._db.get(ids=[job_id], include=["metadatas"])
        if not result["metadatas"]:
            return None
        return result["metadatas"][0]

    def similarity_search(
        self,
        query: str,
        k: int | None = None,
    ) -> list[Document]:
        """Cosine-similarity search. Returns the top-k most similar documents."""
        return self._db.similarity_search(query=query, k=k or self._top_k)

    def mmr_search(
        self,
        query: str,
        k: int | None = None,
        fetch_k: int | None = None,
    ) -> list[Document]:
        """
        Maximum Marginal Relevance search.

        Balances relevance and diversity in the returned documents.
        """
        return self._db.max_marginal_relevance_search(
            query=query,
            k=k or self._top_k,
            fetch_k=fetch_k or self._fetch_k,
        )

    def count(self) -> int:
        """Return the total number of documents in the collection."""
        return self._db._collection.count()
