from __future__ import annotations

import ast
from pathlib import Path

MODULE_BUDGETS = {
    Path('apps/api-core/src/api_core/services/domain.py'): 710,
    Path('apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/fast_path_answers.py'): 600,
    Path('apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/local_retrieval.py'): 1825,
    Path('apps/ai-orchestrator/src/ai_orchestrator/grounded_answer_experience.py'): 4320,
    Path('apps/ai-orchestrator/src/ai_orchestrator/graph.py'): 2600,
    Path('apps/ai-orchestrator/src/ai_orchestrator/graph_classification_runtime.py'): 350,
    Path('apps/ai-orchestrator/src/ai_orchestrator/graph_execution_runtime.py'): 220,
    Path('apps/ai-orchestrator/src/ai_orchestrator/langgraph_message_workflow.py'): 850,
    Path('apps/ai-orchestrator/src/ai_orchestrator/langgraph_public_compound_runtime.py'): 730,
    Path('apps/ai-orchestrator/src/ai_orchestrator/langgraph_public_retrieval_runtime.py'): 550,
    Path('apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_preflight_runtime.py'): 500,
    Path('apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_plan_runtime.py'): 1925,
    Path('apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_runtime.py'): 2600,
    Path('apps/ai-orchestrator/src/ai_orchestrator/native_runtime_preparation.py'): 260,
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_doc_knowledge.py'): 1100,
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_doc_lane_answer_runtime.py'): 80,
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_doc_lane_match_runtime.py'): 650,
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_doc_lane_registry.py'): 50,
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_profile_runtime.py'): 5400,
    Path('apps/ai-orchestrator/src/ai_orchestrator/python_functions_native_plan_runtime.py'): 1600,
    Path('apps/ai-orchestrator/src/ai_orchestrator/python_functions_native_runtime.py'): 340,
}

EXTRACTED_MODULES = [
    Path('apps/api-core/src/api_core/services/public_profile_seed.py'),
    Path('apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/fast_path_answer_runtime.py'),
    Path('apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/local_retrieval_rerank_runtime.py'),
    Path('apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/local_retrieval_search_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/graph_classification_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/graph_execution_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/grounded_answer_pipeline_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/grounded_answer_support_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/langgraph_public_compound_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/langgraph_public_retrieval_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_plan_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_preflight_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_support_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/native_runtime_preparation.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_doc_lane_answer_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_doc_lane_match_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_doc_lane_registry.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_profile_slot_memory_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_profile_legacy_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_profile_routes_runtime.py'),
    Path('apps/ai-orchestrator/src/ai_orchestrator/python_functions_native_plan_runtime.py'),
]

FUNCTION_BUDGETS = {
    Path('apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/fast_path_answers.py'): {
        'build_fast_path_answer': 20,
    },
    Path('apps/ai-orchestrator/src/ai_orchestrator/graph.py'): {
        'classify_request': 10,
        'route_request': 10,
        'structured_tool_call': 10,
        'get_graph_blueprint': 10,
    },
    Path('apps/ai-orchestrator/src/ai_orchestrator/graph_classification_runtime.py'): {
        'classify_request': 250,
        'route_request': 120,
    },
    Path('apps/ai-orchestrator/src/ai_orchestrator/graph_execution_runtime.py'): {
        'structured_tool_call': 160,
        'get_graph_blueprint': 50,
    },
    Path('apps/ai-orchestrator/src/ai_orchestrator/grounded_answer_experience.py'): {
        'apply_grounded_answer_experience': 60,
        '_deterministic_public_direct_answer': 20,
        '_deterministic_protected_academic_direct_answer': 20,
        '_deterministic_protected_attendance_direct_answer': 20,
        '_deterministic_protected_finance_direct_answer': 20,
        '_build_supplemental_focus': 20,
        '_preserve_deterministic_answer_surface': 20,
    },
    Path('apps/ai-orchestrator/src/ai_orchestrator/langgraph_public_compound_runtime.py'): {
        '_public_compound': 725,
    },
    Path('apps/ai-orchestrator/src/ai_orchestrator/langgraph_public_retrieval_runtime.py'): {
        '_public_retrieval': 540,
    },
    Path('apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_plan_runtime.py'): {
        'maybe_execute_llamaindex_native_plan': 1900,
    },
    Path('apps/ai-orchestrator/src/ai_orchestrator/llamaindex_native_runtime.py'): {
        'maybe_execute_llamaindex_native_plan': 25,
    },
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_doc_lane_answer_runtime.py'): {
        'compose_public_canonical_lane_answer': 20,
    },
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_doc_lane_match_runtime.py'): {
        'match_public_canonical_lane': 600,
    },
    Path('apps/ai-orchestrator/src/ai_orchestrator/public_profile_runtime.py'): {
        '_build_conversation_slot_memory': 25,
        '_compose_public_profile_answer_legacy': 25,
        '_compose_public_feature_answer': 20,
        '_try_public_channel_fast_answer': 20,
        '_build_public_profile_context': 25,
        '_handle_public_contacts': 20,
        '_handle_public_timeline': 20,
        '_compose_public_pricing_projection_answer': 20,
    },
    Path('apps/ai-orchestrator/src/ai_orchestrator/python_functions_native_plan_runtime.py'): {
        'maybe_execute_python_functions_native_plan': 1600,
    },
    Path('apps/ai-orchestrator/src/ai_orchestrator/python_functions_native_runtime.py'): {
        'maybe_execute_python_functions_native_plan': 25,
    },
}

METHOD_BUDGETS = {
    Path('apps/ai-orchestrator-specialist/src/ai_orchestrator_specialist/local_retrieval.py'): {
        'RetrievalService': {
            'hybrid_search': 25,
            '_lexical_search': 25,
            '_fuse_hits': 25,
        }
    },
}


def _line_count(path: Path) -> int:
    return path.read_text(encoding='utf-8').count('\n') + 1


def test_hotspot_module_budgets() -> None:
    violations = []
    for module_path, budget in MODULE_BUDGETS.items():
        count = _line_count(module_path)
        if count > budget:
            violations.append(f'{module_path}: {count} > {budget}')
    assert not violations, 'budgets dos hotspots excedidos: ' + '; '.join(violations)


def test_hotspot_extracted_modules_exist() -> None:
    missing = [str(path) for path in EXTRACTED_MODULES if not path.exists()]
    assert not missing, f'modulos extraidos ausentes: {missing}'


def test_hotspot_wrapper_function_budgets() -> None:
    violations: list[str] = []
    for module_path, budgets in FUNCTION_BUDGETS.items():
        tree = ast.parse(module_path.read_text(encoding='utf-8'))
        sizes = {
            node.name: node.end_lineno - node.lineno + 1
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        for name, budget in budgets.items():
            size = sizes.get(name)
            if size is None:
                violations.append(f'{module_path}: funcao ausente {name}')
            elif size > budget:
                violations.append(f'{module_path}:{name} {size} > {budget}')
    assert not violations, 'wrappers dos hotspots cresceram demais: ' + '; '.join(violations)


def test_hotspot_wrapper_method_budgets() -> None:
    violations: list[str] = []
    for module_path, class_budgets in METHOD_BUDGETS.items():
        tree = ast.parse(module_path.read_text(encoding='utf-8'))
        classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
        for class_name, method_budgets in class_budgets.items():
            class_node = classes.get(class_name)
            if class_node is None:
                violations.append(f'{module_path}: classe ausente {class_name}')
                continue
            method_sizes = {
                child.name: child.end_lineno - child.lineno + 1
                for child in class_node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            for method_name, budget in method_budgets.items():
                size = method_sizes.get(method_name)
                if size is None:
                    violations.append(f'{module_path}:{class_name}.{method_name} ausente')
                elif size > budget:
                    violations.append(f'{module_path}:{class_name}.{method_name} {size} > {budget}')
    assert not violations, 'metodos wrapper dos hotspots cresceram demais: ' + '; '.join(violations)
