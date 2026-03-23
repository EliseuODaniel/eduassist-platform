import { NextRequest, NextResponse } from 'next/server';

import { getPortalAccessToken } from '../../../../lib/auth';
import { getPortalConfig } from '../../../../lib/config';

type RouteContext = {
  params: Promise<{
    handoffId: string;
  }>;
};

export async function PATCH(request: NextRequest, context: RouteContext) {
  const accessToken = await getPortalAccessToken();
  if (!accessToken) {
    return NextResponse.json(
      {
        error: 'not_authenticated',
      },
      {
        status: 401,
      },
    );
  }

  const { handoffId } = await context.params;
  const payload = await request.json();
  const config = getPortalConfig();

  const response = await fetch(`${config.apiCoreUrl}/v1/support/handoffs/${handoffId}`, {
    method: 'PATCH',
    cache: 'no-store',
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const rawBody = await response.text();
  let body: unknown = null;
  if (rawBody) {
    try {
      body = JSON.parse(rawBody);
    } catch {
      body = {
        error: 'invalid_json_from_api_core',
        rawBody,
      };
    }
  }

  return NextResponse.json(body, {
    status: response.status,
  });
}
