from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api_core.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class TeacherAssignment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'teacher_assignments'
    __table_args__ = (
        UniqueConstraint('teacher_id', 'class_id', 'subject_id', 'academic_year'),
        {'schema': 'academic'},
    )

    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('school.teachers.id'), nullable=False)
    class_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('school.classes.id'), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('school.subjects.id'), nullable=False)
    academic_year: Mapped[int] = mapped_column(Integer, nullable=False)


class GradeItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'grade_items'
    __table_args__ = {'schema': 'academic'}

    teacher_assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('academic.teacher_assignments.id'),
        nullable=False,
    )
    term_code: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    max_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)


class Grade(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'grades'
    __table_args__ = (
        UniqueConstraint('enrollment_id', 'grade_item_id'),
        {'schema': 'academic'},
    )

    enrollment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('school.enrollments.id'), nullable=False)
    grade_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('academic.grade_items.id'), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    feedback: Mapped[str | None] = mapped_column(String(255))


class AttendanceRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'attendance_records'
    __table_args__ = {'schema': 'academic'}

    enrollment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('school.enrollments.id'), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('school.subjects.id'), nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    minutes_absent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
