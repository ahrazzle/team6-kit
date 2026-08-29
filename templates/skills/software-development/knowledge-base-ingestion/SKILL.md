<!-- GENERICIZED: 5×{CLIENT}, 2×{RELATIONSHIP} | source: skills/software-development/knowledge-base-ingestion/SKILL.md -->
---
name: knowledge-base-ingestion
description: "Ingestion pipelines for heterogeneous knowledge sources."
version: 1.0.0
author: {RELATIONSHIP} ({RELATIONSHIP}), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [knowledge-base, ingestion, clustering, hdbscan, vector-database, metadata]
    related_skills: [{CLIENT}]
---

# Knowledge Base Ingestion

> Build ingestion pipelines for heterogeneous knowledge sources. Quality tiers, incremental sync with state tracking, HDBSCAN dynamic clustering, metadata-first architecture.

## When to Use

- User wants to consolidate knowledge from multiple sources (bookmarks, notes, Discord, feeds) into a central store
- Sources are heterogeneous (mixed quality, mixed format, mixed access method)
- You need to organize knowledge without imposing a fixed taxonomy
- You need to ingest incrementally (APIs, scheduled pulls) without duplicating work

**Don't use for:** Homogeneous single-source ingestion (use source-specific skills). Simple file copying.

## Core Principles

1. **Metadata-first, not deep extraction.** Store URL + title + description + context now. Defer full page crawl. Future agentic capabilities handle deepening.
2. **Quality tiers, not uniform ingestion.** Classify each item as curated/inferred/noise. Don't dilute the index with noise.
3. **Incremental with state tracking.** Track known IDs to avoid re-ingestion. Make sync idempotent.
4. **Dynamic clustering, no fixed taxonomy.** Let clusters emerge from content similarity via HDBSCAN. Recluster as material accumulates.
5. **Continuous incorporation during ingestion.** As new items enter the knowledge base, analyze their *content immediately* and elevate relevant material to Team6 knowledge systems ({CLIENT} patterns, Memory, Soul.md). Do NOT wait until end of session — the user expects ongoing elevation, not retroactive sweeps.

## Quality Tier Taxonomy

Every item gets a `source_tier` classification before ingestion:

| Tier | Definition | Action | Embedding |
|------|-----------|--------|-----------|
| **curated** | User explicitly saved/bookmarked this. High confidence knowledge. | Full ingest | Yes |
| **inferred** | Probably useful but not explicitly curated. Borderline. | Metadata only (title + URL) | No (upgrade later if needed) |
| **noise** | Reactions, greetings, memes, content-free items. | Skip | No |

**Source-specific tier thresholds:**
- **Social media (X, Discord):** Length + engagement heuristics. >200 chars OR 1k+ likes/100+ RTs = curated. <80 chars = noise.
- **Bookmarks:** User saved = curated. External links = curated. Self-referential tweet links = metadata.
- **Notes:** Word count + structure. >50 words with clear topic = curated. <10 words = noise.
- **RSS/Feeds:** Source reputation + engagement signals. Known high-quality sources = curated.

## Incremental Ingestion with State Tracking

Always maintain a state file for each source:

```json
{
  "known_ids": ["id1", "id2", ...],
  "last_sync": "2026-08-20T09:00:00Z",
  "cursor": "pagination_token_if_applicable",
  "total_ingested": 341,
  "total_skipped": 58
}
```

**Pattern:**
1. On each sync run, load state file
2. Fetch new items from source (API, file, etc.)
3. For each item: skip if ID in `known_ids`, else process
4. After successful embedding: append ID to `known_ids`, update `last_sync`
5. Save state file

**Idempotency:** Running the sync twice produces the same result as running it once.

## HDBSCAN Dynamic Clustering

Use HDBSCAN (not K-means, not DBSCAN) for emergent topic discovery. For high-dimensional embeddings (384+ dims), reduce dimensions with UMAP first — dramatically improves coverage.

**Why HDBSCAN:**
- No preset k required
- Handles noise (items that don't belong anywhere)
- Finds clusters of arbitrary shape
- Produces membership probabilities (soft clustering)

**Pipeline:**
1. Load all items with embeddings from vector DB
2. **UMAP reduction:** 384 dims → 15 dims (`n_neighbors=15, min_dist=0.1, metric='euclidean'`)
3. Run HDBSCAN on reduced dimensions with `min_cluster_size=5`, `min_samples=2`, metric=`euclidean`, method=`eom`
4. Auto-label each cluster with top TF-IDF terms from member titles+descriptions
5. Handle URL fragment labels: if TF-IDF produces `www/com/http/amp/x27` terms, fall back to domain-based label (`reddit.com (general)`)
6. Store snapshot + memberships in DB
7. Update `topic_inferred` field on items

**UMAP finding from {CLIENT}:** Reducing 384-dim MiniLM embeddings to 15 dims before HDBSCAN reduced noise from 74% → 28%. The high noise rate was a dimensionality problem, not a clustering failure.

**Iterative parameter tuning:**
- Start with `min_cluster_size=10`. If >80% noise, lower to 5.
- Lower `min_samples` to find more, smaller clusters
- Use `cluster_selection_method="eom"` for stable clusters

**Acceptable noise:** 60-80% noise is normal for metadata-only embeddings. Noise items await richer context (full page crawl) to find cluster homes.

## Schema (PostgreSQL + pgvector)

```sql
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL,
    normalized_url TEXT,
    title TEXT,
    description TEXT,
    source_type TEXT NOT NULL,
    source_id TEXT,
    channel_name TEXT,
    topic_inferred TEXT,
    context_snippet TEXT,
    source_tier TEXT DEFAULT 'curated',
    review_status TEXT DEFAULT 'approved',
    raw_metadata JSONB DEFAULT '{}',
    content_hash TEXT,
    domain TEXT,
    created_at TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE item_embeddings (
    item_id UUID PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
    embedding vector(384),
    model_version TEXT DEFAULT 'all-MiniLM-L6-v2',
    computed_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE cluster_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    computed_at TIMESTAMPTZ DEFAULT now(),
    algorithm TEXT DEFAULT 'hdbscan',
    params JSONB DEFAULT '{}',
    item_count INT,
    cluster_count INT,
    noise_count INT
);

CREATE TABLE cluster_memberships (
    snapshot_id UUID REFERENCES cluster_snapshots(id) ON DELETE CASCADE,
    item_id UUID REFERENCES items(id) ON DELETE CASCADE,
    cluster_label INT,
    probability FLOAT,
    PRIMARY KEY (snapshot_id, item_id)
);

CREATE TABLE item_edges (
    source_item_id UUID REFERENCES items(id) ON DELETE CASCADE,
    target_item_id UUID REFERENCES items(id) ON DELETE CASCADE,
    edge_type TEXT NOT NULL,
    weight FLOAT NOT NULL,
    computed_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (source_item_id, target_item_id, edge_type)
);
```

## Query API (MCP Tools)

```
knowledge_search(query, source_filter?, tier_filter?, limit?)  → ranked items with metadata
knowledge_item(item_id)                                         → full item + embedding
knowledge_similar(item_id, depth?)                             → graph traversal
knowledge_clusters(snapshot_id?)                               → current cluster map
knowledge_cluster_items(cluster_label, snapshot_id?)           → items in a cluster
fetch_content(url)                                              → deep extraction on demand
knowledge_graph_bounds()                                        → graph stats for visualization
```

## Edge Types for Graph

- **similarity** (cosine > 0.7): "these are about the same thing"
- **co-occurrence** (same URL across sources): "these were shared together"
- **shared_channel** (same Discord channel): "these live in the same place"

## Pitfalls

**Don't impose categories at creation.** Let the first reclustering define the initial map. Fixed taxonomies become technical debt.

**Don't re-ingest known items.** Always check state file. Re-ingestion wastes money (API costs) and creates duplicates.

**Don't treat noise as failure.** Items in noise are either awaiting more context or genuinely unique. Both valid states.

**Don't optimize retrieval scores before validation queries.** 0.4-0.5 cosine similarity is normal for metadata-only search. Tune only after real user queries reveal problems.

**Don't crawl everything now.** Metadata-first. Draw the path clearly for future agents. Deep extraction is their job.

## Verification

- State file exists and tracks known IDs
- No duplicate items (check `content_hash` or `source_id`)
- Cluster snapshot saved with membership counts
- Retrieval test: query returns relevant items with scores > 0.4
- Sync is idempotent: running twice = running once

## Related

- [{CLIENT} Absorption]({CLIENT}) — for absorbing context into the collective consciousness
