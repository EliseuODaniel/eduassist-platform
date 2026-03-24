from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_REALM_FILE = (
    Path(__file__).resolve().parents[2] / 'infra' / 'compose' / 'keycloak' / 'import' / 'eduassist-realm.json'
)


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value else default


def _json_request(
    method: str,
    url: str,
    *,
    token: str | None = None,
    payload: dict | list | None = None,
) -> tuple[int, str, object | None]:
    headers = {}
    data = None
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if payload is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(payload).encode('utf-8')

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode('utf-8')
        if not body:
            return response.status, body, None
        return response.status, body, json.loads(body)


def _admin_token(base_url: str, username: str, password: str) -> str:
    token_url = f'{base_url}/realms/master/protocol/openid-connect/token'
    payload = urllib.parse.urlencode(
        {
            'grant_type': 'password',
            'client_id': 'admin-cli',
            'username': username,
            'password': password,
        }
    ).encode('utf-8')
    request = urllib.request.Request(token_url, data=payload, method='POST')
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.loads(response.read().decode('utf-8'))
    return str(body['access_token'])


def _find_user(base_url: str, realm: str, token: str, username: str) -> dict | None:
    query = urllib.parse.urlencode({'username': username, 'exact': 'true'})
    _, _, payload = _json_request(
        'GET',
        f'{base_url}/admin/realms/{realm}/users?{query}',
        token=token,
    )
    if isinstance(payload, list) and payload:
        return payload[0]
    return None


def _ensure_user(base_url: str, realm: str, token: str, user_payload: dict) -> tuple[str, bool]:
    username = str(user_payload['username'])
    existing = _find_user(base_url, realm, token, username)
    payload = {
        'username': username,
        'enabled': user_payload.get('enabled', True),
        'emailVerified': user_payload.get('emailVerified', True),
        'firstName': user_payload.get('firstName', ''),
        'lastName': user_payload.get('lastName', ''),
        'email': user_payload.get('email'),
        'attributes': user_payload.get('attributes', {}),
    }
    if existing is None:
        _json_request('POST', f'{base_url}/admin/realms/{realm}/users', token=token, payload=payload)
        created = True
        existing = _find_user(base_url, realm, token, username)
        if existing is None:
            raise RuntimeError(f'failed to create keycloak user {username}')
    else:
        _json_request(
            'PUT',
            f"{base_url}/admin/realms/{realm}/users/{existing['id']}",
            token=token,
            payload=payload,
        )
        created = False
    return str(existing['id']), created


def _ensure_password(base_url: str, realm: str, token: str, user_id: str, credential: dict | None) -> None:
    if not credential or credential.get('type') != 'password':
        return
    _json_request(
        'PUT',
        f'{base_url}/admin/realms/{realm}/users/{user_id}/reset-password',
        token=token,
        payload={
            'type': 'password',
            'value': credential.get('value', ''),
            'temporary': bool(credential.get('temporary', False)),
        },
    )


def _ensure_roles(base_url: str, realm: str, token: str, user_id: str, role_names: list[str]) -> int:
    if not role_names:
        return 0
    _, _, current_payload = _json_request(
        'GET',
        f'{base_url}/admin/realms/{realm}/users/{user_id}/role-mappings/realm',
        token=token,
    )
    current_names = {
        str(role.get('name'))
        for role in current_payload
        if isinstance(current_payload, list) and isinstance(role, dict)
    }
    missing = [name for name in role_names if name not in current_names]
    if not missing:
        return 0

    role_representations = []
    for role_name in missing:
        _, _, role_payload = _json_request(
            'GET',
            f'{base_url}/admin/realms/{realm}/roles/{urllib.parse.quote(role_name, safe="")}',
            token=token,
        )
        if not isinstance(role_payload, dict):
            raise RuntimeError(f'failed to resolve role {role_name}')
        role_representations.append(role_payload)

    _json_request(
        'POST',
        f'{base_url}/admin/realms/{realm}/users/{user_id}/role-mappings/realm',
        token=token,
        payload=role_representations,
    )
    return len(role_representations)


def main() -> None:
    base_url = _env('KEYCLOAK_SYNC_URL', 'http://localhost:8080')
    admin_username = _env('KEYCLOAK_ADMIN_USERNAME', 'admin')
    admin_password = _env('KEYCLOAK_ADMIN_PASSWORD', 'admin123')
    realm_file = Path(_env('KEYCLOAK_REALM_FILE', str(DEFAULT_REALM_FILE)))

    realm_payload = json.loads(realm_file.read_text(encoding='utf-8'))
    realm = str(realm_payload['realm'])
    users = realm_payload.get('users', [])

    token = _admin_token(base_url, admin_username, admin_password)

    created = 0
    updated = 0
    roles_added = 0
    for user_payload in users:
        if not isinstance(user_payload, dict):
            continue
        user_id, was_created = _ensure_user(base_url, realm, token, user_payload)
        if was_created:
            created += 1
        else:
            updated += 1
        credentials = user_payload.get('credentials') or []
        password_credential = credentials[0] if credentials else None
        _ensure_password(base_url, realm, token, user_id, password_credential)
        roles_added += _ensure_roles(base_url, realm, token, user_id, list(user_payload.get('realmRoles', [])))

    print(f'keycloak users synced: created={created} updated={updated} roles_added={roles_added}')


if __name__ == '__main__':
    main()
