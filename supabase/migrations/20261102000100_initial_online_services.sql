-- Initial Supabase schema for community accounts and backend-owned game metadata.
-- This schema does NOT claim to implement the Xbox 360 wire protocol.
-- Apply with the Supabase SQL Editor or Supabase CLI after creating a project.

create table if not exists public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    display_name text not null check (char_length(display_name) between 1 and 32),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Platform identifiers are opaque until Xbox 360 identity semantics are proven.
-- Never assume this value is an XUID or expose it to other players.
create table if not exists public.platform_identities (
    id uuid primary key default gen_random_uuid(),
    profile_id uuid not null references public.profiles(id) on delete cascade,
    platform text not null check (platform in ('xbox360')),
    external_subject text not null check (char_length(external_subject) between 1 and 256),
    verified_at timestamptz,
    created_at timestamptz not null default now(),
    unique (platform, external_subject),
    unique (profile_id, platform)
);

create table if not exists public.player_characters (
    id uuid primary key default gen_random_uuid(),
    profile_id uuid not null references public.profiles(id) on delete cascade,
    character_name text not null check (char_length(character_name) between 1 and 32),
    game_build text,
    soul_memory bigint check (soul_memory is null or soul_memory >= 0),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.player_presence (
    profile_id uuid primary key references public.profiles(id) on delete cascade,
    presence_state text not null default 'offline'
        check (presence_state in ('offline', 'online', 'in_game', 'searching')),
    current_area text,
    last_seen_at timestamptz not null default now()
);

create table if not exists public.matchmaking_requests (
    id uuid primary key default gen_random_uuid(),
    profile_id uuid not null references public.profiles(id) on delete cascade,
    mode text not null check (mode in ('coop', 'invasion', 'arena')),
    area_key text,
    request_state text not null default 'queued'
        check (request_state in ('queued', 'matched', 'cancelled', 'expired')),
    created_at timestamptz not null default now(),
    expires_at timestamptz
);

create index if not exists matchmaking_requests_lookup_idx
    on public.matchmaking_requests (mode, area_key, request_state, created_at);

-- RLS is deliberately restrictive. The compatibility server will use its
-- server-only service-role credential; the Xbox client must never receive it.
alter table public.profiles enable row level security;
alter table public.platform_identities enable row level security;
alter table public.player_characters enable row level security;
alter table public.player_presence enable row level security;
alter table public.matchmaking_requests enable row level security;

create policy "profiles_select_own"
    on public.profiles for select to authenticated
    using (id = (select auth.uid()));

create policy "profiles_insert_own"
    on public.profiles for insert to authenticated
    with check (id = (select auth.uid()));

create policy "profiles_update_own"
    on public.profiles for update to authenticated
    using (id = (select auth.uid()))
    with check (id = (select auth.uid()));

create policy "characters_select_own"
    on public.player_characters for select to authenticated
    using (profile_id = (select auth.uid()));

create policy "characters_insert_own"
    on public.player_characters for insert to authenticated
    with check (profile_id = (select auth.uid()));

create policy "characters_update_own"
    on public.player_characters for update to authenticated
    using (profile_id = (select auth.uid()))
    with check (profile_id = (select auth.uid()));

create policy "presence_select_own"
    on public.player_presence for select to authenticated
    using (profile_id = (select auth.uid()));

create policy "matchmaking_select_own"
    on public.matchmaking_requests for select to authenticated
    using (profile_id = (select auth.uid()));

-- No client policies are created for platform_identities or matchmaking writes.
-- Only trusted backend code should link console identities or create/match queues.
