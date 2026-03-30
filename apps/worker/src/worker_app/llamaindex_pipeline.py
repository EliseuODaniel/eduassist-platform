from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from fastembed import TextEmbedding
from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.vector_stores.qdrant import QdrantVectorStore
from pydantic import PrivateAttr
from qdrant_client import QdrantClient

from .config import Settings
from .pipeline import CorpusDocument, DocumentPipeline

REPO_ROOT = Path(__file__).resolve().parents[4]


class FastembedLlamaIndexEmbedding(BaseEmbedding):
    _embedder: TextEmbedding = PrivateAttr()

    def __init__(self, *, model_name: str) -> None:
        super().__init__(model_name=model_name)
        self._embedder = _build_embedder(model_name)

    def _embed_once(self, text: str) -> list[float]:
        return list(next(self._embedder.embed([text])))

    def _get_query_embedding(self, query: str) -> list[float]:
        return self._embed_once(query)

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return self._get_query_embedding(query)

    def _get_text_embedding(self, text: str) -> list[float]:
        return self._embed_once(text)

    async def _aget_text_embedding(self, text: str) -> list[float]:
        return self._get_text_embedding(text)


class LlamaIndexDocumentPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.base_pipeline = DocumentPipeline(settings)
        self.qdrant = QdrantClient(url=settings.qdrant_url)
        self.embed_model = FastembedLlamaIndexEmbedding(model_name=settings.document_embedding_model)

    def sync_demo_corpus(self) -> dict[str, Any]:
        corpus_root = self._resolve_corpus_root()
        storage_dir = self._resolve_storage_dir()
        storage_dir.mkdir(parents=True, exist_ok=True)

        documents = self.base_pipeline._load_corpus_documents(corpus_root)
        self.base_pipeline._ensure_minio_bucket()
        llamaindex_documents = [self._build_llamaindex_document(document, corpus_root=corpus_root) for document in documents]

        docstore = self._load_or_create_docstore(storage_dir=storage_dir)
        vector_store = QdrantVectorStore(
            collection_name=self.settings.llamaindex_qdrant_documents_collection,
            client=self.qdrant,
            text_key='text_content',
        )
        storage_context = StorageContext.from_defaults(docstore=docstore, vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context,
            embed_model=self.embed_model,
            transformations=[
                SentenceSplitter(
                    chunk_size=self.settings.llamaindex_chunk_size,
                    chunk_overlap=self.settings.llamaindex_chunk_overlap,
                )
            ],
        )

        existing_ref_docs = docstore.get_all_ref_doc_info() or {}
        desired_ref_doc_ids = {str(document.id_) for document in llamaindex_documents}
        stale_ref_doc_ids = sorted(set(existing_ref_docs.keys()) - desired_ref_doc_ids)
        for ref_doc_id in stale_ref_doc_ids:
            index.delete_ref_doc(ref_doc_id, delete_from_docstore=True)

        refresh_results = index.refresh_ref_docs(llamaindex_documents)
        storage_context.persist(persist_dir=str(storage_dir))
        self._write_manifest(
            storage_dir=storage_dir,
            documents=documents,
            refresh_results=refresh_results,
            stale_ref_doc_ids=stale_ref_doc_ids,
        )

        return {
            'document_count': len(documents),
            'ref_doc_count': len(llamaindex_documents),
            'upserted_count': sum(1 for item in refresh_results if item),
            'unchanged_count': sum(1 for item in refresh_results if not item),
            'deleted_count': len(stale_ref_doc_ids),
            'collection': self.settings.llamaindex_qdrant_documents_collection,
            'storage_dir': str(storage_dir),
        }

    def _resolve_corpus_root(self) -> Path:
        configured = Path(self.settings.document_corpus_dir)
        if configured.exists():
            return configured
        local_fallback = REPO_ROOT / 'data' / 'corpus'
        if local_fallback.exists():
            return local_fallback
        return configured

    def _resolve_storage_dir(self) -> Path:
        configured = Path(self.settings.llamaindex_storage_dir)
        if configured.is_absolute():
            try:
                configured.mkdir(parents=True, exist_ok=True)
                return configured
            except PermissionError:
                pass
        fallback = REPO_ROOT / '.cache' / 'llamaindex_storage'
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback

    def _load_or_create_docstore(self, *, storage_dir: Path) -> SimpleDocumentStore:
        docstore_path = storage_dir / 'docstore.json'
        if docstore_path.exists():
            return SimpleDocumentStore.from_persist_dir(str(storage_dir))
        return SimpleDocumentStore()

    def _build_llamaindex_document(self, document: CorpusDocument, *, corpus_root: Path) -> Document:
        storage_path = self.base_pipeline._upload_source_document(document)
        relative_source_path = str(document.source_path.relative_to(corpus_root))
        checksum = self.base_pipeline._slugify(relative_source_path)
        ref_doc_id = f'{document.document_set_slug}:{document.version_label}:{checksum}'
        metadata = {
            'document_title': document.title,
            'category': document.category,
            'audience': document.audience,
            'visibility': document.visibility,
            'version_label': document.version_label,
            'document_set_slug': document.document_set_slug,
            'document_set_title': document.document_set_title,
            'effective_from': document.effective_from.isoformat(),
            'storage_path': storage_path,
            'source_path': relative_source_path,
            'labels': json.dumps(document.labels, ensure_ascii=False, sort_keys=True),
        }
        return Document(
            id_=ref_doc_id,
            text=document.normalized_markdown,
            metadata=metadata,
            excluded_embed_metadata_keys=['labels'],
            excluded_llm_metadata_keys=['labels'],
        )

    def _write_manifest(
        self,
        *,
        storage_dir: Path,
        documents: list[CorpusDocument],
        refresh_results: list[bool],
        stale_ref_doc_ids: list[str],
    ) -> None:
        payload = {
            'document_count': len(documents),
            'upserted_count': sum(1 for item in refresh_results if item),
            'unchanged_count': sum(1 for item in refresh_results if not item),
            'deleted_count': len(stale_ref_doc_ids),
            'collection': self.settings.llamaindex_qdrant_documents_collection,
            'documents': [
                {
                    'title': document.title,
                    'document_set_slug': document.document_set_slug,
                    'version_label': document.version_label,
                    'visibility': document.visibility,
                }
                for document in documents
            ],
            'deleted_ref_doc_ids': stale_ref_doc_ids,
        }
        (storage_dir / 'manifest.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def _build_embedder(model_name: str) -> TextEmbedding:
    try:
        return TextEmbedding(model_name=model_name)
    except Exception as exc:
        message = str(exc)
        if 'NO_SUCHFILE' not in message and "File doesn't exist" not in message:
            raise
        shutil.rmtree('/tmp/fastembed_cache', ignore_errors=True)
        return TextEmbedding(model_name=model_name)
