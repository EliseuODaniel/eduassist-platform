from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PATHS = (
    REPO_ROOT,
    REPO_ROOT / 'apps/api-core/src',
    REPO_ROOT / 'apps/ai-orchestrator/src',
    REPO_ROOT / 'apps/ai-orchestrator-specialist/src',
    REPO_ROOT / 'apps/telegram-gateway/src',
    REPO_ROOT / 'apps/worker/src',
    REPO_ROOT / 'packages/observability/python/src',
    REPO_ROOT / 'packages/semantic-ingress/python/src',
)

for path in SRC_PATHS:
    resolved = str(path)
    if resolved not in sys.path:
        sys.path.insert(0, resolved)
