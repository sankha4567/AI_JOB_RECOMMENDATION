"""
PDF reading utilities.

Supports reading from a file-system path or an in-memory bytes object,
making it compatible with both CLI usage and Streamlit file uploads.
"""

import io
import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader

from job_recommender.exceptions import ResumeParseError

logger = logging.getLogger(__name__)


class PDFReader:
    """Utility class for extracting text content from PDF files."""

    @staticmethod
    def extract_text_from_path(pdf_path: str | Path) -> str:
        """
        Extract all text from a PDF at the given file-system path.

        Args:
            pdf_path: Absolute or relative path to the PDF file.

        Returns:
            Concatenated plain text from all pages.

        Raises:
            ResumeParseError: If the file is missing or cannot be parsed.
        """
        path = Path(pdf_path)

        if not path.exists():
            raise ResumeParseError(f"PDF not found: {pdf_path}")

        logger.info("Extracting text from PDF path: %s", path)

        try:
            loader = PyPDFLoader(str(path))
            documents = loader.load()
        except Exception as exc:
            raise ResumeParseError(
                f"Failed to load PDF at '{pdf_path}': {exc}"
            ) from exc

        return PDFReader._join_pages(documents)

    @staticmethod
    def extract_text_from_bytes(pdf_bytes: bytes, filename: str = "resume.pdf") -> str:
        """
        Extract all text from a PDF supplied as raw bytes (e.g., Streamlit upload).

        Args:
            pdf_bytes: Raw PDF file content.
            filename:  Optional display name used in error messages.

        Returns:
            Concatenated plain text from all pages.

        Raises:
            ResumeParseError: If the bytes cannot be parsed as a PDF.
        """
        logger.info("Extracting text from in-memory PDF: %s", filename)

        try:
            import pypdf

            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            pages = [
                page.extract_text() or ""
                for page in reader.pages
            ]
        except Exception as exc:
            raise ResumeParseError(
                f"Failed to parse PDF bytes for '{filename}': {exc}"
            ) from exc

        text = "\n\n".join(p.strip() for p in pages if p.strip())

        if not text:
            raise ResumeParseError(
                f"No extractable text found in '{filename}'. "
                "The PDF may be scanned or image-based."
            )

        return text

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _join_pages(documents: list) -> str:
        """Join LangChain document page contents into a single string."""
        text = "\n\n".join(
            doc.page_content.strip()
            for doc in documents
            if doc.page_content.strip()
        )

        if not text:
            raise ResumeParseError("No extractable text found in the PDF.")

        return text
