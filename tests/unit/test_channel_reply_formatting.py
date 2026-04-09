from __future__ import annotations

from ai_orchestrator.channel_reply_formatting import format_reply_for_channel


def test_format_reply_for_telegram_normalizes_inline_markdown_bullets() -> None:
    text = 'As notas de Lucas Oliveira são: * **Biologia**: 8.40 * **História**: 6.70'
    formatted = format_reply_for_channel(text=text, channel='telegram')
    assert 'As notas de Lucas Oliveira são:' in formatted
    assert '- Biologia: 8.40' in formatted
    assert '- História: 6.70' in formatted
    assert '**' not in formatted


def test_format_reply_for_telegram_normalizes_long_grade_list() -> None:
    text = (
        'As notas de Lucas Oliveira são: * **Biologia**: Avaliação B1 - 8.40/10.00 '
        '* **Educação Física**: Avaliação 2026-B1 - EF - 6.40/10.00 '
        '* **História**: Avaliação 2026-B1 - HIS - 6.70/10.00'
    )
    formatted = format_reply_for_channel(text=text, channel='telegram')
    assert '\n- Biologia: Avaliação B1 - 8.40/10.00' in formatted
    assert '\n- Educação Física: Avaliação 2026-B1 - EF - 6.40/10.00' in formatted
    assert '\n- História: Avaliação 2026-B1 - HIS - 6.70/10.00' in formatted
    assert '**' not in formatted


def test_format_reply_for_telegram_breaks_single_line_bullets_from_llm() -> None:
    text = (
        'As notas parciais de Lucas Oliveira são: - Biologia: 7,9/10 '
        '- Educação Física: 6,5/10 - História: 6,8/10'
    )
    formatted = format_reply_for_channel(text=text, channel='telegram')
    assert 'As notas parciais de Lucas Oliveira são:\n- Biologia: 7,9/10' in formatted
    assert '\n- Educação Física: 6,5/10' in formatted
    assert '\n- História: 6,8/10' in formatted
