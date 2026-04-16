from __future__ import annotations

from api_core.services.domain import _teacher_segment_from_class_name_and_level


def test_teacher_segment_from_class_name_and_level_prefers_series_name_for_ensino_medio() -> None:
    assert _teacher_segment_from_class_name_and_level('1o Ano A', 1) == 'Ensino Medio'
    assert _teacher_segment_from_class_name_and_level('3o Ano B', 3) == 'Ensino Medio'


def test_teacher_segment_from_class_name_and_level_keeps_fundamental_for_middle_years() -> None:
    assert _teacher_segment_from_class_name_and_level('6o Ano A', 6) == 'Ensino Fundamental II'
    assert _teacher_segment_from_class_name_and_level('8o Ano B', 8) == 'Ensino Fundamental II'
