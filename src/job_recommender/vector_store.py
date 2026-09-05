from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from job_recommender.config import (
    CHROMA_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K_RESULTS,
    FETCH_K_RESULTS
)


class VectorStore:

    def __init__(self):

        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={
                "device": "cpu"
            },
            encode_kwargs={
                "normalize_embeddings": True
            }
        )

        self.db = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=CHROMA_PATH,
            embedding_function=self.embeddings
        )

    def add_job(self, document, job_id):

        self.db.add_documents(
            documents=[document],
            ids=[job_id]
        )

    def add_jobs(self, documents, ids):

        self.db.add_documents(
            documents=documents,
            ids=ids
        )

    def job_exists(self, job_id):

        result = self.db.get(
            ids=[job_id]
        )

        return len(result["ids"]) > 0

    def get_metadata(self, job_id):

        result = self.db.get(
            ids=[job_id],
            include=["metadatas"]
        )

        if not result["metadatas"]:
            return None

        return result["metadatas"][0]

    def update_job(self, document, job_id):

        self.db.delete(
            ids=[job_id]
        )

        self.db.add_documents(
            documents=[document],
            ids=[job_id]
        )

    def delete_job(self, job_id):

        self.db.delete(
            ids=[job_id]
        )

    def similarity_search(
        self,
        query,
        k=TOP_K_RESULTS
    ):

        return self.db.similarity_search(
            query=query,
            k=k
        )

    def mmr_search(
        self,
        query,
        k=TOP_K_RESULTS,
        fetch_k=FETCH_K_RESULTS
    ):

        return self.db.max_marginal_relevance_search(
            query=query,
            k=k,
            fetch_k=fetch_k
        )

    def count(self):

        return self.db._collection.count()