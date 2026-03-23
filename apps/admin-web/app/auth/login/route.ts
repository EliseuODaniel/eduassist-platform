import { NextResponse } from 'next/server';

import { createLoginRedirectUrl } from '../../../lib/auth';

export async function GET() {
  const redirectUrl = await createLoginRedirectUrl();
  return NextResponse.redirect(redirectUrl, {
    status: 307,
  });
}
