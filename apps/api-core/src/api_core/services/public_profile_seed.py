from __future__ import annotations

from decimal import Decimal

from api_core.contracts import (
    PublicAcademicPolicy,
    PublicAttendancePolicy,
    PublicContactChannel,
    PublicDocumentSubmissionPolicy,
    PublicFeatureAvailability,
    PublicHighlightEntry,
    PublicIntervalWindow,
    PublicKpiEntry,
    PublicLeadershipMember,
    PublicPassingPolicy,
    PublicSchoolProfile,
    PublicServiceCatalogEntry,
    PublicShiftOffer,
    PublicTuitionReference,
    PublicVisitOffer,
)


def _shift_offers() -> list[PublicShiftOffer]:
    return [
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
    ]


def _interval_schedule() -> list[PublicIntervalWindow]:
    return [
        PublicIntervalWindow(
            segment='Ensino Fundamental II',
            label='Intervalo da manha',
            starts_at='09:35',
            ends_at='09:55',
            notes='Janela publica de recreio e lanche do turno regular da manha.',
        ),
        PublicIntervalWindow(
            segment='Ensino Medio',
            label='Intervalo da manha',
            starts_at='09:40',
            ends_at='10:00',
            notes='Janela publica de intervalo do turno regular da manha.',
        ),
        PublicIntervalWindow(
            segment='Integral opcional',
            label='Pausa de almoco e convivio',
            starts_at='12:50',
            ends_at='13:40',
            notes='Os estudantes do integral fazem pausa maior para almoco e retorno ao contraturno.',
        ),
    ]


def _tuition_reference() -> list[PublicTuitionReference]:
    return [
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
    ]


def _contact_channels() -> list[PublicContactChannel]:
    return [
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
        PublicContactChannel(channel='email', label='Talentos', value='talentos@colegiohorizonte.edu.br'),
        PublicContactChannel(channel='instagram', label='Instagram institucional', value='@colegiohorizonte'),
    ]


def _feature_inventory() -> list[PublicFeatureAvailability]:
    return [
        PublicFeatureAvailability(feature_key='biblioteca', label='Biblioteca Aurora', category='service', available=True, notes='Atendimento ao publico de segunda a sexta, das 7h30 as 18h00.'),
        PublicFeatureAvailability(feature_key='laboratorio', label='Laboratorio de Ciencias', category='infrastructure', available=True, notes='Uso em aulas praticas, clubes de ciencias e mostras semestrais.'),
        PublicFeatureAvailability(feature_key='maker', label='Espaco Maker', category='infrastructure', available=True, notes='Ambiente de robotica, prototipagem leve e projetos interdisciplinares.'),
        PublicFeatureAvailability(feature_key='quadra', label='Quadra Poliesportiva Coberta', category='infrastructure', available=True, notes='Usada para educacao fisica, futsal, volei e eventos internos.'),
        PublicFeatureAvailability(feature_key='futebol', label='Futsal e treinos esportivos', category='activity', available=True, notes='Treinos no contraturno para Fundamental II e Ensino Medio.'),
        PublicFeatureAvailability(feature_key='volei', label='Volei escolar', category='activity', available=True, notes='Turmas mistas por faixa etaria no contraturno.'),
        PublicFeatureAvailability(feature_key='danca', label='Oficina de danca e expressao corporal', category='activity', available=True, notes='Oferta semestral no contraturno, vinculada ao programa cultural.'),
        PublicFeatureAvailability(feature_key='teatro', label='Oficina de teatro', category='activity', available=True, notes='Montagens anuais integradas ao projeto cultural.'),
        PublicFeatureAvailability(feature_key='academia', label='Academia', category='infrastructure', available=False, notes='A escola nao mantem academia própria aberta ao publico estudantil.'),
        PublicFeatureAvailability(feature_key='piscina', label='Piscina', category='infrastructure', available=False, notes='A escola nao possui piscina no campus atual.'),
        PublicFeatureAvailability(feature_key='quadra de tenis', label='Quadra de tenis', category='infrastructure', available=False, notes='A escola nao possui quadra de tenis dedicada.'),
        PublicFeatureAvailability(feature_key='cantina', label='Cantina e almoco supervisionado', category='service', available=True, notes='Cantina com lanches e almoco por adesao para estudantes de contraturno.'),
        PublicFeatureAvailability(feature_key='orientacao educacional', label='Orientacao educacional', category='service', available=True, notes='Acompanhamento socioemocional, mediacao escolar e apoio a familias.'),
    ]


def _leadership_team() -> list[PublicLeadershipMember]:
    return [
        PublicLeadershipMember(member_key='direcao_geral', name='Helena Martins', title='Diretora geral', focus='Governanca escolar, cultura institucional e relacionamento com familias.', contact_channel='direcao@colegiohorizonte.edu.br', notes='Atende por agenda institucional e participa dos encontros de familias a cada bimestre.'),
        PublicLeadershipMember(member_key='coordenacao_fundamental_ii', name='Ricardo Paiva', title='Coordenador do Ensino Fundamental II', focus='Acompanhamento pedagogico do 6o ao 9o ano, rotina escolar e projetos interdisciplinares.', contact_channel='fundamental2@colegiohorizonte.edu.br', notes='Conduz reunioes de acolhimento, acompanhamento de rotina e transicao para o Ensino Medio.'),
        PublicLeadershipMember(member_key='coordenacao_ensino_medio', name='Luciana Ferraz', title='Coordenadora do Ensino Medio', focus='Trilhas academicas, monitorias, projeto de vida e preparacao progressiva para vestibulares.', contact_channel='ensinomedio@colegiohorizonte.edu.br', notes='Responsavel pelos itinerarios eletivos, simulados e plantoes de monitoria.'),
    ]


def _public_kpis() -> list[PublicKpiEntry]:
    return [
        PublicKpiEntry(metric_key='aprovacao_geral', label='Aprovacao global', value=96.4, unit='%', reference_period='ano letivo 2025', notes='Indicador institucional consolidado do Fundamental II e Ensino Medio.'),
        PublicKpiEntry(metric_key='frequencia_media', label='Frequencia media', value=97.1, unit='%', reference_period='ano letivo 2025', notes='Media global de presenca nos componentes curriculares regulares.'),
        PublicKpiEntry(metric_key='familias_satisfeitas', label='Familias que avaliaram o atendimento como bom ou excelente', value=92.0, unit='%', reference_period='pesquisa institucional 2025', notes='Resultado agregado da pesquisa anual de experiencia com familias.'),
    ]


def _highlights() -> list[PublicHighlightEntry]:
    return [
        PublicHighlightEntry(highlight_key='tutoria_projeto_de_vida', title='Tutoria academica e projeto de vida', description='Cada estudante do Ensino Medio participa de trilhas de tutoria e planejamento academico com acompanhamento proximo ao longo do ano.', evidence_line='O contraturno combina monitorias, tutorias e trilhas eletivas acompanhadas por coordenacao e orientacao educacional.'),
        PublicHighlightEntry(highlight_key='maker_integrado', title='Espaco Maker integrado ao curriculo', description='O espaco maker nao funciona como atividade isolada; ele entra em projetos interdisciplinares de ciencias, tecnologia e cultura digital.', evidence_line='Projetos do Fundamental II e do Ensino Medio usam o maker como ambiente de prototipagem leve e experimentacao orientada.'),
        PublicHighlightEntry(highlight_key='acolhimento_familias', title='Acolhimento estruturado para familias e estudantes', description='A escola combina secretaria, orientacao educacional e coordenacao em uma jornada de acolhimento que inclui visita, entrevista e acompanhamento inicial.', evidence_line='Ha fluxo de visita institucional, apresentacao pedagogica e entrevista de acolhimento antes da confirmacao de matricula.'),
    ]


def _visit_offers() -> list[PublicVisitOffer]:
    return [
        PublicVisitOffer(offer_key='visita_terca_manha', title='Visita guiada ao campus', audience='familias interessadas', day_label='terca-feira', start_time='09:00', end_time='10:15', location='Recepcao principal e circuito pedagogico', notes='Inclui apresentacao institucional, visita aos espacos e conversa curta com admissions.'),
        PublicVisitOffer(offer_key='visita_quinta_tarde', title='Visita guiada com foco pedagogico', audience='familias interessadas', day_label='quinta-feira', start_time='14:30', end_time='15:45', location='Recepcao principal e salas de projeto', notes='Janela pensada para familias que desejam conhecer infraestrutura, rotina e proposta pedagogica.'),
    ]


def _service_catalog() -> list[PublicServiceCatalogEntry]:
    return [
        PublicServiceCatalogEntry(service_key='atendimento_admissoes', title='Matricula, bolsas e atendimento comercial', audience='familias interessadas e novas matriculas', request_channel='bot, admissions, whatsapp comercial ou visita guiada', typical_eta='retorno em ate 1 dia util', notes='Atende duvidas sobre processo de ingresso, documentos, bolsas, descontos e simulacao financeira inicial.'),
        PublicServiceCatalogEntry(service_key='visita_institucional', title='Agendamento de visita a escola', audience='publico geral', request_channel='bot, whatsapp comercial ou admissions', typical_eta='confirmacao em ate 1 dia util', notes='A equipe comercial confirma a data e envia orientacoes de chegada.'),
        PublicServiceCatalogEntry(service_key='secretaria_escolar', title='Secretaria escolar e documentos', audience='familias, estudantes e egressos', request_channel='bot, secretaria presencial, email institucional ou portal', typical_eta='retorno em ate 2 dias uteis', notes='Usado para declaracoes, historico, transferencia, comprovantes, uniformes e orientacoes administrativas. O envio inicial de documentos pode seguir pelo portal institucional ou pelo email da secretaria.'),
        PublicServiceCatalogEntry(service_key='reuniao_coordenacao', title='Reuniao com coordenacao pedagogica', audience='familias e estudantes', request_channel='bot, secretaria ou portal', typical_eta='retorno em ate 2 dias uteis', notes='Usado para transicao de serie, adaptacao, rotina e acompanhamento escolar.'),
        PublicServiceCatalogEntry(service_key='orientacao_educacional', title='Orientacao educacional e acompanhamento socioemocional', audience='familias e estudantes', request_channel='bot, orientacao educacional ou secretaria', typical_eta='retorno em ate 2 dias uteis', notes='Indicado para adaptacao escolar, convivencia, bem-estar, rotina de estudo e apoio a familias.'),
        PublicServiceCatalogEntry(service_key='financeiro_escolar', title='Financeiro escolar e contratos', audience='responsaveis financeiros e familias', request_channel='bot, financeiro, portal autenticado ou email institucional', typical_eta='retorno em ate 1 dia util', notes='Atende boletos, vencimentos, contratos, acordos e esclarecimentos financeiros.'),
        PublicServiceCatalogEntry(service_key='solicitacao_direcao', title='Solicitacao formal a direcao', audience='familias e comunidade escolar', request_channel='bot, ouvidoria ou protocolo institucional', typical_eta='protocolo imediato e triagem em ate 2 dias uteis', notes='Pedidos formais, elogios, sugestoes e manifestacoes que demandem leitura da direcao.'),
        PublicServiceCatalogEntry(service_key='suporte_digital', title='Suporte de portal, acesso e atendimento digital', audience='familias, estudantes e professores', request_channel='bot, secretaria digital ou suporte digital', typical_eta='retorno em ate 1 dia util', notes='Indicado para portal escolar, acesso, senha, dificuldade com bot e orientacao sobre canais digitais.'),
        PublicServiceCatalogEntry(service_key='carreiras_docentes', title='Trabalhe conosco e oportunidades docentes', audience='professores e profissionais da educacao', request_channel='email talentos@colegiohorizonte.edu.br', typical_eta='retorno em ate 5 dias uteis', notes='Recebe curriculos e orienta sobre processos seletivos quando houver vaga aberta.'),
    ]


def _document_submission_policy() -> PublicDocumentSubmissionPolicy:
    return PublicDocumentSubmissionPolicy(
        accepts_digital_submission=True,
        accepted_channels=['portal institucional', 'email da secretaria', 'secretaria presencial para conferencia final'],
        warning='O chat aberto nao deve receber documentos completos ou dados sensiveis. Quando possivel, use o portal autenticado ou o email institucional.',
        notes='No processo de matricula, o envio inicial pode ser digital. A validacao final continua com a secretaria.',
    )


def _academic_policy() -> PublicAcademicPolicy:
    return PublicAcademicPolicy(
        project_of_life_summary=(
            'Projeto de vida funciona como componente curricular e eixo de tutoria do Ensino Medio. '
            'Na pratica, o estudante trabalha autoconhecimento, planejamento academico, organizacao da rotina '
            'e acompanhamento tutorial ao longo do ano.'
        ),
        passing_policy=PublicPassingPolicy(
            passing_average=Decimal('7.0'),
            reference_scale='0-10',
            recovery_support=(
                'Quando a media fica abaixo da referencia, a escola combina monitorias, plantoes e orientacoes '
                'de recuperacao conforme o calendario pedagogico.'
            ),
            notes=(
                'A referencia publica de aprovacao usada nas orientacoes do colegio e 7,0, com fechamento final '
                'sempre acompanhado pela equipe pedagogica no periodo letivo.'
            ),
        ),
        attendance_policy=PublicAttendancePolicy(
            minimum_attendance_percent=Decimal('75.0'),
            first_absence_guidance=(
                'Uma falta isolada na primeira aula entra normalmente no registro de frequencia da disciplina. '
                'Dependendo da atividade do dia, o professor pode orientar recomposicao ou acompanhamento posterior.'
            ),
            chronic_absence_guidance=(
                'Se a frequencia de um componente cair abaixo de 75%, o estudante entra em alerta academico e a '
                'coordenacao pode acionar a familia. A permanencia abaixo desse limite pode comprometer a aprovacao '
                'por frequencia.'
            ),
            follow_up_channel='Coordenacao pedagogica e orientacao educacional',
            notes=(
                'A escola acompanha justificativas, recorrencia e necessidade de plano de recomposicao junto a '
                'familia e ao estudante.'
            ),
        ),
    )


def build_public_school_profile(*, code: str, name: str, city: str, state: str, timezone_name: str) -> PublicSchoolProfile:
    return PublicSchoolProfile(
        school_unit_code=code,
        school_name=name,
        city=city,
        state=state,
        timezone=timezone_name,
        address_line='Rua das Acacias, 1450',
        district='Vila Mariana',
        postal_code='04567-120',
        website_url='https://www.colegiohorizonte.edu.br',
        fax_number=None,
        short_headline='Escola laica com Ensino Fundamental II e Ensino Medio, acompanhamento tutorial e trilhas academicas no contraturno.',
        education_model='Projeto pedagogico laico, com foco em aprendizagem por projetos, cultura digital responsavel, acompanhamento socioemocional e preparacao academica progressiva.',
        curriculum_basis='A escola segue a BNCC e o curriculo do Ensino Medio articulado com projeto de vida, producao textual, cultura digital e aprofundamento academico progressivo.',
        curriculum_components=[
            'Lingua Portuguesa e producao textual',
            'Matematica',
            'Biologia',
            'Fisica',
            'Quimica',
            'Historia',
            'Geografia',
            'Lingua Inglesa',
            'Educacao Fisica',
            'Projeto de vida',
            'Trilhas eletivas e monitorias no contraturno',
        ],
        confessional_status='laica',
        segments=['Ensino Fundamental II (6o ao 9o ano)', 'Ensino Medio (1a a 3a serie)'],
        shift_offers=_shift_offers(),
        interval_schedule=_interval_schedule(),
        tuition_reference=_tuition_reference(),
        contact_channels=_contact_channels(),
        feature_inventory=_feature_inventory(),
        leadership_team=_leadership_team(),
        public_kpis=_public_kpis(),
        highlights=_highlights(),
        visit_offers=_visit_offers(),
        service_catalog=_service_catalog(),
        document_submission_policy=_document_submission_policy(),
        academic_policy=_academic_policy(),
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
        admissions_required_documents=[
            'Formulario cadastral preenchido',
            'Documento de identificacao do aluno',
            'CPF do aluno, quando houver',
            'Historico escolar',
            'Comprovante de residencia atualizado',
            'Documento de identificacao do responsavel legal',
        ],
    )
