from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


_ROOT_ENV_FILE = Path(__file__).resolve().parents[4] / '.env'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=('/workspace/.env', str(_ROOT_ENV_FILE), '.env'),
        env_ignore_empty=True,
        extra='ignore',
    )

    app_env: str = 'development'
    log_level: str = 'INFO'
    database_url: str = 'postgresql://eduassist:eduassist@postgres:5432/eduassist'
    minio_endpoint: str = 'http://minio:9000'
    minio_root_user: str = 'minioadmin'
    minio_root_password: str = 'minioadmin123'
    minio_bucket_documents: str = 'documents'
    qdrant_url: str = 'http://qdrant:6333'
    qdrant_documents_collection: str = 'school_documents'
    llamaindex_qdrant_documents_collection: str = 'school_documents_llamaindex'
    document_pipeline_backend: str = 'markdown'
    document_corpus_dir: str = '/workspace/data/corpus'
    document_embedding_model: str = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    worker_bootstrap_documents: bool = True
    worker_bootstrap_llamaindex_documents: bool = True
    llamaindex_storage_dir: str = '/tmp/eduassist_llamaindex_storage'
    llamaindex_chunk_size: int = 300
    llamaindex_chunk_overlap: int = 40

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
