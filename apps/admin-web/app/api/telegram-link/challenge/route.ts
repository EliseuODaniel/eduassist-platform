import { NextResponse } from 'next/server';

import { issueTelegramLinkChallenge } from '../../../../lib/auth';

export async function POST() {
  const result = await issueTelegramLinkChallenge();

  if (!result.challenge) {
    return NextResponse.json(
      {
        error: result.error ?? 'challenge_request_failed',
      },
      {
        status: result.status,
      },
    );
  }

  return NextResponse.json(result.challenge, {
    status: 200,
  });
}
