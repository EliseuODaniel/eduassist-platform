from __future__ import annotations

from ai_orchestrator import (
    graph,
    llamaindex_native_runtime,
    python_functions_native_runtime,
)
from ai_orchestrator.extracted_module_contracts import refresh_extracted_module_contract
from ai_orchestrator.graph_classification_contract import GRAPH_CLASSIFICATION_CONTRACT
from ai_orchestrator.graph_execution_contract import GRAPH_EXECUTION_CONTRACT
from ai_orchestrator.llamaindex_native_plan_contract import LLAMAINDEX_NATIVE_PLAN_CONTRACT
from ai_orchestrator.llamaindex_native_support_contract import LLAMAINDEX_NATIVE_SUPPORT_CONTRACT
from ai_orchestrator.python_functions_native_plan_contract import PYTHON_FUNCTIONS_NATIVE_PLAN_CONTRACT
from ai_orchestrator_specialist import fast_path_answers
from ai_orchestrator_specialist.extracted_module_contracts import (
    refresh_extracted_module_contract as refresh_specialist_extracted_module_contract,
)
from ai_orchestrator_specialist.fast_path_answer_contract import FAST_PATH_ANSWER_CONTRACT


def test_python_functions_native_plan_contract_symbols_exist() -> None:
    missing = [name for name in PYTHON_FUNCTIONS_NATIVE_PLAN_CONTRACT if not hasattr(python_functions_native_runtime, name)]
    assert not missing


def test_llamaindex_native_plan_contract_symbols_exist() -> None:
    missing = [name for name in LLAMAINDEX_NATIVE_PLAN_CONTRACT if not hasattr(llamaindex_native_runtime, name)]
    assert not missing


def test_llamaindex_native_support_contract_symbols_exist() -> None:
    missing = [name for name in LLAMAINDEX_NATIVE_SUPPORT_CONTRACT if not hasattr(llamaindex_native_runtime, name)]
    assert not missing


def test_graph_classification_contract_symbols_exist() -> None:
    missing = [name for name in GRAPH_CLASSIFICATION_CONTRACT if not hasattr(graph, name)]
    assert not missing


def test_graph_execution_contract_symbols_exist() -> None:
    missing = [name for name in GRAPH_EXECUTION_CONTRACT if not hasattr(graph, name)]
    assert not missing


def test_specialist_fast_path_contract_symbols_exist() -> None:
    missing = [name for name in FAST_PATH_ANSWER_CONTRACT if not hasattr(fast_path_answers, name)]
    assert not missing


def test_contract_refresh_binds_only_declared_python_functions_symbols() -> None:
    namespace: dict[str, object] = {}
    refresh_extracted_module_contract(
        native_module=python_functions_native_runtime,
        namespace=namespace,
        contract_names=PYTHON_FUNCTIONS_NATIVE_PLAN_CONTRACT,
        local_extracted_names=frozenset({'maybe_execute_python_functions_native_plan'}),
        contract_label='python_functions_native_plan_runtime',
    )
    assert 'maybe_execute_python_functions_native_plan' not in namespace
    assert namespace['rt'] is python_functions_native_runtime.rt
    assert namespace['build_response_candidate'] is python_functions_native_runtime.build_response_candidate


def test_contract_refresh_binds_only_declared_specialist_symbols() -> None:
    namespace: dict[str, object] = {}
    refresh_specialist_extracted_module_contract(
        native_module=fast_path_answers,
        namespace=namespace,
        contract_names=FAST_PATH_ANSWER_CONTRACT,
        local_extracted_names=frozenset({'build_fast_path_answer'}),
        contract_label='fast_path_answer_runtime',
    )
    assert 'build_fast_path_answer' not in namespace
    assert namespace['match_public_canonical_lane'] is fast_path_answers.match_public_canonical_lane


def test_contract_refresh_binds_only_declared_graph_symbols() -> None:
    namespace: dict[str, object] = {}
    refresh_extracted_module_contract(
        native_module=graph,
        namespace=namespace,
        contract_names=GRAPH_EXECUTION_CONTRACT,
        local_extracted_names=frozenset({'structured_tool_call', 'get_graph_blueprint'}),
        contract_label='graph_execution_runtime',
    )
    assert 'structured_tool_call' not in namespace
    assert namespace['_append_path'] is graph._append_path
