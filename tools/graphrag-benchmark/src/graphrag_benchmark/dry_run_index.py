from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[4]
DEFAULT_WORKSPACE = ROOT_DIR / 'artifacts' / 'graphrag' / 'eduassist-public-benchmark'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run GraphRAG index dry-run with clean output.')
    parser.add_argument('--workspace', type=Path, default=DEFAULT_WORKSPACE)
    parser.add_argument('--method', default='standard')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = subprocess.run(
        [
            'graphrag',
            'index',
            '-r',
            str(args.workspace.resolve()),
            '-m',
            args.method,
            '--dry-run',
            '--skip-validation',
        ],
        text=True,
        capture_output=True,
        cwd=str(ROOT_DIR),
    )

    stderr = (result.stderr or '').strip()
    stdout = (result.stdout or '').strip()
    stderr_lines = stderr.splitlines()
    logging_bug_detected = 'Dry run complete, exiting...' in stderr and 'Logging error' in stderr

    summary = {
        'workspace': args.workspace.resolve().as_posix(),
        'method': args.method,
        'exit_code': result.returncode,
        'success': result.returncode == 0,
        'logging_bug_detected': logging_bug_detected,
        'stdout_excerpt': stdout[:600],
        'stderr_excerpt': '\n'.join(stderr_lines[:12]),
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
