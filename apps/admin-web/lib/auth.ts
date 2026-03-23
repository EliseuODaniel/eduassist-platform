import 'server-only';

import { createHash, randomBytes } from 'node:crypto';
import { cookies } from 'next/headers';

import { getPortalConfig } from './config';

const ACCESS_TOKEN_COOKIE = 'eduassist_access_token';
const REFRESH_TOKEN_COOKIE = 'eduassist_refresh_token';
const OIDC_STATE_COOKIE = 'eduassist_oidc_state';
const OIDC_VERIFIER_COOKIE = 'eduassist_oidc_verifier';

type CookieStore = Awaited<ReturnType<typeof cookies>>;

type TokenSet = {
  access_token: string;
  expires_in: number;
  refresh_expires_in?: number;
  refresh_token?: string;
};

export type PortalPrincipal = {
  provider: string;
  subject: string;
  issuer: string;
  azp: string | null;
  audiences: string[];
  preferred_username: string | null;
  email: string | null;
  email_verified: boolean;
  realm_roles: string[];
};

export type LinkedStudentReference = {
  student_id: string;
  full_name: string;
  enrollment_code: string;
  class_name: string | null;
  can_view_academic: boolean;
  can_view_finance: boolean;
};

export type AccessibleClassReference = {
  class_id: string;
  class_name: string;
  subject_name: string | null;
};

export type PortalActor = {
  user_id: string;
  role_code: string;
  external_code: string;
  full_name: string;
  authenticated: boolean;
  telegram_chat_id: number | null;
  telegram_linked: boolean;
  linked_students: LinkedStudentReference[];
  accessible_classes: AccessibleClassReference[];
};

export type PortalSession = {
  actor: PortalActor;
  principal: PortalPrincipal;
  auth_mode: string;
};

export type TelegramLinkChallenge = {
  challenge_code: string;
  expires_at: string;
  bot_username: string | null;
  telegram_deep_link: string | null;
  telegram_command: string;
};

export type SessionState = {
  session: PortalSession | null;
  error: string | null;
};

function buildRealmEndpoint(pathname: string, publicFacing: boolean): URL {
  const config = getPortalConfig();
  const base = publicFacing ? config.keycloakPublicUrl : config.keycloakInternalUrl;
  return new URL(`/realms/${config.keycloakRealm}/protocol/openid-connect/${pathname}`, base);
}

function secureCookieEnabled(): boolean {
  return getPortalConfig().adminWebPublicUrl.startsWith('https://');
}

function sessionCookieOptions(maxAge: number) {
  return {
    httpOnly: true,
    sameSite: 'lax' as const,
    secure: secureCookieEnabled(),
    path: '/',
    maxAge,
  };
}

function transientCookieOptions(maxAge: number) {
  return {
    httpOnly: true,
    sameSite: 'lax' as const,
    secure: secureCookieEnabled(),
    path: '/',
    maxAge,
  };
}

function buildRedirectUri(): string {
  const config = getPortalConfig();
  return `${config.adminWebPublicUrl}/auth/callback`;
}

function buildCodeVerifier(): string {
  return randomBytes(48).toString('base64url');
}

function buildCodeChallenge(verifier: string): string {
  return createHash('sha256').update(verifier).digest('base64url');
}

async function storeTokenSet(tokenSet: TokenSet): Promise<void> {
  const cookieStore = await cookies();
  const accessTtl = Math.max(Number(tokenSet.expires_in || 900), 60);
  cookieStore.set(ACCESS_TOKEN_COOKIE, tokenSet.access_token, sessionCookieOptions(accessTtl));

  if (tokenSet.refresh_token) {
    const refreshTtl = Math.max(Number(tokenSet.refresh_expires_in || 3600), accessTtl);
    cookieStore.set(
      REFRESH_TOKEN_COOKIE,
      tokenSet.refresh_token,
      sessionCookieOptions(refreshTtl),
    );
  } else {
    cookieStore.delete(REFRESH_TOKEN_COOKIE);
  }
}

async function clearTransientLoginCookies(cookieStore?: CookieStore): Promise<void> {
  const target = cookieStore ?? (await cookies());
  target.delete(OIDC_STATE_COOKIE);
  target.delete(OIDC_VERIFIER_COOKIE);
}

export async function clearPortalSession(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete(ACCESS_TOKEN_COOKIE);
  cookieStore.delete(REFRESH_TOKEN_COOKIE);
  await clearTransientLoginCookies(cookieStore);
}

async function refreshAccessToken(refreshToken: string): Promise<string | null> {
  const config = getPortalConfig();
  const response = await fetch(buildRealmEndpoint('token', false), {
    method: 'POST',
    cache: 'no-store',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      client_id: config.keycloakWebClientId,
      refresh_token: refreshToken,
    }),
  });

  if (!response.ok) {
    return null;
  }

  const tokenSet = (await response.json()) as TokenSet;
  await storeTokenSet(tokenSet);
  return tokenSet.access_token;
}

async function getAccessTokenWithRefresh(): Promise<string | null> {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get(ACCESS_TOKEN_COOKIE)?.value ?? null;
  if (accessToken) {
    return accessToken;
  }

  const refreshToken = cookieStore.get(REFRESH_TOKEN_COOKIE)?.value ?? null;
  if (!refreshToken) {
    return null;
  }

  const refreshedAccessToken = await refreshAccessToken(refreshToken);
  if (!refreshedAccessToken) {
    await clearPortalSession();
  }
  return refreshedAccessToken;
}

async function fetchPortalSessionWithToken(accessToken: string): Promise<Response> {
  const config = getPortalConfig();
  return fetch(`${config.apiCoreUrl}/v1/auth/session`, {
    method: 'GET',
    cache: 'no-store',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
}

async function getAccessTokenForApiRequest(): Promise<string | null> {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get(ACCESS_TOKEN_COOKIE)?.value ?? null;
  if (!accessToken) {
    return getAccessTokenWithRefresh();
  }

  return accessToken;
}

export async function getPortalSession(): Promise<SessionState> {
  let accessToken = await getAccessTokenForApiRequest();
  if (!accessToken) {
    return {
      session: null,
      error: null,
    };
  }

  let response = await fetchPortalSessionWithToken(accessToken);
  if (response.status === 401) {
    const cookieStore = await cookies();
    const refreshToken = cookieStore.get(REFRESH_TOKEN_COOKIE)?.value ?? null;
    if (!refreshToken) {
      await clearPortalSession();
      return {
        session: null,
        error: 'session_expired',
      };
    }

    accessToken = await refreshAccessToken(refreshToken);
    if (!accessToken) {
      await clearPortalSession();
      return {
        session: null,
        error: 'session_expired',
      };
    }
    response = await fetchPortalSessionWithToken(accessToken);
  }

  if (!response.ok) {
    return {
      session: null,
      error: `api_core_${response.status}`,
    };
  }

  const session = (await response.json()) as PortalSession;
  return {
    session,
    error: null,
  };
}

export async function createLoginRedirectUrl(): Promise<string> {
  const config = getPortalConfig();
  const cookieStore = await cookies();

  const state = randomBytes(18).toString('hex');
  const verifier = buildCodeVerifier();
  const challenge = buildCodeChallenge(verifier);

  cookieStore.set(OIDC_STATE_COOKIE, state, transientCookieOptions(600));
  cookieStore.set(OIDC_VERIFIER_COOKIE, verifier, transientCookieOptions(600));

  const authUrl = buildRealmEndpoint('auth', true);
  authUrl.searchParams.set('client_id', config.keycloakWebClientId);
  authUrl.searchParams.set('redirect_uri', buildRedirectUri());
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('scope', 'openid profile email');
  authUrl.searchParams.set('state', state);
  authUrl.searchParams.set('code_challenge', challenge);
  authUrl.searchParams.set('code_challenge_method', 'S256');

  return authUrl.toString();
}

export async function consumeLoginCallback(params: {
  code: string | null;
  state: string | null;
}): Promise<{ ok: true } | { ok: false; error: string }> {
  const { code, state } = params;
  const cookieStore = await cookies();
  const expectedState = cookieStore.get(OIDC_STATE_COOKIE)?.value ?? null;
  const codeVerifier = cookieStore.get(OIDC_VERIFIER_COOKIE)?.value ?? null;

  if (!code) {
    await clearTransientLoginCookies(cookieStore);
    return { ok: false, error: 'authorization_code_missing' };
  }

  if (!state || !expectedState || state !== expectedState || !codeVerifier) {
    await clearTransientLoginCookies(cookieStore);
    return { ok: false, error: 'invalid_login_state' };
  }

  const config = getPortalConfig();
  const response = await fetch(buildRealmEndpoint('token', false), {
    method: 'POST',
    cache: 'no-store',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      client_id: config.keycloakWebClientId,
      code,
      redirect_uri: buildRedirectUri(),
      code_verifier: codeVerifier,
    }),
  });

  await clearTransientLoginCookies(cookieStore);

  if (!response.ok) {
    await clearPortalSession();
    return { ok: false, error: 'token_exchange_failed' };
  }

  const tokenSet = (await response.json()) as TokenSet;
  await storeTokenSet(tokenSet);
  return { ok: true };
}

export async function issueTelegramLinkChallenge(): Promise<{
  challenge: TelegramLinkChallenge | null;
  error: string | null;
  status: number;
}> {
  const accessToken = await getAccessTokenForApiRequest();
  if (!accessToken) {
    return {
      challenge: null,
      error: 'not_authenticated',
      status: 401,
    };
  }

  const config = getPortalConfig();
  const response = await fetch(`${config.apiCoreUrl}/v1/auth/telegram-link/challenges`, {
    method: 'POST',
    cache: 'no-store',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (response.status === 401) {
    await clearPortalSession();
  }

  if (!response.ok) {
    return {
      challenge: null,
      error: 'challenge_request_failed',
      status: response.status,
    };
  }

  const challenge = (await response.json()) as TelegramLinkChallenge;
  return {
    challenge,
    error: null,
    status: 200,
  };
}
