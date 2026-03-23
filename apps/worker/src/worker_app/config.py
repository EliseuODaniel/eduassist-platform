from __future__ import annotations

from functools import lru_cache
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    app_env: str = 'development'
    log_level: str = 'INFO'
    database_url: str = 'postgresql://eduassist:eduassist@postgres:5432/eduassist'
    minio_endpoint: str = 'http://minio:9000'
    minio_root_user: str = 'minioadmin'
    minio_root_password: str = 'minioadmin123'
    minio_bucket_documents: str = 'documents'
    qdrant_url: str = 'http://qdrant:6333'
    qdrant_documents_collection: str = 'school_documents'
    document_pipeline_backend: str = 'markdown'
    document_corpus_dir: str = '/workspace/data/corpus'
    document_embedding_model: str = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    worker_bootstrap_documents: bool = True

    @property
    def minio_host(self) -> str:
        parsed = urlparse(self.minio_endpoint)
        return parsed.netloc or parsed.path

    @property
    def minio_secure(self) -> bool:
        parsed = urlparse(self.minio_endpoint)
        return parsed.scheme == 'https'


@lru_cache
def get_settings() -> Settings:
    return Settings()
