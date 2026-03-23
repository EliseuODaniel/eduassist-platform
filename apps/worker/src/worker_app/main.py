from __future__ import annotations

import argparse
import signal
import time
from pathlib import Path

from .config import Settings, get_settings
from .pipeline import DocumentPipeline


READY_FILE = Path('/tmp/worker-ready')
RUNNING = True


def _stop(*_: object) -> None:
    global RUNNING
    RUNNING = False


def _sync_documents(settings: Settings) -> None:
    summary = DocumentPipeline(settings).sync_demo_corpus()
    print(
        '[worker] corpus synchronized',
        f"documents={summary['document_count']}",
        f"chunks={summary['chunk_count']}",
        f"collection={summary['collection']}",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='EduAssist background worker.')
    parser.add_argument('--sync-once', action='store_true', help='Synchronize the demo document corpus and exit.')
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    settings = get_settings()

    if args.sync_once:
        _sync_documents(settings)
        return

    if settings.worker_bootstrap_documents:
        _sync_documents(settings)

    READY_FILE.write_text(
        f'worker running in {settings.app_env} with database {settings.database_url}\n',
        encoding='utf-8',
    )

    print('[worker] bootstrap background loop started')
    while RUNNING:
        time.sleep(5)

    if READY_FILE.exists():
        READY_FILE.unlink()
    print('[worker] shutdown complete')


if __name__ == '__main__':
    main()
