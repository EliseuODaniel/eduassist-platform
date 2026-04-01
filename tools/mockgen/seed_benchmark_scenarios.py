from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

import seed_deep_population as deep
from api_core.db.models import Class, SchoolUnit, Subject, Teacher, TeacherAssignment, User
from api_core.db.session import session_scope
from seed_school_expansion import (
    ensure_attendance,
    ensure_contract,
    ensure_enrollment,
    ensure_grade,
    ensure_grade_item,
    ensure_guardian,
    ensure_guardian_link,
    ensure_invoice,
    ensure_payment,
    ensure_student,
    ensure_subject,
    ensure_teacher,
    ensure_telegram_account,
    ensure_telegram_link,
    ensure_user,
)


ACADEMIC_YEAR = 2026

BENCHMARK_GUARDIANS = [
    {
        'external_code': 'USR-GUARD-201',
        'full_name': 'Helena Nunes',
        'email': 'helena.nunes.family@mock.eduassist.local',
        'phone': '+55 11 98888-2201',
        'relationship_label': 'mae',
        'cpf_masked': '***.222.201-**',
        'subject': '7d24fb1c-791e-5701-a359-1b79dcd90835',
        'username': 'helena.nunes.family',
    },
    {
        'external_code': 'USR-GUARD-202',
        'full_name': 'Marcos Nunes',
        'email': 'marcos.nunes.family@mock.eduassist.local',
        'phone': '+55 11 98888-2202',
        'relationship_label': 'pai',
        'cpf_masked': '***.222.202-**',
        'subject': '0c0e443b-0a09-5a51-bd57-4d98c640b029',
        'username': 'marcos.nunes.family',
    },
    {
        'external_code': 'USR-GUARD-203',
        'full_name': 'Rosa Teixeira',
        'email': 'rosa.teixeira.family@mock.eduassist.local',
        'phone': '+55 11 98888-2203',
        'relationship_label': 'avo',
        'cpf_masked': '***.222.203-**',
        'subject': 'fa0fd3af-ff41-50fa-a816-d79951bdec9f',
        'username': 'rosa.teixeira.family',
    },
    {
        'external_code': 'USR-GUARD-204',
        'full_name': 'Paula Moreira',
        'email': 'paula.moreira.family@mock.eduassist.local',
        'phone': '+55 11 98888-2204',
        'relationship_label': 'mae',
        'cpf_masked': '***.222.204-**',
        'subject': '313510db-c15f-5485-89de-94bf9155b772',
        'username': 'paula.moreira.family',
    },
    {
        'external_code': 'USR-GUARD-205',
        'full_name': 'Fabio Campos',
        'email': 'fabio.campos.family@mock.eduassist.local',
        'phone': '+55 11 98888-2205',
        'relationship_label': 'pai',
        'cpf_masked': '***.222.205-**',
        'subject': '0ebcf078-2dd4-5650-b2d7-3ed384dd3813',
        'username': 'fabio.campos.family',
    },
]

BENCHMARK_TEACHER = {
    'external_code': 'USR-TEACH-008',
    'full_name': 'Fernando Azevedo',
    'email': 'fernando.azevedo@mock.eduassist.local',
    'phone': '+55 11 96666-3008',
    'employee_code': 'DOC-008',
    'department': 'Humanidades',
    'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b3208',
    'username': 'fernando.azevedo',
    'telegram_user_id': 7714501,
    'telegram_chat_id': 1649845501,
}

BENCHMARK_INTERNAL_USERS = [
    {
        'external_code': 'USR-FIN-002',
        'role_code': 'finance',
        'full_name': 'Vinicius Prado',
        'email': 'vinicius.prado@mock.eduassist.local',
        'phone': '+55 11 95555-4002',
        'subject': '290dd0e5-34eb-5517-8481-efb019f843fd',
        'username': 'vinicius.prado',
    },
    {
        'external_code': 'USR-STAFF-002',
        'role_code': 'staff',
        'full_name': 'Priscila Almeida',
        'email': 'priscila.almeida@mock.eduassist.local',
        'phone': '+55 11 95555-4012',
        'subject': 'c6af06db-01a7-51c7-9acf-73cd35388b9f',
        'username': 'priscila.almeida',
    },
    {
        'external_code': 'USR-STAFF-003',
        'role_code': 'staff',
        'full_name': 'Renato Barros',
        'email': 'renato.barros@mock.eduassist.local',
        'phone': '+55 11 95555-4013',
        'subject': '315f85c3-7f35-54ff-8c6e-0b58c99a5ee0',
        'username': 'renato.barros',
    },
]

BENCHMARK_STUDENTS = [
    {
        'external_code': 'USR-STUD-201',
        'full_name': 'Rafael Nunes',
        'email': 'rafael.nunes@mock.eduassist.local',
        'phone': '+55 11 97777-3201',
        'enrollment_code': 'MAT-2026-201',
        'birth_date': date(2009, 3, 18),
        'current_grade_level': 2,
        'class_code': '2EM-A',
        'guardian_links': [('USR-GUARD-201', True, False), ('USR-GUARD-202', False, True)],
        'contract_guardian_code': 'USR-GUARD-202',
        'contract_code': 'CTR-2026-201',
        'monthly_amount': Decimal('1377.50'),
        'subject_scores': {'MAT': Decimal('8.2'), 'POR': Decimal('8.1'), 'HIS': Decimal('7.8'), 'ING': Decimal('8.6')},
    },
    {
        'external_code': 'USR-STUD-202',
        'full_name': 'Manuela Nunes',
        'email': 'manuela.nunes@mock.eduassist.local',
        'phone': '+55 11 97777-3202',
        'enrollment_code': 'MAT-2026-202',
        'birth_date': date(2011, 1, 12),
        'current_grade_level': 9,
        'class_code': '9F-A',
        'guardian_links': [('USR-GUARD-201', True, False), ('USR-GUARD-202', False, True)],
        'contract_guardian_code': 'USR-GUARD-202',
        'contract_code': 'CTR-2026-202',
        'monthly_amount': Decimal('1216.00'),
        'subject_scores': {'MAT': Decimal('7.9'), 'POR': Decimal('8.4'), 'CIE': Decimal('8.1'), 'ING': Decimal('8.5')},
    },
    {
        'external_code': 'USR-STUD-203',
        'full_name': 'Olivia Teixeira',
        'email': 'olivia.teixeira@mock.eduassist.local',
        'phone': '+55 11 97777-3203',
        'enrollment_code': 'MAT-2026-203',
        'birth_date': date(2013, 2, 28),
        'current_grade_level': 7,
        'class_code': '7F-B',
        'guardian_links': [('USR-GUARD-203', True, False)],
        'contract_guardian_code': 'USR-GUARD-203',
        'contract_code': 'CTR-2026-203',
        'monthly_amount': Decimal('1280.00'),
        'subject_scores': {'MAT': Decimal('8.3'), 'POR': Decimal('8.0'), 'CIE': Decimal('7.7'), 'ING': Decimal('8.1')},
    },
    {
        'external_code': 'USR-STUD-204',
        'full_name': 'Diego Moreira',
        'email': 'diego.moreira.student@mock.eduassist.local',
        'phone': '+55 11 97777-3204',
        'enrollment_code': 'MAT-2026-204',
        'birth_date': date(2008, 9, 5),
        'current_grade_level': 3,
        'class_code': '3EM-A',
        'guardian_links': [('USR-GUARD-204', True, True)],
        'contract_guardian_code': 'USR-GUARD-204',
        'contract_code': 'CTR-2026-204',
        'monthly_amount': Decimal('1450.00'),
        'subject_scores': {'MAT': Decimal('8.0'), 'POR': Decimal('8.1'), 'HIS': Decimal('8.3'), 'ING': Decimal('8.0')},
    },
    {
        'external_code': 'USR-STUD-205',
        'full_name': 'Lara Campos',
        'email': 'lara.campos@mock.eduassist.local',
        'phone': '+55 11 97777-3205',
        'enrollment_code': 'MAT-2026-205',
        'birth_date': date(2010, 6, 19),
        'current_grade_level': 1,
        'class_code': '1EM-B',
        'guardian_links': [('USR-GUARD-205', True, True)],
        'contract_guardian_code': 'USR-GUARD-205',
        'contract_code': 'CTR-2026-205',
        'monthly_amount': Decimal('1450.00'),
        'subject_scores': {'MAT': Decimal('8.4'), 'POR': Decimal('8.2'), 'HIS': Decimal('8.0'), 'ING': Decimal('8.7')},
    },
    {
        'external_code': 'USR-STUD-206',
        'full_name': 'Joao Campos',
        'email': 'joao.campos@mock.eduassist.local',
        'phone': '+55 11 97777-3206',
        'enrollment_code': 'MAT-2026-206',
        'birth_date': date(2014, 7, 21),
        'current_grade_level': 6,
        'class_code': '6F-A',
        'guardian_links': [('USR-GUARD-205', True, True)],
        'contract_guardian_code': 'USR-GUARD-205',
        'contract_code': 'CTR-2026-206',
        'monthly_amount': Decimal('1216.00'),
        'subject_scores': {'MAT': Decimal('6.4'), 'POR': Decimal('7.5'), 'CIE': Decimal('7.2'), 'ING': Decimal('7.6')},
        'recovery_score': Decimal('7.3'),
    },
]

BENCHMARK_DOCUMENTS = [
    {
        'set_slug': 'benchmark-public-guidance',
        'set_title': 'Orientacoes Publicas de Benchmark',
        'visibility': 'public',
        'title': 'Orientacao publica para responsaveis com acessos diferentes',
        'category': 'identity',
        'audience': 'familias',
        'chunks': [
            (
                'Em algumas familias, um responsavel pode receber acesso academico e outro acesso financeiro. '
                'Essa divisao existe para refletir o cadastro institucional e evitar exposicao indevida de dados.'
            ),
            (
                'Quando um responsavel pede informacao fora do proprio escopo, o sistema deve negar o dado protegido e orientar o contato correto. '
                'O canal automatico pode abrir atendimento humano quando a familia precisar regularizar o cadastro.'
            ),
        ],
        'labels': ['escopo', 'responsaveis', 'autorizacao'],
    },
    {
        'set_slug': 'benchmark-public-guidance',
        'set_title': 'Orientacoes Publicas de Benchmark',
        'visibility': 'public',
        'title': 'Orientacao publica para segunda chamada por motivo de saude',
        'category': 'academic',
        'audience': 'familias',
        'chunks': [
            (
                'Pedidos de segunda chamada por motivo de saude devem ser registrados no prazo institucional e podem exigir comprovacao adequada. '
                'A orientacao publica explica o fluxo, mas a decisao depende da analise do caso.'
            ),
            (
                'Quando necessario, a familia deve anexar documento ou justificar a ausencia por canal oficial. '
                'A secretaria ou a coordenacao informam a nova data quando o pedido e aceito.'
            ),
        ],
        'labels': ['saude', 'segunda chamada', 'avaliacao'],
    },
    {
        'set_slug': 'benchmark-internal-guidance',
        'set_title': 'Procedimentos Internos de Benchmark',
        'visibility': 'restricted',
        'title': 'Procedimento interno para pagamento parcial e negociacao',
        'category': 'finance',
        'audience': 'staff',
        'chunks': [
            (
                'Quando a familia informa pagamento parcial, o financeiro deve registrar o valor pago, saldo pendente e canal de contato antes de propor negociacao. '
                'O sistema nao deve assumir quitacao total sem evidencia transacional.'
            ),
            (
                'A equipe avalia se o caso segue para renegociacao simples, revisao de juros ou protocolo administrativo. '
                'O bot pode abrir handoff, mas nao aprova acordo sozinho.'
            ),
        ],
        'labels': ['pagamento parcial', 'financeiro', 'negociacao'],
    },
    {
        'set_slug': 'benchmark-internal-guidance',
        'set_title': 'Procedimentos Internos de Benchmark',
        'visibility': 'restricted',
        'title': 'Protocolo interno para responsaveis com escopo parcial',
        'category': 'identity',
        'audience': 'staff',
        'chunks': [
            (
                'Responsaveis com escopo parcial exigem validacao cuidadosa para evitar vazamento de dados. '
                'A equipe deve conferir se o vinculo vigente concede acesso academico, financeiro ou ambos.'
            ),
            (
                'Quando o pedido chega fora do escopo autorizado, o atendimento deve negar o conteudo protegido, registrar a decisao e orientar a regularizacao cadastral. '
                'Excecoes dependem de validacao humana formal.'
            ),
        ],
        'labels': ['policy', 'escopo parcial', 'autorizacao'],
    },
    {
        'set_slug': 'benchmark-internal-guidance',
        'set_title': 'Procedimentos Internos de Benchmark',
        'visibility': 'restricted',
        'title': 'Procedimento interno para transferencia no meio do ano',
        'category': 'secretaria',
        'audience': 'staff',
        'chunks': [
            (
                'Transferencias no meio do ano exigem conferencia documental, historico parcial e alinhamento de pendencias academicas e financeiras. '
                'A secretaria registra protocolo e acompanha a emissao dos documentos finais.'
            ),
            (
                'Sempre que houver cancelamento contratual associado, o financeiro e acionado para validar saldo e encerramento administrativo. '
                'O atendimento humano coordena a conclusao do caso.'
            ),
        ],
        'labels': ['transferencia', 'secretaria', 'documentos finais'],
    },
]


def _teacher_map(session) -> dict[str, Teacher]:
    teacher_codes = ['USR-TEACH-001', 'USR-TEACH-002', 'USR-TEACH-003', 'USR-TEACH-004', 'USR-TEACH-005', 'USR-TEACH-008']
    return {
        user.external_code: teacher
        for teacher, user in session.execute(
            select(Teacher, User)
            .join(User, User.id == Teacher.user_id)
            .where(User.external_code.in_(teacher_codes))
        ).all()
    }


def _ensure_benchmark_teacher(session, *, unit_id) -> tuple[User, Teacher]:
    payload = BENCHMARK_TEACHER
    user = ensure_user(
        session,
        external_code=payload['external_code'],
        role_code='teacher',
        full_name=payload['full_name'],
        email=payload['email'],
        phone=payload['phone'],
        is_staff=True,
    )
    teacher = ensure_teacher(
        session,
        user=user,
        school_unit_id=unit_id,
        employee_code=payload['employee_code'],
        department=payload['department'],
    )
    deep.ensure_federated_identity(
        session,
        user_id=user.id,
        provider=deep.KEYCLOAK_PROVIDER,
        subject=payload['subject'],
        username=payload['username'],
        email=payload['email'],
    )
    telegram_account = ensure_telegram_account(
        session,
        telegram_user_id=payload['telegram_user_id'],
        telegram_chat_id=payload['telegram_chat_id'],
        username=payload['username'],
        first_name=payload['full_name'].split()[0],
        last_name=payload['full_name'].split()[-1],
    )
    ensure_telegram_link(session, user_id=user.id, telegram_account_id=telegram_account.id)
    return user, teacher


def _ensure_benchmark_teacher_schedule(session, *, classes: dict[str, Class], subjects: dict[str, Subject], teacher: Teacher) -> None:
    philosophy = subjects.get('FIL')
    if philosophy is None:
        philosophy = ensure_subject(
            session,
            code='FIL',
            name='Filosofia',
            area='Humanidades',
            weekly_hours=Decimal('2.0'),
        )
        subjects['FIL'] = philosophy

    for class_code in ('1EM-B', '2EM-A', '3EM-A'):
        class_ = classes.get(class_code)
        if class_ is None:
            continue
        deep.ensure_assignment(
            session,
            teacher_id=teacher.id,
            class_id=class_.id,
            subject_id=philosophy.id,
            academic_year=ACADEMIC_YEAR,
        )


def _ensure_benchmark_internal_users(session) -> dict[str, User]:
    users: dict[str, User] = {}
    for payload in BENCHMARK_INTERNAL_USERS:
        user = ensure_user(
            session,
            external_code=payload['external_code'],
            role_code=payload['role_code'],
            full_name=payload['full_name'],
            email=payload['email'],
            phone=payload['phone'],
            is_staff=True,
        )
        deep.ensure_federated_identity(
            session,
            user_id=user.id,
            provider=deep.KEYCLOAK_PROVIDER,
            subject=payload['subject'],
            username=payload['username'],
            email=payload['email'],
        )
        users[payload['external_code']] = user
    return users


def _assignment_for(session, *, class_id, subject_id, subject_code: str, teacher_map: dict[str, Teacher]) -> TeacherAssignment:
    assignment = session.scalar(
        select(TeacherAssignment).where(
            TeacherAssignment.class_id == class_id,
            TeacherAssignment.subject_id == subject_id,
            TeacherAssignment.academic_year == ACADEMIC_YEAR,
        )
    )
    if assignment is not None:
        return assignment
    teacher_code = deep.SUBJECT_TEACHER_FALLBACK[subject_code]
    teacher = teacher_map[teacher_code]
    return deep.ensure_assignment(
        session,
        teacher_id=teacher.id,
        class_id=class_id,
        subject_id=subject_id,
        academic_year=ACADEMIC_YEAR,
    )


def seed_documents(session) -> int:
    count = 0
    for doc_seed in BENCHMARK_DOCUMENTS:
        document_set = deep.ensure_document_set(
            session,
            slug=doc_seed['set_slug'],
            title=doc_seed['set_title'],
            visibility=doc_seed['visibility'],
        )
        document = deep.ensure_document(
            session,
            document_set_id=document_set.id,
            title=doc_seed['title'],
            category=doc_seed['category'],
            audience=doc_seed['audience'],
            visibility=doc_seed['visibility'],
        )
        version = deep.ensure_document_version(
            session,
            document_id=document.id,
            version_label='v2026.3',
            storage_path=f"minio://seed/{doc_seed['set_slug']}/{document.title.lower().replace(' ', '-')}.md",
            mime_type='text/markdown',
            effective_from=date(2026, 3, 31),
        )
        for index, chunk_text in enumerate(doc_seed['chunks']):
            chunk = deep.ensure_document_chunk(
                session,
                document_version_id=version.id,
                chunk_index=index,
                text_content=chunk_text,
                contextual_summary=doc_seed['title'],
                visibility=doc_seed['visibility'],
            )
            deep.ensure_retrieval_label(session, document_chunk_id=chunk.id, label_type='document', label_value=document.title)
            for label in doc_seed['labels']:
                deep.ensure_retrieval_label(session, document_chunk_id=chunk.id, label_type='topic', label_value=label)
        count += 1
    return count


def seed_financials(session, *, unit_id, guardians_by_code, students_by_code) -> int:
    count = 0
    for payload in BENCHMARK_STUDENTS:
        guardian = guardians_by_code[payload['contract_guardian_code']]
        contract = ensure_contract(
            session,
            school_unit_id=unit_id,
            student_id=students_by_code[payload['external_code']].id,
            guardian_id=guardian.id,
            academic_year=ACADEMIC_YEAR,
            contract_code=payload['contract_code'],
            monthly_amount=payload['monthly_amount'],
            status='cancelled' if payload['external_code'] == 'USR-STUD-204' else 'active',
        )

        if payload['external_code'] == 'USR-STUD-201':
            march = ensure_invoice(session, contract_id=contract.id, reference_month='2026-03', due_date=date(2026, 3, 10), amount_due=payload['monthly_amount'], status='paid')
            ensure_payment(session, invoice_id=march.id, paid_at=date(2026, 3, 7), amount_paid=Decimal('600.00'), payment_method='pix')
            ensure_payment(session, invoice_id=march.id, paid_at=date(2026, 3, 8), amount_paid=Decimal('777.50'), payment_method='cartao')
            april = ensure_invoice(session, contract_id=contract.id, reference_month='2026-04', due_date=date(2026, 4, 10), amount_due=payload['monthly_amount'], status='paid')
            ensure_payment(session, invoice_id=april.id, paid_at=date(2026, 4, 7), amount_paid=payload['monthly_amount'], payment_method='pix')
        elif payload['external_code'] == 'USR-STUD-202':
            march = ensure_invoice(session, contract_id=contract.id, reference_month='2026-03', due_date=date(2026, 3, 10), amount_due=payload['monthly_amount'], status='paid')
            ensure_payment(session, invoice_id=march.id, paid_at=date(2026, 3, 9), amount_paid=payload['monthly_amount'], payment_method='pix')
            ensure_invoice(session, contract_id=contract.id, reference_month='2026-04', due_date=date(2026, 4, 10), amount_due=payload['monthly_amount'], status='overdue')
        elif payload['external_code'] == 'USR-STUD-203':
            ensure_invoice(session, contract_id=contract.id, reference_month='2026-03', due_date=date(2026, 3, 10), amount_due=payload['monthly_amount'], status='open')
            ensure_invoice(session, contract_id=contract.id, reference_month='2026-04', due_date=date(2026, 4, 10), amount_due=payload['monthly_amount'], status='overdue')
        elif payload['external_code'] == 'USR-STUD-204':
            jan = ensure_invoice(session, contract_id=contract.id, reference_month='2026-01', due_date=date(2026, 1, 10), amount_due=payload['monthly_amount'], status='paid')
            feb = ensure_invoice(session, contract_id=contract.id, reference_month='2026-02', due_date=date(2026, 2, 10), amount_due=payload['monthly_amount'], status='paid')
            mar = ensure_invoice(session, contract_id=contract.id, reference_month='2026-03', due_date=date(2026, 3, 10), amount_due=payload['monthly_amount'], status='paid')
            ensure_payment(session, invoice_id=jan.id, paid_at=date(2026, 1, 9), amount_paid=payload['monthly_amount'], payment_method='boleto')
            ensure_payment(session, invoice_id=feb.id, paid_at=date(2026, 2, 8), amount_paid=payload['monthly_amount'], payment_method='pix')
            ensure_payment(session, invoice_id=mar.id, paid_at=date(2026, 3, 8), amount_paid=payload['monthly_amount'], payment_method='pix')
        elif payload['external_code'] == 'USR-STUD-205':
            march = ensure_invoice(session, contract_id=contract.id, reference_month='2026-03', due_date=date(2026, 3, 10), amount_due=payload['monthly_amount'], status='paid')
            april = ensure_invoice(session, contract_id=contract.id, reference_month='2026-04', due_date=date(2026, 4, 10), amount_due=payload['monthly_amount'], status='paid')
            ensure_payment(session, invoice_id=march.id, paid_at=date(2026, 3, 9), amount_paid=payload['monthly_amount'], payment_method='pix')
            ensure_payment(session, invoice_id=april.id, paid_at=date(2026, 4, 8), amount_paid=payload['monthly_amount'], payment_method='pix')
        elif payload['external_code'] == 'USR-STUD-206':
            march = ensure_invoice(session, contract_id=contract.id, reference_month='2026-03', due_date=date(2026, 3, 10), amount_due=payload['monthly_amount'], status='overdue')
            ensure_payment(session, invoice_id=march.id, paid_at=date(2026, 3, 18), amount_paid=Decimal('500.00'), payment_method='pix')
            ensure_invoice(session, contract_id=contract.id, reference_month='2026-04', due_date=date(2026, 4, 10), amount_due=payload['monthly_amount'], status='open')
        count += 1
    return count


def seed_academics(session, *, classes, subjects, students_by_code, teacher_map) -> int:
    item_specs = [
        ('T1', 'Avaliacao bimestral', Decimal('10.00'), date(2026, 4, 16)),
        ('T1', 'Trabalho orientado', Decimal('10.00'), date(2026, 4, 2)),
    ]
    count = 0
    enrollments = {}
    for payload in BENCHMARK_STUDENTS:
        student = students_by_code[payload['external_code']]
        class_ = classes[payload['class_code']]
        enrollments[payload['external_code']] = ensure_enrollment(
            session,
            student_id=student.id,
            class_id=class_.id,
            academic_year=ACADEMIC_YEAR,
            status='transferred' if payload['external_code'] == 'USR-STUD-204' else 'active',
        )
        for subject_code, base_score in payload['subject_scores'].items():
            assignment = _assignment_for(
                session,
                class_id=class_.id,
                subject_id=subjects[subject_code].id,
                subject_code=subject_code,
                teacher_map=teacher_map,
            )
            for index, (term_code, title, max_score, due_date) in enumerate(item_specs):
                item = ensure_grade_item(
                    session,
                    teacher_assignment_id=assignment.id,
                    term_code=term_code,
                    title=title,
                    max_score=max_score,
                    due_date=due_date,
                )
                adjustment = Decimal('-0.4') if index == 0 else Decimal('0.1')
                ensure_grade(
                    session,
                    enrollment_id=enrollments[payload['external_code']].id,
                    grade_item_id=item.id,
                    score=max(Decimal('5.8'), min(Decimal('9.8'), base_score + adjustment)),
                    feedback=f'Registro benchmark em {subject_code.lower()}.',
                )
            ensure_attendance(
                session,
                enrollment_id=enrollments[payload['external_code']].id,
                subject_id=subjects[subject_code].id,
                record_date=date(2026, 3, 11),
                status='present',
            )
        count += 1

    recovery_student = next(payload for payload in BENCHMARK_STUDENTS if payload['external_code'] == 'USR-STUD-206')
    recovery_class = classes[recovery_student['class_code']]
    assignment = _assignment_for(
        session,
        class_id=recovery_class.id,
        subject_id=subjects['MAT'].id,
        subject_code='MAT',
        teacher_map=teacher_map,
    )
    item = ensure_grade_item(
        session,
        teacher_assignment_id=assignment.id,
        term_code='RF',
        title='Recuperacao final',
        max_score=Decimal('10.00'),
        due_date=date(2026, 12, 11),
    )
    ensure_grade(
        session,
        enrollment_id=enrollments['USR-STUD-206'].id,
        grade_item_id=item.id,
        score=recovery_student['recovery_score'],
        feedback='Recuperacao final concluida com plano de acompanhamento.',
    )
    ensure_attendance(
        session,
        enrollment_id=enrollments['USR-STUD-206'].id,
        subject_id=subjects['MAT'].id,
        record_date=date(2026, 12, 11),
        status='present',
    )
    return count


def seed_conversations(session, *, users: dict[str, User]) -> int:
    base_time = datetime(2026, 3, 31, 13, 0, tzinfo=UTC)

    finance_conversation = deep.ensure_conversation(
        session,
        external_thread_id='benchmark-seed-finance-partial-001',
        user_id=users['USR-GUARD-205'].id,
        status='open',
        created_at=base_time - timedelta(hours=6),
        updated_at=base_time - timedelta(hours=5, minutes=20),
    )
    deep.ensure_message(session, conversation_id=finance_conversation.id, sender_type='user', content='Paguei parte da mensalidade do Joao e preciso negociar o restante.', created_at=base_time - timedelta(hours=6))
    deep.ensure_message(session, conversation_id=finance_conversation.id, sender_type='assistant', content='Vou registrar o caso com o financeiro para avaliar a negociacao do saldo.', created_at=base_time - timedelta(hours=6) + timedelta(minutes=1))
    deep.ensure_tool_call(
        session,
        conversation_id=finance_conversation.id,
        tool_name='get_financial_summary',
        status='completed',
        request_payload={'student_external_code': 'USR-STUD-206'},
        response_payload={'invoice_reference_month': '2026-03', 'amount_due': '1216.00', 'partial_payment_detected': True},
        created_at=base_time - timedelta(hours=6) + timedelta(minutes=1),
    )
    finance_handoff = deep.ensure_handoff(
        session,
        conversation_id=finance_conversation.id,
        queue_name='financeiro',
        priority_code='high',
        assigned_user_id=users['USR-FIN-002'].id,
        assigned_at=base_time - timedelta(hours=5, minutes=40),
        response_due_at=base_time - timedelta(hours=5),
        resolution_due_at=base_time + timedelta(hours=2),
        status='in_progress',
        summary='Responsavel informou pagamento parcial da mensalidade do aluno Joao Campos e pediu negociacao do saldo.',
        created_at=base_time - timedelta(hours=6),
        updated_at=base_time - timedelta(hours=5, minutes=40),
    )
    deep.ensure_audit_event(session, actor_user_id=users['USR-GUARD-205'].id, event_type='support_handoff.created', resource_type='support_handoff', resource_id=str(finance_handoff.id), metadata={'queue_name': 'financeiro', 'priority_code': 'high'}, occurred_at=base_time - timedelta(hours=6))
    deep.ensure_access_decision(session, actor_user_id=users['USR-GUARD-205'].id, resource_type='financial_summary', action='read', decision='allow', reason='guardian_link_finance_scope', occurred_at=base_time - timedelta(hours=6))

    recovery_conversation = deep.ensure_conversation(
        session,
        external_thread_id='benchmark-seed-recovery-001',
        user_id=users['USR-STUD-206'].id,
        status='open',
        created_at=base_time - timedelta(hours=5),
        updated_at=base_time - timedelta(hours=4, minutes=55),
    )
    deep.ensure_message(session, conversation_id=recovery_conversation.id, sender_type='user', content='Quero entender como ficou minha recuperacao final em matematica.', created_at=base_time - timedelta(hours=5))
    deep.ensure_message(session, conversation_id=recovery_conversation.id, sender_type='assistant', content='Encontrei registro de recuperacao final e posso resumir o desempenho atual.', created_at=base_time - timedelta(hours=5) + timedelta(minutes=1))
    deep.ensure_tool_call(
        session,
        conversation_id=recovery_conversation.id,
        tool_name='get_student_academic_summary',
        status='completed',
        request_payload={'student_external_code': 'USR-STUD-206', 'include_recovery': True},
        response_payload={'recovery_subject': 'MAT', 'recovery_score': '7.30'},
        created_at=base_time - timedelta(hours=5) + timedelta(minutes=1),
    )
    deep.ensure_access_decision(session, actor_user_id=users['USR-STUD-206'].id, resource_type='student_academic_summary', action='read', decision='allow', reason='student_self_scope', occurred_at=base_time - timedelta(hours=5))

    split_academic = deep.ensure_conversation(
        session,
        external_thread_id='benchmark-seed-split-access-academic-001',
        user_id=users['USR-GUARD-202'].id,
        status='open',
        created_at=base_time - timedelta(hours=4),
        updated_at=base_time - timedelta(hours=3, minutes=58),
    )
    deep.ensure_message(session, conversation_id=split_academic.id, sender_type='user', content='Como estao as notas do Rafael em matematica?', created_at=base_time - timedelta(hours=4))
    deep.ensure_message(session, conversation_id=split_academic.id, sender_type='assistant', content='Nao posso abrir o resumo academico no seu escopo atual. Posso orientar o responsavel com acesso academico.', created_at=base_time - timedelta(hours=4) + timedelta(minutes=1))
    deep.ensure_tool_call(
        session,
        conversation_id=split_academic.id,
        tool_name='get_student_academic_summary',
        status='denied',
        request_payload={'student_external_code': 'USR-STUD-201'},
        response_payload={'reason': 'guardian_academic_scope_denied'},
        created_at=base_time - timedelta(hours=4) + timedelta(minutes=1),
    )
    deep.ensure_access_decision(session, actor_user_id=users['USR-GUARD-202'].id, resource_type='student_academic_summary', action='read', decision='deny', reason='guardian_academic_scope_denied', occurred_at=base_time - timedelta(hours=4))

    split_finance = deep.ensure_conversation(
        session,
        external_thread_id='benchmark-seed-split-access-finance-001',
        user_id=users['USR-GUARD-201'].id,
        status='open',
        created_at=base_time - timedelta(hours=3),
        updated_at=base_time - timedelta(hours=2, minutes=58),
    )
    deep.ensure_message(session, conversation_id=split_finance.id, sender_type='user', content='Quero ver a fatura do Rafael e da Manuela.', created_at=base_time - timedelta(hours=3))
    deep.ensure_message(session, conversation_id=split_finance.id, sender_type='assistant', content='Nao posso expor dados financeiros no seu escopo atual. Posso orientar o contato do responsavel financeiro ou abrir atendimento.', created_at=base_time - timedelta(hours=3) + timedelta(minutes=1))
    deep.ensure_tool_call(
        session,
        conversation_id=split_finance.id,
        tool_name='get_financial_summary',
        status='denied',
        request_payload={'student_external_code': 'USR-STUD-201'},
        response_payload={'reason': 'guardian_finance_scope_denied'},
        created_at=base_time - timedelta(hours=3) + timedelta(minutes=1),
    )
    deep.ensure_access_decision(session, actor_user_id=users['USR-GUARD-201'].id, resource_type='financial_summary', action='read', decision='deny', reason='guardian_finance_scope_denied', occurred_at=base_time - timedelta(hours=3))

    transfer_conversation = deep.ensure_conversation(
        session,
        external_thread_id='benchmark-seed-transfer-001',
        user_id=users['USR-GUARD-204'].id,
        status='open',
        created_at=base_time - timedelta(hours=2),
        updated_at=base_time - timedelta(hours=1, minutes=40),
    )
    deep.ensure_message(session, conversation_id=transfer_conversation.id, sender_type='user', content='Preciso concluir a transferencia do Diego e emitir os documentos finais.', created_at=base_time - timedelta(hours=2))
    deep.ensure_message(session, conversation_id=transfer_conversation.id, sender_type='assistant', content='Vou abrir um pedido institucional para a secretaria acompanhar a transferencia.', created_at=base_time - timedelta(hours=2) + timedelta(minutes=1))
    transfer_handoff = deep.ensure_handoff(
        session,
        conversation_id=transfer_conversation.id,
        queue_name='secretaria',
        priority_code='standard',
        assigned_user_id=users['USR-STAFF-003'].id,
        assigned_at=base_time - timedelta(hours=1, minutes=45),
        response_due_at=base_time - timedelta(hours=1),
        resolution_due_at=base_time + timedelta(hours=8),
        status='resolved',
        summary='Solicitacao de transferencia e emissao de documentos finais do aluno Diego Moreira.',
        created_at=base_time - timedelta(hours=2),
        updated_at=base_time - timedelta(hours=1, minutes=40),
    )
    deep.ensure_institutional_request(
        session,
        conversation_id=transfer_conversation.id,
        requester_user_id=users['USR-GUARD-204'].id,
        linked_handoff_id=transfer_handoff.id,
        protocol_code='REQ-20260331-0201',
        target_area='secretaria',
        category='transferencia',
        subject='Transferencia e documentos finais de Diego Moreira',
        details='Familia solicitou conclusao da transferencia com emissao de historico e demais documentos finais.',
        requester_contact='paula.moreira.family@mock.eduassist.local',
        status='resolved',
        created_at=base_time - timedelta(hours=1, minutes=50),
    )

    visit_conversation = deep.ensure_conversation(
        session,
        external_thread_id='benchmark-seed-visit-reschedule-001',
        user_id=users['USR-GUARD-203'].id,
        status='open',
        created_at=base_time - timedelta(hours=1),
        updated_at=base_time - timedelta(minutes=45),
    )
    deep.ensure_message(session, conversation_id=visit_conversation.id, sender_type='user', content='Quero remarcar a visita da Olivia para outro horario.', created_at=base_time - timedelta(hours=1))
    deep.ensure_message(session, conversation_id=visit_conversation.id, sender_type='assistant', content='Posso atualizar a solicitacao de visita e reenfileirar o atendimento.', created_at=base_time - timedelta(hours=1) + timedelta(minutes=1))
    visit_handoff = deep.ensure_handoff(
        session,
        conversation_id=visit_conversation.id,
        queue_name='admissoes',
        priority_code='standard',
        assigned_user_id=users['USR-STAFF-002'].id,
        assigned_at=base_time - timedelta(minutes=50),
        response_due_at=base_time + timedelta(hours=3),
        resolution_due_at=base_time + timedelta(hours=20),
        status='queued',
        summary='Remarcacao de visita institucional para familia de Olivia Teixeira.',
        created_at=base_time - timedelta(hours=1),
        updated_at=base_time - timedelta(minutes=45),
    )
    deep.ensure_visit_booking(
        session,
        conversation_id=visit_conversation.id,
        requester_user_id=users['USR-GUARD-203'].id,
        linked_handoff_id=visit_handoff.id,
        protocol_code='VIS-20260331-0201',
        status='requested',
        audience_name='Rosa Teixeira',
        audience_contact='rosa.teixeira.family@mock.eduassist.local',
        interested_segment='fundamental II',
        preferred_date=date(2026, 4, 8),
        preferred_window='tarde',
        attendee_count=2,
        slot_label='visita guiada remarcada',
        notes='Familia solicitou remarcacao da visita por indisponibilidade no horario anterior.',
        created_at=base_time - timedelta(minutes=50),
    )
    return 6


def main() -> None:
    with session_scope() as session:
        unit = session.scalar(select(SchoolUnit).where(SchoolUnit.code == 'HZ-CAMPUS'))
        if unit is None:
            raise SystemExit('foundation seed missing; run make db-seed-foundation first')

        deep_marker = session.scalar(select(User).where(User.external_code == 'USR-GUARD-101'))
        if deep_marker is None:
            raise SystemExit('deep population seed missing; run make db-seed-deep-population first')

        marker = session.scalar(select(User).where(User.external_code == 'USR-GUARD-201'))
        if marker is not None:
            print('benchmark scenarios seed already present; applying incremental benchmark sync')

        users: dict[str, User] = {}
        guardians_by_code = {}
        users.update(_ensure_benchmark_internal_users(session))

        for payload in BENCHMARK_GUARDIANS:
            user = ensure_user(
                session,
                external_code=payload['external_code'],
                role_code='guardian',
                full_name=payload['full_name'],
                email=payload['email'],
                phone=payload['phone'],
            )
            users[payload['external_code']] = user
            guardians_by_code[payload['external_code']] = ensure_guardian(
                session,
                user=user,
                relationship_label=payload['relationship_label'],
                cpf_masked=payload['cpf_masked'],
                primary_contact=True,
            )
            deep.ensure_federated_identity(
                session,
                user_id=user.id,
                provider=deep.KEYCLOAK_PROVIDER,
                subject=payload['subject'],
                username=payload['username'],
                email=payload['email'],
            )

        classes = {
            class_.code: class_
            for class_ in session.execute(
                select(Class).where(
                    Class.code.in_({'2EM-A', '9F-A', '7F-B', '3EM-A', '1EM-B', '6F-A'})
                )
            ).scalars().all()
        }
        subjects = {
            subject.code: subject
            for subject in session.execute(
                select(Subject).where(Subject.code.in_({'MAT', 'POR', 'CIE', 'ING', 'HIS', 'FIL'}))
            ).scalars().all()
        }
        benchmark_teacher_user, benchmark_teacher = _ensure_benchmark_teacher(session, unit_id=unit.id)
        users[benchmark_teacher_user.external_code] = benchmark_teacher_user
        _ensure_benchmark_teacher_schedule(session, classes=classes, subjects=subjects, teacher=benchmark_teacher)
        teacher_map = _teacher_map(session)

        students_by_code = {}
        for payload in BENCHMARK_STUDENTS:
            user = ensure_user(
                session,
                external_code=payload['external_code'],
                role_code='student',
                full_name=payload['full_name'],
                email=payload['email'],
                phone=payload['phone'],
            )
            users[payload['external_code']] = user
            student = ensure_student(
                session,
                user=user,
                school_unit_id=unit.id,
                enrollment_code=payload['enrollment_code'],
                birth_date=payload['birth_date'],
                current_grade_level=payload['current_grade_level'],
            )
            students_by_code[payload['external_code']] = student

            class_ = classes[payload['class_code']]
            ensure_enrollment(
                session,
                student_id=student.id,
                class_id=class_.id,
                academic_year=ACADEMIC_YEAR,
                status='transferred' if payload['external_code'] == 'USR-STUD-204' else 'active',
            )
            for guardian_code, can_view_academic, can_view_finance in payload['guardian_links']:
                ensure_guardian_link(
                    session,
                    guardian_id=guardians_by_code[guardian_code].id,
                    student_id=student.id,
                    relationship_label=next(item['relationship_label'] for item in BENCHMARK_GUARDIANS if item['external_code'] == guardian_code),
                    can_view_finance=can_view_finance,
                    can_view_academic=can_view_academic,
                )

        telegram_201 = ensure_telegram_account(
            session,
            telegram_user_id=7700201,
            telegram_chat_id=8800201,
            username='helena.nunes.family',
            first_name='Helena',
            last_name='Nunes',
        )
        telegram_202 = ensure_telegram_account(
            session,
            telegram_user_id=7700202,
            telegram_chat_id=8800202,
            username='marcos.nunes.family',
            first_name='Marcos',
            last_name='Nunes',
        )
        telegram_205 = ensure_telegram_account(
            session,
            telegram_user_id=7700205,
            telegram_chat_id=8800205,
            username='fabio.campos.family',
            first_name='Fabio',
            last_name='Campos',
        )
        ensure_telegram_link(session, user_id=users['USR-GUARD-201'].id, telegram_account_id=telegram_201.id)
        ensure_telegram_link(session, user_id=users['USR-GUARD-202'].id, telegram_account_id=telegram_202.id)
        ensure_telegram_link(session, user_id=users['USR-GUARD-205'].id, telegram_account_id=telegram_205.id)

        deep.ensure_telegram_link_challenge(
            session,
            user_id=users['USR-GUARD-201'].id,
            code_hash='tlc-benchmark-201',
            expires_at=datetime(2026, 3, 31, 18, 0, tzinfo=UTC),
            consumed_at=None,
        )
        deep.ensure_telegram_link_challenge(
            session,
            user_id=users['USR-GUARD-202'].id,
            code_hash='tlc-benchmark-202',
            expires_at=datetime(2026, 3, 31, 17, 0, tzinfo=UTC),
            consumed_at=datetime(2026, 3, 31, 16, 10, tzinfo=UTC),
        )
        deep.ensure_telegram_link_challenge(
            session,
            user_id=users['USR-GUARD-203'].id,
            code_hash='tlc-benchmark-203',
            expires_at=datetime(2026, 3, 31, 19, 30, tzinfo=UTC),
            consumed_at=None,
        )

        document_count = seed_documents(session)
        contract_count = seed_financials(
            session,
            unit_id=unit.id,
            guardians_by_code=guardians_by_code,
            students_by_code=students_by_code,
        )
        academic_count = seed_academics(
            session,
            classes=classes,
            subjects=subjects,
            students_by_code=students_by_code,
            teacher_map=teacher_map,
        )
        thread_count = seed_conversations(session, users=users)

        print(
            'benchmark scenarios seed inserted successfully; '
            f'guardians={len(BENCHMARK_GUARDIANS)} students={len(BENCHMARK_STUDENTS)} '
            f'contracts={contract_count} academic_profiles={academic_count} '
            f'documents={document_count} threads={thread_count}'
        )


if __name__ == '__main__':
    main()
