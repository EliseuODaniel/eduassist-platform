import { NextRequest, NextResponse } from 'next/server';

import { consumeLoginCallback } from '../../../lib/auth';
import { getPortalConfig } from '../../../lib/config';

function buildPortalRedirect(path: string): URL {
  return new URL(path, getPortalConfig().adminWebPublicUrl);
}

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get('code');
  const state = request.nextUrl.searchParams.get('state');
  const providerError = request.nextUrl.searchParams.get('error');

  if (providerError) {
    return NextResponse.redirect(buildPortalRedirect(`/?authError=${providerError}`), {
      status: 303,
    });
  }

  const result = await consumeLoginCallback({ code, state });
  if (!result.ok) {
    return NextResponse.redirect(buildPortalRedirect(`/?authError=${result.error}`), {
      status: 303,
    });
  }

  return NextResponse.redirect(buildPortalRedirect('/'), {
    status: 303,
  });
}
