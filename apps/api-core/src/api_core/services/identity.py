from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from api_core.contracts import ActorContext, AccessibleClassReference, LinkedStudentReference
from api_core.db.session import apply_rls_actor_context, apply_rls_identity_context
from api_core.db.models import (
    Class,
    Enrollment,
    FederatedIdentity,
    Guardian,
    GuardianStudentLink,
    Role,
    Student,
    Subject,
    Teacher,
    TeacherAssignment,
    TelegramAccount,
    User,
    UserTelegramLink,
)


def _base_user_query() -> Select:
    return (
        select(User, Role, TelegramAccount.telegram_chat_id)
        .join(Role, Role.code == User.role_code)
        .outerjoin(UserTelegramLink, UserTelegramLink.user_id == User.id)
        .outerjoin(TelegramAccount, TelegramAccount.id == UserTelegramLink.telegram_account_id)
    )


def resolve_actor_context(
    session: Session,
    *,
    telegram_chat_id: int | None = None,
    user_external_code: str | None = None,
    federated_provider: str | None = None,
    federated_subject: str | None = None,
) -> ActorContext | None:
    if (
        telegram_chat_id is None
        and user_external_code is None
        and (federated_provider is None or federated_subject is None)
    ):
        return None

    query = _base_user_query()
    if federated_provider is not None and federated_subject is not None:
        query = (
            query.join(FederatedIdentity, FederatedIdentity.user_id == User.id)
            .where(FederatedIdentity.provider == federated_provider)
            .where(FederatedIdentity.subject == federated_subject)
        )
    elif telegram_chat_id is not None:
        query = query.where(TelegramAccount.telegram_chat_id == telegram_chat_id)
    else:
        query = query.where(User.external_code == user_external_code)

    row = session.execute(query).first()
    if row is None:
        return None

    user, role, linked_chat_id = row
    actor = ActorContext(
        user_id=user.id,
        role_code=role.code,
        external_code=user.external_code,
        full_name=user.full_name,
        authenticated=True,
        telegram_chat_id=linked_chat_id,
        telegram_linked=linked_chat_id is not None,
    )
    apply_rls_identity_context(session, user_id=user.id, role_code=role.code)

    if role.code == 'guardian':
        guardian = session.execute(select(Guardian).where(Guardian.user_id == user.id)).scalar_one_or_none()
        if guardian is not None:
            actor.guardian_id = guardian.id
            rows = session.execute(
                select(
                    Student.id,
                    User.full_name,
                    Student.enrollment_code,
                    Class.id,
                    Class.display_name,
                    GuardianStudentLink.can_view_academic,
                    GuardianStudentLink.can_view_finance,
                )
                .join(GuardianStudentLink, GuardianStudentLink.student_id == Student.id)
                .join(User, User.id == Student.user_id)
                .outerjoin(Enrollment, Enrollment.student_id == Student.id)
                .outerjoin(Class, Class.id == Enrollment.class_id)
                .where(GuardianStudentLink.guardian_id == guardian.id)
            ).all()
            for student_id, full_name, enrollment_code, class_id, class_name, can_view_academic, can_view_finance in rows:
                actor.linked_student_ids.append(student_id)
                if can_view_academic:
                    actor.academic_student_ids.append(student_id)
                if can_view_finance:
                    actor.financial_student_ids.append(student_id)
                actor.linked_students.append(
                    LinkedStudentReference(
                        student_id=student_id,
                        full_name=full_name,
                        enrollment_code=enrollment_code,
                        class_id=class_id,
                        class_name=class_name,
                        can_view_academic=can_view_academic,
                        can_view_finance=can_view_finance,
                    )
                )

    if role.code == 'student':
        row = session.execute(
            select(Student.id, Student.enrollment_code, Class.id, Class.display_name)
            .join(Enrollment, Enrollment.student_id == Student.id)
            .outerjoin(Class, Class.id == Enrollment.class_id)
            .where(Student.user_id == user.id)
        ).first()
        if row is not None:
            student_id, enrollment_code, class_id, class_name = row
            actor.student_id = student_id
            actor.linked_student_ids.append(student_id)
            actor.academic_student_ids.append(student_id)
            actor.financial_student_ids.append(student_id)
            actor.linked_students.append(
                LinkedStudentReference(
                    student_id=student_id,
                    full_name=user.full_name,
                    enrollment_code=enrollment_code,
                    class_id=class_id,
                    class_name=class_name,
                    can_view_academic=True,
                    can_view_finance=True,
                )
            )
            if class_id is not None:
                actor.accessible_class_ids.append(class_id)

    if role.code == 'teacher':
        teacher = session.execute(select(Teacher).where(Teacher.user_id == user.id)).scalar_one_or_none()
        if teacher is not None:
            actor.teacher_id = teacher.id
            rows = session.execute(
                select(Class.id, Class.display_name, Subject.name)
                .join(TeacherAssignment, TeacherAssignment.class_id == Class.id)
                .join(Subject, Subject.id == TeacherAssignment.subject_id)
                .where(TeacherAssignment.teacher_id == teacher.id)
            ).all()
            for class_id, class_name, subject_name in rows:
                actor.accessible_class_ids.append(class_id)
                actor.accessible_classes.append(
                    AccessibleClassReference(
                        class_id=class_id,
                        class_name=class_name,
                        subject_name=subject_name,
                    )
                )

    actor.linked_student_ids = list(dict.fromkeys(actor.linked_student_ids))
    actor.academic_student_ids = list(dict.fromkeys(actor.academic_student_ids))
    actor.financial_student_ids = list(dict.fromkeys(actor.financial_student_ids))
    actor.accessible_class_ids = list(dict.fromkeys(actor.accessible_class_ids))
    apply_rls_actor_context(session, actor)
    return actor
