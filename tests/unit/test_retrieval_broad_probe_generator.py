from collections import Counter

from tools.evals.generate_retrieval_broad_30q_probe_cases import build_cases


def test_broad_battery_has_expected_size_and_persona_coverage() -> None:
    cases = build_cases(seed=20260415, existing_prompts=set())

    assert len(cases) == 30

    roles = Counter(str(case.get("user", {}).get("role") or "") for case in cases)
    assert roles["anonymous"] >= 10
    assert roles["guardian"] >= 10
    assert roles["teacher"] >= 2
    assert roles["student"] >= 1
    assert roles["staff"] >= 1


def test_broad_battery_covers_public_protected_restricted_and_out_of_scope() -> None:
    cases = build_cases(seed=20260415, existing_prompts=set())

    slices = Counter(str(case.get("slice") or "") for case in cases)
    categories = {str(case.get("category") or "") for case in cases}

    assert slices["public"] >= 10
    assert slices["protected"] >= 10
    assert slices["restricted"] >= 4
    assert "public_external_library_boundary" in categories
    assert "public_open_world_out_of_scope" in categories
    assert "protected_boundary_auth_needed" in categories


def test_broad_battery_uses_valid_authenticated_persona_chat_ids() -> None:
    cases = build_cases(seed=20260415, existing_prompts=set())
    by_category = {str(case.get("category") or ""): case for case in cases}

    assert by_category["protected_teacher_schedule"]["telegram_chat_id"] == 1649845501
    assert by_category["protected_teacher_schedule_followup"]["telegram_chat_id"] == 1649845501
    assert by_category["protected_student_academic_self"]["telegram_chat_id"] == 777013
    assert by_category["restricted_staff_finance_protocol"]["telegram_chat_id"] == 888002
    assert "documents:restricted:read" in by_category["restricted_staff_finance_protocol"]["user"]["scopes"]
