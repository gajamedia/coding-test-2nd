from typing import List, Dict, Any
from langchain.schema import Document
from services.vector_store import VectorStoreService
from config import settings
import logging
import openai  # ganti jika pakai LLM lain

logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self, vector_store: VectorStoreService):
        self.vector_store = vector_store
        self.top_k = getattr(settings, "top_k", 5)
        self.similarity_threshold = getattr(settings, "similarity_threshold", 0.7)

        # Set API key jika pakai OpenAI
        openai.api_key = settings.openai_api_key

        logger.info("RAGPipeline initialized.")

    def generate_answer(self, question: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Main RAG method: retrieve -> build context -> call LLM"""
        logger.info("Generating answer for question: %s", question)
        
        retrieved_docs = self._retrieve_documents(question)
        context = self._generate_context(retrieved_docs)
        answer = self._generate_llm_response(question, context, chat_history)

        return {
            "answer": answer,
            "sources": [
                {
                    "content": doc.page_content,
                    "page": doc.metadata.get("page", -1),
                    "score": doc.metadata.get("score", 0.0),
                    "metadata": doc.metadata
                } for doc in retrieved_docs
            ]
        }

    def _retrieve_documents(self, query: str) -> List[Document]:
        """Retrieve top-k relevant documents from vector store"""
        logger.info("Retrieving documents for query: %s", query)
        results = self.vector_store.similarity_search(query, k=self.top_k)
        filtered = []

        for doc, score in results:
            if score >= self.similarity_threshold:
                doc.metadata["score"] = score
                filtered.append(doc)

        logger.info("Retrieved %d relevant documents", len(filtered))
        return filtered

    def _generate_context(self, documents: List[Document]) -> str:
        """Concatenate document content as context"""
        logger.debug("Generating context from documents...")
        return "\n\n".join([doc.page_content for doc in documents])

    def _generate_llm_response(self, question: str, context: str, chat_history: List[Dict[str, str]] = None) -> str:
        """Call LLM API to generate response based on context + question"""
        logger.debug("Generating LLM response...")

        prompt = self._build_prompt(question, context, chat_history)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # atau "gpt-3.5-turbo"
                messages=prompt,
                temperature=0.3,
                max_tokens=512,
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error("LLM generation failed: %s", str(e))
            return "Maaf, saya tidak dapat memberikan jawaban saat ini."

    def _build_prompt(self, question: str, context: str, chat_history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """Builds a chat-style prompt for OpenAI API"""
        messages = [{"role": "system", "content": "You are a financial analyst AI that answers questions based on given documents."}]
        
        if chat_history:
            for turn in chat_history:
                messages.append({"role": "user", "content": turn["user"]})
                messages.append({"role": "assistant", "content": turn["assistant"]})
        
        messages.append({
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}"
        })
        return messages
