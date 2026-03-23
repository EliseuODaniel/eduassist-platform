from __future__ import annotations

from functools import lru_cache

import jwt
from fastapi import HTTPException
from jwt import PyJWKClient

from api_core.config import get_settings
from api_core.contracts import AuthPrincipal


def extract_bearer_token(authorization: str | None) -> str | None:
    if authorization is None:
        return None

    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        raise HTTPException(status_code=401, detail='invalid_authorization_header')
    return token.strip()


@lru_cache
def get_jwks_client() -> PyJWKClient:
    settings = get_settings()
    return PyJWKClient(settings.keycloak_jwks_url)


def _ensure_allowed_client(claims: dict[str, object]) -> None:
    settings = get_settings()
    allowed_clients = set(settings.allowed_keycloak_clients)
    if not allowed_clients:
        return

    audiences: set[str] = set()
    aud = claims.get('aud')
    if isinstance(aud, str):
        audiences.add(aud)
    elif isinstance(aud, list):
        audiences.update(str(item) for item in aud)

    azp = claims.get('azp')
    if isinstance(azp, str):
        audiences.add(azp)

    if audiences.isdisjoint(allowed_clients):
        raise HTTPException(status_code=401, detail='token_client_not_allowed')


def decode_access_token(token: str) -> AuthPrincipal:
    settings = get_settings()

    try:
        signing_key = get_jwks_client().get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=['RS256', 'RS384', 'RS512'],
            issuer=settings.keycloak_issuer,
            options={'verify_aud': False},
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - dependent on third-party token failures
        raise HTTPException(status_code=401, detail=f'invalid_access_token:{exc.__class__.__name__}') from exc

    _ensure_allowed_client(claims)

    audiences: list[str] = []
    aud = claims.get('aud')
    if isinstance(aud, str):
        audiences = [aud]
    elif isinstance(aud, list):
        audiences = [str(item) for item in aud]

    return AuthPrincipal(
        provider='keycloak',
        subject=str(claims['sub']),
        issuer=str(claims['iss']),
        azp=str(claims['azp']) if claims.get('azp') else None,
        audiences=audiences,
        preferred_username=str(claims['preferred_username']) if claims.get('preferred_username') else None,
        email=str(claims['email']) if claims.get('email') else None,
        email_verified=bool(claims.get('email_verified', False)),
        realm_roles=[str(role) for role in claims.get('realm_access', {}).get('roles', [])],
    )
