import { NextRequest, NextResponse } from 'next/server';

import { clearPortalSession, getPortalAccessToken } from '../../../lib/auth';
import { getPortalConfig } from '../../../lib/config';

function buildPortalRedirect(path: string): URL {
  return new URL(path, getPortalConfig().adminWebPublicUrl);
}

function normalizeReturnTo(value: string | null): string {
  if (!value || !value.startsWith('/') || value.startsWith('//')) {
    return '/';
  }
  return value;
}

export async function GET(request: NextRequest) {
  const returnTo = normalizeReturnTo(request.nextUrl.searchParams.get('returnTo'));
  const accessToken = await getPortalAccessToken();
  if (!accessToken) {
    await clearPortalSession();
    return NextResponse.redirect(buildPortalRedirect('/?authError=session_expired'), {
      status: 303,
    });
  }

  return NextResponse.redirect(buildPortalRedirect(returnTo), {
    status: 303,
  });
}
