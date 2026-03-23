"""add document chunk fts index

Revision ID: f4a8f3945d39
Revises: d2b1ef6c8a90
Create Date: 2026-03-23 04:40:00.000000
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f4a8f3945d39'
down_revision: Union[str, Sequence[str], None] = 'd2b1ef6c8a90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        create index if not exists ix_document_chunks_fts
        on documents.document_chunks
        using gin (
          to_tsvector(
            'portuguese',
            coalesce(contextual_summary, '') || ' ' || text_content
          )
        )
        """
    )


def downgrade() -> None:
    op.execute('drop index if exists documents.ix_document_chunks_fts')
