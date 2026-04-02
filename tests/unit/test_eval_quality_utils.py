from __future__ import annotations

from tools.evals.eval_quality_utils import _contains_forbidden_keywords


def test_forbidden_keywords_ignore_punctuation_only_false_positive() -> None:
    answer = 'O Colegio Horizonte nao divulga nome nem contato direto de professor individual por disciplina.'
    assert not _contains_forbidden_keywords(answer, ['@'])


def test_forbidden_keywords_still_detect_raw_at_symbol() -> None:
    answer = 'Se precisar, escreva para contato@colegio.example.'
    assert _contains_forbidden_keywords(answer, ['@'])
