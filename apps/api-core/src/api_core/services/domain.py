from __future__ import annotations

import uuid
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import Integer, func, select
from sqlalchemy.orm import Session, aliased

from api_core.contracts import (
    AttendanceEntry,
    CalendarEventEntry,
    GradeEntry,
    InvoiceEntry,
    PublicSchoolProfile,
    StudentAcademicSummary,
    StudentFinancialSummary,
    TeacherScheduleEntry,
    TeacherScheduleSummary,
)
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


def get_student_academic_summary(session: Session, student_id: uuid.UUID) -> StudentAcademicSummary | None:
    base = session.execute(
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
        select(Class.id, Class.display_name, Subject.code, Subject.name, TeacherAssignment.academic_year)
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
                subject_code=subject_code,
                subject_name=subject_name,
                academic_year=academic_year,
            )
            for class_id, class_name, subject_code, subject_name, academic_year in assignments
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
    return PublicSchoolProfile(
        school_unit_code=code,
        school_name=name,
        city=city,
        state=state,
        timezone=timezone_name,
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
