-- =====================================================================
--  My Paper — tabulky pro odběr e-mailem
--
--  Tohle se pustí JEDNOU v Neonu (SQL Editor) a víc se k tomu nevracíš.
--
--  Proč vlastně vlastní databáze, když e-maily rozesílá poskytovatel:
--  seznam odběratelů je jediná věc, kterou u těchhle novin doopravdy
--  vlastníš. Poskytovatele můžeš kdykoli vyměnit, ceník se může změnit,
--  účet může někdo zavřít — a ty pořád máš svoje lidi. Navíc se tady
--  potkají čtenáři My Paper a zákazníci QMA v jednom přehledu.
--
--  Co tu naopak NENÍ a nikdy nebude:
--    * zdravotní zájmy čtenáře (ty nesmějí opustit jeho prohlížeč)
--    * vybraná země, míra informační zátěže, ztlumená témata
--    * cokoli, co jsme odvodili z chování místo toho, aby nám to řekl
--  Viz data/EDITORIAL-CODE.md, oddíl 5.
-- =====================================================================

create schema if not exists mypaper;

create table if not exists mypaper.subscribers (
  id             bigserial primary key,
  email          text        not null,
  email_lower    text        generated always as (lower(email)) stored,
  lang           text        not null default 'en',   -- 'en' | 'cs'

  -- Jak často chce psát. Čtenář si vybírá při přihlášení, protože
  -- denní a týdenní rytmus jsou dvě různé sliby a jeden se nedá vnutit
  -- druhému. Kdo chce ranní briefing, ten ho chce ráno; kdo chce jednu
  -- zprávu týdně, toho denní e-mail odhlásí.
  --   'daily'  = ranní briefing, každý den
  --   'weekly' = sobotní vydání, jednou týdně
  cadence        text        not null default 'weekly'
                 check (cadence in ('daily', 'weekly')),

  -- Odkud přišel: '/en/', '/cs/problems/housing/', 'weekend'…
  -- Časem z toho poznáš, která stránka lidi doopravdy získává.
  source         text,

  -- GDPR: souhlas se dokládá, ne předpokládá.
  -- IP se ukládá jen jako otisk (SHA-256 se solí), ne v čitelné podobě —
  -- k doložení souhlasu to stačí a nikoho to nezpětně neidentifikuje.
  consent_at     timestamptz not null default now(),
  consent_ip     text,
  consent_text   text,        -- doslovné znění, se kterým člověk souhlasil

  -- Potvrzení adresy (dvojité přihlášení) řeší poskytovatel rozesílky.
  -- Sem se to jen propíše, ať víš, kdo je opravdu potvrzený.
  confirmed_at   timestamptz,
  provider       text,        -- jméno rozesílací služby
  provider_id    text,        -- id odběratele u ní

  unsubscribed_at timestamptz,
  -- Odhlašovací klíč v adrese. Nikdy neposílej v odkazu e-mail samotný.
  unsub_token    uuid        not null default gen_random_uuid(),

  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);

-- Jeden člověk = jeden řádek. Když se přihlásí podruhé, řádek se
-- aktualizuje (viz ON CONFLICT ve workeru), nezaloží se druhý.
-- Kdyby už tabulka existovala z dřívějška, tohle ji dorovná. Skript se
-- smí pustit vícekrát a nic nerozbije.
alter table mypaper.subscribers
  add column if not exists cadence text not null default 'weekly';
do $$
begin
  alter table mypaper.subscribers
    add constraint subscribers_cadence_check check (cadence in ('daily', 'weekly'));
exception
  when duplicate_object then null;
end $$;

create unique index if not exists subscribers_email_key
  on mypaper.subscribers (email_lower);

create index if not exists subscribers_active_idx
  on mypaper.subscribers (unsubscribed_at) where unsubscribed_at is null;

create index if not exists subscribers_lang_idx on mypaper.subscribers (lang);

-- Podle tohohle se vybírá, komu ráno a komu v sobotu.
create index if not exists subscribers_cadence_idx
  on mypaper.subscribers (cadence) where unsubscribed_at is null;

-- Co se komu poslalo. Zatím prázdné; naplní se, až budou kampaně.
create table if not exists mypaper.campaigns (
  id           bigserial primary key,
  slug         text not null unique,
  subject_en   text,
  subject_cs   text,
  sent_at      timestamptz,
  recipients   integer,
  note         text,
  created_at   timestamptz not null default now()
);

-- Přehled pro admin: kolik lidí, odkud a v jakém jazyce.
create or replace view mypaper.subscribers_overview as
select
  date_trunc('day', consent_at)::date as den,
  lang,
  cadence                              as rytmus,
  coalesce(source, '(neznámo)')       as odkud,
  count(*)                             as prihlaseni,
  count(confirmed_at)                  as potvrzeni,
  count(unsubscribed_at)               as odhlaseni
from mypaper.subscribers
group by 1, 2, 3, 4
order by 1 desc, 5 desc;

-- Aktivní příjemci — tohle je ten seznam, který se posílá.
create or replace view mypaper.active_subscribers as
select id, email, lang, cadence, source, consent_at, confirmed_at, unsub_token
from mypaper.subscribers
where unsubscribed_at is null and confirmed_at is not null;

-- Dva seznamy, které se opravdu rozesílají. Ranní briefing chodí každý
-- den, sobotní vydání jednou týdně — a nikdo nedostane obojí.
create or replace view mypaper.list_daily as
select * from mypaper.active_subscribers where cadence = 'daily';

create or replace view mypaper.list_weekly as
select * from mypaper.active_subscribers where cadence = 'weekly';
