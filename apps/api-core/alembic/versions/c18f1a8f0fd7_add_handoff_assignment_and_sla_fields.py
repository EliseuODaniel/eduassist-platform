"""add handoff assignment and sla fields

Revision ID: c18f1a8f0fd7
Revises: f4a8f3945d39
Create Date: 2026-03-23 08:10:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c18f1a8f0fd7'
down_revision: Union[str, Sequence[str], None] = 'f4a8f3945d39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'handoffs',
        sa.Column('priority_code', sa.String(length=20), nullable=True),
        schema='conversation',
    )
    op.add_column(
        'handoffs',
        sa.Column('assigned_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        schema='conversation',
    )
    op.add_column(
        'handoffs',
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True),
        schema='conversation',
    )
    op.add_column(
        'handoffs',
        sa.Column('response_due_at', sa.DateTime(timezone=True), nullable=True),
        schema='conversation',
    )
    op.add_column(
        'handoffs',
        sa.Column('resolution_due_at', sa.DateTime(timezone=True), nullable=True),
        schema='conversation',
    )
    op.create_foreign_key(
        op.f('fk_handoffs_assigned_user_id_users'),
        'handoffs',
        'users',
        ['assigned_user_id'],
        ['id'],
        source_schema='conversation',
        referent_schema='identity',
    )

    op.execute(
        """
        update conversation.handoffs
        set priority_code = case
            when queue_name in ('coordenacao', 'financeiro') then 'high'
            else 'standard'
        end
        """
    )
    op.execute(
        """
        update conversation.handoffs
        set response_due_at = case
                when priority_code = 'high' then created_at + interval '1 hour'
                when priority_code = 'urgent' then created_at + interval '30 minutes'
                else created_at + interval '4 hours'
            end,
            resolution_due_at = case
                when priority_code = 'high' then created_at + interval '8 hours'
                when priority_code = 'urgent' then created_at + interval '4 hours'
                else created_at + interval '24 hours'
            end
        """
    )
    op.alter_column(
        'handoffs',
        'priority_code',
        schema='conversation',
        existing_type=sa.String(length=20),
        nullable=False,
        server_default='standard',
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f('fk_handoffs_assigned_user_id_users'),
        'handoffs',
        schema='conversation',
        type_='foreignkey',
    )
    op.drop_column('handoffs', 'resolution_due_at', schema='conversation')
    op.drop_column('handoffs', 'response_due_at', schema='conversation')
    op.drop_column('handoffs', 'assigned_at', schema='conversation')
    op.drop_column('handoffs', 'assigned_user_id', schema='conversation')
    op.drop_column('handoffs', 'priority_code', schema='conversation')
