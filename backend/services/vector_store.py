from typing import List, Tuple
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings  # Bisa diganti HuggingFaceEmbeddings
from config import settings
import logging
import os

logger = logging.getLogger(__name__)


class VectorStoreService:
    def __init__(self):
        self.collection_name = "rag_collection"
        self.persist_directory = "chroma_db"
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)

        # Inisialisasi atau muat kembali dari disk
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        logger.info("Chroma vector store initialized at '%s'", self.persist_directory)

    def add_documents(self, documents: List[Document]) -> None:
        """Menambahkan dokumen ke vector store dan menyimpannya"""
        logger.info("Menambahkan %d dokumen ke Chroma", len(documents))
        self.vectorstore.add_documents(documents)
        self.vectorstore.persist()
        logger.info("Dokumen berhasil ditambahkan dan disimpan.")

    def similarity_search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Melakukan pencarian similarity dan mengembalikan dokumen + skor"""
        logger.info("Melakukan similarity search untuk query: %s", query)
        results = self.vectorstore.similarity_search(query, k=k)
        logger.info("Ditemukan %d dokumen yang relevan", len(results))
        return results

    def delete_documents(self, document_ids: List[str]) -> None:
        """Menghapus dokumen berdasarkan ID-nya"""
        logger.info("Menghapus dokumen dengan ID: %s", document_ids)
        self.vectorstore.delete(ids=document_ids)
        self.vectorstore.persist()
        logger.info("Dokumen berhasil dihapus.")

    def get_document_count(self) -> int:
        """Mengembalikan total jumlah dokumen dalam koleksi"""
        count = self.vectorstore._collection.count()
        logger.info("Jumlah dokumen dalam koleksi: %d", count)
        return count
