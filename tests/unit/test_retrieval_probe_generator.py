from tools.evals.compare_four_chatbot_paths import STACK_URLS, _user_for_slice
from tools.evals.generate_retrieval_20q_probe_cases import (
    FOCUS_PROTECTED_SQL,
    PROTECTED_SQL_CATEGORIES,
    QUESTION_SPECS,
    _build_selection_units,
    build_cases,
)


def test_small_battery_includes_protected_sql_cases() -> None:
    cases = build_cases(seed=20260403, existing_prompts=set(), count=5)

    assert len(cases) == 5
    assert sum(1 for case in cases if case["slice"] == "public") >= 2
    assert sum(1 for case in cases if case["category"] in PROTECTED_SQL_CATEGORIES) >= 3


def test_followup_threads_are_grouped_as_one_selection_unit() -> None:
    units = _build_selection_units(QUESTION_SPECS)
    family_panorama = next(unit for unit in units if unit["thread_id"] == "retrieval_protected_family_panorama")
    attendance_panorama = next(unit for unit in units if unit["thread_id"] == "retrieval_protected_attendance_panorama")
    assessments_panorama = next(unit for unit in units if unit["thread_id"] == "retrieval_protected_upcoming_assessments")

    assert family_panorama["size"] == 2
    assert attendance_panorama["size"] == 2
    assert assessments_panorama["size"] == 2


def test_compare_four_runner_respects_explicit_user_context() -> None:
    user = _user_for_slice(
        {
            "slice": "public",
            "user": {
                "role": "guardian",
                "authenticated": True,
                "linked_student_ids": ["stu-custom"],
                "scopes": ["students:read", "financial:read"],
            },
        }
    )

    assert user.role.value == "guardian"
    assert user.authenticated is True
    assert user.linked_student_ids == ["stu-custom"]
    assert user.scopes == ["students:read", "financial:read"]


def test_focus_protected_sql_generates_only_sql_backed_protected_cases() -> None:
    cases = build_cases(seed=20260403, existing_prompts=set(), count=8, focus=FOCUS_PROTECTED_SQL)

    assert len(cases) == 8
    assert all(case["slice"] == "protected" for case in cases)
    assert all(case["category"] in PROTECTED_SQL_CATEGORIES for case in cases)


def test_compare_four_runner_defaults_specialist_to_dedicated_compose_port() -> None:
    assert STACK_URLS["specialist_supervisor"] == "http://127.0.0.1:8005"
