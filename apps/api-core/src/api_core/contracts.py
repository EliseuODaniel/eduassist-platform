from __future__ import annotations

import uuid
from datetime import date, datetime
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


class AttendanceRecordEntry(BaseModel):
    subject_code: str
    subject_name: str
    record_date: date
    status: str
    minutes_absent: int


class UpcomingAssessmentEntry(BaseModel):
    subject_code: str
    subject_name: str
    item_title: str
    term_code: str
    due_date: date


class StudentAcademicSummary(BaseModel):
    student_id: uuid.UUID
    class_id: uuid.UUID | None = None
    class_name: str | None = None
    student_name: str
    enrollment_code: str
    grade_level: int
    grades: list[GradeEntry]
    attendance: list[AttendanceEntry]


class StudentAttendanceTimeline(BaseModel):
    student_id: uuid.UUID
    class_id: uuid.UUID | None = None
    class_name: str | None = None
    student_name: str
    enrollment_code: str
    records: list[AttendanceRecordEntry]


class StudentUpcomingAssessments(BaseModel):
    student_id: uuid.UUID
    class_id: uuid.UUID | None = None
    class_name: str | None = None
    student_name: str
    enrollment_code: str
    assessments: list[UpcomingAssessmentEntry]


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


class AdministrativeChecklistItem(BaseModel):
    item_key: str
    label: str
    status: str
    notes: str | None = None


class AdministrativeStatusSummary(BaseModel):
    actor_name: str
    role_code: str
    profile_email: str | None = None
    profile_phone: str | None = None
    overall_status: str
    next_step: str | None = None
    checklist: list[AdministrativeChecklistItem] = Field(default_factory=list)


class StudentAdministrativeStatusSummary(BaseModel):
    student_id: uuid.UUID
    student_name: str
    enrollment_code: str
    guardian_name: str | None = None
    overall_status: str
    next_step: str | None = None
    checklist: list[AdministrativeChecklistItem] = Field(default_factory=list)


class StudentAttendanceTimelineResponse(BaseModel):
    summary: StudentAttendanceTimeline


class StudentUpcomingAssessmentsResponse(BaseModel):
    summary: StudentUpcomingAssessments


class AdministrativeStatusResponse(BaseModel):
    summary: AdministrativeStatusSummary


class StudentAdministrativeStatusResponse(BaseModel):
    summary: StudentAdministrativeStatusSummary


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


class PublicShiftOffer(BaseModel):
    segment: str
    shift_code: str
    shift_label: str
    starts_at: str
    ends_at: str
    notes: str | None = None


class PublicTuitionReference(BaseModel):
    segment: str
    shift_label: str
    monthly_amount: Decimal
    enrollment_fee: Decimal
    notes: str | None = None


class PublicContactChannel(BaseModel):
    channel: str
    label: str
    value: str


class PublicFeatureAvailability(BaseModel):
    feature_key: str
    label: str
    category: str
    available: bool
    notes: str | None = None


class PublicLeadershipMember(BaseModel):
    member_key: str
    name: str
    title: str
    focus: str
    contact_channel: str | None = None
    notes: str | None = None


class PublicKpiEntry(BaseModel):
    metric_key: str
    label: str
    value: float
    unit: str
    reference_period: str
    notes: str | None = None


class PublicHighlightEntry(BaseModel):
    highlight_key: str
    title: str
    description: str
    evidence_line: str | None = None


class PublicVisitOffer(BaseModel):
    offer_key: str
    title: str
    audience: str
    day_label: str
    start_time: str
    end_time: str
    location: str
    notes: str | None = None


class PublicServiceCatalogEntry(BaseModel):
    service_key: str
    title: str
    audience: str
    request_channel: str
    typical_eta: str
    notes: str | None = None


class PublicDocumentSubmissionPolicy(BaseModel):
    accepts_digital_submission: bool
    accepted_channels: list[str] = Field(default_factory=list)
    warning: str | None = None
    notes: str | None = None


class PublicSchoolProfile(BaseModel):
    school_unit_code: str
    school_name: str
    city: str
    state: str
    timezone: str
    address_line: str
    district: str
    postal_code: str | None = None
    website_url: str | None = None
    fax_number: str | None = None
    short_headline: str
    education_model: str
    curriculum_basis: str | None = None
    curriculum_components: list[str] = Field(default_factory=list)
    confessional_status: str
    segments: list[str] = Field(default_factory=list)
    shift_offers: list[PublicShiftOffer] = Field(default_factory=list)
    tuition_reference: list[PublicTuitionReference] = Field(default_factory=list)
    contact_channels: list[PublicContactChannel] = Field(default_factory=list)
    feature_inventory: list[PublicFeatureAvailability] = Field(default_factory=list)
    leadership_team: list[PublicLeadershipMember] = Field(default_factory=list)
    public_kpis: list[PublicKpiEntry] = Field(default_factory=list)
    highlights: list[PublicHighlightEntry] = Field(default_factory=list)
    visit_offers: list[PublicVisitOffer] = Field(default_factory=list)
    service_catalog: list[PublicServiceCatalogEntry] = Field(default_factory=list)
    document_submission_policy: PublicDocumentSubmissionPolicy | None = None
    documented_services: list[str] = Field(default_factory=list)
    admissions_highlights: list[str] = Field(default_factory=list)


class PublicSchoolProfileResponse(BaseModel):
    profile: PublicSchoolProfile


class PublicAssistantCapabilities(BaseModel):
    school_name: str
    segments: list[str] = Field(default_factory=list)
    public_topics: list[str] = Field(default_factory=list)
    protected_topics: list[str] = Field(default_factory=list)
    workflow_topics: list[str] = Field(default_factory=list)


class PublicAssistantCapabilitiesResponse(BaseModel):
    capabilities: PublicAssistantCapabilities


class PublicOrgDirectory(BaseModel):
    school_name: str
    leadership_team: list[PublicLeadershipMember] = Field(default_factory=list)
    contact_channels: list[PublicContactChannel] = Field(default_factory=list)


class PublicOrgDirectoryResponse(BaseModel):
    directory: PublicOrgDirectory


class PublicServiceDirectory(BaseModel):
    school_name: str
    services: list[PublicServiceCatalogEntry] = Field(default_factory=list)


class PublicServiceDirectoryResponse(BaseModel):
    directory: PublicServiceDirectory


class PublicTimelineEntry(BaseModel):
    topic_key: str
    title: str
    summary: str
    event_date: date | None = None
    audience: str | None = None
    notes: str | None = None


class PublicTimeline(BaseModel):
    school_name: str
    entries: list[PublicTimelineEntry] = Field(default_factory=list)


class PublicTimelineResponse(BaseModel):
    timeline: PublicTimeline


class InternalConversationMessageEntry(BaseModel):
    sender_type: str
    content: str
    created_at: datetime


class InternalConversationToolCallEntry(BaseModel):
    tool_name: str
    status: str
    request_payload: dict[str, Any] = Field(default_factory=dict)
    response_payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class InternalConversationContextResponse(BaseModel):
    channel: str
    conversation_external_id: str
    conversation_status: str | None = None
    message_count: int = 0
    recent_messages: list[InternalConversationMessageEntry] = Field(default_factory=list)
    recent_tool_calls: list[InternalConversationToolCallEntry] = Field(default_factory=list)


class InternalConversationMessageCreate(BaseModel):
    sender_type: str
    content: str


class InternalConversationAppendRequest(BaseModel):
    channel: str = 'telegram'
    conversation_external_id: str
    actor_user_id: uuid.UUID | None = None
    messages: list[InternalConversationMessageCreate] = Field(default_factory=list)


class InternalConversationAppendResponse(BaseModel):
    channel: str
    conversation_external_id: str
    stored_messages: int = 0
    deduplicated_messages: int = 0
    message_count: int = 0


class InternalConversationToolCallCreate(BaseModel):
    tool_name: str
    status: str
    request_payload: dict[str, Any] = Field(default_factory=dict)
    response_payload: dict[str, Any] = Field(default_factory=dict)


class InternalConversationToolCallAppendRequest(BaseModel):
    channel: str = 'telegram'
    conversation_external_id: str
    actor_user_id: uuid.UUID | None = None
    tool_calls: list[InternalConversationToolCallCreate] = Field(default_factory=list)


class InternalConversationToolCallAppendResponse(BaseModel):
    channel: str
    conversation_external_id: str
    stored_tool_calls: int = 0
    deduplicated_messages: int = 0
    message_count: int = 0


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


class HandoffQueueOverviewEntry(BaseModel):
    queue_name: str
    open_count: int = 0
    queued_count: int = 0
    in_progress_count: int = 0
    attention_count: int = 0
    breached_count: int = 0
    unassigned_count: int = 0


class HandoffOperatorOverviewEntry(BaseModel):
    operator_user_id: uuid.UUID
    operator_external_code: str
    operator_name: str
    assigned_count: int = 0
    queued_count: int = 0
    in_progress_count: int = 0
    attention_count: int = 0
    breached_count: int = 0


class HandoffPriorityOverviewEntry(BaseModel):
    priority_code: str
    open_count: int = 0
    queued_count: int = 0
    in_progress_count: int = 0
    attention_count: int = 0
    breached_count: int = 0


class HandoffAgingBucketEntry(BaseModel):
    bucket_code: str
    label: str
    open_count: int = 0
    queued_count: int = 0
    in_progress_count: int = 0
    attention_count: int = 0
    breached_count: int = 0


class HandoffAlertEntry(BaseModel):
    handoff_id: uuid.UUID
    ticket_code: str
    queue_name: str
    priority_code: str
    status: str
    summary: str
    requester_name: str | None = None
    assigned_operator_name: str | None = None
    updated_at: datetime
    response_due_at: datetime | None = None
    resolution_due_at: datetime | None = None
    sla_state: str
    alert_flags: list[str] = Field(default_factory=list)


class HandoffTrendPoint(BaseModel):
    period_start: datetime
    label: str
    opened_count: int = 0
    started_count: int = 0
    resolved_count: int = 0


class HandoffObservabilityOverview(BaseModel):
    opened_last_24h: int = 0
    started_last_24h: int = 0
    resolved_last_24h: int = 0
    opened_last_7d: int = 0
    started_last_7d: int = 0
    resolved_last_7d: int = 0
    avg_assignment_minutes_7d: float | None = None
    avg_resolution_minutes_7d: float | None = None
    timeline: list[HandoffTrendPoint] = Field(default_factory=list)


class HandoffOperationsOverview(BaseModel):
    open_total: int = 0
    queued_total: int = 0
    in_progress_total: int = 0
    attention_total: int = 0
    breached_total: int = 0
    unassigned_total: int = 0
    critical_total: int = 0
    queues: list[HandoffQueueOverviewEntry] = Field(default_factory=list)
    operators: list[HandoffOperatorOverviewEntry] = Field(default_factory=list)
    priorities: list[HandoffPriorityOverviewEntry] = Field(default_factory=list)
    aging_buckets: list[HandoffAgingBucketEntry] = Field(default_factory=list)
    alerts: list[HandoffAlertEntry] = Field(default_factory=list)
    oldest_open_ticket_code: str | None = None
    oldest_open_minutes: float | None = None
    observability: HandoffObservabilityOverview | None = None


class OperationsOverviewResponse(BaseModel):
    actor: ActorContext
    scope: str
    metrics: dict[str, int] = Field(default_factory=dict)
    foundation_counts: dict[str, int] | None = None
    audit_events: list[AuditEventFeedEntry] = Field(default_factory=list)
    access_decisions: list[AccessDecisionFeedEntry] = Field(default_factory=list)
    handoff_overview: HandoffOperationsOverview | None = None


class InternalSupportHandoffCreateRequest(BaseModel):
    conversation_external_id: str
    channel: str = 'telegram'
    queue_name: str
    summary: str
    telegram_chat_id: int | None = None
    user_message: str | None = None


class SupportHandoffStatusUpdateRequest(BaseModel):
    status: str | None = None
    operator_note: str | None = None
    assigned_user_id: uuid.UUID | None = None
    clear_assignment: bool = False


class SupportHandoffEntry(BaseModel):
    handoff_id: uuid.UUID
    conversation_id: uuid.UUID
    ticket_code: str
    channel: str
    external_thread_id: str
    queue_name: str
    priority_code: str
    status: str
    summary: str
    requester_name: str | None = None
    requester_role: str | None = None
    assigned_user_id: uuid.UUID | None = None
    assigned_operator_name: str | None = None
    assigned_operator_external_code: str | None = None
    assigned_at: datetime | None = None
    response_due_at: datetime | None = None
    resolution_due_at: datetime | None = None
    sla_state: str = 'unknown'
    last_message_excerpt: str | None = None
    created_at: datetime
    updated_at: datetime


class SupportHandoffFilters(BaseModel):
    status: str | None = None
    queue_name: str | None = None
    assignment: str | None = None
    sla_state: str | None = None
    search: str | None = None
    page: int = 1
    limit: int = 10


class SupportConversationMessageEntry(BaseModel):
    message_id: uuid.UUID
    sender_type: str
    content: str
    created_at: datetime


class SupportConversationThreadEntry(BaseModel):
    conversation_id: uuid.UUID
    channel: str
    external_thread_id: str
    conversation_status: str
    requester_name: str | None = None
    requester_role: str | None = None
    message_count: int = 0
    last_message_excerpt: str | None = None
    latest_message_at: datetime | None = None
    linked_ticket_code: str | None = None
    linked_queue_name: str | None = None
    linked_ticket_status: str | None = None
    created_at: datetime
    updated_at: datetime


class InternalVisitBookingCreateRequest(BaseModel):
    conversation_external_id: str
    channel: str = 'telegram'
    telegram_chat_id: int | None = None
    audience_name: str | None = None
    audience_contact: str | None = None
    interested_segment: str | None = None
    preferred_date: date | None = None
    preferred_window: str | None = None
    attendee_count: int = 1
    notes: str


class VisitBookingEntry(BaseModel):
    booking_id: uuid.UUID
    protocol_code: str
    status: str
    queue_name: str
    linked_ticket_code: str | None = None
    audience_name: str | None = None
    interested_segment: str | None = None
    preferred_date: date | None = None
    preferred_window: str | None = None
    slot_label: str | None = None
    created_at: datetime


class VisitBookingCreateResponse(BaseModel):
    created: bool
    item: VisitBookingEntry


class InternalVisitBookingActionRequest(BaseModel):
    conversation_external_id: str
    channel: str = 'telegram'
    telegram_chat_id: int | None = None
    protocol_code: str | None = None
    action: str
    preferred_date: date | None = None
    preferred_window: str | None = None
    notes: str | None = None


class VisitBookingActionResponse(BaseModel):
    action: str
    item: VisitBookingEntry


class InternalInstitutionalRequestCreateRequest(BaseModel):
    conversation_external_id: str
    channel: str = 'telegram'
    telegram_chat_id: int | None = None
    target_area: str
    category: str
    subject: str
    details: str
    requester_contact: str | None = None


class InstitutionalRequestEntry(BaseModel):
    request_id: uuid.UUID
    protocol_code: str
    target_area: str
    category: str
    subject: str
    status: str
    queue_name: str
    linked_ticket_code: str | None = None
    created_at: datetime


class InstitutionalRequestCreateResponse(BaseModel):
    created: bool
    item: InstitutionalRequestEntry


class InternalInstitutionalRequestActionRequest(BaseModel):
    conversation_external_id: str
    channel: str = 'telegram'
    telegram_chat_id: int | None = None
    protocol_code: str | None = None
    action: str
    details: str | None = None


class InstitutionalRequestActionResponse(BaseModel):
    action: str
    item: InstitutionalRequestEntry


class WorkflowStatusEntry(BaseModel):
    workflow_type: str
    protocol_code: str
    status: str
    queue_name: str | None = None
    linked_ticket_code: str | None = None
    subject: str | None = None
    summary: str | None = None
    target_area: str | None = None
    preferred_date: date | None = None
    preferred_window: str | None = None
    slot_label: str | None = None
    created_at: datetime
    updated_at: datetime


class InternalWorkflowStatusResponse(BaseModel):
    found: bool
    item: WorkflowStatusEntry | None = None


class SupportHandoffCreateResponse(BaseModel):
    created: bool
    deduplicated: bool = False
    item: SupportHandoffEntry


class SupportHandoffPagination(BaseModel):
    page: int = 1
    page_size: int = 10
    total_items: int = 0
    total_pages: int = 1
    has_previous_page: bool = False
    has_next_page: bool = False
    visible_from: int = 0
    visible_to: int = 0


class SupportHandoffListResponse(BaseModel):
    actor: ActorContext
    scope: str
    counts: dict[str, int] = Field(default_factory=dict)
    filters: SupportHandoffFilters = Field(default_factory=SupportHandoffFilters)
    pagination: SupportHandoffPagination = Field(default_factory=SupportHandoffPagination)
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


class SupportConversationListResponse(BaseModel):
    actor: ActorContext
    scope: str
    items: list[SupportConversationThreadEntry] = Field(default_factory=list)


class SupportConversationDetailResponse(BaseModel):
    actor: ActorContext
    scope: str
    item: SupportConversationThreadEntry
    messages: list[SupportConversationMessageEntry] = Field(default_factory=list)
