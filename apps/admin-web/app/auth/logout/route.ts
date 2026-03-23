import { NextRequest, NextResponse } from 'next/server';

import { clearPortalSession } from '../../../lib/auth';
import { getPortalConfig } from '../../../lib/config';

function buildPortalRedirect() {
  return new URL('/', getPortalConfig().adminWebPublicUrl);
}

export async function GET() {
  await clearPortalSession();
  return NextResponse.redirect(buildPortalRedirect(), {
    status: 303,
  });
}

export async function POST(_request: NextRequest) {
  await clearPortalSession();
  return NextResponse.redirect(buildPortalRedirect(), {
    status: 303,
  });
}
