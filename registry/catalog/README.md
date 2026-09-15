# registry/catalog/ — compact skill catalog router

A searchable catalog over the kit's own shipped skill library. It turns a
large library into read-on-demand cards: a query returns **compact metadata
and an exact local read path**, never a skill body. Full bodies load only when
the caller asks, with `--open`.

This layer is a repository artifact (like `build/`), not part of the generated
kit output. It indexes the kit's own `templates/skills/` templates — it never
vendors upstream skill bodies.

## Files

```
registry/catalog/
  README.md                     this contract
  packs/core.json               declared pack: skill_root, license, funnels
  schemas/pack.schema.json      pack declaration shape
  schemas/catalog.schema.json   compact catalog entry shape
  schemas/lock.schema.json      provenance lock shape
  build-catalog.py              generator (+ --check drift gate)
  skill-catalog.py              router CLI (search / audit / list-funnels)
  catalog.json                  generated compact catalog (committed)
  locks/core.lock.json          generated provenance lock (committed)
  run-fixtures.py               the five acceptance fixtures
  fixtures/mini/                hermetic fixture pack + catalog + skill bodies
```

## Quick start

```bash
# Router over the committed core catalog (resolved against the repo root).
python3 registry/catalog/skill-catalog.py search engineering \
  "review a pull request before merge" --limit 3

# Machine-readable candidate cards.
python3 registry/catalog/skill-catalog.py search all "architecture diagram" \
  --format json --engine json

# Show which entries fail closed and why.
python3 registry/catalog/skill-catalog.py audit

# Regenerate after editing skills; --check fails on drift.
python3 registry/catalog/build-catalog.py
python3 registry/catalog/build-catalog.py --check

# Acceptance fixtures.
python3 registry/catalog/run-fixtures.py
```

## Engines: FTS5 fast path and deterministic JSON fallback

`--engine` selects the retrieval path, never the ranking:

- `fts` — an in-memory SQLite FTS5 index retrieves candidates, then the shared
  scorer ranks them.
- `json` — full deterministic scoring over the whole catalog (the fallback).
- `auto` — FTS5 when it is available and safe to represent, else `json`
  (default).

Both engines tokenize identically and apply the **same scorer**, and the FTS
query is a prefix-OR over the query tokens — so the FTS candidate set equals
the scorer's positive set by construction. The two engines therefore return
identical ordered ids and scores for the same catalog; the `fallback` fixture
asserts this. The FTS path exists only to bound candidate retrieval on large
catalogs. `auto` falls back to `json` when FTS5 is unavailable, the query
cannot be represented safely, or the candidate cap is saturated; `fts` fails
closed instead.

Results are bounded: `--limit` defaults to 5 and is capped at 20.

## Fail-closed visibility

An entry is **not router-visible** when any of these hold; it is excluded and
reported by `audit`, never guessed:

- a required provenance field (`id`, `name`, `funnel`, `pack`, `source`,
  `license`, `provenance`, `read_path`) is missing or empty
- its `pack` is not the declared catalog pack
- its `funnel` is not declared by the pack (unclassified)
- its `read_path` escapes the root or does not resolve on disk (stale)
- the lock is present and the entry is absent from it (unprovenanced), or the
  catalog digest does not match the lock (tampered)

## Provenance

Every catalog entry maps to a **declared pack, source, license, and
provenance record**:

- `pack` / `source` — the declared pack (`core`) and its `source` string.
- `license` — the skill's frontmatter `license`; when absent, the pack's
  declared license, recorded as `license_source: pack-default`.
- `provenance` — a stable id derived from the entry id.
- `locks/core.lock.json` — one record per entry plus `catalog_digest`, a
  sha256 over the catalog's canonical entry set. A tampered catalog fails
  closed against the lock.

The generator never writes a skill body into the catalog or the lock.

## Funnels

The pack declares domain funnels mapped to existing skill categories under
`templates/skills/`. Four are declared — `engineering`, `creative`,
`research`, `operations` — and every current category maps to exactly one.
A new category that is not declared is **unclassified** and its skills fail
closed until the pack declares it.

## Determinism

Entries are sorted by id; JSON uses a fixed key order and a trailing newline.
Regenerating from the same tree is byte-identical, so `build-catalog.py
--check` is a clean drift gate.
