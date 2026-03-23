"""add support conversation rls

Revision ID: 4e27f7963646
Revises: 9aa0e8004bc1
Create Date: 2026-03-23 12:55:00.000000
"""

from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '4e27f7963646'
down_revision: str | Sequence[str] | None = '9aa0e8004bc1'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        create or replace function runtime.can_access_support_global()
        returns boolean
        language sql
        stable
        as $$
          select runtime.actor_role_code() in (
            'staff',
            'finance',
            'coordinator',
            'admin',
            'system_internal'
          )
        $$;

        create or replace function runtime.can_access_conversation_owner(target_user_id uuid)
        returns boolean
        language plpgsql
        stable
        security definer
        set search_path = pg_catalog, runtime, conversation
        as $$
        declare
          actor_user_id uuid := runtime.actor_user_id();
        begin
          if runtime.can_access_support_global() then
            return true;
          end if;

          if actor_user_id is null or target_user_id is null then
            return false;
          end if;

          return actor_user_id = target_user_id;
        end;
        $$;

        create or replace function runtime.can_access_conversation(target_conversation_id uuid)
        returns boolean
        language plpgsql
        stable
        security definer
        set search_path = pg_catalog, runtime, conversation
        as $$
        declare
          target_user_id uuid;
        begin
          if target_conversation_id is null then
            return false;
          end if;

          select conversations.user_id
            into target_user_id
          from conversation.conversations conversations
          where conversations.id = target_conversation_id;

          return runtime.can_access_conversation_owner(target_user_id);
        end;
        $$;

        grant execute on function runtime.can_access_support_global() to eduassist_app;
        grant execute on function runtime.can_access_conversation_owner(uuid) to eduassist_app;
        grant execute on function runtime.can_access_conversation(uuid) to eduassist_app;

        alter table conversation.conversations enable row level security;
        alter table conversation.conversations force row level security;
        drop policy if exists conversation_runtime_access on conversation.conversations;
        create policy conversation_runtime_access
          on conversation.conversations
          for all
          using (runtime.can_access_conversation_owner(user_id))
          with check (runtime.can_access_conversation_owner(user_id));

        alter table conversation.messages enable row level security;
        alter table conversation.messages force row level security;
        drop policy if exists conversation_messages_runtime_access on conversation.messages;
        create policy conversation_messages_runtime_access
          on conversation.messages
          for all
          using (runtime.can_access_conversation(conversation_id))
          with check (runtime.can_access_conversation(conversation_id));

        alter table conversation.tool_calls enable row level security;
        alter table conversation.tool_calls force row level security;
        drop policy if exists conversation_tool_calls_runtime_access on conversation.tool_calls;
        create policy conversation_tool_calls_runtime_access
          on conversation.tool_calls
          for all
          using (runtime.can_access_conversation(conversation_id))
          with check (runtime.can_access_conversation(conversation_id));

        alter table conversation.handoffs enable row level security;
        alter table conversation.handoffs force row level security;
        drop policy if exists conversation_handoffs_runtime_access on conversation.handoffs;
        create policy conversation_handoffs_runtime_access
          on conversation.handoffs
          for all
          using (runtime.can_access_conversation(conversation_id))
          with check (runtime.can_access_conversation(conversation_id));
        """
    )


def downgrade() -> None:
    op.execute(
        """
        drop policy if exists conversation_handoffs_runtime_access on conversation.handoffs;
        alter table conversation.handoffs no force row level security;
        alter table conversation.handoffs disable row level security;

        drop policy if exists conversation_tool_calls_runtime_access on conversation.tool_calls;
        alter table conversation.tool_calls no force row level security;
        alter table conversation.tool_calls disable row level security;

        drop policy if exists conversation_messages_runtime_access on conversation.messages;
        alter table conversation.messages no force row level security;
        alter table conversation.messages disable row level security;

        drop policy if exists conversation_runtime_access on conversation.conversations;
        alter table conversation.conversations no force row level security;
        alter table conversation.conversations disable row level security;

        drop function if exists runtime.can_access_conversation(uuid);
        drop function if exists runtime.can_access_conversation_owner(uuid);
        drop function if exists runtime.can_access_support_global();
        """
    )
