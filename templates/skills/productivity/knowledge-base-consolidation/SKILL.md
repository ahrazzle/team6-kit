<!-- GENERICIZED: 3×{AMOUNT}, 1×{CLIENT}, 1×{RELATIONSHIP} | source: skills/productivity/knowledge-base-consolidation/SKILL.md -->
---
name: knowledge-base-consolidation
description: "Consolidate personal knowledge into a searchable base."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [knowledge-base, ingestion, consolidation, rag, personal-data, pgvector]
---

# Knowledge Base Consolidation

Consolidate bookmarks, notes, conversations, documents, and other personal knowledge sources into a unified, searchable, browsable knowledge base.

## When to Use

- User has knowledge scattered across multiple platforms (bookmarks, notes, chat exports, email, documents)
- User wants one central store for agents and humans to query
- User wants semantic search across all their saved content
- User wants to discover emergent topic clusters

## Architecture

### Storage
- PostgreSQL + pgvector for items, embeddings, clusters, and graph edges
- Each item: `{id, url, title, description, source_type, raw_metadata, created_at, ingested_at}`
- Embeddings: 384-dim via `all-MiniLM-L6-v2` (or 768-dim via `all-mpnetbase-v2` for richer matches)
- Edges: similarity, co-occurrence, shared-channel
- Clusters: HDBSCAN with UMAP dimensionality reduction

### Schema
See `references/schema.sql` for the canonical schema.

### Access Layer (Dual-Path)
- **Agent-facing:** Python API with `search()`, `get_item_detail()`, `get_topic_map()`, `get_review_queue()`, `resolve_review()`, `get_stats()`, `get_timeline()`
- **Human-facing:** Force-directed graph visualization with three-tier card degradation
- Both paths consume the same data structure — no dual-write

## Ingestion Pipeline

### Step 1: Source Archaeology
Map the full source landscape before designing ingestion:
- Platform status (alive/dead/merged)
- API availability and pricing
- Export friction
- Rate limits
- **Check for existing user categorizations** (folders, tags, channel names) — use as first-class metadata

### Step 2: Metadata-First Extraction
Pull metadata first (URL + title + description + tags + surrounding context), defer deep extraction. Future agentic capabilities will handle deep extraction when structure is in place.

### Step 3: Quality Filtering
Filter before ingest. Quality heuristics vary by source type:

**Social media bookmarks (X/Twitter):**
- Substantive threads → knowledge base, full embedding
- Reactions/opinions → metadata only or skip
- External links with commentary → link goes in, tweet context is metadata
- Memes/jokes → skip

**Conversations (Grok, Chat):**
- Length + depth heuristics (but length alone is a proxy, not a measure)
- Code blocks, technical terms, structured output signal high value
- Greetings, simple lookups → noise

**Documents:**
- Text-bearing formats (docx, html, rtf, pdf) → extract and ingest
- Images, media → skip or OCR if needed

### Step 4: Source Tier Classification
Every item gets a `source_tier`:
- `curated` — user explicitly saved (bookmarks, notes, manual)
- `inferred` — implied value (likes, follows)
- `noise` — auto-classified as low-value
- `unknown` — default for unmapped sources (NOT `curated`)

### Step 5: Review Queue
- Items needing human judgment go to DB with `review_status='pending'`
- **Set `review_status` at insert time** — never bypass the quality gate
- Review queue SLA: items older than 7 days auto-archive

### Step 6: Embedding + Clustering
- Embed title + description + context as one string
- Run HDBSCAN with UMAP reduction (384→15 dims) for clustering
- Expect 25-30% noise floor for metadata-only items

## UI/UX Principles

### Three-Tier Card Degradation
1. **Full** — title + description
2. **Title only** — show source domain in place of description
3. **Bare URL** — domain as primary label, path as secondary

### Coverage Labeling
When the view shows a sample, label it honestly: "500 most recent of 882 items · {AMOUNT} strongest of {AMOUNT} connections."

### Source Tier Visibility
Expose `source_tier` as a badge so agents and humans can weight results.

## Knowledge Elevation Schema
When consolidating knowledge for a team, classify what gets elevated:

| Category | Destination | Criteria |
|----------|-------------|----------|
| **Operational** | {CLIENT} patterns/skills | Affects how agents work |
| **Environmental** | Memory | Facts about stack/setup |
| **Strategic** | Soul.md or venture docs | Direction/decisions |
| **Noise** | Stays in KB only | Everything else |

## Pitfalls

### 1. "Don't Wait" Has Scale Limits
A directive to proceed autonomously for 39 items does NOT apply to {AMOUNT} items (1,600x jump). Raw personal correspondence (email, DMs) requires explicit user scope definition.

### 2. Length ≠ Knowledge Value
A 50-line regex debug is more valuable than a 200-line poem. Use content signals (code blocks, technical terms, structured output) alongside length heuristics.

### 3. Review Queue Bypass
Every ingestion pipeline MUST set `review_status` at insert time. Bulk-inserting without the quality gate makes the KB unreliable.

### 4. Pattern Inflation
Not every observation becomes a universal pattern. Bar: "Would this change a decision on a future venture we haven't imagined yet?"

### 5. Folder Metadata May Be Inaccessible
X API bookmarks endpoint does NOT return folder metadata. Don't approximate folder names from content — say directly that the data is unavailable.

### 6. Over-Capture
Not every item belongs in the knowledge base. Bar: "Would this change how an agent operates or makes decisions?"

### 7. Multi-Agent Concurrent DB Mutation Deadlocks
When several agents run a big destructive operation (e.g. deleting 63K rows) on the same table, they serialize on row locks — concurrent deletes don't parallelize, they BLOCK each other. If more than one DELETE backend is visible in `ps aux`, kill all but one. See `references/postgres-bulk-mutation.md`.

### 8. Destructive Ops Must Be Restartable
A single-transaction bulk DELETE commits nothing until the end — kill it mid-run and ALL progress is rolled back, restart from scratch. Make destructive ops batch-and-commit-per-batch so completed batches survive a kill and you resume, not restart. The count dropping to zero only happens at commit; a frozen count with an active process may just mean a long final step, not a stall. See `references/postgres-bulk-mutation.md`.

### 9. Verify Live State Before Reporting "Running" / "Done"
Multiple agents reported the mail DELETE as "active" or "dead" — several were wrong. Before asserting a background process's status, check `ps aux` and query `COUNT(*)` yourself. "The process died" and "the count didn't drop" are different claims with different causes; don't conflate them.

## Export / Handoff (Token-Optimized)

When handing parsed data to another team/project, export token-lean rather than shipping raw:
- Drop duplicated fields (same body stored in `description` AND `context_snippet` doubled the file size)
- Metadata-first schema: `id, url, title, subject, sender, date, body, content_hash`
- Trim bodies to ~800 chars with a `…[+N chars]` length marker so the importer knows when to pull full content from the source archive
- Keep the raw archive (e.g. the `.mbox`) on disk for deep extraction later — export is a pointer, not the source of truth

## Verification

- `SELECT COUNT(*) FROM items` matches expected count
- `SELECT COUNT(DISTINCT url) FROM items` equals `COUNT(*)` (unique constraint)
- `SELECT COUNT(*) FROM items WHERE raw_metadata->>'review_status' = 'pending'` matches expected queue
- Semantic search returns relevant results with similarity > 0.4
- Topic map renders without JS errors
