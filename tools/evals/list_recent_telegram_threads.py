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
except Exception:  # pragma: no cover
    psycopg = None  # type: ignore[assignment]


def _default_database_url() -> str:
    return os.environ.get('DATABASE_URL_LOCAL') or 'postgresql://eduassist:eduassist@localhost:5432/eduassist'


def _load_threads(database_url: str, *, days: int, limit: int) -> list[dict[str, Any]]:
    if psycopg is None:
        return _load_threads_via_psql(days=days, limit=limit)
    return _load_threads_via_psycopg(database_url=database_url, days=days, limit=limit)


def _load_threads_via_psycopg(database_url: str, *, days: int, limit: int) -> list[dict[str, Any]]:
    sql = """
        with ranked as (
            select
                c.external_thread_id,
                count(*) filter (where m.sender_type = 'user') as user_messages,
                count(*) as total_messages,
                min(m.created_at at time zone 'America/Sao_Paulo') as first_message_local,
                max(m.created_at at time zone 'America/Sao_Paulo') as last_message_local,
                max(case when m.sender_type = 'user' then regexp_replace(m.content, E'[\\n\\r]+', ' ', 'g') end) filter (where m.created_at = (
                    select max(m2.created_at)
                    from conversation.messages m2
                    where m2.conversation_id = c.id and m2.sender_type = 'user'
                )) as latest_user_message
            from conversation.conversations c
            join conversation.messages m on m.conversation_id = c.id
            where c.external_thread_id like 'telegram:%'
              and m.created_at >= now() - (%s || ' days')::interval
            group by c.external_thread_id, c.id
        )
        select
            external_thread_id,
            user_messages,
            total_messages,
            to_char(first_message_local, 'YYYY-MM-DD HH24:MI:SS'),
            to_char(last_message_local, 'YYYY-MM-DD HH24:MI:SS'),
            coalesce(latest_user_message, '')
        from ranked
        order by last_message_local desc
        limit %s
    """
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, [days, limit])
            rows = cursor.fetchall()
    return [
        {
            'thread_id': row[0],
            'user_messages': row[1],
            'total_messages': row[2],
            'first_message_local': row[3],
            'last_message_local': row[4],
            'latest_user_message': row[5],
        }
        for row in rows
    ]


def _load_threads_via_psql(*, days: int, limit: int) -> list[dict[str, Any]]:
    sql = f"""
        with ranked as (
            select
                c.external_thread_id,
                count(*) filter (where m.sender_type = 'user') as user_messages,
                count(*) as total_messages,
                min(m.created_at at time zone 'America/Sao_Paulo') as first_message_local,
                max(m.created_at at time zone 'America/Sao_Paulo') as last_message_local,
                max(case when m.sender_type = 'user' then regexp_replace(m.content, E'[\\n\\r]+', ' ', 'g') end) filter (where m.created_at = (
                    select max(m2.created_at)
                    from conversation.messages m2
                    where m2.conversation_id = c.id and m2.sender_type = 'user'
                )) as latest_user_message
            from conversation.conversations c
            join conversation.messages m on m.conversation_id = c.id
            where c.external_thread_id like 'telegram:%'
              and m.created_at >= now() - interval '{int(days)} days'
            group by c.external_thread_id, c.id
        )
        select
            external_thread_id,
            user_messages,
            total_messages,
            to_char(first_message_local, 'YYYY-MM-DD HH24:MI:SS'),
            to_char(last_message_local, 'YYYY-MM-DD HH24:MI:SS'),
            coalesce(latest_user_message, '')
        from ranked
        order by last_message_local desc
        limit {int(limit)};
    """
    output = subprocess.check_output(
        [
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
        ],
        text=True,
    )
    rows: list[dict[str, Any]] = []
    for line in output.splitlines():
        parts = line.split('\t')
        if len(parts) != 6:
            continue
        rows.append(
            {
                'thread_id': parts[0],
                'user_messages': int(parts[1]),
                'total_messages': int(parts[2]),
                'first_message_local': parts[3],
                'last_message_local': parts[4],
                'latest_user_message': parts[5],
            }
        )
    return rows


def _to_markdown(rows: list[dict[str, Any]], *, days: int, limit: int) -> str:
    lines = ['# Recent Telegram Threads', '']
    lines.append(f'- Window: last `{days}` day(s)')
    lines.append(f'- Limit: `{limit}`')
    lines.append(f'- Threads listed: `{len(rows)}`')
    lines.append('')
    lines.append('| Thread | User Msgs | Total Msgs | First | Last | Latest User Message |')
    lines.append('| --- | ---: | ---: | --- | --- | --- |')
    for row in rows:
        latest = str(row.get('latest_user_message', '')).replace('|', '\\|')
        lines.append(
            f"| `{row['thread_id']}` | {row['user_messages']} | {row['total_messages']} | "
            f"{row['first_message_local']} | {row['last_message_local']} | {latest} |"
        )
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='List recent Telegram threads for benchmark curation.')
    parser.add_argument('--database-url', default=_default_database_url())
    parser.add_argument('--days', type=int, default=14)
    parser.add_argument('--limit', type=int, default=30)
    parser.add_argument('--output-json')
    parser.add_argument('--output-markdown')
    args = parser.parse_args()

    rows = _load_threads(args.database_url, days=args.days, limit=args.limit)
    payload = {
        'days': args.days,
        'limit': args.limit,
        'thread_count': len(rows),
        'threads': rows,
    }

    if args.output_json:
        path = Path(args.output_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    if args.output_markdown:
        path = Path(args.output_markdown)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_to_markdown(rows, days=args.days, limit=args.limit))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
