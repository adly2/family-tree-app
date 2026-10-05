# Family Tree App

A web application for recording family history — people, relationships, events, sources — and for
**connecting separate family trees** when they turn out to share a person.

Most family history is lost not because nobody knew it, but because it was never written anywhere
connected. One relative knows the names on their grandmother's side; another has the photographs; a
third remembers which village the family left and when. The goal here is one structure that holds all
of it, where a cousin's tree and yours can join at a shared great-grandparent without either family
giving up control of their own records.

> This is primarily a **learning project**. The architecture is chosen to teach relational modeling,
> graph traversal, API design, and performance work on real data — not to be the shortest path to a
> running app. See [CLAUDE.md](CLAUDE.md) for the working agreement.

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Django + Django REST Framework |
| Database | PostgreSQL 18 (Docker) |
| Frontend | TypeScript + React + Vite |
| Visualization | d3-hierarchy (SVG, Canvas above ~500 nodes) |
| Auth | Django sessions + CSRF |
| Tooling | uv (Python), npm (Node), pytest, Vitest, ruff |

The reasoning behind each choice is recorded in [CLAUDE.md §3](CLAUDE.md), so the decisions stay
durable instead of getting re-argued later.

---

## The interesting design problem

A family tree is not a tree. It's a directed acyclic graph with two kinds of node, and the naive model
breaks immediately on real families.

**Unions, not parent pointers.** Putting `mother_id` and `father_id` on a person falls apart on
adoption, step-parents, remarriage, and unknown parents. Instead a `Family` row represents a
*partnership*, and children attach to that union rather than to individuals — the GEDCOM model every
genealogy tool converged on.

**Connected, not absorbed.** Linking two trees must not merge them into one shared pool, or everyone
with access to either tree inherits access to all of it. So `Person.owner_tree` records who *stewards*
a record and never changes, `Family` edges are allowed to cross trees, and a consented `TreeLink`
controls what's visible across the join. The "one huge tree connecting everyone" is computed by
traversal at query time — it is never a stored object.

**The scaling surprise.** Tree size barely matters: ten generations of ancestors is at most 1,024
people whether the database holds ten thousand rows or ten million, and genealogy queries are
inherently local. The expensive part is checking permissions at every hop of a recursive traversal —
which is why the viewer's visible trees are resolved once per request, not per edge.

---

## Roadmap

Each phase ends with something demonstrable and a walkthrough of the concepts behind it.

| Phase | Focus | Demo when done |
|---|---|---|
| **0** | Foundations — repo, uv, Django, Postgres in Docker, custom User, `uuid7()` | `/admin` login works |
| **1** | The data model — Person, Family unions, aliases, events, places, sources | Enter three real generations through the admin |
| **2** | Graph traversal — ancestors, descendants, relationship calculator via lowest common ancestor | `manage.py relate <a> <b>` prints "second cousin once removed" |
| **3** | REST API — DRF serializers, viewsets, tree-scoped permissions, OpenAPI schema | Browsable API at `/api/docs` |
| **4** | Frontend foundation — React, routing, TanStack Query, forms, generated types | Log in and edit your family in the browser |
| **5** | Visualization — pedigree charts, DAG layout, pan/zoom, generation windowing | Click a person, see and explore their tree |
| **6** | Duplicate detection, linking, merging — fuzzy matching, consent flow, undo | Two users link trees at a shared ancestor, merge a duplicate, undo it |
| **7** | Scale & performance — seed 500k people, benchmark, index, cache what measurement justifies | Before/after query-time table |
| **8** | GEDCOM import/export, photos, search | Import a real GEDCOM file |
| **9** | Tests, CI, deploy | Public URL, green CI |

Concepts covered along the way: ER modeling and normalization, through-models, database constraints vs
application validation, BFS/DFS, recursive CTEs, lowest common ancestor, the N+1 query problem, REST
resource design, CORS vs CSRF, server-state vs client-state, the Reingold–Tilford layout algorithm,
record linkage and fuzzy matching, transactions and atomicity, audit logs, query plans and index types,
cache invalidation, parser writing, background jobs, and the test pyramid.

---

## Getting started

Phase 0 is not built yet — these commands become available once it is.

```powershell
# 1. Start Docker Desktop, then bring up Postgres
docker compose up -d db

# 2. Backend
cd backend
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver        # http://localhost:8000/admin

# 3. Frontend (from Phase 4 onward)
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

Requirements: Python 3.14+, Node 20+, uv, Docker Desktop.
