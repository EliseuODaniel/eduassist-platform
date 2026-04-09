#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = REPO_ROOT / 'tests/evals/datasets/retrieval_multiturn_probe_threads.generated.20260406.json'
DEFAULT_REPORT = REPO_ROOT / 'docs/architecture/independent-orchestrators-multiturn-report-20260406.md'
DEFAULT_JSON_REPORT = REPO_ROOT / 'docs/architecture/independent-orchestrators-multiturn-report-20260406.json'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt-file', default=str(DEFAULT_DATASET))
    parser.add_argument('--report', default=str(DEFAULT_REPORT))
    parser.add_argument('--json-report', default=str(DEFAULT_JSON_REPORT))
    parser.add_argument('--llm-forced', action='store_true')
    args = parser.parse_args()

    command = [
        sys.executable,
        str(REPO_ROOT / 'tools/evals/compare_four_chatbot_paths.py'),
        '--prompt-file',
        str(Path(args.prompt_file)),
        '--report',
        str(Path(args.report)),
        '--json-report',
        str(Path(args.json_report)),
    ]
    if args.llm_forced:
        command.append('--llm-forced')
    completed = subprocess.run(command, cwd=REPO_ROOT, check=False)
    return int(completed.returncode)


if __name__ == '__main__':
    raise SystemExit(main())
