-- ============================================================
-- AI Job Scavenger — Supabase / Postgres schema
-- Run this in the Supabase SQL editor (or via `supabase db push`)
-- after enabling the project. Idempotent-ish: uses IF NOT EXISTS
-- where practical, but review before re-running on existing data.
-- ============================================================

-- Required extensions
create extension if not exists "uuid-ossp";
create extension if not exists vector;       -- pgvector for embeddings
create extension if not exists pg_trgm;      -- fuzzy text search on title/company

-- ------------------------------------------------------------
-- ENUM TYPES (mirrors app/models/*.py — keep in sync)
-- ------------------------------------------------------------
do $$ begin
  create type experience_level as enum ('intern','junior','mid','senior','staff','principal','lead','manager');
exception when duplicate_object then null; end $$;

do $$ begin
  create type company_size as enum ('startup','small','medium','large','enterprise');
exception when duplicate_object then null; end $$;

do $$ begin
  create type employment_type as enum ('full_time','part_time','contract','internship','freelance');
exception when duplicate_object then null; end $$;

do $$ begin
  create type job_employment_type as enum ('full_time','part_time','contract','internship','freelance','unknown');
exception when duplicate_object then null; end $$;

do $$ begin
  create type notification_type as enum ('new_match','system');
exception when duplicate_object then null; end $$;

-- ------------------------------------------------------------
-- PROFILES  (1:1 with auth.users)
-- ------------------------------------------------------------
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email varchar(320) not null unique,
  full_name varchar(200),
  avatar_url varchar(1000),
  resume_url varchar(1000),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Auto-create a profile row whenever a new Supabase Auth user signs up.
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, email, full_name)
  values (new.id, new.email, new.raw_user_meta_data ->> 'full_name')
  on conflict (id) do nothing;
  return new;
end;
$$ language plpgsql security definer;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ------------------------------------------------------------
-- PREFERENCES  (1:1 with profiles)
-- ------------------------------------------------------------
create table if not exists public.preferences (
  id uuid primary key default uuid_generate_v4(),
  profile_id uuid not null unique references public.profiles(id) on delete cascade,
  preferred_roles text[] not null default '{}',
  skills text[] not null default '{}',
  preferred_locations text[] not null default '{}',
  remote_only boolean not null default false,
  salary_min integer,
  salary_max integer,
  salary_currency varchar(3) not null default 'USD',
  experience_level experience_level,
  company_size company_size,
  employment_type employment_type,
  embedding vector(1536),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ------------------------------------------------------------
-- JOBS  (global catalog, not user-scoped)
-- ------------------------------------------------------------
create table if not exists public.jobs (
  id uuid primary key default uuid_generate_v4(),
  source varchar(50) not null,
  source_job_id varchar(500) not null,
  source_url varchar(2000) not null,
  title varchar(300) not null,
  company varchar(300) not null,
  location varchar(300),
  remote boolean not null default false,
  salary_min integer,
  salary_max integer,
  salary_currency varchar(3),
  experience_level varchar(50),
  employment_type job_employment_type not null default 'unknown',
  required_skills text[] not null default '{}',
  responsibilities text[] not null default '{}',
  benefits text[] not null default '{}',
  description_raw text not null,
  description_normalized text,
  is_active boolean not null default true,
  embedding vector(1536),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (source, source_job_id)
);

create index if not exists ix_jobs_title_company on public.jobs (title, company);
create index if not exists ix_jobs_company on public.jobs (company);
create index if not exists ix_jobs_title_trgm on public.jobs using gin (title gin_trgm_ops);
-- IVFFlat index for approximate nearest-neighbor search on embeddings.
-- Requires ANALYZE after bulk inserts; `lists` should scale with row count.
create index if not exists ix_jobs_embedding on public.jobs
  using ivfflat (embedding vector_cosine_ops) with (lists = 100);

-- ------------------------------------------------------------
-- JOB_MATCHES
-- ------------------------------------------------------------
create table if not exists public.job_matches (
  id uuid primary key default uuid_generate_v4(),
  profile_id uuid not null references public.profiles(id) on delete cascade,
  job_id uuid not null references public.jobs(id) on delete cascade,
  score double precision not null,
  matched_skills text[] not null default '{}',
  missing_skills text[] not null default '{}',
  explanation text not null,
  notified boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (profile_id, job_id)
);

create index if not exists ix_job_matches_profile on public.job_matches (profile_id);
create index if not exists ix_job_matches_job on public.job_matches (job_id);

-- ------------------------------------------------------------
-- SAVED_JOBS
-- ------------------------------------------------------------
create table if not exists public.saved_jobs (
  id uuid primary key default uuid_generate_v4(),
  profile_id uuid not null references public.profiles(id) on delete cascade,
  job_id uuid not null references public.jobs(id) on delete cascade,
  notes text,
  applied boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (profile_id, job_id)
);

create index if not exists ix_saved_jobs_profile on public.saved_jobs (profile_id);

-- ------------------------------------------------------------
-- NOTIFICATION_HISTORY
-- ------------------------------------------------------------
create table if not exists public.notification_history (
  id uuid primary key default uuid_generate_v4(),
  profile_id uuid not null references public.profiles(id) on delete cascade,
  job_match_id uuid references public.job_matches(id) on delete set null,
  type notification_type not null default 'new_match',
  title varchar(300) not null,
  body text not null,
  read boolean not null default false,
  delivered boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists ix_notification_history_profile on public.notification_history (profile_id);

-- ------------------------------------------------------------
-- RESUME_UPLOADS
-- ------------------------------------------------------------
create table if not exists public.resume_uploads (
  id uuid primary key default uuid_generate_v4(),
  profile_id uuid not null references public.profiles(id) on delete cascade,
  file_url varchar(1000) not null,
  file_name varchar(300) not null,
  parsed_skills text[] not null default '{}',
  parsed_summary text,
  is_primary boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists ix_resume_uploads_profile on public.resume_uploads (profile_id);

-- ============================================================
-- ROW LEVEL SECURITY
-- The FastAPI backend connects with the service_role key (bypasses RLS)
-- for pipeline/admin operations, but RLS is enabled here as defense in
-- depth in case any client ever connects directly with a user JWT
-- (e.g. via Supabase client SDK in the future).
-- ============================================================
alter table public.profiles enable row level security;
alter table public.preferences enable row level security;
alter table public.jobs enable row level security;
alter table public.job_matches enable row level security;
alter table public.saved_jobs enable row level security;
alter table public.notification_history enable row level security;
alter table public.resume_uploads enable row level security;

-- profiles: users can read/update only their own row
drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own" on public.profiles for select using (auth.uid() = id);
drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own" on public.profiles for update using (auth.uid() = id);

-- preferences: owned by profile
drop policy if exists "preferences_all_own" on public.preferences;
create policy "preferences_all_own" on public.preferences for all
  using (auth.uid() = profile_id) with check (auth.uid() = profile_id);

-- jobs: readable by any authenticated user, writes only via service role
drop policy if exists "jobs_select_authenticated" on public.jobs;
create policy "jobs_select_authenticated" on public.jobs for select
  using (auth.role() = 'authenticated');

-- job_matches / saved_jobs / notification_history / resume_uploads: owned by profile
drop policy if exists "job_matches_all_own" on public.job_matches;
create policy "job_matches_all_own" on public.job_matches for all
  using (auth.uid() = profile_id) with check (auth.uid() = profile_id);

drop policy if exists "saved_jobs_all_own" on public.saved_jobs;
create policy "saved_jobs_all_own" on public.saved_jobs for all
  using (auth.uid() = profile_id) with check (auth.uid() = profile_id);

drop policy if exists "notification_history_all_own" on public.notification_history;
create policy "notification_history_all_own" on public.notification_history for all
  using (auth.uid() = profile_id) with check (auth.uid() = profile_id);

drop policy if exists "resume_uploads_all_own" on public.resume_uploads;
create policy "resume_uploads_all_own" on public.resume_uploads for all
  using (auth.uid() = profile_id) with check (auth.uid() = profile_id);
