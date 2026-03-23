"""add federated identities and link challenges

Revision ID: d2b1ef6c8a90
Revises: 434bee84d7d9
Create Date: 2026-03-23 03:40:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd2b1ef6c8a90'
down_revision: Union[str, Sequence[str], None] = '434bee84d7d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'federated_identities',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['identity.users.id'], name=op.f('fk_federated_identities_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_federated_identities')),
        sa.UniqueConstraint('provider', 'subject', name='uq_federated_identities_provider_subject'),
        sa.UniqueConstraint('user_id', 'provider', name='uq_federated_identities_user_id_provider'),
        schema='identity',
    )

    op.create_table(
        'telegram_link_challenges',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('code_hash', sa.String(length=128), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('consumed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('purpose', sa.String(length=50), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['identity.users.id'],
            name=op.f('fk_telegram_link_challenges_user_id_users'),
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_telegram_link_challenges')),
        sa.UniqueConstraint('code_hash', name=op.f('uq_telegram_link_challenges_code_hash')),
        schema='identity',
    )


def downgrade() -> None:
    op.drop_table('telegram_link_challenges', schema='identity')
    op.drop_table('federated_identities', schema='identity')
