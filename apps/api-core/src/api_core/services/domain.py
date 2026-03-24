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
    PublicAssistantCapabilities,
    PublicContactChannel,
    PublicFeatureAvailability,
    PublicHighlightEntry,
    PublicKpiEntry,
    PublicLeadershipMember,
    PublicOrgDirectory,
    PublicSchoolProfile,
    PublicServiceDirectory,
    PublicServiceCatalogEntry,
    PublicShiftOffer,
    PublicTuitionReference,
    PublicVisitOffer,
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
        address_line='Rua das Acacias, 1450',
        district='Vila Mariana',
        short_headline=(
            'Escola laica com Ensino Fundamental II e Ensino Medio, '
            'acompanhamento tutorial e trilhas academicas no contraturno.'
        ),
        education_model=(
            'Projeto pedagogico laico, com foco em aprendizagem por projetos, '
            'cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.'
        ),
        confessional_status='laica',
        segments=[
            'Ensino Fundamental II (6o ao 9o ano)',
            'Ensino Medio (1a a 3a serie)',
        ],
        shift_offers=[
            PublicShiftOffer(
                segment='Ensino Fundamental II',
                shift_code='manha',
                shift_label='Manha',
                starts_at='07:15',
                ends_at='12:30',
                notes='Oficinas, plantoes, esportes e estudo orientado no contraturno em dias alternados.',
            ),
            PublicShiftOffer(
                segment='Ensino Medio',
                shift_code='manha',
                shift_label='Manha',
                starts_at='07:15',
                ends_at='12:50',
                notes='Trilhas eletivas, monitorias e laboratorios no contraturno a partir das 14h00.',
            ),
            PublicShiftOffer(
                segment='Fundamental II e Ensino Medio',
                shift_code='integral',
                shift_label='Integral opcional',
                starts_at='07:00',
                ends_at='17:30',
                notes='Inclui estudo orientado, almoco, oficinas, esportes e acompanhamento no contraturno.',
            ),
        ],
        tuition_reference=[
            PublicTuitionReference(
                segment='Ensino Fundamental II',
                shift_label='Manha',
                monthly_amount=Decimal('1280.00'),
                enrollment_fee=Decimal('350.00'),
                notes='Valor comercial publico de referencia para 2026. Material didatico e uniforme sao cobrados a parte.',
            ),
            PublicTuitionReference(
                segment='Ensino Medio',
                shift_label='Manha',
                monthly_amount=Decimal('1450.00'),
                enrollment_fee=Decimal('350.00'),
                notes='Valor comercial publico de referencia para 2026. Ha politica comercial para irmaos e pagamento pontual.',
            ),
            PublicTuitionReference(
                segment='Periodo integral opcional',
                shift_label='Complemento contraturno',
                monthly_amount=Decimal('480.00'),
                enrollment_fee=Decimal('0.00'),
                notes='Adicional mensal aplicado ao estudante matriculado no turno regular que aderir ao periodo integral.',
            ),
        ],
        contact_channels=[
            PublicContactChannel(channel='telefone', label='Secretaria', value='(11) 3333-4200'),
            PublicContactChannel(channel='telefone', label='Admissoes', value='(11) 3333-4201'),
            PublicContactChannel(channel='telefone', label='Orientacao educacional', value='(11) 3333-4202'),
            PublicContactChannel(channel='telefone', label='Financeiro', value='(11) 3333-4203'),
            PublicContactChannel(channel='whatsapp', label='Atendimento comercial', value='(11) 97500-2040'),
            PublicContactChannel(channel='whatsapp', label='Secretaria digital', value='(11) 97500-2041'),
            PublicContactChannel(channel='email', label='Secretaria', value='secretaria@colegiohorizonte.edu.br'),
            PublicContactChannel(channel='email', label='Admissoes', value='admissoes@colegiohorizonte.edu.br'),
            PublicContactChannel(channel='email', label='Orientacao educacional', value='orientacao@colegiohorizonte.edu.br'),
            PublicContactChannel(channel='email', label='Financeiro', value='financeiro@colegiohorizonte.edu.br'),
            PublicContactChannel(channel='email', label='Direcao', value='direcao@colegiohorizonte.edu.br'),
            PublicContactChannel(channel='email', label='Suporte digital', value='suporte.digital@colegiohorizonte.edu.br'),
        ],
        feature_inventory=[
            PublicFeatureAvailability(
                feature_key='biblioteca',
                label='Biblioteca Aurora',
                category='service',
                available=True,
                notes='Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.',
            ),
            PublicFeatureAvailability(
                feature_key='laboratorio',
                label='Laboratorio de Ciencias',
                category='infrastructure',
                available=True,
                notes='Uso em aulas praticas, clubes de ciencias e mostras semestrais.',
            ),
            PublicFeatureAvailability(
                feature_key='maker',
                label='Espaco Maker',
                category='infrastructure',
                available=True,
                notes='Ambiente de robotica, prototipagem leve e projetos interdisciplinares.',
            ),
            PublicFeatureAvailability(
                feature_key='quadra',
                label='Quadra Poliesportiva Coberta',
                category='infrastructure',
                available=True,
                notes='Usada para educacao fisica, futsal, volei e eventos internos.',
            ),
            PublicFeatureAvailability(
                feature_key='futebol',
                label='Futsal e treinos esportivos',
                category='activity',
                available=True,
                notes='Treinos no contraturno para Fundamental II e Ensino Medio.',
            ),
            PublicFeatureAvailability(
                feature_key='volei',
                label='Volei escolar',
                category='activity',
                available=True,
                notes='Turmas mistas por faixa etaria no contraturno.',
            ),
            PublicFeatureAvailability(
                feature_key='danca',
                label='Oficina de danca e expressao corporal',
                category='activity',
                available=True,
                notes='Oferta semestral no contraturno, vinculada ao programa cultural.',
            ),
            PublicFeatureAvailability(
                feature_key='teatro',
                label='Oficina de teatro',
                category='activity',
                available=True,
                notes='Montagens anuais integradas ao projeto cultural.',
            ),
            PublicFeatureAvailability(
                feature_key='academia',
                label='Academia',
                category='infrastructure',
                available=False,
                notes='A escola nao mantem academia própria aberta ao publico estudantil.',
            ),
            PublicFeatureAvailability(
                feature_key='piscina',
                label='Piscina',
                category='infrastructure',
                available=False,
                notes='A escola nao possui piscina no campus atual.',
            ),
            PublicFeatureAvailability(
                feature_key='quadra de tenis',
                label='Quadra de tenis',
                category='infrastructure',
                available=False,
                notes='A escola nao possui quadra de tenis dedicada.',
            ),
            PublicFeatureAvailability(
                feature_key='cantina',
                label='Cantina e almoco supervisionado',
                category='service',
                available=True,
                notes='Cantina com lanches e almoco por adesao para estudantes de contraturno.',
            ),
            PublicFeatureAvailability(
                feature_key='orientacao educacional',
                label='Orientacao educacional',
                category='service',
                available=True,
                notes='Acompanhamento socioemocional, mediacao escolar e apoio a familias.',
            ),
        ],
        leadership_team=[
            PublicLeadershipMember(
                member_key='direcao_geral',
                name='Helena Martins',
                title='Diretora geral',
                focus='Governanca escolar, cultura institucional e relacionamento com familias.',
                contact_channel='direcao@colegiohorizonte.edu.br',
                notes='Atende por agenda institucional e participa dos encontros de familias a cada bimestre.',
            ),
            PublicLeadershipMember(
                member_key='coordenacao_fundamental_ii',
                name='Ricardo Paiva',
                title='Coordenador do Ensino Fundamental II',
                focus='Acompanhamento pedagogico do 6o ao 9o ano, rotina escolar e projetos interdisciplinares.',
                contact_channel='fundamental2@colegiohorizonte.edu.br',
                notes='Conduz reunioes de acolhimento, acompanhamento de rotina e transicao para o Ensino Medio.',
            ),
            PublicLeadershipMember(
                member_key='coordenacao_ensino_medio',
                name='Luciana Ferraz',
                title='Coordenadora do Ensino Medio',
                focus='Trilhas academicas, monitorias, projeto de vida e preparacao progressiva para vestibulares.',
                contact_channel='ensinomedio@colegiohorizonte.edu.br',
                notes='Responsavel pelos itinerarios eletivos, simulados e plantoes de monitoria.',
            ),
        ],
        public_kpis=[
            PublicKpiEntry(
                metric_key='aprovacao_geral',
                label='Aprovacao global',
                value=96.4,
                unit='%',
                reference_period='ano letivo 2025',
                notes='Indicador institucional consolidado do Fundamental II e Ensino Medio.',
            ),
            PublicKpiEntry(
                metric_key='frequencia_media',
                label='Frequencia media',
                value=97.1,
                unit='%',
                reference_period='ano letivo 2025',
                notes='Media global de presenca nos componentes curriculares regulares.',
            ),
            PublicKpiEntry(
                metric_key='familias_satisfeitas',
                label='Familias que avaliaram o atendimento como bom ou excelente',
                value=92.0,
                unit='%',
                reference_period='pesquisa institucional 2025',
                notes='Resultado agregado da pesquisa anual de experiencia com familias.',
            ),
        ],
        highlights=[
            PublicHighlightEntry(
                highlight_key='tutoria_projeto_de_vida',
                title='Tutoria academica e projeto de vida',
                description='Cada estudante do Ensino Medio participa de trilhas de tutoria e planejamento academico com acompanhamento proximo ao longo do ano.',
                evidence_line='O contraturno combina monitorias, tutorias e trilhas eletivas acompanhadas por coordenacao e orientacao educacional.',
            ),
            PublicHighlightEntry(
                highlight_key='maker_integrado',
                title='Espaco Maker integrado ao curriculo',
                description='O espaco maker nao funciona como atividade isolada; ele entra em projetos interdisciplinares de ciencias, tecnologia e cultura digital.',
                evidence_line='Projetos do Fundamental II e do Ensino Medio usam o maker como ambiente de prototipagem leve e experimentacao orientada.',
            ),
            PublicHighlightEntry(
                highlight_key='acolhimento_familias',
                title='Acolhimento estruturado para familias e estudantes',
                description='A escola combina secretaria, orientacao educacional e coordenacao em uma jornada de acolhimento que inclui visita, entrevista e acompanhamento inicial.',
                evidence_line='Ha fluxo de visita institucional, apresentacao pedagogica e entrevista de acolhimento antes da confirmacao de matricula.',
            ),
        ],
        visit_offers=[
            PublicVisitOffer(
                offer_key='visita_terca_manha',
                title='Visita guiada ao campus',
                audience='familias interessadas',
                day_label='terca-feira',
                start_time='09:00',
                end_time='10:15',
                location='Recepcao principal e circuito pedagogico',
                notes='Inclui apresentacao institucional, visita aos espacos e conversa curta com admissions.',
            ),
            PublicVisitOffer(
                offer_key='visita_quinta_tarde',
                title='Visita guiada com foco pedagogico',
                audience='familias interessadas',
                day_label='quinta-feira',
                start_time='14:30',
                end_time='15:45',
                location='Recepcao principal e salas de projeto',
                notes='Janela pensada para familias que desejam conhecer infraestrutura, rotina e proposta pedagogica.',
            ),
        ],
        service_catalog=[
            PublicServiceCatalogEntry(
                service_key='atendimento_admissoes',
                title='Matricula, bolsas e atendimento comercial',
                audience='familias interessadas e novas matriculas',
                request_channel='bot, admissions, whatsapp comercial ou visita guiada',
                typical_eta='retorno em ate 1 dia util',
                notes='Atende duvidas sobre processo de ingresso, documentos, bolsas, descontos e simulacao financeira inicial.',
            ),
            PublicServiceCatalogEntry(
                service_key='visita_institucional',
                title='Agendamento de visita a escola',
                audience='publico geral',
                request_channel='bot, whatsapp comercial ou admissions',
                typical_eta='confirmacao em ate 1 dia util',
                notes='A equipe comercial confirma a data e envia orientacoes de chegada.',
            ),
            PublicServiceCatalogEntry(
                service_key='secretaria_escolar',
                title='Secretaria escolar e documentos',
                audience='familias, estudantes e egressos',
                request_channel='bot, secretaria presencial, email institucional ou portal',
                typical_eta='retorno em ate 2 dias uteis',
                notes='Usado para declaracoes, historico, transferencia, comprovantes, uniformes e orientacoes administrativas.',
            ),
            PublicServiceCatalogEntry(
                service_key='reuniao_coordenacao',
                title='Reuniao com coordenacao pedagogica',
                audience='familias e estudantes',
                request_channel='bot, secretaria ou portal',
                typical_eta='retorno em ate 2 dias uteis',
                notes='Usado para transicao de serie, adaptacao, rotina e acompanhamento escolar.',
            ),
            PublicServiceCatalogEntry(
                service_key='orientacao_educacional',
                title='Orientacao educacional e acompanhamento socioemocional',
                audience='familias e estudantes',
                request_channel='bot, orientacao educacional ou secretaria',
                typical_eta='retorno em ate 2 dias uteis',
                notes='Indicado para adaptacao escolar, convivencia, bem-estar, rotina de estudo e apoio a familias.',
            ),
            PublicServiceCatalogEntry(
                service_key='financeiro_escolar',
                title='Financeiro escolar e contratos',
                audience='responsaveis financeiros e familias',
                request_channel='bot, financeiro, portal autenticado ou email institucional',
                typical_eta='retorno em ate 1 dia util',
                notes='Atende boletos, vencimentos, contratos, acordos e esclarecimentos financeiros.',
            ),
            PublicServiceCatalogEntry(
                service_key='solicitacao_direcao',
                title='Solicitacao formal a direcao',
                audience='familias e comunidade escolar',
                request_channel='bot, ouvidoria ou protocolo institucional',
                typical_eta='protocolo imediato e triagem em ate 2 dias uteis',
                notes='Pedidos formais, elogios, sugestoes e manifestacoes que demandem leitura da direcao.',
            ),
            PublicServiceCatalogEntry(
                service_key='suporte_digital',
                title='Suporte de portal, acesso e atendimento digital',
                audience='familias, estudantes e professores',
                request_channel='bot, secretaria digital ou suporte digital',
                typical_eta='retorno em ate 1 dia util',
                notes='Indicado para portal escolar, acesso, senha, dificuldade com bot e orientacao sobre canais digitais.',
            ),
        ],
        documented_services=[
            'Secretaria presencial e digital',
            'Orientacao educacional',
            'Plantao de duvidas e monitorias',
            'Programa de acolhimento socioemocional',
            'Cantina com opcao de almoco supervisionado',
            'Biblioteca com estudo orientado',
        ],
        admissions_highlights=[
            'Atendimento comercial para visitas, apresentacao pedagogica e simulacao financeira.',
            'Descontos comerciais para irmaos e campanha de matricula antecipada conforme edital vigente.',
            'Matricula condicionada a analise documental, entrevista de acolhimento e assinatura contratual.',
        ],
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
