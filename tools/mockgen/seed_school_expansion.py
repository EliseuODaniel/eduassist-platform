from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import select

from api_core.db.models import (
    AttendanceRecord,
    CalendarEvent,
    Class,
    Contract,
    Enrollment,
    Grade,
    GradeItem,
    Guardian,
    GuardianStudentLink,
    Invoice,
    Payment,
    SchoolUnit,
    Student,
    Subject,
    Teacher,
    TeacherAssignment,
    TelegramAccount,
    User,
    UserTelegramLink,
)
from api_core.db.session import session_scope


TZ = ZoneInfo('America/Sao_Paulo')


def ensure_user(session, *, external_code: str, role_code: str, full_name: str, email: str, phone: str, is_staff: bool = False) -> User:
    user = session.scalar(select(User).where(User.external_code == external_code))
    if user is None:
        user = User(
            role_code=role_code,
            external_code=external_code,
            full_name=full_name,
            email=email,
            phone_number=phone,
            status='active',
            is_staff=is_staff,
        )
        session.add(user)
        session.flush()
        return user

    user.role_code = role_code
    user.full_name = full_name
    user.email = email
    user.phone_number = phone
    user.is_staff = is_staff
    user.status = 'active'
    session.flush()
    return user


def ensure_guardian(session, *, user: User, relationship_label: str, cpf_masked: str, primary_contact: bool = True) -> Guardian:
    guardian = session.scalar(select(Guardian).where(Guardian.user_id == user.id))
    if guardian is None:
        guardian = Guardian(
            user_id=user.id,
            relationship_label=relationship_label,
            cpf_masked=cpf_masked,
            primary_contact=primary_contact,
        )
        session.add(guardian)
        session.flush()
        return guardian

    guardian.relationship_label = relationship_label
    guardian.cpf_masked = cpf_masked
    guardian.primary_contact = primary_contact
    session.flush()
    return guardian


def ensure_teacher(session, *, user: User, school_unit_id, employee_code: str, department: str) -> Teacher:
    teacher = session.scalar(select(Teacher).where(Teacher.employee_code == employee_code))
    if teacher is None:
        teacher = Teacher(
            user_id=user.id,
            school_unit_id=school_unit_id,
            employee_code=employee_code,
            department=department,
        )
        session.add(teacher)
        session.flush()
        return teacher

    teacher.user_id = user.id
    teacher.school_unit_id = school_unit_id
    teacher.department = department
    session.flush()
    return teacher


def ensure_student(session, *, user: User, school_unit_id, enrollment_code: str, birth_date: date, current_grade_level: int) -> Student:
    student = session.scalar(select(Student).where(Student.enrollment_code == enrollment_code))
    if student is None:
        student = Student(
            user_id=user.id,
            school_unit_id=school_unit_id,
            enrollment_code=enrollment_code,
            birth_date=birth_date,
            current_grade_level=current_grade_level,
            status='active',
        )
        session.add(student)
        session.flush()
        return student

    student.user_id = user.id
    student.school_unit_id = school_unit_id
    student.birth_date = birth_date
    student.current_grade_level = current_grade_level
    student.status = 'active'
    session.flush()
    return student


def ensure_guardian_link(
    session,
    *,
    guardian_id,
    student_id,
    relationship_label: str,
    can_view_finance: bool = True,
    can_view_academic: bool = True,
) -> None:
    link = session.scalar(
        select(GuardianStudentLink).where(
            GuardianStudentLink.guardian_id == guardian_id,
            GuardianStudentLink.student_id == student_id,
        )
    )
    if link is None:
        link = GuardianStudentLink(
            guardian_id=guardian_id,
            student_id=student_id,
            relationship_label=relationship_label,
            can_view_finance=can_view_finance,
            can_view_academic=can_view_academic,
        )
        session.add(link)
    else:
        link.relationship_label = relationship_label
        link.can_view_finance = can_view_finance
        link.can_view_academic = can_view_academic
    session.flush()


def ensure_telegram_account(
    session,
    *,
    telegram_user_id: int,
    telegram_chat_id: int,
    username: str,
    first_name: str,
    last_name: str,
) -> TelegramAccount:
    account = session.scalar(select(TelegramAccount).where(TelegramAccount.telegram_chat_id == telegram_chat_id))
    if account is None:
        account = TelegramAccount(
            telegram_user_id=telegram_user_id,
            telegram_chat_id=telegram_chat_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )
        session.add(account)
        session.flush()
        return account

    account.telegram_user_id = telegram_user_id
    account.username = username
    account.first_name = first_name
    account.last_name = last_name
    account.is_active = True
    session.flush()
    return account


def ensure_telegram_link(session, *, user_id, telegram_account_id) -> None:
    link = session.scalar(select(UserTelegramLink).where(UserTelegramLink.user_id == user_id))
    if link is None:
        link = UserTelegramLink(
            user_id=user_id,
            telegram_account_id=telegram_account_id,
            verification_status='verified',
        )
        session.add(link)
    else:
        link.telegram_account_id = telegram_account_id
        link.verification_status = 'verified'
    session.flush()


def ensure_class(
    session,
    *,
    school_unit_id,
    code: str,
    display_name: str,
    academic_year: int,
    grade_level: int,
    shift: str,
    homeroom_teacher_id,
) -> Class:
    class_ = session.scalar(
        select(Class).where(
            Class.school_unit_id == school_unit_id,
            Class.code == code,
        )
    )
    if class_ is None:
        class_ = Class(
            school_unit_id=school_unit_id,
            code=code,
            display_name=display_name,
            academic_year=academic_year,
            grade_level=grade_level,
            shift=shift,
            homeroom_teacher_id=homeroom_teacher_id,
        )
        session.add(class_)
        session.flush()
        return class_

    class_.display_name = display_name
    class_.academic_year = academic_year
    class_.grade_level = grade_level
    class_.shift = shift
    class_.homeroom_teacher_id = homeroom_teacher_id
    session.flush()
    return class_


def ensure_subject(session, *, code: str, name: str, area: str, weekly_hours: Decimal) -> Subject:
    subject = session.scalar(select(Subject).where(Subject.code == code))
    if subject is None:
        subject = Subject(code=code, name=name, area=area, weekly_hours=weekly_hours)
        session.add(subject)
        session.flush()
        return subject

    subject.name = name
    subject.area = area
    subject.weekly_hours = weekly_hours
    session.flush()
    return subject


def ensure_enrollment(session, *, student_id, class_id, academic_year: int, status: str = 'active') -> Enrollment:
    enrollment = session.scalar(
        select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.class_id == class_id,
            Enrollment.academic_year == academic_year,
        )
    )
    if enrollment is None:
        enrollment = Enrollment(
            student_id=student_id,
            class_id=class_id,
            academic_year=academic_year,
            enrollment_status=status,
        )
        session.add(enrollment)
        session.flush()
        return enrollment

    enrollment.enrollment_status = status
    session.flush()
    return enrollment


def ensure_assignment(session, *, teacher_id, class_id, subject_id, academic_year: int) -> TeacherAssignment:
    assignment = session.scalar(
        select(TeacherAssignment).where(
            TeacherAssignment.teacher_id == teacher_id,
            TeacherAssignment.class_id == class_id,
            TeacherAssignment.subject_id == subject_id,
            TeacherAssignment.academic_year == academic_year,
        )
    )
    if assignment is None:
        assignment = TeacherAssignment(
            teacher_id=teacher_id,
            class_id=class_id,
            subject_id=subject_id,
            academic_year=academic_year,
        )
        session.add(assignment)
        session.flush()
        return assignment
    return assignment


def ensure_grade_item(session, *, teacher_assignment_id, term_code: str, title: str, max_score: Decimal, due_date: date) -> GradeItem:
    item = session.scalar(
        select(GradeItem).where(
            GradeItem.teacher_assignment_id == teacher_assignment_id,
            GradeItem.term_code == term_code,
            GradeItem.title == title,
        )
    )
    if item is None:
        item = GradeItem(
            teacher_assignment_id=teacher_assignment_id,
            term_code=term_code,
            title=title,
            max_score=max_score,
            due_date=due_date,
        )
        session.add(item)
        session.flush()
        return item

    item.max_score = max_score
    item.due_date = due_date
    session.flush()
    return item


def ensure_grade(session, *, enrollment_id, grade_item_id, score: Decimal, feedback: str) -> None:
    grade = session.scalar(
        select(Grade).where(
            Grade.enrollment_id == enrollment_id,
            Grade.grade_item_id == grade_item_id,
        )
    )
    if grade is None:
        grade = Grade(
            enrollment_id=enrollment_id,
            grade_item_id=grade_item_id,
            score=score,
            feedback=feedback,
        )
        session.add(grade)
    else:
        grade.score = score
        grade.feedback = feedback
    session.flush()


def ensure_attendance(session, *, enrollment_id, subject_id, record_date: date, status: str, minutes_absent: int = 0) -> None:
    record = session.scalar(
        select(AttendanceRecord).where(
            AttendanceRecord.enrollment_id == enrollment_id,
            AttendanceRecord.subject_id == subject_id,
            AttendanceRecord.record_date == record_date,
        )
    )
    if record is None:
        record = AttendanceRecord(
            enrollment_id=enrollment_id,
            subject_id=subject_id,
            record_date=record_date,
            status=status,
            minutes_absent=minutes_absent,
        )
        session.add(record)
    else:
        record.status = status
        record.minutes_absent = minutes_absent
    session.flush()


def ensure_contract(
    session,
    *,
    school_unit_id,
    student_id,
    guardian_id,
    academic_year: int,
    contract_code: str,
    monthly_amount: Decimal,
    status: str = 'active',
) -> Contract:
    contract = session.scalar(select(Contract).where(Contract.contract_code == contract_code))
    if contract is None:
        contract = Contract(
            school_unit_id=school_unit_id,
            student_id=student_id,
            guardian_id=guardian_id,
            academic_year=academic_year,
            contract_code=contract_code,
            monthly_amount=monthly_amount,
            status=status,
        )
        session.add(contract)
        session.flush()
        return contract

    contract.student_id = student_id
    contract.guardian_id = guardian_id
    contract.school_unit_id = school_unit_id
    contract.academic_year = academic_year
    contract.monthly_amount = monthly_amount
    contract.status = status
    session.flush()
    return contract


def ensure_invoice(session, *, contract_id, reference_month: str, due_date: date, amount_due: Decimal, status: str) -> Invoice:
    invoice = session.scalar(
        select(Invoice).where(
            Invoice.contract_id == contract_id,
            Invoice.reference_month == reference_month,
        )
    )
    if invoice is None:
        invoice = Invoice(
            contract_id=contract_id,
            reference_month=reference_month,
            due_date=due_date,
            amount_due=amount_due,
            status=status,
        )
        session.add(invoice)
        session.flush()
        return invoice

    invoice.due_date = due_date
    invoice.amount_due = amount_due
    invoice.status = status
    session.flush()
    return invoice


def ensure_payment(session, *, invoice_id, paid_at: date, amount_paid: Decimal, payment_method: str) -> None:
    payment = session.scalar(
        select(Payment).where(
            Payment.invoice_id == invoice_id,
            Payment.paid_at == paid_at,
            Payment.amount_paid == amount_paid,
        )
    )
    if payment is None:
        payment = Payment(
            invoice_id=invoice_id,
            paid_at=paid_at,
            amount_paid=amount_paid,
            payment_method=payment_method,
        )
        session.add(payment)
    else:
        payment.payment_method = payment_method
    session.flush()


def ensure_calendar_event(
    session,
    *,
    school_unit_id,
    class_id,
    audience: str,
    category: str,
    title: str,
    description: str,
    starts_at: datetime,
    ends_at: datetime,
    visibility: str,
) -> None:
    event = session.scalar(
        select(CalendarEvent).where(
            CalendarEvent.title == title,
            CalendarEvent.starts_at == starts_at,
        )
    )
    if event is None:
        event = CalendarEvent(
            school_unit_id=school_unit_id,
            class_id=class_id,
            audience=audience,
            category=category,
            title=title,
            description=description,
            starts_at=starts_at,
            ends_at=ends_at,
            visibility=visibility,
        )
        session.add(event)
    else:
        event.school_unit_id = school_unit_id
        event.class_id = class_id
        event.audience = audience
        event.category = category
        event.description = description
        event.ends_at = ends_at
        event.visibility = visibility
    session.flush()


def main() -> None:
    with session_scope() as session:
        unit = session.scalar(select(SchoolUnit).where(SchoolUnit.code == 'HZ-CAMPUS'))
        if unit is None:
            raise SystemExit('foundation seed missing; run make db-seed-foundation first')

        users = {
            'guardian_fernanda': ensure_user(
                session,
                external_code='USR-GUARD-003',
                role_code='guardian',
                full_name='Fernanda Souza',
                email='fernanda.souza@mock.eduassist.local',
                phone='+55 11 98888-1003',
            ),
            'guardian_roberto': ensure_user(
                session,
                external_code='USR-GUARD-004',
                role_code='guardian',
                full_name='Roberto Araujo',
                email='roberto.araujo@mock.eduassist.local',
                phone='+55 11 98888-1004',
            ),
            'guardian_juliana': ensure_user(
                session,
                external_code='USR-GUARD-005',
                role_code='guardian',
                full_name='Juliana Lima',
                email='juliana.lima@mock.eduassist.local',
                phone='+55 11 98888-1005',
            ),
            'guardian_carla': ensure_user(
                session,
                external_code='USR-GUARD-006',
                role_code='guardian',
                full_name='Carla Mendes',
                email='carla.mendes@mock.eduassist.local',
                phone='+55 11 98888-1006',
            ),
            'student_gabriel': ensure_user(
                session,
                external_code='USR-STUD-004',
                role_code='student',
                full_name='Gabriel Souza',
                email='gabriel.souza@mock.eduassist.local',
                phone='+55 11 97777-2004',
            ),
            'student_sofia': ensure_user(
                session,
                external_code='USR-STUD-005',
                role_code='student',
                full_name='Sofia Souza',
                email='sofia.souza@mock.eduassist.local',
                phone='+55 11 97777-2005',
            ),
            'student_marina': ensure_user(
                session,
                external_code='USR-STUD-006',
                role_code='student',
                full_name='Marina Araujo',
                email='marina.araujo@mock.eduassist.local',
                phone='+55 11 97777-2006',
            ),
            'student_pedro': ensure_user(
                session,
                external_code='USR-STUD-007',
                role_code='student',
                full_name='Pedro Lima',
                email='pedro.lima@mock.eduassist.local',
                phone='+55 11 97777-2007',
            ),
            'student_isabela': ensure_user(
                session,
                external_code='USR-STUD-008',
                role_code='student',
                full_name='Isabela Lima',
                email='isabela.lima@mock.eduassist.local',
                phone='+55 11 97777-2008',
            ),
            'student_thiago': ensure_user(
                session,
                external_code='USR-STUD-009',
                role_code='student',
                full_name='Thiago Mendes',
                email='thiago.mendes@mock.eduassist.local',
                phone='+55 11 97777-2009',
            ),
            'teacher_daniela': ensure_user(
                session,
                external_code='USR-TEACH-003',
                role_code='teacher',
                full_name='Daniela Campos',
                email='daniela.campos@mock.eduassist.local',
                phone='+55 11 96666-3003',
                is_staff=True,
            ),
            'teacher_rafael': ensure_user(
                session,
                external_code='USR-TEACH-004',
                role_code='teacher',
                full_name='Rafael Gomes',
                email='rafael.gomes@mock.eduassist.local',
                phone='+55 11 96666-3004',
                is_staff=True,
            ),
            'teacher_patricia': ensure_user(
                session,
                external_code='USR-TEACH-005',
                role_code='teacher',
                full_name='Patricia Neves',
                email='patricia.neves@mock.eduassist.local',
                phone='+55 11 96666-3005',
                is_staff=True,
            ),
            'teacher_tiago': ensure_user(
                session,
                external_code='USR-TEACH-006',
                role_code='teacher',
                full_name='Tiago Moura',
                email='tiago.moura@mock.eduassist.local',
                phone='+55 11 96666-3006',
                is_staff=True,
            ),
            'teacher_luana': ensure_user(
                session,
                external_code='USR-TEACH-007',
                role_code='teacher',
                full_name='Luana Ferraz',
                email='luana.ferraz@mock.eduassist.local',
                phone='+55 11 96666-3007',
                is_staff=True,
            ),
            'coordinator_murilo': ensure_user(
                session,
                external_code='USR-COORD-001',
                role_code='coordinator',
                full_name='Murilo Bastos',
                email='murilo.bastos@mock.eduassist.local',
                phone='+55 11 95555-4003',
                is_staff=True,
            ),
        }

        guardians = {
            'fernanda': ensure_guardian(session, user=users['guardian_fernanda'], relationship_label='mae', cpf_masked='***.321.654-**'),
            'roberto': ensure_guardian(session, user=users['guardian_roberto'], relationship_label='pai', cpf_masked='***.852.741-**'),
            'juliana': ensure_guardian(session, user=users['guardian_juliana'], relationship_label='mae', cpf_masked='***.963.852-**'),
            'carla': ensure_guardian(session, user=users['guardian_carla'], relationship_label='mae', cpf_masked='***.147.258-**'),
        }

        teachers = {
            'helena': session.scalar(select(Teacher).where(Teacher.employee_code == 'DOC-001')),
            'marcos': session.scalar(select(Teacher).where(Teacher.employee_code == 'DOC-002')),
            'daniela': ensure_teacher(session, user=users['teacher_daniela'], school_unit_id=unit.id, employee_code='DOC-003', department='Ciencias da Natureza'),
            'rafael': ensure_teacher(session, user=users['teacher_rafael'], school_unit_id=unit.id, employee_code='DOC-004', department='Humanidades'),
            'patricia': ensure_teacher(session, user=users['teacher_patricia'], school_unit_id=unit.id, employee_code='DOC-005', department='Linguas Estrangeiras'),
            'tiago': ensure_teacher(session, user=users['teacher_tiago'], school_unit_id=unit.id, employee_code='DOC-006', department='Educacao Fisica'),
            'luana': ensure_teacher(session, user=users['teacher_luana'], school_unit_id=unit.id, employee_code='DOC-007', department='Artes e Cultura'),
        }
        if teachers['helena'] is None or teachers['marcos'] is None:
            raise SystemExit('foundation teacher records missing; run make db-seed-foundation first')

        students = {
            'gabriel': ensure_student(
                session,
                user=users['student_gabriel'],
                school_unit_id=unit.id,
                enrollment_code='MAT-2026-004',
                birth_date=date(2014, 3, 2),
                current_grade_level=6,
            ),
            'sofia': ensure_student(
                session,
                user=users['student_sofia'],
                school_unit_id=unit.id,
                enrollment_code='MAT-2026-005',
                birth_date=date(2012, 8, 11),
                current_grade_level=8,
            ),
            'marina': ensure_student(
                session,
                user=users['student_marina'],
                school_unit_id=unit.id,
                enrollment_code='MAT-2026-006',
                birth_date=date(2011, 12, 19),
                current_grade_level=9,
            ),
            'pedro': ensure_student(
                session,
                user=users['student_pedro'],
                school_unit_id=unit.id,
                enrollment_code='MAT-2026-007',
                birth_date=date(2008, 5, 17),
                current_grade_level=3,
            ),
            'isabela': ensure_student(
                session,
                user=users['student_isabela'],
                school_unit_id=unit.id,
                enrollment_code='MAT-2026-008',
                birth_date=date(2009, 1, 27),
                current_grade_level=2,
            ),
            'thiago': ensure_student(
                session,
                user=users['student_thiago'],
                school_unit_id=unit.id,
                enrollment_code='MAT-2026-009',
                birth_date=date(2013, 9, 9),
                current_grade_level=7,
            ),
        }

        ensure_guardian_link(session, guardian_id=guardians['fernanda'].id, student_id=students['gabriel'].id, relationship_label='mae')
        ensure_guardian_link(session, guardian_id=guardians['fernanda'].id, student_id=students['sofia'].id, relationship_label='mae')
        ensure_guardian_link(session, guardian_id=guardians['roberto'].id, student_id=students['marina'].id, relationship_label='pai')
        ensure_guardian_link(session, guardian_id=guardians['juliana'].id, student_id=students['pedro'].id, relationship_label='mae')
        ensure_guardian_link(session, guardian_id=guardians['juliana'].id, student_id=students['isabela'].id, relationship_label='mae')
        ensure_guardian_link(session, guardian_id=guardians['carla'].id, student_id=students['thiago'].id, relationship_label='mae')

        telegram_accounts = {
            'fernanda': ensure_telegram_account(
                session,
                telegram_user_id=555003,
                telegram_chat_id=555003,
                username='fernanda.souza',
                first_name='Fernanda',
                last_name='Souza',
            ),
            'roberto': ensure_telegram_account(
                session,
                telegram_user_id=555004,
                telegram_chat_id=555004,
                username='roberto.araujo',
                first_name='Roberto',
                last_name='Araujo',
            ),
            'juliana': ensure_telegram_account(
                session,
                telegram_user_id=555005,
                telegram_chat_id=555005,
                username='juliana.lima',
                first_name='Juliana',
                last_name='Lima',
            ),
            'carla': ensure_telegram_account(
                session,
                telegram_user_id=555006,
                telegram_chat_id=555006,
                username='carla.mendes',
                first_name='Carla',
                last_name='Mendes',
            ),
        }
        ensure_telegram_link(
            session,
            user_id=users['guardian_fernanda'].id,
            telegram_account_id=telegram_accounts['fernanda'].id,
        )
        ensure_telegram_link(
            session,
            user_id=users['guardian_roberto'].id,
            telegram_account_id=telegram_accounts['roberto'].id,
        )
        ensure_telegram_link(
            session,
            user_id=users['guardian_juliana'].id,
            telegram_account_id=telegram_accounts['juliana'].id,
        )
        ensure_telegram_link(
            session,
            user_id=users['guardian_carla'].id,
            telegram_account_id=telegram_accounts['carla'].id,
        )

        subjects = {
            'mat': ensure_subject(session, code='MAT', name='Matematica', area='Exatas', weekly_hours=Decimal('5.0')),
            'por': ensure_subject(session, code='POR', name='Portugues', area='Linguagens', weekly_hours=Decimal('4.0')),
            'ing': ensure_subject(session, code='ING', name='Ingles', area='Linguagens', weekly_hours=Decimal('2.0')),
            'his': ensure_subject(session, code='HIS', name='Historia', area='Humanidades', weekly_hours=Decimal('2.0')),
            'geo': ensure_subject(session, code='GEO', name='Geografia', area='Humanidades', weekly_hours=Decimal('2.0')),
            'cie': ensure_subject(session, code='CIE', name='Ciencias', area='Natureza', weekly_hours=Decimal('3.0')),
            'bio': ensure_subject(session, code='BIO', name='Biologia', area='Natureza', weekly_hours=Decimal('3.0')),
            'qui': ensure_subject(session, code='QUI', name='Quimica', area='Natureza', weekly_hours=Decimal('3.0')),
            'fis': ensure_subject(session, code='FIS', name='Fisica', area='Natureza', weekly_hours=Decimal('3.0')),
            'edf': ensure_subject(session, code='EDF', name='Educacao Fisica', area='Corpo e Movimento', weekly_hours=Decimal('2.0')),
            'art': ensure_subject(session, code='ART', name='Artes', area='Linguagens', weekly_hours=Decimal('1.0')),
        }

        classes = {
            '6f_a': ensure_class(
                session,
                school_unit_id=unit.id,
                code='6F-A',
                display_name='6o Ano A',
                academic_year=2026,
                grade_level=6,
                shift='manha',
                homeroom_teacher_id=teachers['patricia'].id,
            ),
            '7f_a': ensure_class(
                session,
                school_unit_id=unit.id,
                code='7F-A',
                display_name='7o Ano A',
                academic_year=2026,
                grade_level=7,
                shift='manha',
                homeroom_teacher_id=teachers['rafael'].id,
            ),
            '8f_a': ensure_class(
                session,
                school_unit_id=unit.id,
                code='8F-A',
                display_name='8o Ano A',
                academic_year=2026,
                grade_level=8,
                shift='manha',
                homeroom_teacher_id=teachers['daniela'].id,
            ),
            '9f_a': ensure_class(
                session,
                school_unit_id=unit.id,
                code='9F-A',
                display_name='9o Ano A',
                academic_year=2026,
                grade_level=9,
                shift='manha',
                homeroom_teacher_id=teachers['marcos'].id,
            ),
            '1em_a': ensure_class(
                session,
                school_unit_id=unit.id,
                code='1EM-A',
                display_name='1o Ano A',
                academic_year=2026,
                grade_level=1,
                shift='manha',
                homeroom_teacher_id=teachers['helena'].id,
            ),
            '2em_a': ensure_class(
                session,
                school_unit_id=unit.id,
                code='2EM-A',
                display_name='2o Ano A',
                academic_year=2026,
                grade_level=2,
                shift='manha',
                homeroom_teacher_id=teachers['marcos'].id,
            ),
            '3em_a': ensure_class(
                session,
                school_unit_id=unit.id,
                code='3EM-A',
                display_name='3o Ano A',
                academic_year=2026,
                grade_level=3,
                shift='manha',
                homeroom_teacher_id=teachers['daniela'].id,
            ),
        }

        enrollments = {
            'gabriel_6f': ensure_enrollment(session, student_id=students['gabriel'].id, class_id=classes['6f_a'].id, academic_year=2026),
            'sofia_8f': ensure_enrollment(session, student_id=students['sofia'].id, class_id=classes['8f_a'].id, academic_year=2026),
            'marina_9f': ensure_enrollment(session, student_id=students['marina'].id, class_id=classes['9f_a'].id, academic_year=2026),
            'pedro_3em': ensure_enrollment(session, student_id=students['pedro'].id, class_id=classes['3em_a'].id, academic_year=2026),
            'isabela_2em': ensure_enrollment(session, student_id=students['isabela'].id, class_id=classes['2em_a'].id, academic_year=2026),
            'thiago_7f': ensure_enrollment(session, student_id=students['thiago'].id, class_id=classes['7f_a'].id, academic_year=2026),
        }

        assignment_specs = {
            '6f_a': [('mat', 'helena'), ('por', 'marcos'), ('ing', 'patricia'), ('his', 'rafael'), ('cie', 'daniela'), ('edf', 'tiago'), ('art', 'luana')],
            '7f_a': [('mat', 'helena'), ('por', 'marcos'), ('ing', 'patricia'), ('geo', 'rafael'), ('cie', 'daniela'), ('edf', 'tiago')],
            '8f_a': [('mat', 'helena'), ('por', 'marcos'), ('ing', 'patricia'), ('his', 'rafael'), ('geo', 'rafael'), ('cie', 'daniela'), ('edf', 'tiago')],
            '9f_a': [('mat', 'helena'), ('por', 'marcos'), ('ing', 'patricia'), ('his', 'rafael'), ('geo', 'rafael'), ('cie', 'daniela')],
            '1em_a': [('mat', 'helena'), ('por', 'marcos'), ('ing', 'patricia'), ('bio', 'daniela'), ('his', 'rafael')],
            '2em_a': [('mat', 'helena'), ('por', 'marcos'), ('qui', 'daniela'), ('fis', 'daniela'), ('his', 'rafael')],
            '3em_a': [('mat', 'helena'), ('por', 'marcos'), ('bio', 'daniela'), ('qui', 'daniela'), ('fis', 'daniela')],
        }
        assignments: dict[tuple[str, str], TeacherAssignment] = {}
        for class_key, items in assignment_specs.items():
            for subject_key, teacher_key in items:
                assignments[(class_key, subject_key)] = ensure_assignment(
                    session,
                    teacher_id=teachers[teacher_key].id,
                    class_id=classes[class_key].id,
                    subject_id=subjects[subject_key].id,
                    academic_year=2026,
                )

        grade_item_templates = [
            ('2026-B1', 'Avaliacao B1', date(2026, 4, 10)),
            ('2026-B1', 'Trabalho B1', date(2026, 4, 18)),
            ('2026-B2', 'Avaliacao B2', date(2026, 6, 12)),
        ]
        grade_items: dict[tuple[str, str, str], GradeItem] = {}
        for (class_key, subject_key), assignment in assignments.items():
            for term_code, title, due_date_value in grade_item_templates:
                grade_items[(class_key, subject_key, title)] = ensure_grade_item(
                    session,
                    teacher_assignment_id=assignment.id,
                    term_code=term_code,
                    title=title,
                    max_score=Decimal('10.00'),
                    due_date=due_date_value,
                )

        grade_seed = {
            'lucas_1em': ('1em_a', 'lucas_1em', {'mat': [Decimal('8.70'), Decimal('8.90'), Decimal('8.20')], 'por': [Decimal('9.10'), Decimal('8.80'), Decimal('9.00')], 'bio': [Decimal('8.40'), Decimal('8.10'), Decimal('8.60')], 'ing': [Decimal('8.90'), Decimal('9.20'), Decimal('9.00')]}),
            'ana_1em': ('1em_a', 'ana_1em', {'mat': [Decimal('7.80'), Decimal('8.10'), Decimal('7.90')], 'por': [Decimal('8.90'), Decimal('8.70'), Decimal('9.00')], 'bio': [Decimal('8.20'), Decimal('8.50'), Decimal('8.30')], 'ing': [Decimal('9.30'), Decimal('9.10'), Decimal('9.40')]}),
            'bruno_2em': ('2em_a', 'bruno_2em', {'mat': [Decimal('6.40'), Decimal('6.90'), Decimal('7.10')], 'por': [Decimal('7.20'), Decimal('7.00'), Decimal('7.50')], 'qui': [Decimal('6.80'), Decimal('7.10'), Decimal('7.00')], 'fis': [Decimal('6.50'), Decimal('6.70'), Decimal('6.90')]}),
            'gabriel_6f': ('6f_a', 'gabriel_6f', {'mat': [Decimal('8.60'), Decimal('8.30'), Decimal('8.50')], 'por': [Decimal('8.90'), Decimal('9.00'), Decimal('8.70')], 'cie': [Decimal('8.40'), Decimal('8.60'), Decimal('8.50')], 'ing': [Decimal('9.00'), Decimal('8.80'), Decimal('8.90')]}),
            'sofia_8f': ('8f_a', 'sofia_8f', {'mat': [Decimal('9.20'), Decimal('9.10'), Decimal('9.30')], 'por': [Decimal('8.70'), Decimal('8.90'), Decimal('8.80')], 'cie': [Decimal('9.00'), Decimal('8.80'), Decimal('9.10')], 'ing': [Decimal('9.40'), Decimal('9.50'), Decimal('9.30')]}),
            'marina_9f': ('9f_a', 'marina_9f', {'mat': [Decimal('7.90'), Decimal('8.00'), Decimal('8.20')], 'por': [Decimal('8.10'), Decimal('8.40'), Decimal('8.30')], 'cie': [Decimal('8.00'), Decimal('8.10'), Decimal('8.20')], 'his': [Decimal('8.60'), Decimal('8.70'), Decimal('8.80')]}),
            'pedro_3em': ('3em_a', 'pedro_3em', {'mat': [Decimal('8.10'), Decimal('8.20'), Decimal('8.30')], 'por': [Decimal('8.40'), Decimal('8.30'), Decimal('8.50')], 'bio': [Decimal('7.80'), Decimal('8.00'), Decimal('8.10')], 'fis': [Decimal('7.60'), Decimal('7.80'), Decimal('7.90')]}),
            'isabela_2em': ('2em_a', 'isabela_2em', {'mat': [Decimal('8.80'), Decimal('8.90'), Decimal('9.00')], 'por': [Decimal('9.10'), Decimal('9.00'), Decimal('9.20')], 'qui': [Decimal('8.40'), Decimal('8.50'), Decimal('8.60')], 'fis': [Decimal('8.20'), Decimal('8.30'), Decimal('8.40')]}),
            'thiago_7f': ('7f_a', 'thiago_7f', {'mat': [Decimal('7.40'), Decimal('7.60'), Decimal('7.80')], 'por': [Decimal('8.00'), Decimal('8.20'), Decimal('8.10')], 'cie': [Decimal('7.90'), Decimal('8.00'), Decimal('8.10')], 'ing': [Decimal('8.50'), Decimal('8.60'), Decimal('8.40')]}),
        }
        all_enrollments = {
            'lucas_1em': session.scalar(select(Enrollment).where(Enrollment.student_id == session.scalar(select(Student.id).where(Student.enrollment_code == 'MAT-2026-001')), Enrollment.class_id == classes['1em_a'].id, Enrollment.academic_year == 2026)),
            'ana_1em': session.scalar(select(Enrollment).where(Enrollment.student_id == session.scalar(select(Student.id).where(Student.enrollment_code == 'MAT-2026-002')), Enrollment.class_id == classes['1em_a'].id, Enrollment.academic_year == 2026)),
            'bruno_2em': session.scalar(select(Enrollment).where(Enrollment.student_id == session.scalar(select(Student.id).where(Student.enrollment_code == 'MAT-2026-003')), Enrollment.class_id == classes['2em_a'].id, Enrollment.academic_year == 2026)),
            **enrollments,
        }
        for _, (class_key, enrollment_key, subject_scores) in grade_seed.items():
            enrollment = all_enrollments[enrollment_key]
            if enrollment is None:
                continue
            for subject_key, scores in subject_scores.items():
                titles = ['Avaliacao B1', 'Trabalho B1', 'Avaliacao B2']
                feedback = f'Desempenho acompanhado em {subjects[subject_key].name.lower()}.'
                for title, score in zip(titles, scores, strict=True):
                    item = grade_items.get((class_key, subject_key, title))
                    if item is None:
                        continue
                    ensure_grade(
                        session,
                        enrollment_id=enrollment.id,
                        grade_item_id=item.id,
                        score=score,
                        feedback=feedback,
                    )

        attendance_seed = [
            ('lucas_1em', 'mat', date(2026, 3, 9), 'present', 0),
            ('lucas_1em', 'bio', date(2026, 3, 11), 'present', 0),
            ('ana_1em', 'por', date(2026, 3, 9), 'late', 15),
            ('ana_1em', 'bio', date(2026, 3, 18), 'present', 0),
            ('bruno_2em', 'mat', date(2026, 3, 10), 'absent', 50),
            ('bruno_2em', 'qui', date(2026, 3, 17), 'present', 0),
            ('gabriel_6f', 'mat', date(2026, 3, 12), 'present', 0),
            ('gabriel_6f', 'cie', date(2026, 3, 20), 'present', 0),
            ('sofia_8f', 'ing', date(2026, 3, 14), 'present', 0),
            ('sofia_8f', 'mat', date(2026, 3, 21), 'late', 10),
            ('marina_9f', 'his', date(2026, 3, 13), 'present', 0),
            ('marina_9f', 'mat', date(2026, 3, 22), 'absent', 45),
            ('pedro_3em', 'fis', date(2026, 3, 16), 'present', 0),
            ('pedro_3em', 'mat', date(2026, 3, 23), 'late', 5),
            ('isabela_2em', 'qui', date(2026, 3, 18), 'present', 0),
            ('thiago_7f', 'cie', date(2026, 3, 19), 'present', 0),
        ]
        for enrollment_key, subject_key, record_date_value, status, minutes_absent in attendance_seed:
            enrollment = all_enrollments.get(enrollment_key)
            if enrollment is None:
                continue
            ensure_attendance(
                session,
                enrollment_id=enrollment.id,
                subject_id=subjects[subject_key].id,
                record_date=record_date_value,
                status=status,
                minutes_absent=minutes_absent,
            )

        contracts = {
            'gabriel': ensure_contract(session, school_unit_id=unit.id, student_id=students['gabriel'].id, guardian_id=guardians['fernanda'].id, academic_year=2026, contract_code='CTR-2026-004', monthly_amount=Decimal('1280.00')),
            'sofia': ensure_contract(session, school_unit_id=unit.id, student_id=students['sofia'].id, guardian_id=guardians['fernanda'].id, academic_year=2026, contract_code='CTR-2026-005', monthly_amount=Decimal('1280.00')),
            'marina': ensure_contract(session, school_unit_id=unit.id, student_id=students['marina'].id, guardian_id=guardians['roberto'].id, academic_year=2026, contract_code='CTR-2026-006', monthly_amount=Decimal('1280.00')),
            'pedro': ensure_contract(session, school_unit_id=unit.id, student_id=students['pedro'].id, guardian_id=guardians['juliana'].id, academic_year=2026, contract_code='CTR-2026-007', monthly_amount=Decimal('1450.00')),
            'isabela': ensure_contract(session, school_unit_id=unit.id, student_id=students['isabela'].id, guardian_id=guardians['juliana'].id, academic_year=2026, contract_code='CTR-2026-008', monthly_amount=Decimal('1450.00')),
            'thiago': ensure_contract(session, school_unit_id=unit.id, student_id=students['thiago'].id, guardian_id=guardians['carla'].id, academic_year=2026, contract_code='CTR-2026-009', monthly_amount=Decimal('1280.00')),
        }

        invoice_specs = [
            ('gabriel', '2026-02', Decimal('1280.00'), 'paid', date(2026, 2, 10), date(2026, 2, 8)),
            ('gabriel', '2026-03', Decimal('1280.00'), 'paid', date(2026, 3, 10), date(2026, 3, 8)),
            ('sofia', '2026-03', Decimal('1280.00'), 'open', date(2026, 3, 10), None),
            ('marina', '2026-03', Decimal('1280.00'), 'overdue', date(2026, 3, 10), None),
            ('pedro', '2026-03', Decimal('1450.00'), 'paid', date(2026, 3, 10), date(2026, 3, 10)),
            ('isabela', '2026-03', Decimal('1450.00'), 'open', date(2026, 3, 10), None),
            ('thiago', '2026-03', Decimal('1280.00'), 'paid', date(2026, 3, 10), date(2026, 3, 9)),
        ]
        for contract_key, reference_month, amount_due, status, due_date_value, payment_date in invoice_specs:
            invoice = ensure_invoice(
                session,
                contract_id=contracts[contract_key].id,
                reference_month=reference_month,
                due_date=due_date_value,
                amount_due=amount_due,
                status=status,
            )
            if payment_date is not None:
                ensure_payment(
                    session,
                    invoice_id=invoice.id,
                    paid_at=payment_date,
                    amount_paid=amount_due,
                    payment_method='pix',
                )

        public_events = [
            (
                None,
                'public',
                'open_house',
                'Visita guiada para familias interessadas',
                'Apresentacao institucional do Fundamental II e Ensino Medio com tour pelos espacos.',
                datetime(2026, 4, 6, 9, 0, tzinfo=TZ),
                datetime(2026, 4, 6, 11, 0, tzinfo=TZ),
                'public',
            ),
            (
                None,
                'public',
                'cultural',
                'Mostra de projetos e feira de ciencias',
                'Evento aberto para familias e visitantes com exposicao de projetos do Fundamental II e Ensino Medio.',
                datetime(2026, 5, 23, 9, 0, tzinfo=TZ),
                datetime(2026, 5, 23, 13, 0, tzinfo=TZ),
                'public',
            ),
            (
                None,
                'public',
                'sports',
                'Festival esportivo da comunidade escolar',
                'Atividades de futsal, volei e integracao entre turmas no contraturno.',
                datetime(2026, 6, 13, 8, 30, tzinfo=TZ),
                datetime(2026, 6, 13, 12, 30, tzinfo=TZ),
                'public',
            ),
        ]
        for class_id, audience, category, title, description, starts_at, ends_at, visibility in public_events:
            ensure_calendar_event(
                session,
                school_unit_id=unit.id,
                class_id=class_id,
                audience=audience,
                category=category,
                title=title,
                description=description,
                starts_at=starts_at,
                ends_at=ends_at,
                visibility=visibility,
            )

        restricted_events = [
            (classes['6f_a'].id, 'students', 'exam', 'Avaliacoes integradas do 6o ano', 'Provas consolidadas do primeiro bimestre.', datetime(2026, 4, 15, 7, 15, tzinfo=TZ), datetime(2026, 4, 17, 12, 30, tzinfo=TZ), 'restricted'),
            (classes['8f_a'].id, 'students', 'project', 'Semana maker do 8o ano', 'Apresentacao de projetos interdisciplinares com robotica e ciencias.', datetime(2026, 5, 11, 13, 30, tzinfo=TZ), datetime(2026, 5, 15, 16, 30, tzinfo=TZ), 'restricted'),
            (classes['3em_a'].id, 'students', 'exam', 'Simulado intensivo da 3a serie', 'Bloco de simulados preparatorios para vestibulares.', datetime(2026, 4, 27, 7, 15, tzinfo=TZ), datetime(2026, 4, 29, 12, 50, tzinfo=TZ), 'restricted'),
        ]
        for class_id, audience, category, title, description, starts_at, ends_at, visibility in restricted_events:
            ensure_calendar_event(
                session,
                school_unit_id=unit.id,
                class_id=class_id,
                audience=audience,
                category=category,
                title=title,
                description=description,
                starts_at=starts_at,
                ends_at=ends_at,
                visibility=visibility,
            )

        print('school expansion seed applied successfully')


if __name__ == '__main__':
    main()
