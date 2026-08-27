-- ============================================================================
-- M1 — Account setup & verification
-- Run this once in the Supabase dashboard: SQL Editor → New query → paste → Run.
-- Safe to re-run (idempotent): uses IF NOT EXISTS / CREATE OR REPLACE / DROP..CREATE.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- members: one profile row per verified club member.
-- id matches auth.users.id so the profile and the auth account are the same
-- person; deleting the auth user cascades to the profile.
-- ---------------------------------------------------------------------------
create table if not exists public.members (
    id         uuid primary key references auth.users (id) on delete cascade,
    email      text        not null,
    full_name  text,
    created_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Restrict sign-ups to the club's email domain.
-- Runs BEFORE a new auth user is inserted; raising here blocks the sign-up,
-- so a non-@nd.edu address never even receives a code.
-- ---------------------------------------------------------------------------
create or replace function public.enforce_email_domain()
returns trigger
language plpgsql
as $$
begin
    if lower(split_part(new.email, '@', 2)) <> 'nd.edu' then
        raise exception 'Only @nd.edu email addresses may register.';
    end if;
    return new;
end;
$$;

drop trigger if exists enforce_email_domain on auth.users;
create trigger enforce_email_domain
    before insert on auth.users
    for each row execute function public.enforce_email_domain();

-- ---------------------------------------------------------------------------
-- Auto-create the members profile row when a new auth user is created.
-- SECURITY DEFINER lets this insert bypass RLS (the row is created for the
-- member, not by them). Runs AFTER the domain check above has passed.
-- full_name is pulled from the Google profile metadata when available.
-- ---------------------------------------------------------------------------
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    insert into public.members (id, email, full_name)
    values (
        new.id,
        new.email,
        coalesce(
            new.raw_user_meta_data ->> 'full_name',
            new.raw_user_meta_data ->> 'name'
        )
    )
    on conflict (id) do nothing;
    return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute function public.handle_new_user();

-- ---------------------------------------------------------------------------
-- Row-Level Security: a member may read and update only their own row.
-- With RLS enabled and only these policies, no member can see anyone else's
-- profile through the public (anon) API key.
-- ---------------------------------------------------------------------------
alter table public.members enable row level security;

drop policy if exists "members can read own row" on public.members;
create policy "members can read own row"
    on public.members for select
    using (auth.uid() = id);

drop policy if exists "members can update own row" on public.members;
create policy "members can update own row"
    on public.members for update
    using (auth.uid() = id)
    with check (auth.uid() = id);

-- ---------------------------------------------------------------------------
-- Table-level privileges. RLS decides *which rows* the authenticated role may
-- touch, but the role still needs base table privileges to touch it at all.
-- Tables made in the SQL Editor (unlike the Table Editor) don't get these
-- automatically. Only select+update: inserts happen via the SECURITY DEFINER
-- trigger above, and members never delete their profile.
-- ---------------------------------------------------------------------------
grant select, update on public.members to authenticated;
