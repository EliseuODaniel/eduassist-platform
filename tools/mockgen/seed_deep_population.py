from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

from api_core.db.models import (
    AccessDecision,
    AuditEvent,
    Class,
    Conversation,
    Document,
    DocumentChunk,
    DocumentSet,
    DocumentVersion,
    FederatedIdentity,
    Handoff,
    InstitutionalRequest,
    Message,
    RetrievalLabel,
    SchoolUnit,
    Subject,
    Teacher,
    TeacherAssignment,
    TelegramLinkChallenge,
    ToolCall,
    User,
    VisitBooking,
)
from api_core.db.session import session_scope
from seed_school_expansion import (
    TZ,
    ensure_assignment,
    ensure_attendance,
    ensure_calendar_event,
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
    ensure_user,
)


KEYCLOAK_PROVIDER = 'keycloak'
ACADEMIC_YEAR = 2026

SUBJECT_TEACHER_FALLBACK = {
    'MAT': 'USR-TEACH-001',
    'POR': 'USR-TEACH-002',
    'CIE': 'USR-TEACH-003',
    'FIS': 'USR-TEACH-003',
    'QUI': 'USR-TEACH-003',
    'BIO': 'USR-TEACH-003',
    'HIS': 'USR-TEACH-004',
    'GEO': 'USR-TEACH-004',
    'ING': 'USR-TEACH-005',
}

DEEP_SUPPORT_USERS = [
    {
        'external_code': 'USR-ADMIN-001',
        'role_code': 'admin',
        'full_name': 'Leonardo Pires',
        'email': 'leonardo.pires@mock.eduassist.local',
        'phone': '+55 11 95555-4005',
        'is_staff': True,
        'subject': '120d83cd-c3e5-511b-b826-4d4b5722ad69',
        'username': 'leonardo.pires',
    },
    {
        'external_code': 'USR-FIN-002',
        'role_code': 'finance',
        'full_name': 'Vinicius Prado',
        'email': 'vinicius.prado@mock.eduassist.local',
        'phone': '+55 11 95555-4012',
        'is_staff': True,
        'subject': '290dd0e5-34eb-5517-8481-efb019f843fd',
        'username': 'vinicius.prado',
    },
    {
        'external_code': 'USR-STAFF-002',
        'role_code': 'staff',
        'full_name': 'Priscila Almeida',
        'email': 'priscila.almeida@mock.eduassist.local',
        'phone': '+55 11 95555-4006',
        'is_staff': True,
        'subject': 'c6af06db-01a7-51c7-9acf-73cd35388b9f',
        'username': 'priscila.almeida',
    },
    {
        'external_code': 'USR-STAFF-003',
        'role_code': 'staff',
        'full_name': 'Renato Barros',
        'email': 'renato.barros@mock.eduassist.local',
        'phone': '+55 11 95555-4007',
        'is_staff': True,
        'subject': '315f85c3-7f35-54ff-8c6e-0b58c99a5ee0',
        'username': 'renato.barros',
    },
]

DEEP_GUARDIANS = [
    {
        'external_code': 'USR-GUARD-101',
        'full_name': 'Camila Duarte',
        'email': 'camila.duarte.family@mock.eduassist.local',
        'phone': '+55 11 98888-2101',
        'relationship_label': 'responsavel',
        'cpf_masked': '***.111.201-**',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b1101',
        'username': 'camila.duarte',
        'children': ['USR-STUD-101', 'USR-STUD-102'],
    },
    {
        'external_code': 'USR-GUARD-102',
        'full_name': 'Renata Lima',
        'email': 'renata.lima.family@mock.eduassist.local',
        'phone': '+55 11 98888-2102',
        'relationship_label': 'responsavel',
        'cpf_masked': '***.111.202-**',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b1102',
        'username': 'renata.lima',
        'children': ['USR-STUD-103', 'USR-STUD-104'],
    },
    {
        'external_code': 'USR-GUARD-103',
        'full_name': 'Diego Moreira',
        'email': 'diego.moreira.family@mock.eduassist.local',
        'phone': '+55 11 98888-2103',
        'relationship_label': 'responsavel',
        'cpf_masked': '***.111.203-**',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b1103',
        'username': 'diego.moreira',
        'children': ['USR-STUD-105', 'USR-STUD-106'],
    },
    {
        'external_code': 'USR-GUARD-104',
        'full_name': 'Teresa Almeida',
        'email': 'teresa.almeida.family@mock.eduassist.local',
        'phone': '+55 11 98888-2104',
        'relationship_label': 'responsavel',
        'cpf_masked': '***.111.204-**',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b1104',
        'username': 'teresa.almeida',
        'children': ['USR-STUD-107', 'USR-STUD-108'],
    },
    {
        'external_code': 'USR-GUARD-105',
        'full_name': 'Fabio Martins',
        'email': 'fabio.martins.family@mock.eduassist.local',
        'phone': '+55 11 98888-2105',
        'relationship_label': 'responsavel',
        'cpf_masked': '***.111.205-**',
        'subject': '9d7f1f4a-8c5d-4b14-8a61-5d7c1e8b1105',
        'username': 'fabio.martins',
        'children': ['USR-STUD-109', 'USR-STUD-110', 'USR-STUD-111'],
    },
]

DEEP_STUDENTS = [
    {
        'external_code': 'USR-STUD-101',
        'full_name': 'Sofia Duarte',
        'email': 'sofia.duarte@mock.eduassist.local',
        'phone': '+55 11 97777-3101',
        'enrollment_code': 'MAT-2026-101',
        'birth_date': date(2014, 4, 18),
        'current_grade_level': 6,
        'class_code': '6EF-A',
        'contract_amount': Decimal('890.00'),
        'subject_scores': {'MAT': Decimal('8.9'), 'POR': Decimal('8.6'), 'CIE': Decimal('9.1'), 'ING': Decimal('8.4')},
    },
    {
        'external_code': 'USR-STUD-102',
        'full_name': 'Julia Duarte',
        'email': 'julia.duarte@mock.eduassist.local',
        'phone': '+55 11 97777-3102',
        'enrollment_code': 'MAT-2026-102',
        'birth_date': date(2014, 9, 6),
        'current_grade_level': 6,
        'class_code': '6EF-A',
        'contract_amount': Decimal('890.00'),
        'subject_scores': {'MAT': Decimal('8.2'), 'POR': Decimal('8.8'), 'CIE': Decimal('8.5'), 'ING': Decimal('8.9')},
    },
    {
        'external_code': 'USR-STUD-103',
        'full_name': 'Miguel Lima',
        'email': 'miguel.lima@mock.eduassist.local',
        'phone': '+55 11 97777-3103',
        'enrollment_code': 'MAT-2026-103',
        'birth_date': date(2013, 7, 15),
        'current_grade_level': 7,
        'class_code': '7EF-A',
        'contract_amount': Decimal('910.00'),
        'subject_scores': {'MAT': Decimal('7.8'), 'POR': Decimal('8.1'), 'CIE': Decimal('7.9'), 'ING': Decimal('8.0')},
    },
    {
        'external_code': 'USR-STUD-104',
        'full_name': 'Rafaela Lima',
        'email': 'rafaela.lima@mock.eduassist.local',
        'phone': '+55 11 97777-3104',
        'enrollment_code': 'MAT-2026-104',
        'birth_date': date(2013, 11, 2),
        'current_grade_level': 7,
        'class_code': '7EF-A',
        'contract_amount': Decimal('910.00'),
        'subject_scores': {'MAT': Decimal('8.7'), 'POR': Decimal('8.4'), 'CIE': Decimal('8.6'), 'ING': Decimal('8.5')},
    },
    {
        'external_code': 'USR-STUD-105',
        'full_name': 'Helena Moreira',
        'email': 'helena.moreira@mock.eduassist.local',
        'phone': '+55 11 97777-3105',
        'enrollment_code': 'MAT-2026-105',
        'birth_date': date(2012, 3, 25),
        'current_grade_level': 8,
        'class_code': '8EF-A',
        'contract_amount': Decimal('930.00'),
        'subject_scores': {'MAT': Decimal('7.4'), 'POR': Decimal('8.0'), 'CIE': Decimal('7.7'), 'ING': Decimal('8.2')},
    },
    {
        'external_code': 'USR-STUD-106',
        'full_name': 'Enzo Moreira',
        'email': 'enzo.moreira@mock.eduassist.local',
        'phone': '+55 11 97777-3106',
        'enrollment_code': 'MAT-2026-106',
        'birth_date': date(2012, 8, 14),
        'current_grade_level': 8,
        'class_code': '8EF-A',
        'contract_amount': Decimal('930.00'),
        'subject_scores': {'MAT': Decimal('8.5'), 'POR': Decimal('8.1'), 'CIE': Decimal('8.3'), 'ING': Decimal('8.0')},
    },
    {
        'external_code': 'USR-STUD-107',
        'full_name': 'Pedro Almeida',
        'email': 'pedro.almeida@mock.eduassist.local',
        'phone': '+55 11 97777-3107',
        'enrollment_code': 'MAT-2026-107',
        'birth_date': date(2011, 5, 10),
        'current_grade_level': 9,
        'class_code': '9EF-A',
        'contract_amount': Decimal('950.00'),
        'subject_scores': {'MAT': Decimal('8.9'), 'POR': Decimal('8.2'), 'CIE': Decimal('8.8'), 'ING': Decimal('8.6')},
    },
    {
        'external_code': 'USR-STUD-108',
        'full_name': 'Laura Almeida',
        'email': 'laura.almeida@mock.eduassist.local',
        'phone': '+55 11 97777-3108',
        'enrollment_code': 'MAT-2026-108',
        'birth_date': date(2011, 12, 1),
        'current_grade_level': 9,
        'class_code': '9EF-A',
        'contract_amount': Decimal('950.00'),
        'subject_scores': {'MAT': Decimal('8.1'), 'POR': Decimal('8.7'), 'CIE': Decimal('8.4'), 'ING': Decimal('8.9')},
    },
    {
        'external_code': 'USR-STUD-109',
        'full_name': 'Theo Martins',
        'email': 'theo.martins@mock.eduassist.local',
        'phone': '+55 11 97777-3109',
        'enrollment_code': 'MAT-2026-109',
        'birth_date': date(2009, 4, 30),
        'current_grade_level': 2,
        'class_code': '2EM-A',
        'contract_amount': Decimal('1490.00'),
        'subject_scores': {'MAT': Decimal('7.9'), 'POR': Decimal('8.4'), 'HIS': Decimal('8.0'), 'ING': Decimal('8.7')},
    },
    {
        'external_code': 'USR-STUD-110',
        'full_name': 'Bianca Martins',
        'email': 'bianca.martins@mock.eduassist.local',
        'phone': '+55 11 97777-3110',
        'enrollment_code': 'MAT-2026-110',
        'birth_date': date(2008, 8, 9),
        'current_grade_level': 3,
        'class_code': '3EM-A',
        'contract_amount': None,
        'subject_scores': {},
    },
    {
        'external_code': 'USR-STUD-111',
        'full_name': 'Amanda Martins',
        'email': 'amanda.martins@mock.eduassist.local',
        'phone': '+55 11 97777-3111',
        'enrollment_code': 'MAT-2026-111',
        'birth_date': date(2008, 10, 27),
        'current_grade_level': 3,
        'class_code': '3EM-A',
        'contract_amount': None,
        'subject_scores': {},
    },
]

DEEP_DOCUMENTS = [
    {
        'set_slug': 'family-services-public',
        'set_title': 'Guias Publicos de Atendimento Familiar',
        'visibility': 'public',
        'title': 'Guia rapido de rematricula',
        'category': 'secretaria',
        'audience': 'familias',
        'chunks': [
            (
                'A rematricula de alunos veteranos exige revisao cadastral, confirmacao contratual e verificacao de eventuais pendencias. '
                'A reserva de vaga depende do cumprimento da janela administrativa divulgada pela escola.'
            ),
            (
                'Quando a familia precisa de apoio da secretaria, o canal digital pode registrar protocolo e orientar os documentos basicos. '
                'Mudancas de responsavel, contato de emergencia ou endereco devem ser formalizadas.'
            ),
        ],
        'labels': ['rematricula', 'secretaria', 'cadastro'],
    },
    {
        'set_slug': 'family-services-public',
        'set_title': 'Guias Publicos de Atendimento Familiar',
        'visibility': 'public',
        'title': 'Politica publica de segunda chamada',
        'category': 'academic',
        'audience': 'familias',
        'chunks': [
            (
                'Pedidos de segunda chamada devem ser registrados no prazo institucional e podem exigir comprovacao de saude ou justificativa formal. '
                'A analise considera o motivo apresentado e o tipo de atividade avaliativa.'
            ),
            (
                'A secretaria ou a coordenacao informam a familia sobre a decisao e, quando necessario, sobre a data reagendada. '
                'O canal automatico pode orientar o fluxo, mas nao substitui o registro do pedido.'
            ),
        ],
        'labels': ['segunda chamada', 'avaliacao', 'saude'],
    },
    {
        'set_slug': 'school-internal-operations',
        'set_title': 'Playbooks Internos de Operacao Escolar',
        'visibility': 'restricted',
        'title': 'Playbook interno de negociacao financeira',
        'category': 'finance',
        'audience': 'staff',
        'chunks': [
            (
                'Casos de inadimplencia parcial devem ser tratados pelo financeiro com registro de saldo, historico de contato e proposta formal. '
                'A equipe avalia pagamento ja realizado, risco de reincidencia e necessidade de encaminhamento administrativo.'
            ),
            (
                'O bot pode abrir handoff para a fila financeira, mas nao define condicoes comerciais sozinho. '
                'Negociacao, concessao excepcional e cancelamento de multa exigem operador autorizado.'
            ),
        ],
        'labels': ['financeiro', 'negociacao', 'handoff'],
    },
    {
        'set_slug': 'school-internal-operations',
        'set_title': 'Playbooks Internos de Operacao Escolar',
        'visibility': 'restricted',
        'title': 'Roteiro interno de acolhimento do 6o ano',
        'category': 'operations',
        'audience': 'staff',
        'chunks': [
            (
                'O acolhimento do 6o ano inclui orientacao de rotina, integracao com familias, apresentacao de canais oficiais e reforco das regras de convivencia. '
                'A equipe registra ajustes de turma, observacoes de adaptacao e demandas de acompanhamento.'
            ),
            (
                'Questes recorrentes sobre horario, materiais, retirada e adaptacao sao respondidas com base no guia publico. '
                'Quando houver caso individual sensivel, o atendimento deve abrir protocolo com a coordenacao ou a secretaria.'
            ),
        ],
        'labels': ['acolhimento', '6o ano', 'operacao'],
    },
]


def _set_timestamps(record, *, created_at: datetime, updated_at: datetime | None = None) -> None:
    record.created_at = created_at
    record.updated_at = updated_at or created_at


def ensure_federated_identity(
    session,
    *,
    user_id,
    provider: str,
    subject: str,
    username: str,
    email: str,
) -> FederatedIdentity:
    identity = session.scalar(
        select(FederatedIdentity).where(
            FederatedIdentity.user_id == user_id,
            FederatedIdentity.provider == provider,
        )
    )
    if identity is None:
        identity = FederatedIdentity(
            user_id=user_id,
            provider=provider,
            subject=subject,
            username=username,
            email=email,
            email_verified=True,
        )
        session.add(identity)
    else:
        identity.subject = subject
        identity.username = username
        identity.email = email
        identity.email_verified = True
    session.flush()
    return identity


def ensure_telegram_link_challenge(
    session,
    *,
    user_id,
    code_hash: str,
    expires_at: datetime,
    consumed_at: datetime | None,
    purpose: str = 'telegram_link',
) -> TelegramLinkChallenge:
    challenge = session.scalar(
        select(TelegramLinkChallenge).where(TelegramLinkChallenge.code_hash == code_hash)
    )
    if challenge is None:
        challenge = TelegramLinkChallenge(
            user_id=user_id,
            code_hash=code_hash,
            expires_at=expires_at,
            consumed_at=consumed_at,
            purpose=purpose,
        )
        session.add(challenge)
    else:
        challenge.user_id = user_id
        challenge.expires_at = expires_at
        challenge.consumed_at = consumed_at
        challenge.purpose = purpose
    session.flush()
    return challenge


def ensure_document_set(
    session,
    *,
    slug: str,
    title: str,
    visibility: str,
) -> DocumentSet:
    document_set = session.scalar(select(DocumentSet).where(DocumentSet.slug == slug))
    if document_set is None:
        document_set = DocumentSet(slug=slug, title=title, visibility=visibility)
        session.add(document_set)
    else:
        document_set.title = title
        document_set.visibility = visibility
    session.flush()
    return document_set


def ensure_document(
    session,
    *,
    document_set_id,
    title: str,
    category: str,
    audience: str,
    visibility: str,
) -> Document:
    document = session.scalar(
        select(Document).where(
            Document.document_set_id == document_set_id,
            Document.title == title,
        )
    )
    if document is None:
        document = Document(
            document_set_id=document_set_id,
            title=title,
            category=category,
            audience=audience,
            visibility=visibility,
        )
        session.add(document)
    else:
        document.category = category
        document.audience = audience
        document.visibility = visibility
    session.flush()
    return document


def ensure_document_version(
    session,
    *,
    document_id,
    version_label: str,
    storage_path: str,
    mime_type: str,
    effective_from: date,
) -> DocumentVersion:
    version = session.scalar(
        select(DocumentVersion).where(
            DocumentVersion.document_id == document_id,
            DocumentVersion.version_label == version_label,
        )
    )
    if version is None:
        version = DocumentVersion(
            document_id=document_id,
            version_label=version_label,
            storage_path=storage_path,
            mime_type=mime_type,
            effective_from=effective_from,
        )
        session.add(version)
    else:
        version.storage_path = storage_path
        version.mime_type = mime_type
        version.effective_from = effective_from
        version.effective_to = None
    session.flush()
    return version


def ensure_document_chunk(
    session,
    *,
    document_version_id,
    chunk_index: int,
    text_content: str,
    contextual_summary: str,
    visibility: str,
) -> DocumentChunk:
    chunk = session.scalar(
        select(DocumentChunk).where(
            DocumentChunk.document_version_id == document_version_id,
            DocumentChunk.chunk_index == chunk_index,
        )
    )
    if chunk is None:
        chunk = DocumentChunk(
            document_version_id=document_version_id,
            chunk_index=chunk_index,
            text_content=text_content,
            contextual_summary=contextual_summary,
            visibility=visibility,
        )
        session.add(chunk)
    else:
        chunk.text_content = text_content
        chunk.contextual_summary = contextual_summary
        chunk.visibility = visibility
    session.flush()
    return chunk


def ensure_retrieval_label(session, *, document_chunk_id, label_type: str, label_value: str) -> RetrievalLabel:
    label = session.scalar(
        select(RetrievalLabel).where(
            RetrievalLabel.document_chunk_id == document_chunk_id,
            RetrievalLabel.label_type == label_type,
            RetrievalLabel.label_value == label_value,
        )
    )
    if label is None:
        label = RetrievalLabel(
            document_chunk_id=document_chunk_id,
            label_type=label_type,
            label_value=label_value,
        )
        session.add(label)
        session.flush()
    return label


def ensure_conversation(
    session,
    *,
    external_thread_id: str,
    user_id,
    status: str,
    created_at: datetime,
    updated_at: datetime,
) -> Conversation:
    conversation = session.scalar(
        select(Conversation).where(Conversation.external_thread_id == external_thread_id)
    )
    if conversation is None:
        conversation = Conversation(
            user_id=user_id,
            channel='telegram',
            external_thread_id=external_thread_id,
            status=status,
        )
        session.add(conversation)
    else:
        conversation.user_id = user_id
        conversation.status = status
    session.flush()
    _set_timestamps(conversation, created_at=created_at, updated_at=updated_at)
    return conversation


def ensure_message(
    session,
    *,
    conversation_id,
    sender_type: str,
    content: str,
    created_at: datetime,
) -> Message:
    message = session.scalar(
        select(Message).where(
            Message.conversation_id == conversation_id,
            Message.sender_type == sender_type,
            Message.content == content,
        )
    )
    if message is None:
        message = Message(
            conversation_id=conversation_id,
            sender_type=sender_type,
            content=content,
        )
        session.add(message)
    session.flush()
    _set_timestamps(message, created_at=created_at, updated_at=created_at)
    return message


def ensure_tool_call(
    session,
    *,
    conversation_id,
    tool_name: str,
    status: str,
    request_payload: dict,
    response_payload: dict,
    created_at: datetime,
) -> ToolCall:
    tool_call = session.scalar(
        select(ToolCall).where(
            ToolCall.conversation_id == conversation_id,
            ToolCall.tool_name == tool_name,
        )
    )
    if tool_call is None:
        tool_call = ToolCall(
            conversation_id=conversation_id,
            tool_name=tool_name,
            status=status,
            request_payload=request_payload,
            response_payload=response_payload,
        )
        session.add(tool_call)
    else:
        tool_call.status = status
        tool_call.request_payload = request_payload
        tool_call.response_payload = response_payload
    session.flush()
    _set_timestamps(tool_call, created_at=created_at, updated_at=created_at)
    return tool_call


def ensure_handoff(
    session,
    *,
    conversation_id,
    queue_name: str,
    priority_code: str,
    assigned_user_id,
    assigned_at: datetime | None,
    response_due_at: datetime | None,
    resolution_due_at: datetime | None,
    status: str,
    summary: str,
    created_at: datetime,
    updated_at: datetime,
) -> Handoff:
    handoff = session.scalar(
        select(Handoff).where(
            Handoff.conversation_id == conversation_id,
            Handoff.queue_name == queue_name,
        )
    )
    if handoff is None:
        handoff = Handoff(
            conversation_id=conversation_id,
            queue_name=queue_name,
            priority_code=priority_code,
            assigned_user_id=assigned_user_id,
            assigned_at=assigned_at,
            response_due_at=response_due_at,
            resolution_due_at=resolution_due_at,
            status=status,
            summary=summary,
        )
        session.add(handoff)
    else:
        handoff.priority_code = priority_code
        handoff.assigned_user_id = assigned_user_id
        handoff.assigned_at = assigned_at
        handoff.response_due_at = response_due_at
        handoff.resolution_due_at = resolution_due_at
        handoff.status = status
        handoff.summary = summary
    session.flush()
    _set_timestamps(handoff, created_at=created_at, updated_at=updated_at)
    return handoff


def ensure_visit_booking(
    session,
    *,
    conversation_id,
    requester_user_id,
    linked_handoff_id,
    protocol_code: str,
    status: str,
    audience_name: str,
    audience_contact: str,
    interested_segment: str,
    preferred_date: date,
    preferred_window: str,
    attendee_count: int,
    slot_label: str,
    notes: str,
    created_at: datetime,
) -> VisitBooking:
    booking = session.scalar(select(VisitBooking).where(VisitBooking.protocol_code == protocol_code))
    if booking is None:
        booking = VisitBooking(
            conversation_id=conversation_id,
            requester_user_id=requester_user_id,
            linked_handoff_id=linked_handoff_id,
            protocol_code=protocol_code,
            status=status,
            audience_name=audience_name,
            audience_contact=audience_contact,
            interested_segment=interested_segment,
            preferred_date=preferred_date,
            preferred_window=preferred_window,
            attendee_count=attendee_count,
            slot_label=slot_label,
            notes=notes,
        )
        session.add(booking)
    else:
        booking.conversation_id = conversation_id
        booking.requester_user_id = requester_user_id
        booking.linked_handoff_id = linked_handoff_id
        booking.status = status
        booking.audience_name = audience_name
        booking.audience_contact = audience_contact
        booking.interested_segment = interested_segment
        booking.preferred_date = preferred_date
        booking.preferred_window = preferred_window
        booking.attendee_count = attendee_count
        booking.slot_label = slot_label
        booking.notes = notes
    session.flush()
    _set_timestamps(booking, created_at=created_at, updated_at=created_at)
    return booking


def ensure_institutional_request(
    session,
    *,
    conversation_id,
    requester_user_id,
    linked_handoff_id,
    protocol_code: str,
    target_area: str,
    category: str,
    subject: str,
    details: str,
    requester_contact: str,
    status: str,
    created_at: datetime,
) -> InstitutionalRequest:
    request = session.scalar(
        select(InstitutionalRequest).where(InstitutionalRequest.protocol_code == protocol_code)
    )
    if request is None:
        request = InstitutionalRequest(
            conversation_id=conversation_id,
            requester_user_id=requester_user_id,
            linked_handoff_id=linked_handoff_id,
            protocol_code=protocol_code,
            target_area=target_area,
            category=category,
            subject=subject,
            details=details,
            requester_contact=requester_contact,
            status=status,
        )
        session.add(request)
    else:
        request.conversation_id = conversation_id
        request.requester_user_id = requester_user_id
        request.linked_handoff_id = linked_handoff_id
        request.target_area = target_area
        request.category = category
        request.subject = subject
        request.details = details
        request.requester_contact = requester_contact
        request.status = status
    session.flush()
    _set_timestamps(request, created_at=created_at, updated_at=created_at)
    return request


def ensure_audit_event(
    session,
    *,
    actor_user_id,
    event_type: str,
    resource_type: str,
    resource_id: str,
    metadata: dict,
    occurred_at: datetime,
) -> AuditEvent:
    event = session.scalar(
        select(AuditEvent).where(
            AuditEvent.actor_user_id == actor_user_id,
            AuditEvent.event_type == event_type,
            AuditEvent.resource_type == resource_type,
            AuditEvent.resource_id == resource_id,
        )
    )
    if event is None:
        event = AuditEvent(
            actor_user_id=actor_user_id,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata_json=metadata,
        )
        session.add(event)
    else:
        event.metadata_json = metadata
    session.flush()
    _set_timestamps(event, created_at=occurred_at, updated_at=occurred_at)
    return event


def ensure_access_decision(
    session,
    *,
    actor_user_id,
    resource_type: str,
    action: str,
    decision: str,
    reason: str,
    occurred_at: datetime,
) -> AccessDecision:
    access = session.scalar(
        select(AccessDecision).where(
            AccessDecision.actor_user_id == actor_user_id,
            AccessDecision.resource_type == resource_type,
            AccessDecision.action == action,
            AccessDecision.reason == reason,
        )
    )
    if access is None:
        access = AccessDecision(
            actor_user_id=actor_user_id,
            resource_type=resource_type,
            action=action,
            decision=decision,
            reason=reason,
        )
        session.add(access)
    else:
        access.decision = decision
    session.flush()
    _set_timestamps(access, created_at=occurred_at, updated_at=occurred_at)
    return access


def resolve_assignment(session, *, class_id, class_code: str, subject_id, subject_code: str, teacher_map: dict[str, Teacher]) -> TeacherAssignment:
    assignment = session.scalar(
        select(TeacherAssignment).where(
            TeacherAssignment.class_id == class_id,
            TeacherAssignment.subject_id == subject_id,
            TeacherAssignment.academic_year == ACADEMIC_YEAR,
        )
    )
    if assignment is not None:
        return assignment

    teacher_code = SUBJECT_TEACHER_FALLBACK[subject_code]
    teacher = teacher_map[teacher_code]
    return ensure_assignment(
        session,
        teacher_id=teacher.id,
        class_id=class_id,
        subject_id=subject_id,
        academic_year=ACADEMIC_YEAR,
    )


def seed_documents(session) -> int:
    inserted = 0
    for doc_seed in DEEP_DOCUMENTS:
        document_set = ensure_document_set(
            session,
            slug=doc_seed['set_slug'],
            title=doc_seed['set_title'],
            visibility=doc_seed['visibility'],
        )
        document = ensure_document(
            session,
            document_set_id=document_set.id,
            title=doc_seed['title'],
            category=doc_seed['category'],
            audience=doc_seed['audience'],
            visibility=doc_seed['visibility'],
        )
        version = ensure_document_version(
            session,
            document_id=document.id,
            version_label='v2026.3',
            storage_path=f"minio://seed/{doc_seed['set_slug']}/{document.title.lower().replace(' ', '-')}.md",
            mime_type='text/markdown',
            effective_from=date(2026, 3, 31),
        )
        for index, chunk_text in enumerate(doc_seed['chunks']):
            chunk = ensure_document_chunk(
                session,
                document_version_id=version.id,
                chunk_index=index,
                text_content=chunk_text,
                contextual_summary=doc_seed['title'],
                visibility=doc_seed['visibility'],
            )
            ensure_retrieval_label(session, document_chunk_id=chunk.id, label_type='document', label_value=document.title)
            for label in doc_seed['labels']:
                ensure_retrieval_label(session, document_chunk_id=chunk.id, label_type='topic', label_value=label)
        inserted += 1
    return inserted


def seed_operational_scenarios(session, *, users: dict[str, User]) -> int:
    now = datetime(2026, 3, 31, 15, 0, tzinfo=UTC)
    inserted = 0

    conversation = ensure_conversation(
        session,
        external_thread_id='deep-seed-rematricula-001',
        user_id=users['USR-GUARD-101'].id,
        status='open',
        created_at=now - timedelta(days=2),
        updated_at=now - timedelta(days=2, minutes=-5),
    )
    ensure_message(
        session,
        conversation_id=conversation.id,
        sender_type='user',
        content='Quais documentos faltam para concluir a rematricula das meninas?',
        created_at=now - timedelta(days=2),
    )
    ensure_message(
        session,
        conversation_id=conversation.id,
        sender_type='assistant',
        content='Posso orientar a lista publica e, se necessario, abrir protocolo com a secretaria.',
        created_at=now - timedelta(days=2) + timedelta(minutes=1),
    )
    ensure_tool_call(
        session,
        conversation_id=conversation.id,
        tool_name='search_public_documents',
        status='completed',
        request_payload={'topic': 'rematricula'},
        response_payload={'documents': ['Guia rapido de rematricula']},
        created_at=now - timedelta(days=2) + timedelta(minutes=1),
    )

    finance_created_at = now - timedelta(days=1, hours=3)
    finance_conversation = ensure_conversation(
        session,
        external_thread_id='deep-seed-negociacao-001',
        user_id=users['USR-GUARD-103'].id,
        status='open',
        created_at=finance_created_at,
        updated_at=finance_created_at + timedelta(hours=1),
    )
    ensure_message(
        session,
        conversation_id=finance_conversation.id,
        sender_type='user',
        content='Quero entender se posso parcelar o saldo deste mes.',
        created_at=finance_created_at,
    )
    ensure_message(
        session,
        conversation_id=finance_conversation.id,
        sender_type='assistant',
        content='Vou registrar o caso para o financeiro avaliar a melhor alternativa.',
        created_at=finance_created_at + timedelta(minutes=2),
    )
    handoff = ensure_handoff(
        session,
        conversation_id=finance_conversation.id,
        queue_name='financeiro',
        priority_code='high',
        assigned_user_id=users['USR-FIN-002'].id,
        assigned_at=finance_created_at + timedelta(minutes=20),
        response_due_at=finance_created_at + timedelta(hours=1),
        resolution_due_at=finance_created_at + timedelta(hours=12),
        status='in_progress',
        summary='Responsavel pediu orientacao sobre parcelamento do saldo da mensalidade.',
        created_at=finance_created_at,
        updated_at=finance_created_at + timedelta(minutes=20),
    )
    ensure_audit_event(
        session,
        actor_user_id=users['USR-GUARD-103'].id,
        event_type='support_handoff.created',
        resource_type='support_handoff',
        resource_id=str(handoff.id),
        metadata={'queue_name': 'financeiro', 'priority_code': 'high'},
        occurred_at=finance_created_at,
    )
    ensure_access_decision(
        session,
        actor_user_id=users['USR-GUARD-103'].id,
        resource_type='financial_summary',
        action='read',
        decision='allow',
        reason='guardian_link_finance_scope',
        occurred_at=finance_created_at,
    )

    visit_created_at = now - timedelta(hours=16)
    visit_conversation = ensure_conversation(
        session,
        external_thread_id='deep-seed-acolhimento-001',
        user_id=users['USR-GUARD-101'].id,
        status='open',
        created_at=visit_created_at,
        updated_at=visit_created_at + timedelta(minutes=15),
    )
    ensure_message(
        session,
        conversation_id=visit_conversation.id,
        sender_type='user',
        content='Quero confirmar como funciona o acolhimento do 6o ano.',
        created_at=visit_created_at,
    )
    ensure_message(
        session,
        conversation_id=visit_conversation.id,
        sender_type='assistant',
        content='Posso explicar a rotina publica e registrar uma visita institucional, se voce quiser.',
        created_at=visit_created_at + timedelta(minutes=2),
    )
    ensure_visit_booking(
        session,
        conversation_id=visit_conversation.id,
        requester_user_id=users['USR-GUARD-101'].id,
        linked_handoff_id=None,
        protocol_code='VIS-20260329-0101',
        status='requested',
        audience_name='Camila Duarte',
        audience_contact='camila.duarte.family@mock.eduassist.local',
        interested_segment='fundamental II',
        preferred_date=date(2026, 4, 6),
        preferred_window='manha',
        attendee_count=2,
        slot_label='acolhimento 6o ano',
        notes='Familia quer conhecer detalhes da rotina e do acolhimento inicial.',
        created_at=visit_created_at + timedelta(minutes=5),
    )
    inserted += 3
    return inserted


def main() -> None:
    with session_scope() as session:
        unit = session.scalar(select(SchoolUnit).where(SchoolUnit.code == 'HZ-CAMPUS'))
        if unit is None:
            raise SystemExit('foundation seed missing; run make db-seed-foundation first')

        existing_marker = session.scalar(
            select(User).where(User.external_code == 'USR-GUARD-101')
        )
        if existing_marker is not None:
            print('deep population seed already present; skipping')
            return

        for code, name, area, weekly_hours in [
            ('MAT', 'Matematica', 'Exatas', Decimal('4.0')),
            ('POR', 'Portugues', 'Linguagens', Decimal('4.0')),
            ('CIE', 'Ciencias', 'Natureza', Decimal('3.0')),
            ('ING', 'Ingles', 'Linguagens', Decimal('2.0')),
            ('HIS', 'Historia', 'Humanidades', Decimal('2.0')),
        ]:
            ensure_subject(session, code=code, name=name, area=area, weekly_hours=weekly_hours)

        users: dict[str, User] = {}
        guardians_by_code = {}

        for payload in DEEP_SUPPORT_USERS:
            user = ensure_user(
                session,
                external_code=payload['external_code'],
                role_code=payload['role_code'],
                full_name=payload['full_name'],
                email=payload['email'],
                phone=payload['phone'],
                is_staff=payload['is_staff'],
            )
            ensure_federated_identity(
                session,
                user_id=user.id,
                provider=KEYCLOAK_PROVIDER,
                subject=payload['subject'],
                username=payload['username'],
                email=payload['email'],
            )
            users[payload['external_code']] = user

        teacher_codes = ['USR-TEACH-001', 'USR-TEACH-002', 'USR-TEACH-003', 'USR-TEACH-004', 'USR-TEACH-005']
        teachers = {
            user.external_code: teacher
            for teacher, user in session.execute(
                select(Teacher, User)
                .join(User, User.id == Teacher.user_id)
                .where(User.external_code.in_(teacher_codes))
            ).all()
        }

        for payload in DEEP_GUARDIANS:
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
            ensure_federated_identity(
                session,
                user_id=user.id,
                provider=KEYCLOAK_PROVIDER,
                subject=payload['subject'],
                username=payload['username'],
                email=payload['email'],
            )

        class_codes = {payload['class_code'] for payload in DEEP_STUDENTS}
        classes = {
            class_.code: class_
            for class_ in session.execute(select(Class).where(Class.code.in_(class_codes))).scalars().all()
        }
        if set(classes) != class_codes:
            missing = sorted(class_codes - set(classes))
            raise SystemExit(
                f'class seeds missing for deep population: {", ".join(missing)}; run make db-seed-school-expansion first'
            )

        subjects = {
            subject.code: subject
            for subject in session.execute(
                select(Subject).where(Subject.code.in_({'MAT', 'POR', 'CIE', 'ING', 'HIS'}))
            ).scalars().all()
        }

        student_records = {}
        enrollment_records = {}
        contract_count = 0

        for payload in DEEP_STUDENTS:
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
            student_records[payload['external_code']] = student

            class_ = classes[payload['class_code']]
            enrollment = ensure_enrollment(
                session,
                student_id=student.id,
                class_id=class_.id,
                academic_year=ACADEMIC_YEAR,
                status='active',
            )
            enrollment_records[payload['external_code']] = enrollment

            guardian_code = next(
                guardian['external_code']
                for guardian in DEEP_GUARDIANS
                if payload['external_code'] in guardian['children']
            )
            guardian = guardians_by_code[guardian_code]
            ensure_guardian_link(
                session,
                guardian_id=guardian.id,
                student_id=student.id,
                relationship_label='responsavel',
                can_view_finance=True,
                can_view_academic=True,
            )

            if payload['contract_amount'] is not None:
                contract = ensure_contract(
                    session,
                    school_unit_id=unit.id,
                    student_id=student.id,
                    guardian_id=guardian.id,
                    academic_year=ACADEMIC_YEAR,
                    contract_code=f"CTR-2026-{payload['enrollment_code']}",
                    monthly_amount=payload['contract_amount'],
                    status='active',
                )
                march = ensure_invoice(
                    session,
                    contract_id=contract.id,
                    reference_month='2026-03',
                    due_date=date(2026, 3, 10),
                    amount_due=payload['contract_amount'],
                    status='paid',
                )
                ensure_payment(
                    session,
                    invoice_id=march.id,
                    paid_at=date(2026, 3, 8),
                    amount_paid=payload['contract_amount'],
                    payment_method='pix',
                )
                april_status = 'paid' if payload['external_code'] in {'USR-STUD-102', 'USR-STUD-104', 'USR-STUD-106'} else 'open'
                april = ensure_invoice(
                    session,
                    contract_id=contract.id,
                    reference_month='2026-04',
                    due_date=date(2026, 4, 10),
                    amount_due=payload['contract_amount'],
                    status=april_status,
                )
                if april_status == 'paid':
                    ensure_payment(
                        session,
                        invoice_id=april.id,
                        paid_at=date(2026, 4, 7),
                        amount_paid=payload['contract_amount'],
                        payment_method='boleto',
                    )
                contract_count += 1

        grade_item_specs = [
            ('T1', 'Diagnostico orientado', Decimal('10.00'), date(2026, 3, 12)),
            ('T1', 'Avaliacao bimestral', Decimal('10.00'), date(2026, 4, 16)),
        ]
        academic_count = 0
        for payload in DEEP_STUDENTS:
            if not payload['subject_scores']:
                continue
            enrollment = enrollment_records[payload['external_code']]
            class_ = classes[payload['class_code']]
            for subject_code, base_score in payload['subject_scores'].items():
                assignment = resolve_assignment(
                    session,
                    class_id=class_.id,
                    class_code=class_.code,
                    subject_id=subjects[subject_code].id,
                    subject_code=subject_code,
                    teacher_map=teachers,
                )
                for index, (term_code, title, max_score, due_date) in enumerate(grade_item_specs):
                    item = ensure_grade_item(
                        session,
                        teacher_assignment_id=assignment.id,
                        term_code=term_code,
                        title=title,
                        max_score=max_score,
                        due_date=due_date,
                    )
                    adjustment = Decimal('-0.3') if index == 0 else Decimal('0.2')
                    score = max(Decimal('6.0'), min(Decimal('9.8'), base_score + adjustment))
                    ensure_grade(
                        session,
                        enrollment_id=enrollment.id,
                        grade_item_id=item.id,
                        score=score,
                        feedback=f'Desempenho consistente em {subject_code.lower()}.',
                    )
                ensure_attendance(
                    session,
                    enrollment_id=enrollment.id,
                    subject_id=subjects[subject_code].id,
                    record_date=date(2026, 3, 10),
                    status='present',
                )
                ensure_attendance(
                    session,
                    enrollment_id=enrollment.id,
                    subject_id=subjects[subject_code].id,
                    record_date=date(2026, 3, 24),
                    status='present' if base_score >= Decimal('8.0') else 'late',
                    minutes_absent=0 if base_score >= Decimal('8.0') else 10,
                )
                academic_count += 1

        ensure_calendar_event(
            session,
            school_unit_id=unit.id,
            class_id=classes['6EF-A'].id,
            audience='familias',
            category='acolhimento',
            title='Plantao de acolhimento do 6o ano',
            description='Espaco de orientacao para familias ingressantes do 6o ano.',
            starts_at=datetime(2026, 4, 4, 9, 0, tzinfo=TZ),
            ends_at=datetime(2026, 4, 4, 11, 0, tzinfo=TZ),
            visibility='public',
        )
        ensure_calendar_event(
            session,
            school_unit_id=unit.id,
            class_id=None,
            audience='familias',
            category='secretaria',
            title='Plantao assistido de rematricula',
            description='Apoio da secretaria para revisao cadastral e protocolos de rematricula.',
            starts_at=datetime(2026, 4, 6, 14, 0, tzinfo=TZ),
            ends_at=datetime(2026, 4, 6, 17, 0, tzinfo=TZ),
            visibility='public',
        )

        document_count = seed_documents(session)
        operational_count = seed_operational_scenarios(session, users=users)

        print(
            'deep population seed inserted successfully; '
            f'users={len(DEEP_SUPPORT_USERS) + len(DEEP_GUARDIANS) + len(DEEP_STUDENTS)} '
            f'contracts={contract_count} academic_profiles={academic_count} '
            f'documents={document_count} threads={operational_count}'
        )


if __name__ == '__main__':
    main()
