#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_dataset(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise SystemExit(f"invalid_dataset_payload:{path}")
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            raise SystemExit(f"invalid_dataset_row:{path}:{index}")
        rows.append(dict(item))
    return rows


def _merge_datasets(
    paths: list[Path],
    *,
    id_prefix: str,
    note_suffix: str | None,
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen_prompts: set[str] = set()
    running_index = 1

    for source_index, path in enumerate(paths, start=1):
        rows = _load_dataset(path)
        source_tag = path.stem
        for row in rows:
            prompt = str(row.get("prompt") or "").strip()
            if not prompt:
                raise SystemExit(f"missing_prompt:{path}")
            if prompt in seen_prompts:
                raise SystemExit(f"duplicate_prompt_across_inputs:{path}:{prompt}")

            merged_row = dict(row)
            merged_row["id"] = f"{id_prefix}{running_index:03d}"

            thread_id = str(merged_row.get("thread_id") or "").strip()
            if thread_id:
                merged_row["thread_id"] = f"{thread_id}:merge{source_index}"

            note = str(merged_row.get("note") or "").strip()
            suffix = note_suffix or f"merged from {source_tag}"
            merged_row["note"] = f"{note}; {suffix}" if note else suffix

            merged.append(merged_row)
            seen_prompts.add(prompt)
            running_index += 1

    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge multiple probe datasets into one reindexed dataset.")
    parser.add_argument("--input", type=Path, action="append", required=True, help="Input JSON dataset list.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--id-prefix", default="Q")
    parser.add_argument("--note-suffix", default=None)
    args = parser.parse_args()

    merged = _merge_datasets(args.input, id_prefix=str(args.id_prefix), note_suffix=args.note_suffix)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"merged {len(args.input)} datasets -> {len(merged)} rows -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
