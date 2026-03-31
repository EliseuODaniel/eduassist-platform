from __future__ import annotations

import json
from pathlib import Path

from ai_orchestrator.llamaindex_native_runtime import (
    _heuristic_llamaindex_native_public_decision,
    _should_trust_llamaindex_native_deterministic_answer,
)


CASES = (
    {
        'message': 'por que deveria colocar meus filhos nesse colegio?',
        'expected_act': 'highlight',
        'expected_mode': 'profile',
        'expected_attribute': None,
        'expected_unpublished': None,
        'selected_tools': ('public_profile',),
        'expected_trust': True,
    },
    {
        'message': 'o que preciso para uma bolsa de 50%?',
        'expected_act': 'pricing',
        'expected_mode': 'profile',
        'expected_attribute': 'scholarship_policy',
        'expected_unpublished': None,
        'selected_tools': ('public_profile',),
        'expected_trust': True,
    },
    {
        'message': 'qual idade minima pra estudar no colegio?',
        'expected_act': 'segments',
        'expected_mode': 'unpublished',
        'expected_attribute': 'minimum_age',
        'expected_unpublished': 'minimum_age',
        'selected_tools': ('public_profile',),
        'expected_trust': True,
    },
    {
        'message': 'quantas salas de aula o colegio tem?',
        'expected_act': 'features',
        'expected_mode': 'unpublished',
        'expected_attribute': 'classroom_count',
        'expected_unpublished': 'classroom_count',
        'selected_tools': ('public_profile',),
        'expected_trust': True,
    },
    {
        'message': 'qual o nome do diretor da escola?',
        'expected_act': 'leadership',
        'expected_mode': 'profile',
        'expected_attribute': 'leadership',
        'expected_unpublished': None,
        'selected_tools': ('public_profile',),
        'expected_trust': True,
    },
)


def main() -> None:
    rows: list[dict[str, object]] = []
    passed = 0
    for case in CASES:
        decision = _heuristic_llamaindex_native_public_decision(
            message=str(case['message']),
            conversation_context=None,
        )
        trust = _should_trust_llamaindex_native_deterministic_answer(
            native_decision=decision,
            selected_tool_names=tuple(case['selected_tools']),
        )
        ok = (
            decision is not None
            and decision.conversation_act == case['expected_act']
            and decision.answer_mode == case['expected_mode']
            and decision.requested_attribute == case['expected_attribute']
            and decision.unpublished_key == case['expected_unpublished']
            and trust is case['expected_trust']
        )
        if ok:
            passed += 1
        rows.append(
            {
                'message': case['message'],
                'decision': decision.model_dump(mode='json') if decision is not None else None,
                'trust_native_deterministic_answer': trust,
                'passed': ok,
            }
        )

    report = {
        'passed': passed,
        'total': len(CASES),
        'rows': rows,
    }
    Path('/tmp/llamaindex_native_public_routing_report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
