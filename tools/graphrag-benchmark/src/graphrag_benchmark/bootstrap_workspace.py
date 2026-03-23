from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml

from graphrag_benchmark.preflight import (
    LOCAL_OPENAI_COMPATIBLE_PROFILE,
    REMOTE_OPENAI_PROFILE,
)


ROOT_DIR = Path(__file__).resolve().parents[4]
DEFAULT_WORKSPACE = ROOT_DIR / 'artifacts' / 'graphrag' / 'eduassist-public-benchmark'
DEFAULT_CORPUS_DIR = ROOT_DIR / 'data' / 'corpus' / 'public'
DEFAULT_DATASET = ROOT_DIR / 'tools' / 'graphrag-benchmark' / 'datasets' / 'public_corpus_queries.json'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Bootstrap a selective GraphRAG benchmark workspace.')
    parser.add_argument('--workspace', type=Path, default=DEFAULT_WORKSPACE)
    parser.add_argument('--corpus-dir', type=Path, default=DEFAULT_CORPUS_DIR)
    parser.add_argument('--dataset', type=Path, default=DEFAULT_DATASET)
    parser.add_argument(
        '--profile',
        choices=[REMOTE_OPENAI_PROFILE, LOCAL_OPENAI_COMPATIBLE_PROFILE],
        default=REMOTE_OPENAI_PROFILE,
    )
    parser.add_argument('--model', default='gpt-4.1')
    parser.add_argument('--embedding-model', default='text-embedding-3-large')
    parser.add_argument('--force-init', action='store_true')
    parser.add_argument('--rewrite-env', action='store_true')
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


def _detect_ollama_models() -> tuple[str | None, str | None]:
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            check=True,
            text=True,
            capture_output=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None, None

    completion_candidates: list[str] = []
    embedding_candidates: list[str] = []
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if not line or line.lower().startswith('name'):
            continue
        model_name = line.split()[0]
        lowered = model_name.lower()
        if 'embed' in lowered:
            embedding_candidates.append(model_name)
        else:
            completion_candidates.append(model_name)

    completion_model = completion_candidates[0] if completion_candidates else None
    embedding_model = embedding_candidates[0] if embedding_candidates else None
    return completion_model, embedding_model


def _patch_settings(*, settings_path: Path, profile: str, model: str, embedding_model: str) -> None:
    payload = yaml.safe_load(settings_path.read_text(encoding='utf-8')) or {}
    if profile == REMOTE_OPENAI_PROFILE:
        payload['completion_models'] = {
            'default_completion_model': {
                'model_provider': 'openai',
                'model': model,
                'auth_method': 'api_key',
                'api_key': '${GRAPHRAG_API_KEY}',
                'retry': {'type': 'exponential_backoff'},
            }
        }
        payload['embedding_models'] = {
            'default_embedding_model': {
                'model_provider': 'openai',
                'model': embedding_model,
                'auth_method': 'api_key',
                'api_key': '${GRAPHRAG_API_KEY}',
                'retry': {'type': 'exponential_backoff'},
            }
        }
    else:
        payload['completion_models'] = {
            'default_completion_model': {
                'model_provider': 'openai',
                'model': '${GRAPHRAG_LOCAL_CHAT_MODEL}',
                'auth_method': 'api_key',
                'api_key': '${GRAPHRAG_LOCAL_CHAT_API_KEY}',
                'api_base': '${GRAPHRAG_LOCAL_CHAT_API_BASE}',
                'retry': {'type': 'exponential_backoff'},
            }
        }
        payload['embedding_models'] = {
            'default_embedding_model': {
                'model_provider': 'openai',
                'model': '${GRAPHRAG_LOCAL_EMBEDDING_MODEL}',
                'auth_method': 'api_key',
                'api_key': '${GRAPHRAG_LOCAL_EMBEDDING_API_KEY}',
                'api_base': '${GRAPHRAG_LOCAL_EMBEDDING_API_BASE}',
                'retry': {'type': 'exponential_backoff'},
            }
        }
        vector_store = payload.setdefault('vector_store', {})
        vector_store['vector_size'] = 768
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


def _build_env_template(*, profile: str) -> str:
    if profile == REMOTE_OPENAI_PROFILE:
        return '\n'.join(
            [
                f'GRAPHRAG_PROVIDER_PROFILE={REMOTE_OPENAI_PROFILE}',
                'GRAPHRAG_API_KEY=<API_KEY>',
                '',
            ]
        )

    completion_model, embedding_model = _detect_ollama_models()
    chat_value = completion_model or 'qwen2.5:7b'
    embedding_value = embedding_model or 'nomic-embed-text'
    return '\n'.join(
        [
            f'GRAPHRAG_PROVIDER_PROFILE={LOCAL_OPENAI_COMPATIBLE_PROFILE}',
            'GRAPHRAG_LOCAL_CHAT_API_BASE=http://127.0.0.1:18080/v1',
            'GRAPHRAG_LOCAL_CHAT_API_KEY=llama.cpp',
            f'GRAPHRAG_LOCAL_CHAT_MODEL={chat_value}',
            'GRAPHRAG_LOCAL_EMBEDDING_API_BASE=http://127.0.0.1:11435/v1',
            'GRAPHRAG_LOCAL_EMBEDDING_API_KEY=ollama',
            f'GRAPHRAG_LOCAL_EMBEDDING_MODEL={embedding_value or "nomic-embed-text:latest"}',
            '',
        ]
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


def _write_workspace_readme(*, workspace: Path, profile: str) -> None:
    provider_note = (
        '- `.env`: definir `GRAPHRAG_API_KEY`\n'
        '- perfil ativo: `openai-remote`'
        if profile == REMOTE_OPENAI_PROFILE
        else '- `.env`: definir `GRAPHRAG_LOCAL_CHAT_API_BASE`, `GRAPHRAG_LOCAL_EMBEDDING_API_BASE`, '
        '`GRAPHRAG_LOCAL_CHAT_MODEL` e `GRAPHRAG_LOCAL_EMBEDDING_MODEL`\n'
        '- perfil ativo: `local-openai-compatible`'
    )
    content = f"""# EduAssist GraphRAG Benchmark Workspace

Workspace gerado automaticamente para benchmark seletivo do GraphRAG.

Objetivo:

- comparar `GraphRAG` com o baseline hibrido atual do projeto;
- rodar experimentos apenas sobre o corpus institucional publico;
- manter a integracao experimental separada do runtime principal.

Arquivos importantes:

- `settings.yaml`: configuracao atual do GraphRAG
{provider_note}
- `input/`: corpus exportado do projeto
- `benchmark-dataset.json`: perguntas padrao para comparacao
- `input/manifest.json`: mapeamento entre documentos do repo e documentos exportados

Fluxo sugerido:

1. preencher `.env`
2. se usar provider local, validar com `make graphrag-benchmark-local-check`
3. `make graphrag-benchmark-index`
4. `make graphrag-benchmark-run`

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
    env_target = workspace / '.env'

    if args.force_init or not settings_path.exists():
        _run_graphrag_init(
            workspace=workspace,
            model=args.model,
            embedding_model=args.embedding_model,
        )

    _patch_settings(
        settings_path=settings_path,
        profile=args.profile,
        model=args.model,
        embedding_model=args.embedding_model,
    )

    if input_dir.exists():
        shutil.rmtree(input_dir)
    manifest = _export_corpus(corpus_dir=args.corpus_dir.resolve(), input_dir=input_dir)
    (input_dir / 'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    shutil.copyfile(args.dataset.resolve(), dataset_target)

    env_template = _build_env_template(profile=args.profile)
    env_example_path.write_text(env_template, encoding='utf-8')
    if args.rewrite_env or not env_target.exists():
        env_target.write_text(env_template, encoding='utf-8')

    _write_workspace_readme(workspace=workspace, profile=args.profile)

    print(
        json.dumps(
            {
                'workspace': workspace.as_posix(),
                'profile': args.profile,
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
