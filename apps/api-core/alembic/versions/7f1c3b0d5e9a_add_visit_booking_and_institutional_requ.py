"""add visit booking and institutional request workflows

Revision ID: 7f1c3b0d5e9a
Revises: e6d4c9a4b2f1
Create Date: 2026-03-24 02:35:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '7f1c3b0d5e9a'
down_revision: str | Sequence[str] | None = 'e6d4c9a4b2f1'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'visit_bookings',
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('requester_user_id', sa.UUID(), nullable=True),
        sa.Column('linked_handoff_id', sa.UUID(), nullable=True),
        sa.Column('protocol_code', sa.String(length=40), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('audience_name', sa.String(length=160), nullable=True),
        sa.Column('audience_contact', sa.String(length=255), nullable=True),
        sa.Column('interested_segment', sa.String(length=80), nullable=True),
        sa.Column('preferred_date', sa.Date(), nullable=True),
        sa.Column('preferred_window', sa.String(length=80), nullable=True),
        sa.Column('attendee_count', sa.Integer(), nullable=False),
        sa.Column('slot_label', sa.String(length=120), nullable=True),
        sa.Column('notes', sa.Text(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['conversation_id'],
            ['conversation.conversations.id'],
            name=op.f('fk_visit_bookings_conversation_id_conversations'),
        ),
        sa.ForeignKeyConstraint(
            ['requester_user_id'],
            ['identity.users.id'],
            name=op.f('fk_visit_bookings_requester_user_id_users'),
        ),
        sa.ForeignKeyConstraint(
            ['linked_handoff_id'],
            ['conversation.handoffs.id'],
            name=op.f('fk_visit_bookings_linked_handoff_id_handoffs'),
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_visit_bookings')),
        sa.UniqueConstraint('protocol_code', name=op.f('uq_visit_bookings_protocol_code')),
        schema='conversation',
    )
    op.create_index(
        op.f('ix_visit_bookings_conversation_id'),
        'visit_bookings',
        ['conversation_id'],
        unique=False,
        schema='conversation',
    )
    op.create_index(
        op.f('ix_visit_bookings_linked_handoff_id'),
        'visit_bookings',
        ['linked_handoff_id'],
        unique=False,
        schema='conversation',
    )

    op.create_table(
        'institutional_requests',
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('requester_user_id', sa.UUID(), nullable=True),
        sa.Column('linked_handoff_id', sa.UUID(), nullable=True),
        sa.Column('protocol_code', sa.String(length=40), nullable=False),
        sa.Column('target_area', sa.String(length=60), nullable=False),
        sa.Column('category', sa.String(length=60), nullable=False),
        sa.Column('subject', sa.String(length=160), nullable=False),
        sa.Column('details', sa.Text(), nullable=False),
        sa.Column('requester_contact', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['conversation_id'],
            ['conversation.conversations.id'],
            name=op.f('fk_institutional_requests_conversation_id_conversations'),
        ),
        sa.ForeignKeyConstraint(
            ['requester_user_id'],
            ['identity.users.id'],
            name=op.f('fk_institutional_requests_requester_user_id_users'),
        ),
        sa.ForeignKeyConstraint(
            ['linked_handoff_id'],
            ['conversation.handoffs.id'],
            name=op.f('fk_institutional_requests_linked_handoff_id_handoffs'),
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_institutional_requests')),
        sa.UniqueConstraint('protocol_code', name=op.f('uq_institutional_requests_protocol_code')),
        schema='conversation',
    )
    op.create_index(
        op.f('ix_institutional_requests_conversation_id'),
        'institutional_requests',
        ['conversation_id'],
        unique=False,
        schema='conversation',
    )
    op.create_index(
        op.f('ix_institutional_requests_linked_handoff_id'),
        'institutional_requests',
        ['linked_handoff_id'],
        unique=False,
        schema='conversation',
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_institutional_requests_linked_handoff_id'), table_name='institutional_requests', schema='conversation')
    op.drop_index(op.f('ix_institutional_requests_conversation_id'), table_name='institutional_requests', schema='conversation')
    op.drop_table('institutional_requests', schema='conversation')

    op.drop_index(op.f('ix_visit_bookings_linked_handoff_id'), table_name='visit_bookings', schema='conversation')
    op.drop_index(op.f('ix_visit_bookings_conversation_id'), table_name='visit_bookings', schema='conversation')
    op.drop_table('visit_bookings', schema='conversation')
