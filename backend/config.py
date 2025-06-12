from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # OpenAI API configuration
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")

    # Vector database configuration
    vector_db_path: str = Field(default="./vector_store", alias="VECTOR_DB_PATH")
    vector_db_type: str = Field(default="chromadb", alias="VECTOR_DB_TYPE")

    # PDF upload path
    pdf_upload_path: str = Field(default="../data", alias="PDF_UPLOAD_PATH")

    # Embedding model configuration
    embedding_model: str = Field(default="text-embedding-ada-002", alias="EMBEDDING_MODEL")

    # LLM configuration
    llm_model: str = Field(default="gpt-3.5-turbo", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.1, alias="LLM_TEMPERATURE")
    max_tokens: int = Field(default=1000, alias="MAX_TOKENS")

    # Chunking configuration
    chunk_size: int = Field(default=1000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, alias="CHUNK_OVERLAP")

    # Retrieval configuration
    retrieval_k: int = Field(default=5, alias="RETRIEVAL_K")
    similarity_threshold: float = Field(default=0.7, alias="SIMILARITY_THRESHOLD")

    # Server configuration
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    debug: bool = Field(default=True, alias="DEBUG")

    # CORS configuration
    allowed_origins: List[str] = Field(default=["http://localhost:3000", "http://127.0.0.1:3000"], alias="ALLOWED_ORIGINS")

    # Logging configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "allow",
        "populate_by_name": True,  # agar bisa gunakan nama field di kode
    }


settings = Settings()
