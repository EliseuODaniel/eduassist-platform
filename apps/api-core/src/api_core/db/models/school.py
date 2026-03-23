from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_core.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SchoolUnit(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'school_units'
    __table_args__ = {'schema': 'school'}

    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default='America/Sao_Paulo', nullable=False)


class Guardian(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'guardians'
    __table_args__ = {'schema': 'school'}

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('identity.users.id'), nullable=False)
    relationship_label: Mapped[str] = mapped_column(String(40), nullable=False)
    cpf_masked: Mapped[str] = mapped_column(String(20), nullable=False)
    primary_contact: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Student(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'students'
    __table_args__ = {'schema': 'school'}

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('identity.users.id'), nullable=False)
    school_unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('school.school_units.id'),
        nullable=False,
    )
    enrollment_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    current_grade_level: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default='active', nullable=False)


class Teacher(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'teachers'
    __table_args__ = {'schema': 'school'}

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('identity.users.id'), nullable=False)
    school_unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('school.school_units.id'),
        nullable=False,
    )
    employee_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)


class GuardianStudentLink(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'guardian_student_links'
    __table_args__ = (
        UniqueConstraint('guardian_id', 'student_id'),
        {'schema': 'school'},
    )

    guardian_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('school.guardians.id'), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('school.students.id'), nullable=False)
    relationship_label: Mapped[str] = mapped_column(String(40), nullable=False)
    can_view_finance: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_view_academic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Class(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'classes'
    __table_args__ = (
        UniqueConstraint('school_unit_id', 'code'),
        {'schema': 'school'},
    )

    school_unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('school.school_units.id'),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    academic_year: Mapped[int] = mapped_column(Integer, nullable=False)
    grade_level: Mapped[int] = mapped_column(Integer, nullable=False)
    shift: Mapped[str] = mapped_column(String(30), nullable=False)
    homeroom_teacher_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('school.teachers.id'))


class Subject(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'subjects'
    __table_args__ = (
        UniqueConstraint('code'),
        {'schema': 'school'},
    )

    code: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    weekly_hours: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False)


class Enrollment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'enrollments'
    __table_args__ = (
        UniqueConstraint('student_id', 'class_id', 'academic_year'),
        {'schema': 'school'},
    )

    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('school.students.id'), nullable=False)
    class_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('school.classes.id'), nullable=False)
    academic_year: Mapped[int] = mapped_column(Integer, nullable=False)
    enrollment_status: Mapped[str] = mapped_column(String(30), default='active', nullable=False)

    student: Mapped[Student] = relationship()
    class_: Mapped[Class] = relationship('Class')
