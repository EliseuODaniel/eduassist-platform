from __future__ import annotations

import argparse
import json
from pathlib import Path

from graphrag_benchmark.preflight import get_workspace_provider_status


ROOT_DIR = Path(__file__).resolve().parents[4]
DEFAULT_WORKSPACE = ROOT_DIR / 'artifacts' / 'graphrag' / 'eduassist-public-benchmark'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Check local GraphRAG provider readiness.')
    parser.add_argument('--workspace', type=Path, default=DEFAULT_WORKSPACE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    status = get_workspace_provider_status(args.workspace.resolve())
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0 if status.get('provider_ready') else 1


if __name__ == '__main__':
    raise SystemExit(main())
