<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/knowledge-base-ingestion/SKILL.md -->
---
name: knowledge-base-ingestion
description: "Ingest sources into a searchable knowledge base."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [ingestion, knowledge-base, vector-database, semantic-search]
    related_skills: [apple-notes]
prerequisites:
  commands: [psql, python3]
---

# Knowledge Base Ingestion

Build ingestion pipelines that consolidate heterogeneous data sources into a unified vector store (PostgreSQL + pgvector).

## When to Use

- User wants to consolidate knowledge from multiple platforms (bookmarks, notes, chat logs, exports, APIs)
- Setting up a searchable personal or team knowledge base
- Adding a new data source to an existing knowledge base
- Building RAG (Retrieval-Augmented Generation) systems

## Core Principles

### 1. Metadata-First Over Deep Extraction

Pull metadata first (URL + title + description + tags + surrounding context), defer full page content extraction. Future agentic capabilities will handle deep extraction when the structure is in place.

**Why:** 80% of URLs are paywalled or block simple crawling. Metadata is sufficient for semantic search and retrieval.

### 2. Validate Before Scale

Sample 50+ URLs before building the full pipeline. Measure: % accessible, % extractable, % useful. This prevents building the wrong architecture.

### 3. Dedup Before Embed

Normalize URLs (strip tracking params, collapse domains), hash content, deduplicate BEFORE embedding. Cross-source duplicates reveal natural topic clusters.

### 4. Capture Source Organization

Always capture the source's own organization (folder names, channel names, tags) as first-class metadata. Don't replace with ML-derived categories — augment.

### 5. Sample-then-Scale with Validation Gates

Enforce: sample (50 items) → categorize → validate content quality → test retrieval usefulness → THEN build the full pipeline.

## Architecture

```
[Sources] → [Ingestion Layer] → [Storage Layer] → [Query Layer] → [Agents/Humans]
```

### Storage: PostgreSQL + pgvector

- Single system for structured queries + vector search
- HNSW index on embeddings for fast cosine similarity
- Schema: `items` (metadata) + `item_embeddings` (vectors) + `item_edges` (graph) + `cluster_snapshots` (drift tracking)

### Embedding: Local Models

- Default: `all-MiniLM-L6-v2` (384 dims, fast, privacy-safe)
- Higher quality: `all-mpnet-base-v2` (768 dims) for richer semantics
- Run via `sentence-transformers` Python library

### Query Layer: Dual-Path Access

- **Agents:** MCP tools or Python API (`access_layer.py`)
- **Humans:** Force-directed graph visualization (`arif_map.html`)

## Ingestion Patterns

### API-Based Sources (X/Twitter, REST APIs)

1. Use incremental sync with state tracking (track newest ID/timestamp)
2. Batch inserts (500-1000 items per transaction)
3. Rate-limit with sleep intervals
4. Cost: track per-resource pricing

### File-Based Sources (mbox, HTML, JSON, docx)

1. Parse with format-specific libraries (`mailbox`, `python-docx`, `html.parser`)
2. Clean text: strip NUL bytes, normalize whitespace, cap length
3. Skip spam/low-value with keyword heuristics
4. Key by content hash when no URL exists

### Chat/Conversation Exports

1. Parse message arrays from JSON exports
2. Filter by length and substance
3. Embed full conversation body (produces stronger embeddings than metadata only)
4. Use conversation ID as unique key

### Local Notes (Apple Notes)

1. Export via `memo notes -ex` (requires interactive confirmation — pipe `y\n`)
2. HTML export goes to `~/Desktop/notes/`
3. Parse with `html.parser` (simple div/text extraction)
4. Filter: skip <10 words, numeric-only, gibberish
5. Key by content hash (notes have no URLs)

## Quality Filtering

### Skip Criteria

- Too short: <10-15 words
- Numeric-only content
- Automated/spam patterns (noreply, notifications, digests)
- Media files without extractable text (JPG, PNG, MOV, PSD)
- Spreadsheets (hard to parse meaningfully)

### Tier System

- `curated`: User deliberately saved (bookmarks, manual notes)
- `inferred`: System classified as valuable (semantic match, length)
- `noise`: Auto-classified as low-value
- `unknown`: Unmapped source (default for new types)

## Incremental Sync Pattern

```python
# Track newest timestamp/ID in state file
state = {"newest_id": None, "newest_created_at": None, "known_ids": []}

# Fetch only items newer than last sync
new_items = fetch_items_since(state["newest_created_at"])

# Insert batch, update state
insert_batch(new_items)
state["newest_created_at"] = max(i.created_at for i in new_items)
save_state(state)
```

## Graph Edges

Three edge types for the knowledge graph:
- **Similarity**: cosine > 0.7 between embeddings
- **Co-occurrence**: same URL across sources
- **Shared channel**: same Discord channel/folder

## HDBSCAN Clustering

- Use UMAP dimensionality reduction before HDBSCAN (384→15 dims)
- `min_cluster_size=5`, `min_samples=2` as starting params
- Preserve cluster snapshots for drift tracking
- Auto-label with TF-IDF on titles/descriptions

## Common Pitfalls

1. **Interactive CLI prompts**: Pipe confirmation (`printf 'y\n' | memo notes -ex`)
2. **NUL bytes in email**: Strip `\x00` before inserting to PostgreSQL
3. **UUID type mismatches**: Use subqueries (`WHERE id IN (SELECT...)`) instead of `ANY(%s)` with UUID arrays
4. **Header objects**: Wrap email headers with `str()` before slicing
5. **Pattern inflation**: Don't create universal patterns from single-venture observations
6. **Cost waste**: Always use incremental sync for API sources — never re-fetch entire history

## Verification Checklist

- [ ] Unique constraint on `items.url`
- [ ] Items count matches unique URL count (no duplicates)
- [ ] Review queue reports correct pending count
- [ ] Source tier keys match actual `source_type` values
- [ ] Embeddings exist for all items
- [ ] Graph edges built for new items
- [ ] Cluster snapshot created after major ingestion
- [ ] State file updated for incremental sync
