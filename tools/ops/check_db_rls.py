from __future__ import annotations

import json
import os
from dataclasses import dataclass

import psycopg


@dataclass(frozen=True)
class ActorSpec:
    external_code: str
    role_code: str


def main() -> int:
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print(json.dumps({'ok': False, 'error': 'DATABASE_URL_missing'}))
        return 1

    with psycopg.connect(database_url) as connection:
        payload = run_checks(connection)

    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0 if payload['ok'] else 1


def run_checks(connection: psycopg.Connection) -> dict[str, object]:
    zero_visibility = query_scalar(
        connection,
        """
        select count(*)
        from school.students
        """,
        actor=None,
    )

    maria_visible_students = query_scalar(
        connection,
        """
        select count(*)
        from school.students students
        join identity.users users on users.id = students.user_id
        where users.external_code in ('USR-STUD-001', 'USR-STUD-002', 'USR-STUD-003')
        """,
        actor=ActorSpec(external_code='USR-GUARD-001', role_code='guardian'),
    )
    maria_bruno_grades = query_scalar(
        connection,
        """
        select count(*)
        from academic.grades grades
        join school.enrollments enrollments on enrollments.id = grades.enrollment_id
        join school.students students on students.id = enrollments.student_id
        join identity.users users on users.id = students.user_id
        where users.external_code = 'USR-STUD-003'
        """,
        actor=ActorSpec(external_code='USR-GUARD-001', role_code='guardian'),
    )
    maria_visible_invoices = query_scalar(
        connection,
        """
        select count(*)
        from finance.invoices invoices
        join finance.contracts contracts on contracts.id = invoices.contract_id
        join school.students students on students.id = contracts.student_id
        join identity.users users on users.id = students.user_id
        where users.external_code in ('USR-STUD-001', 'USR-STUD-002', 'USR-STUD-003')
        """,
        actor=ActorSpec(external_code='USR-GUARD-001', role_code='guardian'),
    )

    marcos_lucas_grades = query_scalar(
        connection,
        """
        select count(*)
        from academic.grades grades
        join school.enrollments enrollments on enrollments.id = grades.enrollment_id
        join school.students students on students.id = enrollments.student_id
        join identity.users users on users.id = students.user_id
        where users.external_code = 'USR-STUD-001'
        """,
        actor=ActorSpec(external_code='USR-TEACH-002', role_code='teacher'),
    )
    marcos_bruno_grades = query_scalar(
        connection,
        """
        select count(*)
        from academic.grades grades
        join school.enrollments enrollments on enrollments.id = grades.enrollment_id
        join school.students students on students.id = enrollments.student_id
        join identity.users users on users.id = students.user_id
        where users.external_code = 'USR-STUD-003'
        """,
        actor=ActorSpec(external_code='USR-TEACH-002', role_code='teacher'),
    )

    carla_visible_invoices = query_scalar(
        connection,
        """
        select count(*)
        from finance.invoices invoices
        """,
        actor=ActorSpec(external_code='USR-FIN-001', role_code='finance'),
    )

    lucas_visible_students = query_scalar(
        connection,
        """
        select count(*)
        from school.students students
        join identity.users users on users.id = students.user_id
        where users.external_code in ('USR-STUD-001', 'USR-STUD-003')
        """,
        actor=ActorSpec(external_code='USR-STUD-001', role_code='student'),
    )

    maria_visible_conversations = query_scalar(
        connection,
        """
        select count(*)
        from conversation.conversations conversations
        """,
        actor=ActorSpec(external_code='USR-GUARD-001', role_code='guardian'),
    )
    ana_visible_handoffs = query_scalar(
        connection,
        """
        select count(*)
        from conversation.handoffs handoffs
        """,
        actor=ActorSpec(external_code='USR-STUD-002', role_code='student'),
    )
    carla_visible_handoffs = query_scalar(
        connection,
        """
        select count(*)
        from conversation.handoffs handoffs
        """,
        actor=ActorSpec(external_code='USR-FIN-001', role_code='finance'),
    )
    anonymous_public_calendar_events = query_scalar(
        connection,
        """
        select count(*)
        from calendar.calendar_events events
        """,
        actor=None,
    )
    maria_visible_classes = query_scalar(
        connection,
        """
        select count(*)
        from school.classes classes
        """,
        actor=ActorSpec(external_code='USR-GUARD-001', role_code='guardian'),
    )
    maria_visible_guardian_links = query_scalar(
        connection,
        """
        select count(*)
        from school.guardian_student_links links
        """,
        actor=ActorSpec(external_code='USR-GUARD-001', role_code='guardian'),
    )
    maria_visible_guardians = query_scalar(
        connection,
        """
        select count(*)
        from school.guardians guardians
        """,
        actor=ActorSpec(external_code='USR-GUARD-001', role_code='guardian'),
    )
    marcos_visible_teacher_assignments = query_scalar(
        connection,
        """
        select count(*)
        from academic.teacher_assignments assignments
        """,
        actor=ActorSpec(external_code='USR-TEACH-002', role_code='teacher'),
    )
    maria_visible_grade_items = query_scalar(
        connection,
        """
        select count(*)
        from academic.grade_items grade_items
        """,
        actor=ActorSpec(external_code='USR-GUARD-001', role_code='guardian'),
    )
    maria_visible_calendar_events = query_scalar(
        connection,
        """
        select count(*)
        from calendar.calendar_events events
        """,
        actor=ActorSpec(external_code='USR-GUARD-001', role_code='guardian'),
    )
    bruno_visible_calendar_events = query_scalar(
        connection,
        """
        select count(*)
        from calendar.calendar_events events
        """,
        actor=ActorSpec(external_code='USR-STUD-003', role_code='student'),
    )

    checks = {
        'default_deny_students': zero_visibility == 0,
        'guardian_student_scope': maria_visible_students == 2,
        'guardian_denied_other_student_grades': maria_bruno_grades == 0,
        'guardian_finance_scope': maria_visible_invoices == 2,
        'teacher_visible_assigned_class_grades': marcos_lucas_grades > 0,
        'teacher_denied_other_class_grades': marcos_bruno_grades == 0,
        'finance_team_visible_all_invoices': carla_visible_invoices == 3,
        'student_self_scope_only': lucas_visible_students == 1,
        'guardian_visible_own_conversations': maria_visible_conversations >= 1,
        'unrelated_student_denied_handoffs': ana_visible_handoffs == 0,
        'finance_team_visible_handoffs': carla_visible_handoffs >= 1,
        'anonymous_public_calendar_visible': anonymous_public_calendar_events == 1,
        'guardian_visible_classes': maria_visible_classes == 1,
        'guardian_visible_guardian_links': maria_visible_guardian_links == 2,
        'guardian_visible_own_guardian_profile': maria_visible_guardians == 1,
        'teacher_visible_accessible_assignments': marcos_visible_teacher_assignments == 3,
        'guardian_visible_grade_items': maria_visible_grade_items == 2,
        'guardian_visible_calendar_events': maria_visible_calendar_events == 2,
        'student_visible_calendar_events': bruno_visible_calendar_events == 2,
    }

    return {
        'ok': all(checks.values()),
        'checks': checks,
        'measurements': {
            'default_deny_students': zero_visibility,
            'guardian_visible_students': maria_visible_students,
            'guardian_bruno_grades': maria_bruno_grades,
            'guardian_visible_invoices': maria_visible_invoices,
            'teacher_lucas_grades': marcos_lucas_grades,
            'teacher_bruno_grades': marcos_bruno_grades,
            'finance_visible_invoices': carla_visible_invoices,
            'student_visible_students': lucas_visible_students,
            'guardian_visible_conversations': maria_visible_conversations,
            'unrelated_student_visible_handoffs': ana_visible_handoffs,
            'finance_visible_handoffs': carla_visible_handoffs,
            'anonymous_public_calendar_events': anonymous_public_calendar_events,
            'guardian_visible_classes': maria_visible_classes,
            'guardian_visible_guardian_links': maria_visible_guardian_links,
            'guardian_visible_guardians': maria_visible_guardians,
            'teacher_visible_assignments': marcos_visible_teacher_assignments,
            'guardian_visible_grade_items': maria_visible_grade_items,
            'guardian_visible_calendar_events': maria_visible_calendar_events,
            'student_visible_calendar_events': bruno_visible_calendar_events,
        },
    }


def query_scalar(connection: psycopg.Connection, sql: str, *, actor: ActorSpec | None) -> int:
    with connection.transaction():
        with connection.cursor() as cursor:
            if actor is None:
                cursor.execute("select set_config('eduassist.actor_context', '{}', true)")
            else:
                user_id = resolve_user_id(cursor, actor.external_code)
                cursor.execute(
                    "select set_config('eduassist.actor_context', %s, true)",
                    (
                        json.dumps(
                            {
                                'user_id': str(user_id),
                                'role_code': actor.role_code,
                            },
                            separators=(',', ':'),
                            sort_keys=True,
                        ),
                    ),
                )
            cursor.execute(sql)
            row = cursor.fetchone()
            if row is None:
                raise RuntimeError('query_did_not_return_row')
            return int(row[0])


def resolve_user_id(cursor: psycopg.Cursor, external_code: str) -> str:
    cursor.execute(
        """
        select id::text
        from identity.users
        where external_code = %s
        """,
        (external_code,),
    )
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError(f'user_not_found:{external_code}')
    return str(row[0])


if __name__ == '__main__':
    raise SystemExit(main())
