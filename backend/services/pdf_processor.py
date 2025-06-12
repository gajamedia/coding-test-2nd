import os
from typing import List, Dict, Any
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import settings
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self):
        # Konfigurasi text splitter dari settings atau default
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=getattr(settings, "chunk_size", 1000),
            chunk_overlap=getattr(settings, "chunk_overlap", 100),
        )
        logger.info("PDFProcessor initialized with chunk_size=%s, chunk_overlap=%s",
                    self.text_splitter._chunk_size, self.text_splitter._chunk_overlap)

    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF and return page-wise content with metadata"""
        logger.info("Extracting text from PDF: %s", file_path)
        pages = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        pages.append({
                            "page": i + 1,
                            "content": text.strip()
                        })
        except Exception as e:
            logger.error("Failed to extract PDF: %s", e)
            raise e

        logger.info("Extracted %d pages from PDF", len(pages))
        return pages

    def split_into_chunks(self, pages_content: List[Dict[str, Any]]) -> List[Document]:
        """Split each page's text into smaller overlapping chunks"""
        logger.info("Splitting text into chunks...")
        all_chunks = []

        for page_data in pages_content:
            page = page_data["page"]
            text = page_data["content"]
            chunks = self.text_splitter.split_text(text)

            for chunk in chunks:
                doc = Document(
                    page_content=chunk,
                    metadata={"page": page, "source": f"page_{page}"}
                )
                all_chunks.append(doc)

        logger.info("Created %d chunks from %d pages", len(all_chunks), len(pages_content))
        return all_chunks

    def process_pdf(self, file_path: str) -> List[Document]:
        """Full pipeline: extract + chunk PDF into Document objects"""
        logger.info("Processing PDF: %s", file_path)
        pages_content = self.extract_text_from_pdf(file_path)
        documents = self.split_into_chunks(pages_content)
        logger.info("Finished processing PDF: %s. Total chunks: %d", file_path, len(documents))
        return documents
