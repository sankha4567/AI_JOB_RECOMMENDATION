from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


class PDFReader:
    """
    Utility class for reading PDF files.
    """

    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """
        Extracts all text from a PDF.

        Args:
            pdf_path: Path to PDF

        Returns:
            Complete PDF text
        """

        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        loader = PyPDFLoader(str(path))

        documents = loader.load()

        text = "\n\n".join(
            document.page_content.strip()
            for document in documents
            if document.page_content.strip()
        )

        return text

    @staticmethod
    def page_count(pdf_path: str) -> int:

        loader = PyPDFLoader(pdf_path)

        documents = loader.load()

        return len(documents)