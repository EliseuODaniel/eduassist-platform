from __future__ import annotations

import ast
from pathlib import Path

RUNTIME_PATH = Path('apps/ai-orchestrator/src/ai_orchestrator/runtime.py')
CORE_RUNTIME_PATH = Path('apps/ai-orchestrator/src/ai_orchestrator/runtime_core.py')
MESSAGE_RESPONSE_PATH = Path('apps/ai-orchestrator/src/ai_orchestrator/message_response_runtime.py')
MODULE_BUDGETS = {
    Path('apps/ai-orchestrator/src/ai_orchestrator/runtime.py'): 2_000,
    Path('apps/ai-orchestrator/src/ai_orchestrator/runtime_core.py'): 500,
    Path('apps/ai-orchestrator/src/ai_orchestrator/message_response_runtime.py'): 1_950,
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_orchestration_runtime.py'): 3_050,
    Path('apps/ai-orchestrator/src/ai_orchestrator/intent_analysis_runtime.py'): 1_800,
    Path('apps/ai-orchestrator/src/ai_orchestrator/protected_domain_runtime.py'): 1_800,
}
EXTRACTED_MODULES = [
    Path('apps/ai-orchestrator/src/ai_orchestrator/runtime_api.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_profile_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/protected_records_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/structured_tool_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/message_response_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/workflow_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/answer_verification_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/conversation_focus_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/analysis_context_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/runtime_core_constants.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/intent_analysis_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_act_rules_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_orchestration_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/reply_experience_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/student_scope_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/protected_summary_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/protected_domain_runtime.py'),
]


def _line_count(path: Path) -> int:
    return path.read_text(encoding='utf-8').count('\n') + 1


def test_runtime_module_budgets() -> None:
    violations = []
    for module_path, budget in MODULE_BUDGETS.items():
        line_count = _line_count(module_path)
        if line_count > budget:
            violations.append(f'{module_path}: {line_count} > {budget}')
    assert not violations, 'budgets estruturais excedidos: ' + '; '.join(violations)


def test_runtime_core_no_longer_holds_god_function() -> None:
    module = ast.parse(CORE_RUNTIME_PATH.read_text(encoding='utf-8'))
    function_sizes = [
        node.end_lineno - node.lineno + 1
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert function_sizes, 'runtime_core.py nao possui funcoes top-level para inspecao'
    assert max(function_sizes) <= 400, (
        f'runtime_core.py ainda contem funcao grande demais: {max(function_sizes)} linhas'
    )


def test_message_response_runtime_main_flow_stays_readable() -> None:
    module = ast.parse(MESSAGE_RESPONSE_PATH.read_text(encoding='utf-8'))
    sizes = {
        node.name: node.end_lineno - node.lineno + 1
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert 'generate_message_response' in sizes, 'generate_message_response nao encontrado'
    assert sizes['generate_message_response'] <= 800, (
        'generate_message_response voltou a ficar grande demais: '
        f"{sizes['generate_message_response']} linhas"
    )


def test_runtime_decomposition_modules_exist() -> None:
    missing = [str(path) for path in EXTRACTED_MODULES if not path.exists()]
    assert not missing, f'modulos extraidos ausentes: {missing}'
