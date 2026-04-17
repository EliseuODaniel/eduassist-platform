from __future__ import annotations

import uuid
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import Integer, func, select
from sqlalchemy.orm import Session, aliased

from api_core.contracts import (
    AdministrativeChecklistItem,
    AdministrativeStatusSummary,
    AttendanceEntry,
    AttendanceRecordEntry,
    CalendarEventEntry,
    GradeEntry,
    InvoiceEntry,
    PublicAssistantCapabilities,
    PublicOrgDirectory,
    PublicSchoolProfile,
    PublicServiceDirectory,
    PublicTimeline,
    PublicTimelineEntry,
    StudentAcademicSummary,
    StudentAdministrativeStatusSummary,
    StudentAttendanceTimeline,
    StudentFinancialSummary,
    StudentUpcomingAssessments,
    TeacherScheduleEntry,
    TeacherScheduleSummary,
    UpcomingAssessmentEntry,
)
from .public_profile_seed import build_public_school_profile

from api_core.db.models import (
    AttendanceRecord,
    CalendarEvent,
    Class,
    Contract,
    Enrollment,
    Grade,
    GradeItem,
    Guardian,
    Invoice,
    Payment,
    SchoolUnit,
    Student,
    Subject,
    Teacher,
    TeacherAssignment,
    User,
)


def _student_base_context(
    session: Session,
    student_id: uuid.UUID,
) -> tuple[uuid.UUID, str, str, int, uuid.UUID | None, str | None, uuid.UUID] | None:
    return session.execute(
        select(
            Student.id,
            User.full_name,
            Student.enrollment_code,
            Student.current_grade_level,
            Class.id,
            Class.display_name,
            Enrollment.id,
        )
        .join(User, User.id == Student.user_id)
        .join(Enrollment, Enrollment.student_id == Student.id)
        .join(Class, Class.id == Enrollment.class_id)
        .where(Student.id == student_id)
    ).first()


def get_student_academic_summary(session: Session, student_id: uuid.UUID) -> StudentAcademicSummary | None:
    base = _student_base_context(session, student_id)
    if base is None:
        return None

    student_id_value, student_name, enrollment_code, grade_level, class_id, class_name, enrollment_id = base

    grade_rows = session.execute(
        select(
            Subject.code,
            Subject.name,
            GradeItem.title,
            GradeItem.term_code,
            Grade.score,
            GradeItem.max_score,
            Grade.feedback,
        )
        .join(GradeItem, GradeItem.id == Grade.grade_item_id)
        .join(TeacherAssignment, TeacherAssignment.id == GradeItem.teacher_assignment_id)
        .join(Subject, Subject.id == TeacherAssignment.subject_id)
        .where(Grade.enrollment_id == enrollment_id)
        .order_by(Subject.code, GradeItem.due_date)
    ).all()

    attendance_rows = session.execute(
        select(
            Subject.code,
            Subject.name,
            func.sum((AttendanceRecord.status == 'present').cast(Integer)).label('present_count'),
            func.sum((AttendanceRecord.status == 'late').cast(Integer)).label('late_count'),
            func.sum((AttendanceRecord.status == 'absent').cast(Integer)).label('absent_count'),
            func.coalesce(func.sum(AttendanceRecord.minutes_absent), 0).label('absent_minutes'),
        )
        .join(Subject, Subject.id == AttendanceRecord.subject_id)
        .where(AttendanceRecord.enrollment_id == enrollment_id)
        .group_by(Subject.code, Subject.name)
        .order_by(Subject.code)
    ).all()

    return StudentAcademicSummary(
        student_id=student_id_value,
        class_id=class_id,
        class_name=class_name,
        student_name=student_name,
        enrollment_code=enrollment_code,
        grade_level=grade_level,
        grades=[
            GradeEntry(
                subject_code=subject_code,
                subject_name=subject_name,
                item_title=item_title,
                term_code=term_code,
                score=score,
                max_score=max_score,
                feedback=feedback,
            )
            for subject_code, subject_name, item_title, term_code, score, max_score, feedback in grade_rows
        ],
        attendance=[
            AttendanceEntry(
                subject_code=subject_code,
                subject_name=subject_name,
                present_count=int(present_count or 0),
                late_count=int(late_count or 0),
                absent_count=int(absent_count or 0),
                absent_minutes=int(absent_minutes or 0),
            )
            for subject_code, subject_name, present_count, late_count, absent_count, absent_minutes in attendance_rows
        ],
    )


def get_student_attendance_timeline(
    session: Session,
    student_id: uuid.UUID,
    *,
    subject_code: str | None = None,
    limit: int = 12,
) -> StudentAttendanceTimeline | None:
    base = _student_base_context(session, student_id)
    if base is None:
        return None

    student_id_value, student_name, enrollment_code, _grade_level, class_id, class_name, enrollment_id = base

    query = (
        select(
            Subject.code,
            Subject.name,
            AttendanceRecord.record_date,
            AttendanceRecord.status,
            AttendanceRecord.minutes_absent,
        )
        .join(Subject, Subject.id == AttendanceRecord.subject_id)
        .where(AttendanceRecord.enrollment_id == enrollment_id)
        .order_by(AttendanceRecord.record_date.desc(), Subject.code.asc())
        .limit(limit)
    )
    if subject_code:
        query = query.where(func.lower(Subject.code) == subject_code.lower())

    records = session.execute(query).all()
    return StudentAttendanceTimeline(
        student_id=student_id_value,
        class_id=class_id,
        class_name=class_name,
        student_name=student_name,
        enrollment_code=enrollment_code,
        records=[
            AttendanceRecordEntry(
                subject_code=row_subject_code,
                subject_name=row_subject_name,
                record_date=record_date,
                status=status,
                minutes_absent=int(minutes_absent or 0),
            )
            for row_subject_code, row_subject_name, record_date, status, minutes_absent in records
        ],
    )


def get_student_upcoming_assessments(
    session: Session,
    student_id: uuid.UUID,
    *,
    subject_code: str | None = None,
    from_date: date | None = None,
    limit: int = 8,
) -> StudentUpcomingAssessments | None:
    base = _student_base_context(session, student_id)
    if base is None:
        return None

    student_id_value, student_name, enrollment_code, _grade_level, class_id, class_name, _enrollment_id = base
    if class_id is None:
        return None

    start_date = from_date or date.today()
    query = (
        select(
            Subject.code,
            Subject.name,
            GradeItem.title,
            GradeItem.term_code,
            GradeItem.due_date,
        )
        .join(TeacherAssignment, TeacherAssignment.id == GradeItem.teacher_assignment_id)
        .join(Subject, Subject.id == TeacherAssignment.subject_id)
        .where(TeacherAssignment.class_id == class_id)
        .where(GradeItem.due_date >= start_date)
        .order_by(GradeItem.due_date.asc(), Subject.code.asc(), GradeItem.title.asc())
        .limit(limit)
    )
    if subject_code:
        query = query.where(func.lower(Subject.code) == subject_code.lower())

    assessments = session.execute(query).all()
    return StudentUpcomingAssessments(
        student_id=student_id_value,
        class_id=class_id,
        class_name=class_name,
        student_name=student_name,
        enrollment_code=enrollment_code,
        assessments=[
            UpcomingAssessmentEntry(
                subject_code=row_subject_code,
                subject_name=row_subject_name,
                item_title=item_title,
                term_code=term_code,
                due_date=due_date,
            )
            for row_subject_code, row_subject_name, item_title, term_code, due_date in assessments
        ],
    )


def get_student_financial_summary(session: Session, student_id: uuid.UUID) -> StudentFinancialSummary | None:
    student_user = aliased(User)
    guardian_user = aliased(User)
    base = session.execute(
        select(
            Student.id,
            student_user.full_name,
            Contract.id,
            Contract.contract_code,
            Contract.monthly_amount,
            Guardian.id,
            guardian_user.full_name,
        )
        .join(student_user, student_user.id == Student.user_id)
        .join(Contract, Contract.student_id == Student.id)
        .join(Guardian, Guardian.id == Contract.guardian_id)
        .join(guardian_user, guardian_user.id == Guardian.user_id)
        .where(Student.id == student_id)
    ).first()
    if base is None:
        return None

    student_id_value, student_name, contract_id, contract_code, monthly_amount, guardian_id, guardian_name = base

    payment_totals = {
        invoice_id: amount_paid
        for invoice_id, amount_paid in session.execute(
            select(Payment.invoice_id, func.coalesce(func.sum(Payment.amount_paid), 0))
            .group_by(Payment.invoice_id)
        )
    }

    invoices = session.execute(
        select(Invoice.id, Invoice.reference_month, Invoice.due_date, Invoice.amount_due, Invoice.status)
        .where(Invoice.contract_id == contract_id)
        .order_by(Invoice.reference_month)
    ).all()

    invoice_entries = [
        InvoiceEntry(
            invoice_id=invoice_id,
            reference_month=reference_month,
            due_date=due_date.isoformat(),
            amount_due=amount_due,
            status=status,
            paid_amount=Decimal(payment_totals.get(invoice_id, Decimal('0.00'))),
        )
        for invoice_id, reference_month, due_date, amount_due, status in invoices
    ]

    return StudentFinancialSummary(
        student_id=student_id_value,
        student_name=student_name,
        contract_code=contract_code,
        guardian_name=guardian_name,
        monthly_amount=monthly_amount,
        invoices=invoice_entries,
        open_invoice_count=sum(1 for invoice in invoice_entries if invoice.status == 'open'),
        overdue_invoice_count=sum(1 for invoice in invoice_entries if invoice.status == 'overdue'),
    )


def get_actor_administrative_status(session: Session, actor: Any) -> AdministrativeStatusSummary:
    user = session.get(User, actor.user_id)
    profile_email = user.email if user is not None else None
    profile_phone = user.phone_number if user is not None else None

    document_status_map: dict[str, tuple[str, str | None]] = {
        'USR-GUARD-001': (
            'pending',
            'Ainda falta reenviar um comprovante de residencia atualizado para concluir a conferência documental.',
        ),
        'USR-STUD-001': (
            'review',
            'A secretaria marcou o cadastro academico para revisão leve antes do fechamento do trimestre.',
        ),
    }
    document_status, document_notes = document_status_map.get(
        str(actor.external_code),
        ('complete', 'Nao ha pendencias documentais relevantes registradas nesta base de testes.'),
    )

    checklist = [
        AdministrativeChecklistItem(
            item_key='profile_email',
            label='Email cadastral',
            status='complete' if profile_email else 'pending',
            notes=profile_email or 'Ainda nao existe email cadastrado.',
        ),
        AdministrativeChecklistItem(
            item_key='profile_phone',
            label='Telefone cadastral',
            status='complete' if profile_phone else 'pending',
            notes=profile_phone or 'Ainda nao existe telefone cadastrado.',
        ),
        AdministrativeChecklistItem(
            item_key='document_package',
            label='Documentacao administrativa',
            status=document_status,
            notes=document_notes,
        ),
    ]

    overall_status = 'complete'
    if any(item.status == 'pending' for item in checklist):
        overall_status = 'pending'
    elif any(item.status == 'review' for item in checklist):
        overall_status = 'review'

    next_step = None
    if document_status == 'pending':
        next_step = 'Envie o comprovante atualizado pela secretaria ou pelo canal de documentos para concluir a conferência.'
    elif document_status == 'review':
        next_step = 'A secretaria esta revisando o cadastro e pode pedir confirmacao pontual antes de concluir.'
    elif not profile_email:
        next_step = 'Vale atualizar o email cadastral com a secretaria para garantir recebimento de comunicados.'

    return AdministrativeStatusSummary(
        actor_name=str(actor.full_name),
        role_code=str(actor.role_code),
        profile_email=profile_email,
        profile_phone=profile_phone,
        overall_status=overall_status,
        next_step=next_step,
        checklist=checklist,
    )


def get_student_administrative_status(
    session: Session,
    student_id: uuid.UUID,
) -> StudentAdministrativeStatusSummary | None:
    student_user = aliased(User)
    guardian_user = aliased(User)
    base = session.execute(
        select(
            Student.id,
            student_user.full_name,
            Student.enrollment_code,
            guardian_user.full_name,
        )
        .join(student_user, student_user.id == Student.user_id)
        .outerjoin(Contract, Contract.student_id == Student.id)
        .outerjoin(Guardian, Guardian.id == Contract.guardian_id)
        .outerjoin(guardian_user, guardian_user.id == Guardian.user_id)
        .where(Student.id == student_id)
    ).first()
    if base is None:
        return None

    student_id_value, student_name, enrollment_code, guardian_name = base

    document_status_map: dict[str, tuple[str, str | None, str | None]] = {
        'MAT-2026-001': (
            'complete',
            'A documentacao escolar de Lucas Oliveira esta conferida e sem pendencias relevantes nesta base de testes.',
            None,
        ),
        'MAT-2026-002': (
            'pending',
            'Ainda falta anexar um comprovante de residencia atualizado para Ana Oliveira concluir a conferencia documental.',
            'Envie o comprovante atualizado pelo portal autenticado ou pela secretaria escolar para concluir a analise.',
        ),
    }
    document_status, document_notes, next_step = document_status_map.get(
        str(enrollment_code),
        (
            'review',
            'A secretaria marcou a documentacao deste aluno para uma revisao leve antes do fechamento da etapa.',
            'Aguarde a conferencia final da secretaria ou envie o comprovante solicitado, se houver retorno do setor.',
        ),
    )

    checklist = [
        AdministrativeChecklistItem(
            item_key='student_identity',
            label='Identificacao escolar do aluno',
            status='complete' if enrollment_code else 'pending',
            notes=f'Codigo de matricula: {enrollment_code}' if enrollment_code else 'Codigo de matricula indisponivel.',
        ),
        AdministrativeChecklistItem(
            item_key='guardian_link',
            label='Responsavel vinculado',
            status='complete' if guardian_name else 'review',
            notes=guardian_name or 'Nao foi possivel confirmar o responsavel vinculado nesta base de testes.',
        ),
        AdministrativeChecklistItem(
            item_key='student_document_package',
            label='Documentacao escolar do aluno',
            status=document_status,
            notes=document_notes,
        ),
    ]

    overall_status = 'complete'
    if any(item.status == 'pending' for item in checklist):
        overall_status = 'pending'
    elif any(item.status == 'review' for item in checklist):
        overall_status = 'review'

    return StudentAdministrativeStatusSummary(
        student_id=student_id_value,
        student_name=student_name,
        enrollment_code=enrollment_code,
        guardian_name=guardian_name,
        overall_status=overall_status,
        next_step=next_step,
        checklist=checklist,
    )


def _teacher_segment_from_class_name_and_level(class_name: str, grade_level: int) -> str:
    normalized_class = str(class_name or '').strip().lower()
    if any(marker in normalized_class for marker in ('1o ano', '2o ano', '3o ano')):
        return 'Ensino Medio'
    if any(marker in normalized_class for marker in ('6o ano', '7o ano', '8o ano', '9o ano')):
        return 'Ensino Fundamental II'
    if grade_level >= 10:
        return 'Ensino Medio'
    return 'Ensino Fundamental II'


def get_teacher_schedule(session: Session, teacher_user_id: uuid.UUID) -> TeacherScheduleSummary | None:
    teacher_base = session.execute(
        select(Teacher.id, Teacher.employee_code, Teacher.department, User.full_name)
        .join(User, User.id == Teacher.user_id)
        .where(Teacher.user_id == teacher_user_id)
    ).first()
    if teacher_base is None:
        return None

    teacher_id, employee_code, department, teacher_name = teacher_base
    assignments = session.execute(
        select(
            Class.id,
            Class.display_name,
            Class.grade_level,
            Class.shift,
            Subject.code,
            Subject.name,
            TeacherAssignment.academic_year,
        )
        .join(TeacherAssignment, TeacherAssignment.class_id == Class.id)
        .join(Subject, Subject.id == TeacherAssignment.subject_id)
        .where(TeacherAssignment.teacher_id == teacher_id)
        .order_by(Class.display_name, Subject.code)
    ).all()

    return TeacherScheduleSummary(
        teacher_id=teacher_id,
        teacher_name=teacher_name,
        employee_code=employee_code,
        department=department,
        assignments=[
            TeacherScheduleEntry(
                class_id=class_id,
                class_name=class_name,
                grade_level=grade_level,
                shift=shift,
                segment=_teacher_segment_from_class_name_and_level(
                    str(class_name or ''),
                    int(grade_level),
                ),
                subject_code=subject_code,
                subject_name=subject_name,
                academic_year=academic_year,
            )
            for class_id, class_name, grade_level, shift, subject_code, subject_name, academic_year in assignments
        ],
    )


def get_public_school_profile(session: Session) -> PublicSchoolProfile | None:
    school_unit = session.execute(
        select(
            SchoolUnit.code,
            SchoolUnit.name,
            SchoolUnit.city,
            SchoolUnit.state,
            SchoolUnit.timezone,
        )
        .order_by(SchoolUnit.code.asc())
        .limit(1)
    ).first()
    if school_unit is None:
        return None

    code, name, city, state, timezone_name = school_unit
    return build_public_school_profile(
        code=code,
        name=name,
        city=city,
        state=state,
        timezone_name=timezone_name,
    )


def get_public_assistant_capabilities(session: Session) -> PublicAssistantCapabilities | None:
    profile = get_public_school_profile(session)
    if profile is None:
        return None
    return PublicAssistantCapabilities(
        school_name=profile.school_name,
        segments=list(profile.segments),
        public_topics=[
            'matricula, bolsas, descontos e visitas',
            'turnos, horarios, calendario e rotina escolar',
            'biblioteca, uniforme, transporte e estrutura da escola',
            'canais oficiais, secretaria e orientacao por setor',
        ],
        protected_topics=[
            'notas, faltas e resumo academico',
            'boletos, contratos e vida financeira',
        ],
        workflow_topics=[
            'agendar visita',
            'abrir solicitacao para secretaria, coordenacao, orientacao, financeiro ou direcao',
        ],
    )


def get_public_org_directory(session: Session) -> PublicOrgDirectory | None:
    profile = get_public_school_profile(session)
    if profile is None:
        return None
    return PublicOrgDirectory(
        school_name=profile.school_name,
        leadership_team=list(profile.leadership_team),
        contact_channels=list(profile.contact_channels),
    )


def get_public_service_directory(session: Session) -> PublicServiceDirectory | None:
    profile = get_public_school_profile(session)
    if profile is None:
        return None
    return PublicServiceDirectory(
        school_name=profile.school_name,
        services=list(profile.service_catalog),
    )


def get_public_timeline(session: Session) -> PublicTimeline | None:
    profile = get_public_school_profile(session)
    if profile is None:
        return None
    return PublicTimeline(
        school_name=profile.school_name,
        entries=[
            PublicTimelineEntry(
                topic_key='admissions_opening_2026',
                title='Abertura do ciclo publico de matricula 2026',
                summary=(
                    'O ciclo publico de matricula para 2026 foi aberto em 6 de outubro de 2025, '
                    'com pre-cadastro, visita orientada opcional e triagem inicial de documentos.'
                ),
                event_date=date(2025, 10, 6),
                audience='familias interessadas',
                notes='O atendimento comercial segue enquanto houver vagas por segmento.',
            ),
            PublicTimelineEntry(
                topic_key='school_year_start_2026',
                title='Inicio das aulas do ano letivo 2026',
                summary='As aulas do Ensino Fundamental II e do Ensino Medio comecam em 2 de fevereiro de 2026.',
                event_date=date(2026, 2, 2),
                audience='alunos e familias',
                notes='A semana de acolhimento do 6o ano e da primeira serie ocorre entre 2 e 6 de fevereiro.',
            ),
            PublicTimelineEntry(
                topic_key='family_meeting_cycle_2026',
                title='Primeira reuniao geral com responsaveis de 2026',
                summary='A primeira reuniao geral com responsaveis de 2026 acontece em 28 de marco de 2026.',
                event_date=date(2026, 3, 28),
                audience='responsaveis e familias',
                notes='A escola tambem pode convocar reunioes extraordinarias quando houver acompanhamento pedagogico individual.',
            ),
            PublicTimelineEntry(
                topic_key='fundamental_graduation_2026',
                title='Formatura interna do 9o ano',
                summary=(
                    'A cerimonia interna de conclusao do Ensino Fundamental II esta prevista para 12 de dezembro de 2026, '
                    'no fim da tarde, apos o encerramento do ano letivo.'
                ),
                event_date=date(2026, 12, 12),
                audience='familias do 9o ano',
                notes='A agenda final e reconfirmada pela escola perto da data.',
            ),
        ],
    )


def list_public_calendar_events(
    session: Session,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 6,
) -> list[CalendarEventEntry]:
    start_date = date_from or date.today()
    end_date = date_to or (start_date + timedelta(days=120))
    starts_at_from = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
    starts_at_to = datetime.combine(end_date, time.max, tzinfo=timezone.utc)

    rows = session.execute(
        select(
            CalendarEvent.id,
            CalendarEvent.class_id,
            CalendarEvent.title,
            CalendarEvent.description,
            CalendarEvent.category,
            CalendarEvent.audience,
            CalendarEvent.visibility,
            CalendarEvent.starts_at,
            CalendarEvent.ends_at,
        )
        .where(CalendarEvent.visibility == 'public')
        .where(CalendarEvent.starts_at >= starts_at_from)
        .where(CalendarEvent.starts_at <= starts_at_to)
        .order_by(CalendarEvent.starts_at.asc(), CalendarEvent.title.asc())
        .limit(limit)
    ).all()

    return [
        CalendarEventEntry(
            event_id=event_id,
            class_id=class_id,
            title=title,
            description=description,
            category=category,
            audience=audience,
            visibility=visibility,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        for event_id, class_id, title, description, category, audience, visibility, starts_at, ends_at in rows
    ]
