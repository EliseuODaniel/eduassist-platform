package eduassist.authz

import rego.v1

default allow := false
default reason := "no_matching_policy"

decision := {"allow": allow, "reason": reason}

allow if health_check
reason := "health_check" if health_check

allow if identity_context_for_authenticated_actor
reason := "identity_context_for_authenticated_actor" if identity_context_for_authenticated_actor

allow if public_calendar
reason := "public_calendar" if public_calendar

allow if public_ticket_creation
reason := "public_ticket_creation" if public_ticket_creation

allow if guardian_linked_academic_access
reason := "guardian_linked_academic_access" if guardian_linked_academic_access

allow if student_self_academic_access
reason := "student_self_academic_access" if student_self_academic_access

allow if teacher_class_academic_access
reason := "teacher_class_academic_access" if teacher_class_academic_access

allow if coordination_academic_access
reason := "coordination_academic_access" if coordination_academic_access

allow if guardian_linked_finance_access
reason := "guardian_linked_finance_access" if guardian_linked_finance_access

allow if student_self_finance_access
reason := "student_self_finance_access" if student_self_finance_access

allow if finance_team_access
reason := "finance_team_access" if finance_team_access

allow if guardian_linked_admin_access
reason := "guardian_linked_admin_access" if guardian_linked_admin_access

allow if student_self_admin_access
reason := "student_self_admin_access" if student_self_admin_access

allow if coordination_admin_access
reason := "coordination_admin_access" if coordination_admin_access

allow if teacher_own_schedule
reason := "teacher_own_schedule" if teacher_own_schedule

allow if admin_schedule_access
reason := "admin_schedule_access" if admin_schedule_access

allow if self_administrative_status_read
reason := "self_administrative_status_read" if self_administrative_status_read

allow if self_operations_overview
reason := "self_operations_overview" if self_operations_overview

allow if global_operations_overview
reason := "global_operations_overview" if global_operations_overview

allow if self_support_handoffs_read
reason := "self_support_handoffs_read" if self_support_handoffs_read

allow if global_support_handoffs_read
reason := "global_support_handoffs_read" if global_support_handoffs_read

allow if manage_support_handoffs
reason := "manage_support_handoffs" if manage_support_handoffs

health_check if {
    input.action == "health.read"
}

identity_context_for_authenticated_actor if {
    input.action == "identity.context.read"
    input.subject.authenticated
}

public_calendar if {
    input.action == "calendar.read"
    input.resource.visibility == "public"
}

public_ticket_creation if {
    input.action == "ticket.create"
}

guardian_linked_academic_access if {
    input.action == "student.academic.read"
    input.subject.authenticated
    input.subject.role == "guardian"
    input.resource.student_id in input.subject.academic_student_ids
}

student_self_academic_access if {
    input.action == "student.academic.read"
    input.subject.authenticated
    input.subject.role == "student"
    input.resource.student_id == input.subject.student_id
}

teacher_class_academic_access if {
    input.action == "student.academic.read"
    input.subject.authenticated
    input.subject.role == "teacher"
    input.resource.class_id != null
    input.resource.class_id in input.subject.accessible_class_ids
}

coordination_academic_access if {
    input.action == "student.academic.read"
    input.subject.authenticated
    input.subject.role in {"coordinator", "admin"}
}

guardian_linked_finance_access if {
    input.action == "student.finance.read"
    input.subject.authenticated
    input.subject.role == "guardian"
    input.resource.student_id in input.subject.financial_student_ids
}

student_self_finance_access if {
    input.action == "student.finance.read"
    input.subject.authenticated
    input.subject.role == "student"
    input.resource.student_id == input.subject.student_id
}

finance_team_access if {
    input.action == "student.finance.read"
    input.subject.authenticated
    input.subject.role in {"finance", "admin"}
}

guardian_linked_admin_access if {
    input.action == "student.admin.read"
    input.subject.authenticated
    input.subject.role == "guardian"
    input.resource.student_id in input.subject.linked_student_ids
}

student_self_admin_access if {
    input.action == "student.admin.read"
    input.subject.authenticated
    input.subject.role == "student"
    input.resource.student_id == input.subject.student_id
}

coordination_admin_access if {
    input.action == "student.admin.read"
    input.subject.authenticated
    input.subject.role in {"coordinator", "admin"}
}

teacher_own_schedule if {
    input.action == "teacher.schedule.read"
    input.subject.authenticated
    input.subject.role == "teacher"
    input.resource.teacher_id == input.subject.teacher_id
}

admin_schedule_access if {
    input.action == "teacher.schedule.read"
    input.subject.authenticated
    input.subject.role in {"coordinator", "admin"}
}

self_administrative_status_read if {
    input.action == "actor.administrative.read"
    input.subject.authenticated
    input.resource.user_id == input.subject.user_id
}

self_operations_overview if {
    input.action == "operations.overview.read"
    input.subject.authenticated
    input.resource.scope == "self"
}

global_operations_overview if {
    input.action == "operations.overview.read"
    input.subject.authenticated
    input.resource.scope == "global"
    input.subject.role in {"staff", "finance", "coordinator", "admin"}
}

self_support_handoffs_read if {
    input.action == "support.handoffs.read"
    input.subject.authenticated
    input.resource.scope == "self"
}

global_support_handoffs_read if {
    input.action == "support.handoffs.read"
    input.subject.authenticated
    input.resource.scope == "global"
    input.subject.role in {"staff", "finance", "coordinator", "admin"}
}

manage_support_handoffs if {
    input.action == "support.handoffs.manage"
    input.subject.authenticated
    input.subject.role in {"staff", "finance", "coordinator", "admin"}
}
