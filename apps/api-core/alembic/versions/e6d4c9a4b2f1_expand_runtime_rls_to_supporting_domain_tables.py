"""expand runtime rls to supporting domain tables

Revision ID: e6d4c9a4b2f1
Revises: 4e27f7963646
Create Date: 2026-03-23 20:10:00.000000
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e6d4c9a4b2f1'
down_revision: str | Sequence[str] | None = '4e27f7963646'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        create or replace function runtime.can_access_guardian(target_guardian_id uuid)
        returns boolean
        language plpgsql
        stable
        security definer
        set search_path = pg_catalog, runtime, identity, school, finance
        as $$
        declare
          actor_user_id uuid := runtime.actor_user_id();
          actor_role text := runtime.actor_role_code();
        begin
          if actor_user_id is null or actor_role is null or target_guardian_id is null then
            return false;
          end if;

          if actor_role in ('finance', 'admin', 'system_internal') then
            return true;
          end if;

          if actor_role = 'guardian' then
            return exists(
              select 1
              from school.guardians guardians
              where guardians.id = target_guardian_id
                and guardians.user_id = actor_user_id
            );
          end if;

          if actor_role = 'student' then
            return exists(
              select 1
              from school.students students
              join school.guardian_student_links links on links.student_id = students.id
              where students.user_id = actor_user_id
                and links.guardian_id = target_guardian_id
            );
          end if;

          return false;
        end;
        $$;

        create or replace function runtime.can_access_teacher(target_teacher_id uuid)
        returns boolean
        language plpgsql
        stable
        security definer
        set search_path = pg_catalog, runtime, identity, school
        as $$
        declare
          actor_user_id uuid := runtime.actor_user_id();
          actor_role text := runtime.actor_role_code();
        begin
          if actor_user_id is null or actor_role is null or target_teacher_id is null then
            return false;
          end if;

          if actor_role in ('staff', 'coordinator', 'admin', 'system_internal') then
            return true;
          end if;

          if actor_role = 'teacher' then
            return exists(
              select 1
              from school.teachers teachers
              where teachers.id = target_teacher_id
                and teachers.user_id = actor_user_id
            );
          end if;

          return false;
        end;
        $$;

        create or replace function runtime.can_access_class(target_class_id uuid)
        returns boolean
        language plpgsql
        stable
        security definer
        set search_path = pg_catalog, runtime, identity, school, academic
        as $$
        declare
          actor_user_id uuid := runtime.actor_user_id();
          actor_role text := runtime.actor_role_code();
        begin
          if actor_user_id is null or actor_role is null or target_class_id is null then
            return false;
          end if;

          if actor_role in ('staff', 'coordinator', 'admin', 'system_internal') then
            return true;
          end if;

          if actor_role = 'teacher' then
            return exists(
              select 1
              from school.teachers teachers
              left join academic.teacher_assignments assignments
                on assignments.teacher_id = teachers.id
              left join school.classes classes
                on classes.homeroom_teacher_id = teachers.id
              where teachers.user_id = actor_user_id
                and (
                  assignments.class_id = target_class_id
                  or classes.id = target_class_id
                )
            );
          end if;

          if actor_role = 'guardian' then
            return exists(
              select 1
              from school.guardians guardians
              join school.guardian_student_links links on links.guardian_id = guardians.id
              join school.enrollments enrollments on enrollments.student_id = links.student_id
              where guardians.user_id = actor_user_id
                and enrollments.class_id = target_class_id
            );
          end if;

          if actor_role = 'student' then
            return exists(
              select 1
              from school.students students
              join school.enrollments enrollments on enrollments.student_id = students.id
              where students.user_id = actor_user_id
                and enrollments.class_id = target_class_id
            );
          end if;

          return false;
        end;
        $$;

        create or replace function runtime.can_access_teacher_assignment(target_assignment_id uuid)
        returns boolean
        language plpgsql
        stable
        security definer
        set search_path = pg_catalog, runtime, school, academic
        as $$
        declare
          assignment_teacher_id uuid;
          assignment_class_id uuid;
          actor_role text := runtime.actor_role_code();
        begin
          if target_assignment_id is null or actor_role is null then
            return false;
          end if;

          select assignments.teacher_id, assignments.class_id
            into assignment_teacher_id, assignment_class_id
          from academic.teacher_assignments assignments
          where assignments.id = target_assignment_id;

          if assignment_teacher_id is null or assignment_class_id is null then
            return false;
          end if;

          if actor_role in ('staff', 'coordinator', 'admin', 'system_internal') then
            return true;
          end if;

          if runtime.can_access_teacher(assignment_teacher_id) then
            return true;
          end if;

          return runtime.can_access_class(assignment_class_id);
        end;
        $$;

        create or replace function runtime.can_access_grade_item(target_grade_item_id uuid)
        returns boolean
        language plpgsql
        stable
        security definer
        set search_path = pg_catalog, runtime, academic
        as $$
        declare
          target_assignment_id uuid;
        begin
          if target_grade_item_id is null then
            return false;
          end if;

          select grade_items.teacher_assignment_id
            into target_assignment_id
          from academic.grade_items
          where grade_items.id = target_grade_item_id;

          if target_assignment_id is null then
            return false;
          end if;

          return runtime.can_access_teacher_assignment(target_assignment_id);
        end;
        $$;

        create or replace function runtime.can_access_calendar_event(target_event_id uuid)
        returns boolean
        language plpgsql
        stable
        security definer
        set search_path = pg_catalog, runtime, calendar
        as $$
        declare
          target_visibility text;
          target_class_id uuid;
          actor_role text := runtime.actor_role_code();
        begin
          if target_event_id is null then
            return false;
          end if;

          select events.visibility, events.class_id
            into target_visibility, target_class_id
          from calendar.calendar_events events
          where events.id = target_event_id;

          if target_visibility is null then
            return false;
          end if;

          if target_visibility = 'public' then
            return true;
          end if;

          if actor_role in ('staff', 'finance', 'coordinator', 'admin', 'system_internal') then
            return true;
          end if;

          if target_class_id is null then
            return false;
          end if;

          return runtime.can_access_class(target_class_id);
        end;
        $$;

        grant execute on function runtime.can_access_guardian(uuid) to eduassist_app;
        grant execute on function runtime.can_access_teacher(uuid) to eduassist_app;
        grant execute on function runtime.can_access_class(uuid) to eduassist_app;
        grant execute on function runtime.can_access_teacher_assignment(uuid) to eduassist_app;
        grant execute on function runtime.can_access_grade_item(uuid) to eduassist_app;
        grant execute on function runtime.can_access_calendar_event(uuid) to eduassist_app;

        alter table school.guardians enable row level security;
        alter table school.guardians force row level security;
        drop policy if exists school_guardians_runtime_access on school.guardians;
        create policy school_guardians_runtime_access
          on school.guardians
          for all
          using (runtime.can_access_guardian(id))
          with check (runtime.can_access_guardian(id));

        alter table school.guardian_student_links enable row level security;
        alter table school.guardian_student_links force row level security;
        drop policy if exists school_guardian_student_links_runtime_access on school.guardian_student_links;
        create policy school_guardian_student_links_runtime_access
          on school.guardian_student_links
          for all
          using (
            runtime.can_access_guardian(guardian_id)
            or runtime.can_access_student(student_id, 'academic')
            or runtime.can_access_student(student_id, 'finance')
          )
          with check (
            runtime.can_access_guardian(guardian_id)
            or runtime.can_access_student(student_id, 'academic')
            or runtime.can_access_student(student_id, 'finance')
          );

        alter table school.teachers enable row level security;
        alter table school.teachers force row level security;
        drop policy if exists school_teachers_runtime_access on school.teachers;
        create policy school_teachers_runtime_access
          on school.teachers
          for all
          using (runtime.can_access_teacher(id))
          with check (runtime.can_access_teacher(id));

        alter table school.classes enable row level security;
        alter table school.classes force row level security;
        drop policy if exists school_classes_runtime_access on school.classes;
        create policy school_classes_runtime_access
          on school.classes
          for all
          using (runtime.can_access_class(id))
          with check (runtime.can_access_class(id));

        alter table academic.teacher_assignments enable row level security;
        alter table academic.teacher_assignments force row level security;
        drop policy if exists academic_teacher_assignments_runtime_access on academic.teacher_assignments;
        create policy academic_teacher_assignments_runtime_access
          on academic.teacher_assignments
          for all
          using (runtime.can_access_teacher_assignment(id))
          with check (runtime.can_access_teacher_assignment(id));

        alter table academic.grade_items enable row level security;
        alter table academic.grade_items force row level security;
        drop policy if exists academic_grade_items_runtime_access on academic.grade_items;
        create policy academic_grade_items_runtime_access
          on academic.grade_items
          for all
          using (runtime.can_access_grade_item(id))
          with check (runtime.can_access_grade_item(id));

        alter table calendar.calendar_events enable row level security;
        alter table calendar.calendar_events force row level security;
        drop policy if exists calendar_events_runtime_access on calendar.calendar_events;
        create policy calendar_events_runtime_access
          on calendar.calendar_events
          for all
          using (runtime.can_access_calendar_event(id))
          with check (runtime.can_access_calendar_event(id));
        """
    )


def downgrade() -> None:
    op.execute(
        """
        drop policy if exists calendar_events_runtime_access on calendar.calendar_events;
        alter table calendar.calendar_events no force row level security;
        alter table calendar.calendar_events disable row level security;

        drop policy if exists academic_grade_items_runtime_access on academic.grade_items;
        alter table academic.grade_items no force row level security;
        alter table academic.grade_items disable row level security;

        drop policy if exists academic_teacher_assignments_runtime_access on academic.teacher_assignments;
        alter table academic.teacher_assignments no force row level security;
        alter table academic.teacher_assignments disable row level security;

        drop policy if exists school_classes_runtime_access on school.classes;
        alter table school.classes no force row level security;
        alter table school.classes disable row level security;

        drop policy if exists school_teachers_runtime_access on school.teachers;
        alter table school.teachers no force row level security;
        alter table school.teachers disable row level security;

        drop policy if exists school_guardian_student_links_runtime_access on school.guardian_student_links;
        alter table school.guardian_student_links no force row level security;
        alter table school.guardian_student_links disable row level security;

        drop policy if exists school_guardians_runtime_access on school.guardians;
        alter table school.guardians no force row level security;
        alter table school.guardians disable row level security;

        drop function if exists runtime.can_access_calendar_event(uuid);
        drop function if exists runtime.can_access_grade_item(uuid);
        drop function if exists runtime.can_access_teacher_assignment(uuid);
        drop function if exists runtime.can_access_class(uuid);
        drop function if exists runtime.can_access_teacher(uuid);
        drop function if exists runtime.can_access_guardian(uuid);
        """
    )
