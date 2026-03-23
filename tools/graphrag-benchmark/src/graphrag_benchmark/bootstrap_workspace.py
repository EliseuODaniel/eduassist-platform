from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml


ROOT_DIR = Path(__file__).resolve().parents[4]
DEFAULT_WORKSPACE = ROOT_DIR / 'artifacts' / 'graphrag' / 'eduassist-public-benchmark'
DEFAULT_CORPUS_DIR = ROOT_DIR / 'data' / 'corpus' / 'public'
DEFAULT_DATASET = ROOT_DIR / 'tools' / 'graphrag-benchmark' / 'datasets' / 'public_corpus_queries.json'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Bootstrap a selective GraphRAG benchmark workspace.')
    parser.add_argument('--workspace', type=Path, default=DEFAULT_WORKSPACE)
    parser.add_argument('--corpus-dir', type=Path, default=DEFAULT_CORPUS_DIR)
    parser.add_argument('--dataset', type=Path, default=DEFAULT_DATASET)
    parser.add_argument('--model', default='gpt-4.1')
    parser.add_argument('--embedding-model', default='text-embedding-3-large')
    parser.add_argument('--force-init', action='store_true')
    return parser.parse_args()


def _load_markdown_document(path: Path) -> tuple[dict[str, Any], str]:
    content = path.read_text(encoding='utf-8')
    if content.startswith('---\n'):
        _, frontmatter, body = content.split('---\n', 2)
        metadata = yaml.safe_load(frontmatter) or {}
        return metadata, body.strip()
    return {}, content.strip()


def _render_text_document(*, source_path: Path, metadata: dict[str, Any], body: str) -> str:
    labels = metadata.get('labels', {})
    label_parts: list[str] = []
    if isinstance(labels, dict):
        for key, values in labels.items():
            if isinstance(values, list):
                label_parts.append(f'{key}={", ".join(str(value) for value in values)}')
    header_lines = [
        f'Title: {metadata.get("title", source_path.stem)}',
        f'Category: {metadata.get("category", "unknown")}',
        f'Audience: {metadata.get("audience", "publico")}',
        f'Visibility: {metadata.get("visibility", "public")}',
        f'Version: {metadata.get("version_label", "v0")}',
        f'Source Path: {source_path.as_posix()}',
    ]
    if label_parts:
        header_lines.append(f'Labels: {"; ".join(label_parts)}')
    return '\n'.join([*header_lines, '', body, ''])


def _run_graphrag_init(*, workspace: Path, model: str, embedding_model: str) -> None:
    workspace.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            'graphrag',
            'init',
            '-r',
            str(workspace),
            '-f',
            '-m',
            model,
            '-e',
            embedding_model,
        ],
        check=True,
    )


def _patch_settings(settings_path: Path) -> None:
    payload = yaml.safe_load(settings_path.read_text(encoding='utf-8')) or {}
    payload.setdefault('input', {})['type'] = 'text'
    chunking = payload.setdefault('chunking', {})
    chunking['type'] = 'tokens'
    chunking['size'] = 300
    chunking['overlap'] = 40
    chunking['encoding_model'] = 'o200k_base'
    snapshots = payload.setdefault('snapshots', {})
    snapshots['graphml'] = True
    snapshots['embeddings'] = False
    settings_path.write_text(
        yaml.safe_dump(payload, allow_unicode=False, sort_keys=False),
        encoding='utf-8',
    )


def _export_corpus(*, corpus_dir: Path, input_dir: Path) -> list[dict[str, Any]]:
    input_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    for path in sorted(corpus_dir.rglob('*.md')):
        metadata, body = _load_markdown_document(path)
        target = input_dir / f'{path.stem}.txt'
        rendered = _render_text_document(source_path=path.relative_to(ROOT_DIR), metadata=metadata, body=body)
        target.write_text(rendered, encoding='utf-8')
        manifest.append(
            {
                'source_path': path.relative_to(ROOT_DIR).as_posix(),
                'workspace_input_path': target.relative_to(input_dir.parent).as_posix(),
                'title': metadata.get('title', path.stem),
                'category': metadata.get('category', 'unknown'),
                'audience': metadata.get('audience', 'publico'),
                'visibility': metadata.get('visibility', 'public'),
                'version_label': metadata.get('version_label', 'v0'),
            }
        )
    return manifest


def _write_workspace_readme(workspace: Path) -> None:
    content = f"""# EduAssist GraphRAG Benchmark Workspace

Workspace gerado automaticamente para benchmark seletivo do GraphRAG.

Objetivo:

- comparar `GraphRAG` com o baseline hibrido atual do projeto;
- rodar experimentos apenas sobre o corpus institucional publico;
- manter a integracao experimental separada do runtime principal.

Arquivos importantes:

- `settings.yaml`: configuracao atual do GraphRAG
- `.env`: definir `GRAPHRAG_API_KEY`
- `input/`: corpus exportado do projeto
- `benchmark-dataset.json`: perguntas padrao para comparacao
- `input/manifest.json`: mapeamento entre documentos do repo e documentos exportados

Fluxo sugerido:

1. preencher `.env`
2. `make graphrag-benchmark-index`
3. `make graphrag-benchmark-run`

Nota importante:

- para corpus em portugues, prefira `GRAPHRAG_INDEX_METHOD=standard` no benchmark principal;
- o modo `fast` e util para custo/latencia, mas a extracao NLP padrao do GraphRAG e otimizada para ingles.
"""
    (workspace / 'README.md').write_text(content, encoding='utf-8')


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    settings_path = workspace / 'settings.yaml'
    input_dir = workspace / 'input'
    dataset_target = workspace / 'benchmark-dataset.json'
    env_example_path = workspace / '.env.example'

    if args.force_init or not settings_path.exists():
        _run_graphrag_init(
            workspace=workspace,
            model=args.model,
            embedding_model=args.embedding_model,
        )

    _patch_settings(settings_path)

    if input_dir.exists():
        shutil.rmtree(input_dir)
    manifest = _export_corpus(corpus_dir=args.corpus_dir.resolve(), input_dir=input_dir)
    (input_dir / 'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    shutil.copyfile(args.dataset.resolve(), dataset_target)

    generated_env = workspace / '.env'
    if generated_env.exists() and not env_example_path.exists():
        shutil.copyfile(generated_env, env_example_path)
    elif not env_example_path.exists():
        env_example_path.write_text('GRAPHRAG_API_KEY=<API_KEY>\n', encoding='utf-8')

    _write_workspace_readme(workspace)

    print(
        json.dumps(
            {
                'workspace': workspace.as_posix(),
                'documents_exported': len(manifest),
                'settings': settings_path.as_posix(),
                'dataset': dataset_target.as_posix(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
