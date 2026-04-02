from __future__ import annotations

import importlib
import sys
import types
from datetime import date
from pathlib import Path

sys.modules.setdefault('minio', types.SimpleNamespace(Minio=object))
pipeline_module = importlib.import_module('worker_app.pipeline')
CorpusDocument = pipeline_module.CorpusDocument
DocumentPipeline = pipeline_module.DocumentPipeline


def test_build_summary_records_groups_chunks_by_parent_ref_key() -> None:
    pipeline = object.__new__(DocumentPipeline)
    document = CorpusDocument(
        source_path=Path('/tmp/manual-matricula.md'),
        document_set_slug='matricula',
        document_set_title='Matricula',
        title='Manual de Matricula',
        category='admissions',
        audience='familias',
        visibility='public',
        version_label='2026.1',
        effective_from=date(2026, 1, 1),
        labels={},
        raw_content='raw',
        normalized_markdown=(
            '## Documentos\nEnvio pelo portal\n\n## Documentos\nPrazo da secretaria'
        ),
    )
    indexed_documents = [
        {
            'document': document,
            'storage_path': 'corpus/public/matricula/manual-2026.md',
            'chunks': [
                {
                    'chunk_id': 'chunk-1',
                    'chunk_index': 0,
                    'document_title': 'Manual de Matricula',
                    'category': 'admissions',
                    'audience': 'familias',
                    'visibility': 'public',
                    'contextual_summary': 'Matricula > Documentos',
                    'text_content': 'Envio dos documentos pelo portal institucional.',
                    'section_path': 'Matricula > Documentos',
                    'section_parent': 'Matricula',
                    'section_title': 'Documentos',
                    'parent_ref_key': 'corpus/public/matricula/manual-2026.md::Matricula',
                },
                {
                    'chunk_id': 'chunk-2',
                    'chunk_index': 1,
                    'document_title': 'Manual de Matricula',
                    'category': 'admissions',
                    'audience': 'familias',
                    'visibility': 'public',
                    'contextual_summary': 'Matricula > Documentos',
                    'text_content': 'A secretaria valida os anexos e informa pendencias.',
                    'section_path': 'Matricula > Documentos',
                    'section_parent': 'Matricula',
                    'section_title': 'Documentos',
                    'parent_ref_key': 'corpus/public/matricula/manual-2026.md::Matricula',
                },
            ],
        }
    ]

    records = DocumentPipeline._build_summary_records(pipeline, indexed_documents)

    assert len(records) == 1
    record = records[0]
    assert record.parent_ref_key == 'corpus/public/matricula/manual-2026.md::Matricula'
    assert record.document_title == 'Manual de Matricula'
    assert record.section_title == 'Documentos'
    assert 'Resumo contextual:' in record.summary_text
    assert 'Trechos relacionados:' in record.summary_text
