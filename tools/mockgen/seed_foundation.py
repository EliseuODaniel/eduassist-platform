from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from faker import Faker
from sqlalchemy import select

from api_core.config import get_settings
from api_core.db.models import (
    AccessDecision,
    AttendanceRecord,
    AuditEvent,
    CalendarEvent,
    Class,
    Contract,
    Conversation,
    Document,
    DocumentChunk,
    DocumentSet,
    DocumentVersion,
    Enrollment,
    Grade,
    GradeItem,
    Guardian,
    GuardianStudentLink,
    Handoff,
    Invoice,
    Message,
    Payment,
    RetrievalLabel,
    Role,
    SchoolUnit,
    Student,
    Subject,
    Teacher,
    TeacherAssignment,
    TelegramAccount,
    ToolCall,
    User,
    UserTelegramLink,
)
from api_core.db.session import session_scope


def seed_roles(session) -> dict[str, Role]:
    definitions = {
        'guardian': ('Responsável', 'Acompanha dependentes e financeiro vinculado.'),
        'student': ('Aluno', 'Consulta dados próprios e calendário.'),
        'teacher': ('Professor', 'Consulta turmas e grade docente.'),
        'staff': ('Secretaria', 'Operação interna limitada.'),
        'finance': ('Financeiro', 'Opera contratos, cobranças e pagamentos.'),
        'coordinator': ('Coordenação', 'Visão pedagógica ampliada.'),
        'admin': ('Administrador', 'Operação administrativa da plataforma.'),
    }
    roles: dict[str, Role] = {}
    for code, (name, description) in definitions.items():
        role = session.get(Role, code)
        if role is None:
            role = Role(code=code, name=name, description=description)
            session.add(role)
        roles[code] = role
    session.flush()
    return roles


def make_user(*, role_code: str, external_code: str, full_name: str, email: str, phone: str, is_staff: bool = False) -> User:
    return User(
        role_code=role_code,
        external_code=external_code,
        full_name=full_name,
        email=email,
        phone_number=phone,
        status='active',
        is_staff=is_staff,
    )


def main() -> None:
    settings = get_settings()
    Faker.seed(settings.foundation_seed)
    fake = Faker('pt_BR')
    tz = ZoneInfo('America/Sao_Paulo')

    with session_scope() as session:
        existing_unit = session.scalar(select(SchoolUnit).where(SchoolUnit.code == 'HZ-CAMPUS'))
        if existing_unit is not None:
            print('foundation seed already present; skipping')
            return

        seed_roles(session)

        unit = SchoolUnit(
            code='HZ-CAMPUS',
            name='Colegio Horizonte',
            city='Sao Paulo',
            state='SP',
            timezone='America/Sao_Paulo',
        )
        session.add(unit)
        session.flush()

        users = {
            'guardian_maria': make_user(
                role_code='guardian',
                external_code='USR-GUARD-001',
                full_name='Maria Oliveira',
                email='maria.oliveira@mock.eduassist.local',
                phone='+55 11 98888-1001',
            ),
            'guardian_paulo': make_user(
                role_code='guardian',
                external_code='USR-GUARD-002',
                full_name='Paulo Santos',
                email='paulo.santos@mock.eduassist.local',
                phone='+55 11 98888-1002',
            ),
            'student_lucas': make_user(
                role_code='student',
                external_code='USR-STUD-001',
                full_name='Lucas Oliveira',
                email='lucas.oliveira@mock.eduassist.local',
                phone='+55 11 97777-2001',
            ),
            'student_ana': make_user(
                role_code='student',
                external_code='USR-STUD-002',
                full_name='Ana Oliveira',
                email='ana.oliveira@mock.eduassist.local',
                phone='+55 11 97777-2002',
            ),
            'student_bruno': make_user(
                role_code='student',
                external_code='USR-STUD-003',
                full_name='Bruno Santos',
                email='bruno.santos@mock.eduassist.local',
                phone='+55 11 97777-2003',
            ),
            'teacher_helena': make_user(
                role_code='teacher',
                external_code='USR-TEACH-001',
                full_name='Helena Rocha',
                email='helena.rocha@mock.eduassist.local',
                phone='+55 11 96666-3001',
                is_staff=True,
            ),
            'teacher_marcos': make_user(
                role_code='teacher',
                external_code='USR-TEACH-002',
                full_name='Marcos Lima',
                email='marcos.lima@mock.eduassist.local',
                phone='+55 11 96666-3002',
                is_staff=True,
            ),
            'staff_beatriz': make_user(
                role_code='staff',
                external_code='USR-STAFF-001',
                full_name='Beatriz Costa',
                email='beatriz.costa@mock.eduassist.local',
                phone='+55 11 95555-4001',
                is_staff=True,
            ),
            'finance_carla': make_user(
                role_code='finance',
                external_code='USR-FIN-001',
                full_name='Carla Nogueira',
                email='carla.nogueira@mock.eduassist.local',
                phone='+55 11 95555-4002',
                is_staff=True,
            ),
        }
        session.add_all(users.values())
        session.flush()

        guardians = {
            'maria': Guardian(
                user_id=users['guardian_maria'].id,
                relationship_label='mae',
                cpf_masked='***.456.789-**',
                primary_contact=True,
            ),
            'paulo': Guardian(
                user_id=users['guardian_paulo'].id,
                relationship_label='pai',
                cpf_masked='***.654.321-**',
                primary_contact=True,
            ),
        }
        session.add_all(guardians.values())

        teachers = {
            'helena': Teacher(
                user_id=users['teacher_helena'].id,
                school_unit_id=unit.id,
                employee_code='DOC-001',
                department='Matematica',
            ),
            'marcos': Teacher(
                user_id=users['teacher_marcos'].id,
                school_unit_id=unit.id,
                employee_code='DOC-002',
                department='Linguagens',
            ),
        }
        session.add_all(teachers.values())
        session.flush()

        students = {
            'lucas': Student(
                user_id=users['student_lucas'].id,
                school_unit_id=unit.id,
                enrollment_code='MAT-2026-001',
                birth_date=date(2010, 4, 12),
                current_grade_level=1,
                status='active',
            ),
            'ana': Student(
                user_id=users['student_ana'].id,
                school_unit_id=unit.id,
                enrollment_code='MAT-2026-002',
                birth_date=date(2010, 9, 5),
                current_grade_level=1,
                status='active',
            ),
            'bruno': Student(
                user_id=users['student_bruno'].id,
                school_unit_id=unit.id,
                enrollment_code='MAT-2026-003',
                birth_date=date(2009, 7, 30),
                current_grade_level=2,
                status='active',
            ),
        }
        session.add_all(students.values())
        session.flush()

        session.add_all(
            [
                GuardianStudentLink(
                    guardian_id=guardians['maria'].id,
                    student_id=students['lucas'].id,
                    relationship_label='mae',
                    can_view_finance=True,
                    can_view_academic=True,
                ),
                GuardianStudentLink(
                    guardian_id=guardians['maria'].id,
                    student_id=students['ana'].id,
                    relationship_label='mae',
                    can_view_finance=True,
                    can_view_academic=True,
                ),
                GuardianStudentLink(
                    guardian_id=guardians['paulo'].id,
                    student_id=students['bruno'].id,
                    relationship_label='pai',
                    can_view_finance=True,
                    can_view_academic=True,
                ),
            ]
        )

        classes = {
            '1em_a': Class(
                school_unit_id=unit.id,
                code='1EM-A',
                display_name='1o Ano A',
                academic_year=2026,
                grade_level=1,
                shift='manha',
                homeroom_teacher_id=teachers['helena'].id,
            ),
            '2em_a': Class(
                school_unit_id=unit.id,
                code='2EM-A',
                display_name='2o Ano A',
                academic_year=2026,
                grade_level=2,
                shift='manha',
                homeroom_teacher_id=teachers['marcos'].id,
            ),
        }
        session.add_all(classes.values())

        subjects = {
            'mat': Subject(code='MAT', name='Matematica', area='Exatas', weekly_hours=Decimal('5.0')),
            'por': Subject(code='POR', name='Portugues', area='Linguagens', weekly_hours=Decimal('4.0')),
            'bio': Subject(code='BIO', name='Biologia', area='Natureza', weekly_hours=Decimal('3.0')),
        }
        session.add_all(subjects.values())
        session.flush()

        enrollments = {
            'lucas_1em': Enrollment(student_id=students['lucas'].id, class_id=classes['1em_a'].id, academic_year=2026),
            'ana_1em': Enrollment(student_id=students['ana'].id, class_id=classes['1em_a'].id, academic_year=2026),
            'bruno_2em': Enrollment(student_id=students['bruno'].id, class_id=classes['2em_a'].id, academic_year=2026),
        }
        session.add_all(enrollments.values())
        session.flush()

        assignments = {
            'mat_1em': TeacherAssignment(
                teacher_id=teachers['helena'].id,
                class_id=classes['1em_a'].id,
                subject_id=subjects['mat'].id,
                academic_year=2026,
            ),
            'por_1em': TeacherAssignment(
                teacher_id=teachers['marcos'].id,
                class_id=classes['1em_a'].id,
                subject_id=subjects['por'].id,
                academic_year=2026,
            ),
            'mat_2em': TeacherAssignment(
                teacher_id=teachers['helena'].id,
                class_id=classes['2em_a'].id,
                subject_id=subjects['mat'].id,
                academic_year=2026,
            ),
        }
        session.add_all(assignments.values())
        session.flush()

        grade_items = {
            'mat1_bim1': GradeItem(
                teacher_assignment_id=assignments['mat_1em'].id,
                term_code='2026-B1',
                title='Prova 1 de Matematica',
                max_score=Decimal('10.00'),
                due_date=date(2026, 4, 10),
            ),
            'por1_bim1': GradeItem(
                teacher_assignment_id=assignments['por_1em'].id,
                term_code='2026-B1',
                title='Redacao 1',
                max_score=Decimal('10.00'),
                due_date=date(2026, 4, 12),
            ),
            'mat2_bim1': GradeItem(
                teacher_assignment_id=assignments['mat_2em'].id,
                term_code='2026-B1',
                title='Simulado 1',
                max_score=Decimal('10.00'),
                due_date=date(2026, 4, 14),
            ),
        }
        session.add_all(grade_items.values())
        session.flush()

        session.add_all(
            [
                Grade(enrollment_id=enrollments['lucas_1em'].id, grade_item_id=grade_items['mat1_bim1'].id, score=Decimal('8.70'), feedback='Bom desempenho.'),
                Grade(enrollment_id=enrollments['lucas_1em'].id, grade_item_id=grade_items['por1_bim1'].id, score=Decimal('9.10'), feedback='Boa argumentacao.'),
                Grade(enrollment_id=enrollments['ana_1em'].id, grade_item_id=grade_items['mat1_bim1'].id, score=Decimal('7.80'), feedback='Revisar fracoes.'),
                Grade(enrollment_id=enrollments['ana_1em'].id, grade_item_id=grade_items['por1_bim1'].id, score=Decimal('8.90'), feedback='Texto consistente.'),
                Grade(enrollment_id=enrollments['bruno_2em'].id, grade_item_id=grade_items['mat2_bim1'].id, score=Decimal('6.40'), feedback='Precisa reforcar geometria analitica.'),
            ]
        )

        session.add_all(
            [
                AttendanceRecord(
                    enrollment_id=enrollments['lucas_1em'].id,
                    subject_id=subjects['mat'].id,
                    record_date=date(2026, 3, 9),
                    status='present',
                    minutes_absent=0,
                ),
                AttendanceRecord(
                    enrollment_id=enrollments['ana_1em'].id,
                    subject_id=subjects['por'].id,
                    record_date=date(2026, 3, 9),
                    status='late',
                    minutes_absent=15,
                ),
                AttendanceRecord(
                    enrollment_id=enrollments['bruno_2em'].id,
                    subject_id=subjects['mat'].id,
                    record_date=date(2026, 3, 10),
                    status='absent',
                    minutes_absent=50,
                ),
            ]
        )

        contracts = {
            'lucas': Contract(
                school_unit_id=unit.id,
                student_id=students['lucas'].id,
                guardian_id=guardians['maria'].id,
                academic_year=2026,
                contract_code='CTR-2026-001',
                monthly_amount=Decimal('1450.00'),
                status='active',
            ),
            'ana': Contract(
                school_unit_id=unit.id,
                student_id=students['ana'].id,
                guardian_id=guardians['maria'].id,
                academic_year=2026,
                contract_code='CTR-2026-002',
                monthly_amount=Decimal('1450.00'),
                status='active',
            ),
            'bruno': Contract(
                school_unit_id=unit.id,
                student_id=students['bruno'].id,
                guardian_id=guardians['paulo'].id,
                academic_year=2026,
                contract_code='CTR-2026-003',
                monthly_amount=Decimal('1550.00'),
                status='active',
            ),
        }
        session.add_all(contracts.values())
        session.flush()

        invoices = {
            'lucas_mar': Invoice(contract_id=contracts['lucas'].id, reference_month='2026-03', due_date=date(2026, 3, 10), amount_due=Decimal('1450.00'), status='paid'),
            'ana_mar': Invoice(contract_id=contracts['ana'].id, reference_month='2026-03', due_date=date(2026, 3, 10), amount_due=Decimal('1450.00'), status='open'),
            'bruno_mar': Invoice(contract_id=contracts['bruno'].id, reference_month='2026-03', due_date=date(2026, 3, 10), amount_due=Decimal('1550.00'), status='overdue'),
        }
        session.add_all(invoices.values())
        session.flush()

        session.add_all(
            [
                Payment(
                    invoice_id=invoices['lucas_mar'].id,
                    paid_at=date(2026, 3, 8),
                    amount_paid=Decimal('1450.00'),
                    payment_method='pix',
                )
            ]
        )

        session.add_all(
            [
                CalendarEvent(
                    school_unit_id=unit.id,
                    class_id=None,
                    audience='public',
                    category='meeting',
                    title='Reuniao geral de pais e responsaveis',
                    description='Apresentacao do planejamento do primeiro bimestre.',
                    starts_at=datetime(2026, 3, 28, 9, 0, tzinfo=tz),
                    ends_at=datetime(2026, 3, 28, 10, 30, tzinfo=tz),
                    visibility='public',
                ),
                CalendarEvent(
                    school_unit_id=unit.id,
                    class_id=classes['1em_a'].id,
                    audience='students',
                    category='exam',
                    title='Semana de provas do 1o ano',
                    description='Calendario consolidado do primeiro bimestre.',
                    starts_at=datetime(2026, 4, 13, 7, 15, tzinfo=tz),
                    ends_at=datetime(2026, 4, 17, 12, 0, tzinfo=tz),
                    visibility='restricted',
                ),
                CalendarEvent(
                    school_unit_id=unit.id,
                    class_id=classes['2em_a'].id,
                    audience='students',
                    category='exam',
                    title='Simulados do 2o ano',
                    description='Simulados preparatorios do primeiro bimestre.',
                    starts_at=datetime(2026, 4, 20, 7, 15, tzinfo=tz),
                    ends_at=datetime(2026, 4, 22, 10, 30, tzinfo=tz),
                    visibility='restricted',
                ),
            ]
        )

        public_set = DocumentSet(slug='institutional-public', title='Base publica institucional', visibility='public')
        internal_set = DocumentSet(slug='internal-school', title='Base interna escolar', visibility='restricted')
        session.add_all([public_set, internal_set])
        session.flush()

        documents = {
            'faq': Document(document_set_id=public_set.id, title='FAQ institucional', category='faq', audience='public', visibility='public'),
            'calendar': Document(document_set_id=public_set.id, title='Calendario letivo 2026', category='calendar', audience='public', visibility='public'),
            'teacher_manual': Document(document_set_id=internal_set.id, title='Manual interno do professor', category='policy', audience='teacher', visibility='restricted'),
        }
        session.add_all(documents.values())
        session.flush()

        versions = {
            'faq_v1': DocumentVersion(
                document_id=documents['faq'].id,
                version_label='v1',
                storage_path='documents/public/faq-v1.md',
                mime_type='text/markdown',
                effective_from=date(2026, 1, 15),
                effective_to=None,
            ),
            'calendar_v1': DocumentVersion(
                document_id=documents['calendar'].id,
                version_label='v1',
                storage_path='documents/public/calendar-2026-v1.md',
                mime_type='text/markdown',
                effective_from=date(2026, 1, 15),
                effective_to=None,
            ),
            'teacher_v1': DocumentVersion(
                document_id=documents['teacher_manual'].id,
                version_label='v1',
                storage_path='documents/internal/teacher-manual-v1.md',
                mime_type='text/markdown',
                effective_from=date(2026, 2, 1),
                effective_to=None,
            ),
        }
        session.add_all(versions.values())
        session.flush()

        chunks = [
            DocumentChunk(
                document_version_id=versions['faq_v1'].id,
                chunk_index=0,
                text_content='A escola funciona de segunda a sexta, com atendimento da secretaria das 7h as 17h.',
                contextual_summary='Horario administrativo e funcionamento geral da instituicao.',
                visibility='public',
            ),
            DocumentChunk(
                document_version_id=versions['calendar_v1'].id,
                chunk_index=0,
                text_content='O primeiro bimestre termina em 17 de abril de 2026. A semana de provas do 1o ano ocorre entre 13 e 17 de abril.',
                contextual_summary='Resumo do calendario letivo do primeiro bimestre.',
                visibility='public',
            ),
            DocumentChunk(
                document_version_id=versions['teacher_v1'].id,
                chunk_index=0,
                text_content='Professores devem registrar frequencia ate o fechamento do turno e comunicar ocorrencias relevantes a coordenacao.',
                contextual_summary='Procedimento interno de registro academico docente.',
                visibility='restricted',
            ),
        ]
        session.add_all(chunks)
        session.flush()

        session.add_all(
            [
                RetrievalLabel(document_chunk_id=chunks[0].id, label_type='topic', label_value='atendimento'),
                RetrievalLabel(document_chunk_id=chunks[1].id, label_type='topic', label_value='calendario'),
                RetrievalLabel(document_chunk_id=chunks[2].id, label_type='audience', label_value='teacher'),
            ]
        )

        telegram_account = TelegramAccount(
            telegram_user_id=987654321,
            telegram_chat_id=987654321,
            username='mariaoliveira_mock',
            first_name='Maria',
            last_name='Oliveira',
            is_active=True,
        )
        session.add(telegram_account)
        session.flush()

        session.add(
            UserTelegramLink(
                user_id=users['guardian_maria'].id,
                telegram_account_id=telegram_account.id,
                verification_status='verified',
            )
        )

        conversation = Conversation(
            user_id=users['guardian_maria'].id,
            channel='telegram',
            external_thread_id='tg-987654321',
            status='open',
        )
        session.add(conversation)
        session.flush()

        message = Message(
            conversation_id=conversation.id,
            sender_type='user',
            content='Quais sao as provas do primeiro bimestre do Lucas?',
        )
        session.add(message)
        session.flush()

        session.add(
            ToolCall(
                conversation_id=conversation.id,
                tool_name='get_school_calendar',
                status='completed',
                request_payload={'student_id': str(students['lucas'].id), 'term': '2026-B1'},
                response_payload={'events': 1},
            )
        )
        session.add(
            Handoff(
                conversation_id=conversation.id,
                queue_name='secretaria',
                status='queued',
                summary='Usuario pediu confirmacao humana sobre calendario de provas.',
            )
        )

        session.add(
            AuditEvent(
                actor_user_id=users['guardian_maria'].id,
                event_type='telegram_linked',
                resource_type='telegram_account',
                resource_id=str(telegram_account.id),
                metadata_json={'chat_id': telegram_account.telegram_chat_id},
            )
        )
        session.add(
            AccessDecision(
                actor_user_id=users['guardian_maria'].id,
                resource_type='student_academic_summary',
                action='read',
                decision='allow',
                reason='guardian linked to student lucas with academic scope',
            )
        )

        sample_name = fake.name()
        print(f'foundation seed inserted successfully; sample faker reference={sample_name}')


if __name__ == '__main__':
    main()
