"""add runtime rls policies

Revision ID: 9aa0e8004bc1
Revises: c18f1a8f0fd7
Create Date: 2026-03-23 12:05:00.000000
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9aa0e8004bc1'
down_revision: str | Sequence[str] | None = 'c18f1a8f0fd7'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        create schema if not exists runtime;
        revoke all on schema runtime from public;
        grant usage on schema runtime to eduassist_app;

        create or replace function runtime.actor_context()
        returns jsonb
        language sql
        stable
        as $$
          select coalesce(
            nullif(current_setting('eduassist.actor_context', true), '')::jsonb,
            '{}'::jsonb
          )
        $$;

        create or replace function runtime.actor_user_id()
        returns uuid
        language sql
        stable
        as $$
          select nullif(runtime.actor_context() ->> 'user_id', '')::uuid
        $$;

        create or replace function runtime.actor_role_code()
        returns text
        language sql
        stable
        as $$
          select nullif(runtime.actor_context() ->> 'role_code', '')
        $$;

        create or replace function runtime.can_access_student(
          target_student_id uuid,
          access_domain text
        )
        returns boolean
        language plpgsql
        stable
        security definer
        set search_path = pg_catalog, runtime, identity, school, academic, finance
        as $$
        declare
          actor_user_id uuid := runtime.actor_user_id();
          actor_role text := runtime.actor_role_code();
        begin
          if actor_user_id is null or actor_role is null or target_student_id is null then
            return false;
          end if;

          if access_domain = 'academic' then
            if actor_role in ('coordinator', 'admin') then
              return true;
            end if;

            if actor_role = 'student' then
              return exists(
                select 1
                from school.students students
                where students.id = target_student_id
                  and students.user_id = actor_user_id
              );
            end if;

            if actor_role = 'guardian' then
              return exists(
                select 1
                from school.guardians guardians
                join school.guardian_student_links links on links.guardian_id = guardians.id
                where guardians.user_id = actor_user_id
                  and links.student_id = target_student_id
                  and links.can_view_academic
              );
            end if;

            if actor_role = 'teacher' then
              return exists(
                select 1
                from school.teachers teachers
                join academic.teacher_assignments assignments
                  on assignments.teacher_id = teachers.id
                join school.enrollments enrollments on enrollments.class_id = assignments.class_id
                where teachers.user_id = actor_user_id
                  and enrollments.student_id = target_student_id
              );
            end if;

            return false;
          end if;

          if access_domain = 'finance' then
            if actor_role in ('finance', 'admin') then
              return true;
            end if;

            if actor_role = 'student' then
              return exists(
                select 1
                from school.students students
                where students.id = target_student_id
                  and students.user_id = actor_user_id
              );
            end if;

            if actor_role = 'guardian' then
              return exists(
                select 1
                from school.guardians guardians
                join school.guardian_student_links links on links.guardian_id = guardians.id
                where guardians.user_id = actor_user_id
                  and links.student_id = target_student_id
                  and links.can_view_finance
              );
            end if;

            return false;
          end if;

          return false;
        end;
        $$;

        create or replace function runtime.can_access_enrollment(
          target_enrollment_id uuid,
          access_domain text
        )
        returns boolean
        language plpgsql
        stable
        security definer
        set search_path = pg_catalog, runtime, identity, school, academic, finance
        as $$
        declare
          target_student_id uuid;
        begin
          if target_enrollment_id is null then
            return false;
          end if;

          select enrollments.student_id
            into target_student_id
          from school.enrollments enrollments
          where enrollments.id = target_enrollment_id;

          if target_student_id is null then
            return false;
          end if;

          return runtime.can_access_student(target_student_id, access_domain);
        end;
        $$;

        grant execute on all functions in schema runtime to eduassist_app;
        alter default privileges for role eduassist in schema runtime
          grant execute on functions to eduassist_app;

        alter table school.students enable row level security;
        alter table school.students force row level security;
        drop policy if exists school_students_runtime_access on school.students;
        create policy school_students_runtime_access
          on school.students
          for all
          using (
            runtime.can_access_student(id, 'academic')
            or runtime.can_access_student(id, 'finance')
          )
          with check (
            runtime.can_access_student(id, 'academic')
            or runtime.can_access_student(id, 'finance')
          );

        alter table school.enrollments enable row level security;
        alter table school.enrollments force row level security;
        drop policy if exists school_enrollments_runtime_access on school.enrollments;
        create policy school_enrollments_runtime_access
          on school.enrollments
          for all
          using (
            runtime.can_access_enrollment(id, 'academic')
            or runtime.can_access_enrollment(id, 'finance')
          )
          with check (
            runtime.can_access_enrollment(id, 'academic')
            or runtime.can_access_enrollment(id, 'finance')
          );

        alter table academic.grades enable row level security;
        alter table academic.grades force row level security;
        drop policy if exists academic_grades_runtime_access on academic.grades;
        create policy academic_grades_runtime_access
          on academic.grades
          for all
          using (runtime.can_access_enrollment(enrollment_id, 'academic'))
          with check (runtime.can_access_enrollment(enrollment_id, 'academic'));

        alter table academic.attendance_records enable row level security;
        alter table academic.attendance_records force row level security;
        drop policy if exists academic_attendance_runtime_access on academic.attendance_records;
        create policy academic_attendance_runtime_access
          on academic.attendance_records
          for all
          using (runtime.can_access_enrollment(enrollment_id, 'academic'))
          with check (runtime.can_access_enrollment(enrollment_id, 'academic'));

        alter table finance.contracts enable row level security;
        alter table finance.contracts force row level security;
        drop policy if exists finance_contracts_runtime_access on finance.contracts;
        create policy finance_contracts_runtime_access
          on finance.contracts
          for all
          using (runtime.can_access_student(student_id, 'finance'))
          with check (runtime.can_access_student(student_id, 'finance'));

        alter table finance.invoices enable row level security;
        alter table finance.invoices force row level security;
        drop policy if exists finance_invoices_runtime_access on finance.invoices;
        create policy finance_invoices_runtime_access
          on finance.invoices
          for all
          using (
            exists (
              select 1
              from finance.contracts contracts
              where contracts.id = contract_id
                and runtime.can_access_student(contracts.student_id, 'finance')
            )
          )
          with check (
            exists (
              select 1
              from finance.contracts contracts
              where contracts.id = contract_id
                and runtime.can_access_student(contracts.student_id, 'finance')
            )
          );

        alter table finance.payments enable row level security;
        alter table finance.payments force row level security;
        drop policy if exists finance_payments_runtime_access on finance.payments;
        create policy finance_payments_runtime_access
          on finance.payments
          for all
          using (
            exists (
              select 1
              from finance.invoices invoices
              join finance.contracts contracts on contracts.id = invoices.contract_id
              where invoices.id = invoice_id
                and runtime.can_access_student(contracts.student_id, 'finance')
            )
          )
          with check (
            exists (
              select 1
              from finance.invoices invoices
              join finance.contracts contracts on contracts.id = invoices.contract_id
              where invoices.id = invoice_id
                and runtime.can_access_student(contracts.student_id, 'finance')
            )
          );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        drop policy if exists finance_payments_runtime_access on finance.payments;
        alter table finance.payments no force row level security;
        alter table finance.payments disable row level security;

        drop policy if exists finance_invoices_runtime_access on finance.invoices;
        alter table finance.invoices no force row level security;
        alter table finance.invoices disable row level security;

        drop policy if exists finance_contracts_runtime_access on finance.contracts;
        alter table finance.contracts no force row level security;
        alter table finance.contracts disable row level security;

        drop policy if exists academic_attendance_runtime_access on academic.attendance_records;
        alter table academic.attendance_records no force row level security;
        alter table academic.attendance_records disable row level security;

        drop policy if exists academic_grades_runtime_access on academic.grades;
        alter table academic.grades no force row level security;
        alter table academic.grades disable row level security;

        drop policy if exists school_enrollments_runtime_access on school.enrollments;
        alter table school.enrollments no force row level security;
        alter table school.enrollments disable row level security;

        drop policy if exists school_students_runtime_access on school.students;
        alter table school.students no force row level security;
        alter table school.students disable row level security;

        revoke all on schema runtime from eduassist_app;
        revoke execute on all functions in schema runtime from eduassist_app;
        drop function if exists runtime.can_access_enrollment(uuid, text);
        drop function if exists runtime.can_access_student(uuid, text);
        drop function if exists runtime.actor_role_code();
        drop function if exists runtime.actor_user_id();
        drop function if exists runtime.actor_context();
        drop schema if exists runtime cascade;
        """
    )
