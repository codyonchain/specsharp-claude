-- SpecSharp Supabase auth isolation hardening
-- Apply in Supabase SQL Editor against production/staging database.
-- This script is idempotent.

begin;

create extension if not exists pgcrypto;

create table if not exists public.organizations (
  id text primary key,
  name text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.organization_members (
  id bigserial primary key,
  org_id text not null references public.organizations(id) on delete cascade,
  user_id text not null,
  email text not null,
  role text not null default 'member',
  is_default boolean not null default false,
  created_at timestamptz not null default now()
);

create unique index if not exists uq_org_members_user
  on public.organization_members(org_id, user_id);
create index if not exists idx_org_members_user_id
  on public.organization_members(user_id);
create index if not exists idx_org_members_email
  on public.organization_members(lower(email));

create table if not exists public.project_access (
  id bigserial primary key,
  project_id text not null unique,
  org_id text not null references public.organizations(id) on delete cascade,
  owner_user_id text not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_project_access_org_id
  on public.project_access(org_id);
create index if not exists idx_project_access_owner_user_id
  on public.project_access(owner_user_id);

do $$
begin
  if to_regclass('public.projects') is not null then
    create index if not exists idx_projects_project_id on public.projects(project_id);
  end if;
end $$;

alter table if exists public.organizations enable row level security;
alter table if exists public.organization_members enable row level security;
alter table if exists public.project_access enable row level security;
alter table if exists public.projects enable row level security;

do $$
begin
  if to_regclass('public.organizations') is not null then
    drop policy if exists org_select_for_members on public.organizations;
    create policy org_select_for_members
      on public.organizations
      for select
      to authenticated
      using (
        exists (
          select 1
          from public.organization_members m
          where m.org_id = organizations.id
            and (
              m.user_id = auth.uid()::text
              or lower(m.email) = lower(coalesce(auth.jwt() ->> 'email', ''))
            )
        )
      );
  end if;
end $$;

do $$
begin
  if to_regclass('public.organization_members') is not null then
    drop policy if exists org_members_select_self on public.organization_members;
    create policy org_members_select_self
      on public.organization_members
      for select
      to authenticated
      using (
        user_id = auth.uid()::text
        or lower(email) = lower(coalesce(auth.jwt() ->> 'email', ''))
      );
  end if;
end $$;

do $$
begin
  if to_regclass('public.project_access') is not null then
    drop policy if exists project_access_select_member on public.project_access;
    create policy project_access_select_member
      on public.project_access
      for select
      to authenticated
      using (
        exists (
          select 1
          from public.organization_members m
          where m.org_id = project_access.org_id
            and (
              m.user_id = auth.uid()::text
              or lower(m.email) = lower(coalesce(auth.jwt() ->> 'email', ''))
            )
        )
      );
  end if;
end $$;

do $$
begin
  if to_regclass('public.projects') is not null then
    drop policy if exists projects_select_scoped_member on public.projects;
    create policy projects_select_scoped_member
      on public.projects
      for select
      to authenticated
      using (
        exists (
          select 1
          from public.project_access pa
          join public.organization_members m
            on m.org_id = pa.org_id
          where pa.project_id = projects.project_id
            and (
              m.user_id = auth.uid()::text
              or lower(m.email) = lower(coalesce(auth.jwt() ->> 'email', ''))
            )
        )
      );
  end if;
end $$;

revoke all on table public.organizations from anon;
revoke all on table public.organization_members from anon;
revoke all on table public.project_access from anon;

grant select on table public.organizations to authenticated;
grant select on table public.organization_members to authenticated;
grant select on table public.project_access to authenticated;

do $$
begin
  if to_regclass('public.projects') is not null then
    revoke all on table public.projects from anon;
    grant select on table public.projects to authenticated;
  end if;
end $$;

commit;
