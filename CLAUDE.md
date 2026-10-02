# CLAUDE.md

Operating instructions for Claude Code on this project. Read this first, every session.

---

## 1. What this project is

Family history disappears because it lives in scattered heads and shoeboxes instead of one connected
structure. This is a web application where families record people and relationships, and where two
separate family trees can be **connected** when they turn out to share a person — a cousin's tree and
yours joining at a shared great-grandparent.

Connecting trees does **not** fuse them into one blob. That distinction drives the whole data model
(see §6).

**The primary goal is learning.** This is built to understand every line, not to ship fast. A
working feature that cannot be explained is a failed feature. The stack in §3 favors mature,
well-documented tools for the same reason: the hard thinking belongs in the domain model, not in
fighting the tooling.

---

## 2. Working agreement

The first two rules come directly from the user and matter more than anything else in this file.

### Hard rule: small batches

One unit at a time — a single model, a single endpoint, a single component. **Roughly 40 lines of new
code as a ceiling**, then stop, explain what was just written, and wait for a go-ahead before
continuing.

Never dump multiple files or a whole feature in one turn, even when the pieces are obviously related
and it would be "more efficient" to do them together. It is not more efficient. Code the user has to
catch up on later is a net loss.

### Hard rule: ask before writing

At the start of each unit, list the functions and methods it needs, then **ask which ones the user
wants to write themselves.** Write only the ones handed over, then review what the user wrote.

Ask this every single time, not once per phase. The answer changes depending on whether the concept is
new or familiar.

### The rest

- Explain *why* before *what*. No unexplained code, no "just trust me" blocks.
- Introduce one new concept at a time. Name it, say what problem it solves, then use it.
- Comment the non-obvious lines only. No noise comments on `import os`.
- Never add a dependency without stating what it replaces and what the tradeoff is.
- Never optimize without a measurement first — an `EXPLAIN ANALYZE` or a timing, not a hunch.
- Stop at each phase boundary rather than racing ahead into the next one.
- When the user's reasoning is partly wrong, say which part and why. Don't smooth over it.

---

## 3. Stack, and why

These are settled. Don't re-litigate them without a new reason.

| Decision | Choice | Why |
|---|---|---|
| Backend | **Django + Django REST Framework** | A data-heavy relational domain needs a mature ORM, real migrations, and auth/permissions on day one. The built-in admin is the deciding factor: it makes genealogy data entry possible before any frontend exists, so Phase 1 can be tested against real family data. FastAPI was the alternative and is excellent for async I/O-bound services, but here it would mean hand-assembling the ORM, migrations, admin, and auth that this project needs immediately. |
| Database | **PostgreSQL 18 (Docker)** | Recursive CTEs for traversal, `pg_trgm` for fuzzy name matching, real query plans. v18 also has `uuid_extract_timestamp()`. |
| Frontend | **TypeScript + React + Vite** | Static types across the API boundary catch model/UI drift at compile time rather than in the browser. React has the mature visualization ecosystem (d3) that Phase 5 depends on. |
| Primary keys | **UUIDv7, generated in Python** | Globally unique, so two trees never collide on connect; time-ordered, so B-tree inserts append at the right edge instead of scattering. |
| Tree model | **Private trees, connected rather than absorbed** | Separate families keep separate trees. See §6. |
| Auth | **Session + CSRF** (JWT covered as a lesson, not used) | More secure for a same-site SPA and fewer moving parts than refresh-token rotation. |

Pin exact versions at install time and note them in `backend/pyproject.toml` — prefer the current
Django LTS.

---

## 4. Repo layout

```
Family Tree App/
├── CLAUDE.md
├── README.md
├── .gitignore
├── docker-compose.yml          # postgres (redis added in Phase 7)
├── .env.example
├── backend/
│   ├── pyproject.toml          # uv-managed
│   ├── manage.py
│   ├── config/                 # settings/, urls.py, asgi.py, wsgi.py
│   └── apps/
│       ├── core/               # uuid7(), abstract base models, shared mixins
│       ├── accounts/           # custom User model
│       ├── trees/              # Tree, TreeMembership, TreeLink, permissions
│       ├── people/             # Person, Family, PersonAlias, Event, Place, Source
│       ├── graph/              # traversal + relationship calculator (no models)
│       └── merge/              # duplicate detection, merge execution, audit log
└── frontend/
    └── src/
        ├── api/                # generated OpenAPI types + fetch client
        ├── features/           # auth/, people/, tree/, merge/
        ├── components/
        └── routes/
```

`apps/graph/` holds no models on purpose — it is query and algorithm code over the `people` models.
Keeping it separate stops traversal logic from scattering into model methods.

---

## 5. Commands

Available from Phase 0 onward. Run from the repo root unless noted.

```powershell
# Database (Docker Desktop must be running first)
docker compose up -d db
docker compose ps                   # wait for "(healthy)", not just "Up"
docker compose down                 # stops containers, KEEPS your data
docker compose down -v              # also DELETES the volume - wipes the database

# psql — use the container's client, NOT the psql on PATH (see §9)
docker compose exec db psql -U familytree -d familytree

# Backend (from backend/)
uv sync                             # install/lock dependencies
uv run manage.py makemigrations
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver          # http://localhost:8000/admin
uv run pytest
uv run ruff check . && uv run ruff format .

# Frontend (from frontend/)
npm install
npm run dev                         # http://localhost:5173
npm run test
npm run build
```

---

## 6. Data model invariants

These are the load-bearing decisions. Breaking one silently is the worst thing that can happen to this
project.

### Union nodes, not parent pointers

A naive model puts `mother_id` / `father_id` on `Person`, and it collapses on adoption, step-parents,
remarriage, and unknown parents. Instead, following the GEDCOM standard every genealogy tool uses:

```
Person ──┐
         ├─< Family >─┬── partners  (through FamilyPartner: role, start/end date)
Person ──┘            └── children  (through FamilyChild: birth|adopted|step|foster)
```

A `Family` is a **union** — a node representing a partnership. Children attach to the union, not to
individuals. Someone with two marriages belongs to two `Family` rows.

### Ownership and connectivity are different things

`Tree` must never do both jobs at once. If connecting two trees fused them into one `Tree` row, then
everyone with access to either tree would gain access to all of it — a cousin's extended family
reading your living children's records. Unacceptable, and unfixable after the fact.

- **`Person.owner_tree`** — the tree that *stewards* this record. Never changes, never merges away.
  This is the permission anchor, and it keeps each tree bounded at human scale.
- **`Family` edges may cross trees.** This is how one tree connects to another: a shared
  great-grandparent's union links people stewarded by different trees.
- **`TreeLink`** — an explicit, consented connection between two trees, carrying its own visibility
  setting (generations exposed across the link, whether living people are included).
- **The "one huge tree connecting everyone" is derived, never stored.** It is whatever traversal finds
  when it walks across links the current viewer is permitted to cross.

### Tombstones, not deletes

Merging person A into B sets `A.merged_into = B` and keeps the row. Old links and bookmarks still
resolve instead of 404ing, and the merge stays undoable. Every merge writes a `MergeLog` row.

### Enforced in the database, not only in Python

- Every `Person` has exactly one `owner_tree`.
- No cycles — nobody is their own ancestor. Checked on write.
- A parent's birth date precedes the child's — a *warning*, not a hard error. Real data is messy and
  rejecting it loses information.
- Dates are partial-friendly. `circa 1890` and `before 1900` are normal genealogical values, so a
  plain `DateField` cannot express reality — store precision alongside the value.

### On performance

Tree size is not the threat. Genealogy queries are inherently **local**: ten generations of ancestors
is at most 2¹⁰ = 1,024 people whether the database holds 10k rows or 10M, and the screen only ever
renders a few hundred nodes.

What *does* get expensive is checking permissions at every hop of a recursive traversal. The mitigation
is to resolve the viewer's visible tree IDs **once per request** (a short list), then let the CTE filter
on `owner_tree_id IN (...)`, which stays index-friendly. Built in Phase 3, measured in Phase 7.

---

## 7. Conventions

- **UUIDv7 primary keys everywhere**, from `apps/core/ids.py`. Never `AutoField`.
- **Type hints on all Python.** They are a teaching tool here, not decoration.
- `snake_case` in Python, `camelCase` in TypeScript. Serializers bridge the two.
- **Raw SQL only for documented recursive CTEs**, always with a comment explaining what the query
  walks and why the ORM can't express it.
- **No business logic in serializers or React components.** Domain logic lives in the app's service
  or query module so it can be tested without HTTP.
- Tests alongside the code from Phase 2 onward, not deferred to Phase 9.
- TS types for the API are **generated from the OpenAPI schema**, never hand-written — that's what
  keeps frontend and backend from drifting.
- **Test data is fictional. Always.** Fixtures, factories, and seed scripts use invented people, never
  real relatives. This repository is public: no real names, dates, or places in committed test data, no
  GEDCOM exports, no screenshots showing living people. Real family data lives only in the local
  database, which is a Docker volume outside the repo.
- `uv.lock` is committed, `.venv/` is not. The lockfile pins exact resolved versions so the project
  builds identically elsewhere; the virtualenv is a local build artifact.

---

## 8. Current phase

**Phase 0 — Foundations. In progress.**

| Unit | What | State |
|---|---|---|
| 1 | Postgres via Docker Compose | done |
| 2 | Dependencies via uv | done |
| 3 | `startproject`, settings split, `.env` wiring | next |
| 4 | `apps/core/ids.py` — `uuid7()` + test | user writes |
| 5 | Custom User model | user writes the model, Claude wires it up |

Done when `manage.py runserver` serves a working `/admin` login and `pytest` shows `uuid7()` producing
increasing IDs.

The full ten-phase roadmap lives in `README.md`. Update this section when a phase completes.

---

## 9. Environment gotchas

Verified on this machine: Python 3.13.7, Node 24.14.0, npm 11.9.0, uv 0.9.11, git, Docker 28.5.1.

- **Docker Desktop is not running by default** on this machine. `docker compose up` fails with a
  missing `dockerDesktopLinuxEngine` pipe until Docker Desktop is started.
- **The `psql` on PATH is the rtools/mingw build**, not a matching Postgres client. Using it produces
  confusing client/server version errors. Always go through
  `docker compose exec db psql -U familytree`.
- **The repo path contains a space** (`...\Desktop\Family Tree App`). Quote paths in every shell
  command.
- The project sits inside a OneDrive folder, but **this OneDrive is inactive** and behaves as an
  ordinary local directory, so no sync exclusions are needed. Git plus a remote is the real backup.
- **Python on Windows defaults to cp1252, not UTF-8.** `Path.read_text()` without
  `encoding="utf-8"` crashes on any non-ASCII character. Always pass it explicitly — this will matter
  a lot in Phase 8, since GEDCOM files arrive as UTF-8, ANSEL, or Windows-1252 depending on which tool
  exported them.
- **Postgres 18 changed the Docker data path.** The volume mounts at `/var/lib/postgresql`, not the
  `/var/lib/postgresql/data` every older tutorial shows. See the comment in `docker-compose.yml`.
- Python 3.13 has no `uuid.uuid7()` — that landed in 3.14. We generate v7 ourselves in
  `apps/core/ids.py` rather than add a dependency, and app-side generation is what Django wants anyway
  so the PK exists before INSERT.
