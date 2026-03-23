from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class LinkedStudentReference(BaseModel):
    student_id: uuid.UUID
    full_name: str
    enrollment_code: str
    class_id: uuid.UUID | None = None
    class_name: str | None = None
    can_view_academic: bool = True
    can_view_finance: bool = True


class AccessibleClassReference(BaseModel):
    class_id: uuid.UUID
    class_name: str
    subject_name: str | None = None


class ActorContext(BaseModel):
    user_id: uuid.UUID
    role_code: str
    external_code: str
    full_name: str
    authenticated: bool = True
    telegram_chat_id: int | None = None
    telegram_linked: bool = False
    guardian_id: uuid.UUID | None = None
    student_id: uuid.UUID | None = None
    teacher_id: uuid.UUID | None = None
    linked_student_ids: list[uuid.UUID] = Field(default_factory=list)
    academic_student_ids: list[uuid.UUID] = Field(default_factory=list)
    financial_student_ids: list[uuid.UUID] = Field(default_factory=list)
    accessible_class_ids: list[uuid.UUID] = Field(default_factory=list)
    linked_students: list[LinkedStudentReference] = Field(default_factory=list)
    accessible_classes: list[AccessibleClassReference] = Field(default_factory=list)

    def to_policy_subject(self) -> dict[str, object]:
        return {
            'user_id': str(self.user_id),
            'role': self.role_code,
            'authenticated': self.authenticated,
            'telegram_linked': self.telegram_linked,
            'guardian_id': str(self.guardian_id) if self.guardian_id else None,
            'student_id': str(self.student_id) if self.student_id else None,
            'teacher_id': str(self.teacher_id) if self.teacher_id else None,
            'linked_student_ids': [str(student_id) for student_id in self.linked_student_ids],
            'academic_student_ids': [str(student_id) for student_id in self.academic_student_ids],
            'financial_student_ids': [str(student_id) for student_id in self.financial_student_ids],
            'accessible_class_ids': [str(class_id) for class_id in self.accessible_class_ids],
        }


class PolicyDecision(BaseModel):
    allow: bool
    reason: str
    source: str


class PolicyCheckRequest(BaseModel):
    action: str
    telegram_chat_id: int | None = None
    user_external_code: str | None = None
    resource: dict[str, object] = Field(default_factory=dict)


class PolicyCheckResponse(BaseModel):
    actor: ActorContext
    decision: PolicyDecision
    action: str
    resource: dict[str, object]


class AuthPrincipal(BaseModel):
    provider: str
    subject: str
    issuer: str
    azp: str | None = None
    audiences: list[str] = Field(default_factory=list)
    preferred_username: str | None = None
    email: str | None = None
    email_verified: bool = False
    realm_roles: list[str] = Field(default_factory=list)


class AuthSessionResponse(BaseModel):
    actor: ActorContext
    principal: AuthPrincipal
    auth_mode: str


class TelegramLinkChallengeResponse(BaseModel):
    challenge_code: str
    expires_at: datetime
    bot_username: str | None = None
    telegram_deep_link: str | None = None
    telegram_command: str


class TelegramLinkConsumeRequest(BaseModel):
    challenge_code: str
    telegram_user_id: int | None = None
    telegram_chat_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class TelegramLinkConsumeResponse(BaseModel):
    linked: bool
    actor: ActorContext
    telegram_chat_id: int
    telegram_username: str | None = None


class GradeEntry(BaseModel):
    subject_code: str
    subject_name: str
    item_title: str
    term_code: str
    score: Decimal
    max_score: Decimal
    feedback: str | None = None


class AttendanceEntry(BaseModel):
    subject_code: str
    subject_name: str
    present_count: int
    late_count: int
    absent_count: int
    absent_minutes: int


class StudentAcademicSummary(BaseModel):
    student_id: uuid.UUID
    class_id: uuid.UUID | None = None
    class_name: str | None = None
    student_name: str
    enrollment_code: str
    grade_level: int
    grades: list[GradeEntry]
    attendance: list[AttendanceEntry]


class InvoiceEntry(BaseModel):
    invoice_id: uuid.UUID
    reference_month: str
    due_date: str
    amount_due: Decimal
    status: str
    paid_amount: Decimal = Decimal('0.00')


class StudentFinancialSummary(BaseModel):
    student_id: uuid.UUID
    student_name: str
    contract_code: str
    guardian_name: str
    monthly_amount: Decimal
    invoices: list[InvoiceEntry]
    open_invoice_count: int
    overdue_invoice_count: int


class TeacherScheduleEntry(BaseModel):
    class_id: uuid.UUID
    class_name: str
    subject_code: str
    subject_name: str
    academic_year: int


class TeacherScheduleSummary(BaseModel):
    teacher_id: uuid.UUID
    teacher_name: str
    employee_code: str
    department: str
    assignments: list[TeacherScheduleEntry]


class CalendarEventEntry(BaseModel):
    event_id: uuid.UUID
    class_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    category: str
    audience: str
    visibility: str
    starts_at: datetime
    ends_at: datetime


class CalendarEventsResponse(BaseModel):
    events: list[CalendarEventEntry]


class AuditEventFeedEntry(BaseModel):
    occurred_at: datetime
    actor_user_id: uuid.UUID | None = None
    actor_external_code: str | None = None
    actor_full_name: str | None = None
    event_type: str
    resource_type: str
    resource_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AccessDecisionFeedEntry(BaseModel):
    occurred_at: datetime
    actor_user_id: uuid.UUID | None = None
    actor_external_code: str | None = None
    actor_full_name: str | None = None
    resource_type: str
    action: str
    decision: str
    reason: str | None = None


class OperationsOverviewResponse(BaseModel):
    actor: ActorContext
    scope: str
    metrics: dict[str, int] = Field(default_factory=dict)
    foundation_counts: dict[str, int] | None = None
    audit_events: list[AuditEventFeedEntry] = Field(default_factory=list)
    access_decisions: list[AccessDecisionFeedEntry] = Field(default_factory=list)


class InternalSupportHandoffCreateRequest(BaseModel):
    conversation_external_id: str
    channel: str = 'telegram'
    queue_name: str
    summary: str
    telegram_chat_id: int | None = None
    user_message: str | None = None


class SupportHandoffStatusUpdateRequest(BaseModel):
    status: str
    operator_note: str | None = None


class SupportHandoffEntry(BaseModel):
    handoff_id: uuid.UUID
    conversation_id: uuid.UUID
    ticket_code: str
    channel: str
    external_thread_id: str
    queue_name: str
    status: str
    summary: str
    requester_name: str | None = None
    requester_role: str | None = None
    last_message_excerpt: str | None = None
    created_at: datetime
    updated_at: datetime


class SupportConversationMessageEntry(BaseModel):
    message_id: uuid.UUID
    sender_type: str
    content: str
    created_at: datetime


class SupportHandoffCreateResponse(BaseModel):
    created: bool
    deduplicated: bool = False
    item: SupportHandoffEntry


class SupportHandoffListResponse(BaseModel):
    actor: ActorContext
    scope: str
    counts: dict[str, int] = Field(default_factory=dict)
    items: list[SupportHandoffEntry] = Field(default_factory=list)


class SupportHandoffUpdateResponse(BaseModel):
    actor: ActorContext
    item: SupportHandoffEntry


class SupportHandoffDetailResponse(BaseModel):
    actor: ActorContext
    scope: str
    item: SupportHandoffEntry
    conversation_status: str
    messages: list[SupportConversationMessageEntry] = Field(default_factory=list)
