from __future__ import annotations

import hashlib
import io
import uuid
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from tempfile import NamedTemporaryFile

import psycopg
import yaml
from fastembed import TextEmbedding
from minio import Minio
from psycopg.rows import dict_row
from qdrant_client import QdrantClient, models

from .config import Settings


@dataclass(slots=True)
class CorpusDocument:
    source_path: Path
    document_set_slug: str
    document_set_title: str
    title: str
    category: str
    audience: str
    visibility: str
    version_label: str
    effective_from: date
    labels: dict[str, list[str]]
    raw_content: str
    normalized_markdown: str


@dataclass(slots=True)
class DocumentChunkRecord:
    chunk_index: int
    text_content: str
    contextual_summary: str
    visibility: str
    labels: dict[str, list[str]]


class DocumentPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embedder = TextEmbedding(model_name=settings.document_embedding_model)
        self.qdrant = QdrantClient(url=settings.qdrant_url)
        self.minio = Minio(
            settings.minio_host,
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            secure=settings.minio_secure,
        )

    def sync_demo_corpus(self) -> dict[str, int | str]:
        documents = self._load_corpus_documents(Path(self.settings.document_corpus_dir))
        self._ensure_minio_bucket()
        indexed = self._replace_document_catalog(documents)
        self._rebuild_qdrant_index(indexed)
        return {
            'document_count': len(documents),
            'chunk_count': sum(len(item['chunks']) for item in indexed),
            'collection': self.settings.qdrant_documents_collection,
        }

    def _load_corpus_documents(self, root: Path) -> list[CorpusDocument]:
        documents: list[CorpusDocument] = []
        for source_path in sorted(root.rglob('*.md')):
            metadata, raw_body = self._parse_frontmatter(source_path)
            normalized_markdown = self._convert_with_docling(source_path.suffix, raw_body)
            documents.append(
                CorpusDocument(
                    source_path=source_path,
                    document_set_slug=str(metadata['document_set_slug']),
                    document_set_title=str(metadata['document_set_title']),
                    title=str(metadata['title']),
                    category=str(metadata['category']),
                    audience=str(metadata['audience']),
                    visibility=str(metadata['visibility']),
                    version_label=str(metadata['version_label']),
                    effective_from=date.fromisoformat(str(metadata['effective_from'])),
                    labels={str(key): [str(item) for item in value] for key, value in dict(metadata.get('labels', {})).items()},
                    raw_content=raw_body,
                    normalized_markdown=normalized_markdown,
                )
            )
        return documents

    def _parse_frontmatter(self, path: Path) -> tuple[dict[str, object], str]:
        content = path.read_text(encoding='utf-8')
        if not content.startswith('---\n'):
            raise ValueError(f'missing frontmatter in {path}')

        _, _, remainder = content.partition('---\n')
        frontmatter_text, separator, body = remainder.partition('\n---\n')
        if not separator:
            raise ValueError(f'invalid frontmatter in {path}')

        metadata = yaml.safe_load(frontmatter_text) or {}
        return metadata, body.strip()

    def _convert_with_docling(self, suffix: str, body: str) -> str:
        if self.settings.document_pipeline_backend != 'docling':
            return body.strip()

        try:
            from docling.document_converter import DocumentConverter

            with NamedTemporaryFile('w', suffix=suffix, encoding='utf-8', delete=True) as temp_file:
                temp_file.write(body)
                temp_file.flush()
                result = DocumentConverter().convert(temp_file.name)
                return result.document.export_to_markdown().strip()
        except Exception:
            return body.strip()

    def _chunk_document(self, document: CorpusDocument) -> list[DocumentChunkRecord]:
        chunks: list[DocumentChunkRecord] = []
        headings: list[str] = []
        buffer: list[str] = []

        def flush() -> None:
            text = '\n'.join(line for line in buffer if line.strip()).strip()
            if not text:
                buffer.clear()
                return
            summary = ' > '.join(headings[-2:]) if headings else document.title
            pieces = self._split_long_text(text)
            for piece in pieces:
                chunks.append(
                    DocumentChunkRecord(
                        chunk_index=len(chunks),
                        text_content=piece,
                        contextual_summary=summary,
                        visibility=document.visibility,
                        labels=document.labels,
                    )
                )
            buffer.clear()

        for raw_line in document.normalized_markdown.splitlines():
            line = raw_line.strip()
            if not line:
                if buffer:
                    buffer.append('')
                continue
            if line.startswith('#'):
                flush()
                heading = line.lstrip('#').strip()
                if heading:
                    headings.append(heading)
                continue
            buffer.append(line)

        flush()
        return chunks

    def _split_long_text(self, text: str, max_chars: int = 900) -> list[str]:
        if len(text) <= max_chars:
            return [text]

        paragraphs = [part.strip() for part in text.split('\n\n') if part.strip()]
        chunks: list[str] = []
        current = ''

        for paragraph in paragraphs:
            candidate = paragraph if not current else f'{current}\n\n{paragraph}'
            if len(candidate) <= max_chars:
                current = candidate
                continue
            if current:
                chunks.append(current)
            current = paragraph

        if current:
            chunks.append(current)
        return chunks

    def _ensure_minio_bucket(self) -> None:
        if not self.minio.bucket_exists(self.settings.minio_bucket_documents):
            self.minio.make_bucket(self.settings.minio_bucket_documents)

    def _replace_document_catalog(self, documents: list[CorpusDocument]) -> list[dict[str, object]]:
        grouped: dict[str, list[CorpusDocument]] = {}
        for document in documents:
            grouped.setdefault(document.document_set_slug, []).append(document)

        indexed_documents: list[dict[str, object]] = []
        with psycopg.connect(self.settings.database_url, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                for document_set_slug, set_documents in grouped.items():
                    document_set_title = set_documents[0].document_set_title
                    visibility = set_documents[0].visibility
                    document_set_id = self._ensure_document_set(cursor, document_set_slug, document_set_title, visibility)
                    self._delete_existing_document_set_contents(cursor, document_set_id)

                    for document in set_documents:
                        storage_path = self._upload_source_document(document)
                        document_id = self._insert_document(cursor, document_set_id, document)
                        document_version_id = self._insert_document_version(cursor, document_id, document, storage_path)
                        chunks = self._chunk_document(document)
                        chunk_records = self._insert_chunks(cursor, document_version_id, document, chunks)
                        indexed_documents.append(
                            {
                                'document': document,
                                'document_id': document_id,
                                'document_version_id': document_version_id,
                                'storage_path': storage_path,
                                'chunks': chunk_records,
                            }
                        )
            connection.commit()

        return indexed_documents

    def _ensure_document_set(self, cursor: psycopg.Cursor, slug: str, title: str, visibility: str) -> uuid.UUID:
        document_set_id = uuid.uuid4()
        cursor.execute(
            """
            insert into documents.document_sets (id, slug, title, visibility)
            values (%s, %s, %s, %s)
            on conflict (slug)
            do update set
              title = excluded.title,
              visibility = excluded.visibility,
              updated_at = now()
            returning id
            """,
            (document_set_id, slug, title, visibility),
        )
        row = cursor.fetchone()
        return row['id']

    def _delete_existing_document_set_contents(self, cursor: psycopg.Cursor, document_set_id: uuid.UUID) -> None:
        cursor.execute(
            """
            delete from documents.retrieval_labels
            where document_chunk_id in (
              select chunk.id
              from documents.document_chunks chunk
              join documents.document_versions version on version.id = chunk.document_version_id
              join documents.documents document on document.id = version.document_id
              where document.document_set_id = %s
            )
            """,
            (document_set_id,),
        )
        cursor.execute(
            """
            delete from documents.document_chunks
            where document_version_id in (
              select version.id
              from documents.document_versions version
              join documents.documents document on document.id = version.document_id
              where document.document_set_id = %s
            )
            """,
            (document_set_id,),
        )
        cursor.execute(
            """
            delete from documents.document_versions
            where document_id in (
              select id from documents.documents where document_set_id = %s
            )
            """,
            (document_set_id,),
        )
        cursor.execute('delete from documents.documents where document_set_id = %s', (document_set_id,))

    def _insert_document(self, cursor: psycopg.Cursor, document_set_id: uuid.UUID, document: CorpusDocument) -> uuid.UUID:
        document_id = uuid.uuid4()
        cursor.execute(
            """
            insert into documents.documents (
              id, document_set_id, title, category, audience, visibility
            ) values (%s, %s, %s, %s, %s, %s)
            """,
            (
                document_id,
                document_set_id,
                document.title,
                document.category,
                document.audience,
                document.visibility,
            ),
        )
        return document_id

    def _insert_document_version(
        self,
        cursor: psycopg.Cursor,
        document_id: uuid.UUID,
        document: CorpusDocument,
        storage_path: str,
    ) -> uuid.UUID:
        document_version_id = uuid.uuid4()
        cursor.execute(
            """
            insert into documents.document_versions (
              id, document_id, version_label, storage_path, mime_type, effective_from
            ) values (%s, %s, %s, %s, %s, %s)
            returning id
            """,
            (
                document_version_id,
                document_id,
                document.version_label,
                storage_path,
                'text/markdown',
                document.effective_from,
            ),
        )
        row = cursor.fetchone()
        return row['id']

    def _insert_chunks(
        self,
        cursor: psycopg.Cursor,
        document_version_id: uuid.UUID,
        document: CorpusDocument,
        chunks: list[DocumentChunkRecord],
    ) -> list[dict[str, object]]:
        records: list[dict[str, object]] = []
        for chunk in chunks:
            chunk_id = uuid.uuid4()
            cursor.execute(
                """
                insert into documents.document_chunks (
                  id, document_version_id, chunk_index, text_content, contextual_summary, visibility
                ) values (%s, %s, %s, %s, %s, %s)
                returning id
                """,
                (
                    chunk_id,
                    document_version_id,
                    chunk.chunk_index,
                    chunk.text_content,
                    chunk.contextual_summary,
                    chunk.visibility,
                ),
            )
            row = cursor.fetchone()
            stored_chunk_id = row['id']
            for label_type, values in chunk.labels.items():
                for label_value in values:
                    cursor.execute(
                        """
                        insert into documents.retrieval_labels (
                          id, document_chunk_id, label_type, label_value
                        ) values (%s, %s, %s, %s)
                        """,
                        (uuid.uuid4(), stored_chunk_id, label_type, label_value),
                    )
            records.append(
                {
                    'chunk_id': stored_chunk_id,
                    'chunk_index': chunk.chunk_index,
                    'text_content': chunk.text_content,
                    'contextual_summary': chunk.contextual_summary,
                    'visibility': chunk.visibility,
                    'document_title': document.title,
                    'category': document.category,
                    'audience': document.audience,
                    'labels': chunk.labels,
                }
            )
        return records

    def _upload_source_document(self, document: CorpusDocument) -> str:
        body_bytes = document.source_path.read_bytes()
        object_path = (
            f'corpus/{document.visibility}/{document.document_set_slug}/'
            f'{self._slugify(document.title)}/{document.version_label}.md'
        )
        self.minio.put_object(
            self.settings.minio_bucket_documents,
            object_path,
            io.BytesIO(body_bytes),
            length=len(body_bytes),
            content_type='text/markdown',
        )
        return object_path

    def _rebuild_qdrant_index(self, indexed_documents: list[dict[str, object]]) -> None:
        collection = self.settings.qdrant_documents_collection
        if self.qdrant.collection_exists(collection):
            self.qdrant.delete_collection(collection)

        payloads: list[dict[str, object]] = []
        ids: list[str] = []
        texts: list[str] = []
        for item in indexed_documents:
            document: CorpusDocument = item['document']
            for chunk in item['chunks']:
                chunk_id = str(chunk['chunk_id'])
                ids.append(chunk_id)
                texts.append(chunk['text_content'])
                payloads.append(
                    {
                        'chunk_id': chunk_id,
                        'chunk_index': chunk['chunk_index'],
                        'document_title': chunk['document_title'],
                        'category': chunk['category'],
                        'audience': chunk['audience'],
                        'visibility': chunk['visibility'],
                        'contextual_summary': chunk['contextual_summary'],
                        'text_content': chunk['text_content'],
                        'storage_path': item['storage_path'],
                        'version_label': document.version_label,
                        'document_set_slug': document.document_set_slug,
                        'source_checksum': hashlib.sha256(document.raw_content.encode('utf-8')).hexdigest(),
                        'labels': chunk['labels'],
                    }
                )

        embeddings = list(self.embedder.embed(texts))
        if not embeddings:
            self.qdrant.create_collection(
                collection_name=collection,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )
            return

        self.qdrant.create_collection(
            collection_name=collection,
            vectors_config=models.VectorParams(size=len(embeddings[0]), distance=models.Distance.COSINE),
        )
        points = [
            models.PointStruct(id=point_id, vector=vector.tolist(), payload=payload)
            for point_id, vector, payload in zip(ids, embeddings, payloads, strict=True)
        ]
        self.qdrant.upsert(collection_name=collection, points=points)

    def _slugify(self, value: str) -> str:
        normalized = ''.join(char.lower() if char.isalnum() else '-' for char in value)
        while '--' in normalized:
            normalized = normalized.replace('--', '-')
        return normalized.strip('-')
