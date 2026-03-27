#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
from typing import Any

try:
    import psycopg
except Exception:  # pragma: no cover - optional local dependency
    psycopg = None  # type: ignore[assignment]


def _default_database_url() -> str:
    return os.environ.get('DATABASE_URL_LOCAL') or 'postgresql://eduassist:eduassist@localhost:5432/eduassist'


def _load_messages(database_url: str, thread_id: str, limit: int | None) -> list[dict[str, Any]]:
    if psycopg is None:
        return _load_messages_via_psql(thread_id=thread_id, limit=limit)
    return _load_messages_via_psycopg(database_url=database_url, thread_id=thread_id, limit=limit)


def _load_messages_via_psycopg(database_url: str, thread_id: str, limit: int | None) -> list[dict[str, Any]]:
    sql = """
        select
            c.external_thread_id,
            m.sender_type,
            regexp_replace(m.content, E'[\\n\\r]+', ' ', 'g') as content,
            to_char(m.created_at at time zone 'America/Sao_Paulo', 'YYYY-MM-DD HH24:MI:SS') as created_at
        from conversation.conversations c
        join conversation.messages m on m.conversation_id = c.id
        where c.external_thread_id = %s
        order by m.created_at asc
    """
    params: list[Any] = [thread_id]
    if limit is not None:
        sql += ' limit %s'
        params.append(limit)
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
    return [
        {
            'thread_id': row[0],
            'sender_type': row[1],
            'content': row[2],
            'created_at': row[3],
        }
        for row in rows
    ]


def _load_messages_via_psql(*, thread_id: str, limit: int | None) -> list[dict[str, Any]]:
    sql = f"""
        select
            c.external_thread_id,
            m.sender_type,
            regexp_replace(m.content, E'[\\n\\r]+', ' ', 'g') as content,
            to_char(m.created_at at time zone 'America/Sao_Paulo', 'YYYY-MM-DD HH24:MI:SS') as created_at
        from conversation.conversations c
        join conversation.messages m on m.conversation_id = c.id
        where c.external_thread_id = '{thread_id}'
        order by m.created_at asc
    """
    if limit is not None:
        sql += f' limit {int(limit)}'
    command = [
        'docker',
        'exec',
        'eduassist-postgres',
        'psql',
        '-U',
        'eduassist',
        '-d',
        'eduassist',
        '-At',
        '-F',
        '\t',
        '-c',
        sql,
    ]
    output = subprocess.check_output(command, text=True)
    rows: list[dict[str, Any]] = []
    for line in output.splitlines():
        parts = line.split('\t')
        if len(parts) != 4:
            continue
        rows.append(
            {
                'thread_id': parts[0],
                'sender_type': parts[1],
                'content': parts[2],
                'created_at': parts[3],
            }
        )
    return rows


def _to_markdown(messages: list[dict[str, Any]]) -> str:
    lines = ['# Telegram Thread Export', '']
    if messages:
        lines.append(f"- Thread: `{messages[0]['thread_id']}`")
        lines.append(f"- Messages: `{len(messages)}`")
        lines.append('')
    for message in messages:
        sender = message['sender_type']
        created_at = message['created_at']
        content = message['content']
        lines.append(f"## {sender} - {created_at}")
        lines.append('')
        lines.append(content)
        lines.append('')
    return '\n'.join(lines)


def _to_benchmark_skeleton(messages: list[dict[str, Any]], *, thread_id: str) -> list[dict[str, Any]]:
    telegram_chat_id: int | None = None
    if thread_id.startswith('telegram:'):
        raw = thread_id.split(':', 1)[1]
        if raw.isdigit():
            telegram_chat_id = int(raw)
    turns: list[dict[str, Any]] = []
    for message in messages:
        if message['sender_type'] != 'user':
            continue
        turns.append(
            {
                'prompt': message['content'],
                'expected_keywords': [],
                'note': f"from_real_transcript:{message['created_at']}",
            }
        )
    skeleton = {
        'thread_id': thread_id.replace(':', '_'),
        'slice': 'protected',
        'category': 'threaded_real_transcript',
        'turns': turns,
    }
    if telegram_chat_id is not None:
        skeleton['telegram_chat_id'] = telegram_chat_id
    return [skeleton]


def main() -> int:
    parser = argparse.ArgumentParser(description='Export a real Telegram thread from Postgres for benchmark curation.')
    parser.add_argument('--thread-id', required=True)
    parser.add_argument('--database-url', default=_default_database_url())
    parser.add_argument('--limit', type=int)
    parser.add_argument('--output-json')
    parser.add_argument('--output-markdown')
    parser.add_argument('--benchmark-skeleton-output')
    args = parser.parse_args()

    messages = _load_messages(args.database_url, args.thread_id, args.limit)
    payload = {'thread_id': args.thread_id, 'message_count': len(messages), 'messages': messages}

    if args.output_json:
        output = Path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    if args.output_markdown:
        output = Path(args.output_markdown)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(_to_markdown(messages))

    if args.benchmark_skeleton_output:
        output = Path(args.benchmark_skeleton_output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(_to_benchmark_skeleton(messages, thread_id=args.thread_id), ensure_ascii=False, indent=2))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
