from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api_core.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DocumentSet(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'document_sets'
    __table_args__ = {'schema': 'documents'}

    slug: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    visibility: Mapped[str] = mapped_column(String(30), nullable=False)


class Document(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'documents'
    __table_args__ = {'schema': 'documents'}

    document_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('documents.document_sets.id'),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    audience: Mapped[str] = mapped_column(String(60), nullable=False)
    visibility: Mapped[str] = mapped_column(String(30), nullable=False)


class DocumentVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'document_versions'
    __table_args__ = (
        UniqueConstraint('document_id', 'version_label'),
        {'schema': 'documents'},
    )

    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('documents.documents.id'), nullable=False)
    version_label: Mapped[str] = mapped_column(String(20), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(80), nullable=False)
    effective_from: Mapped[date] = mapped_column(nullable=False)
    effective_to: Mapped[date | None] = mapped_column()


class DocumentChunk(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'document_chunks'
    __table_args__ = (
        UniqueConstraint('document_version_id', 'chunk_index'),
        {'schema': 'documents'},
    )

    document_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('documents.document_versions.id'),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    contextual_summary: Mapped[str | None] = mapped_column(Text)
    visibility: Mapped[str] = mapped_column(String(30), nullable=False)


class RetrievalLabel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'retrieval_labels'
    __table_args__ = {'schema': 'documents'}

    document_chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('documents.document_chunks.id'),
        nullable=False,
    )
    label_type: Mapped[str] = mapped_column(String(40), nullable=False)
    label_value: Mapped[str] = mapped_column(String(120), nullable=False)
