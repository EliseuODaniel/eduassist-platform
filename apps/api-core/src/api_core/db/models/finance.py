from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from api_core.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Contract(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'contracts'
    __table_args__ = {'schema': 'finance'}

    school_unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('school.school_units.id'),
        nullable=False,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('school.students.id'), nullable=False)
    guardian_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('school.guardians.id'), nullable=False)
    academic_year: Mapped[int] = mapped_column(Integer, nullable=False)
    contract_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    monthly_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='active', nullable=False)


class Invoice(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'invoices'
    __table_args__ = (
        UniqueConstraint('contract_id', 'reference_month'),
        {'schema': 'finance'},
    )

    contract_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('finance.contracts.id'), nullable=False)
    reference_month: Mapped[str] = mapped_column(String(7), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount_due: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)


class Payment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'payments'
    __table_args__ = {'schema': 'finance'}

    invoice_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('finance.invoices.id'), nullable=False)
    paid_at: Mapped[date] = mapped_column(Date, nullable=False)
    amount_paid: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False)
