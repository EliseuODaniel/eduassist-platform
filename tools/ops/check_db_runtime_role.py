from __future__ import annotations

import json
import os
import sys

import psycopg


def main() -> int:
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print(json.dumps({'ok': False, 'error': 'DATABASE_URL_missing'}))
        return 1

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select
                  current_user,
                  session_user,
                  r.rolsuper,
                  r.rolcreatedb,
                  r.rolcreaterole
                from pg_roles r
                where r.rolname = current_user
                """
            )
            row = cursor.fetchone()

    if row is None:
        print(json.dumps({'ok': False, 'error': 'runtime_role_not_found'}))
        return 1

    current_user, session_user, is_superuser, can_create_db, can_create_role = row
    payload = {
        'ok': not bool(is_superuser),
        'current_user': current_user,
        'session_user': session_user,
        'rolsuper': bool(is_superuser),
        'rolcreatedb': bool(can_create_db),
        'rolcreaterole': bool(can_create_role),
    }
    print(json.dumps(payload, ensure_ascii=True))
    return 0 if payload['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
