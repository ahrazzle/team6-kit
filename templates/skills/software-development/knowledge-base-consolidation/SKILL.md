<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/software-development/knowledge-base-consolidation/SKILL.md -->
---
name: knowledge-base-consolidation
description: "Build semantic knowledge bases from heterogeneous sources."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [knowledge-base, rag, pgvector, semantic-search, ingestion-pipeline]
---

# Knowledge Base Consolidation

Build semantic knowledge bases that serve both agents and humans from day one. Validates extraction feasibility *before* building infrastructure — the path matters more than the payload.

## When to Use

- User wants to consolidate knowledge from multiple sources (bookmarks, Discord, Notes, Drive, X, files)
- User says "compile everything," "knowledge base," "pull everything together," or "supercharge productivity"
- Agent is asked to build a search/RAG/ingestion system for personal or team knowledge

## Core Principles

1. **Metadata-First Over Extraction** — Pull URL + title + description + tags + surrounding context first. Future agentic capabilities will handle deep extraction when structure is in place.
2. **Source Triage Before Architecture** — Map source landscape (alive/dead/merged, API availability, export friction) before choosing architecture.
3. **Validate Before Scale** — Sample 50+ URLs, measure accessible/extractable/useful percentages, test retrieval quality at simplest level, THEN build full pipeline.
4. **Dual-Path Access** — Every knowledge system serves agents AND humans from day one. Query API for agents, browsable visualization for humans.
5. **Dynamic Over Fixed** — Self-organizing clusters (HDBSCAN) over fixed taxonomies. The map evolves as material accumulates.

## Pipeline Steps

### 1. Source Archaeology
Map every source: platform status, API availability/pricing, export friction, volume estimate, duplication risk.

### 2. Validation Sample
Pull 50-100 items from the highest-value source. Measure accessibility (% not paywalled), extractable metadata, and retrieval quality against real queries.

### 3. Metadata-First Ingestion
For each item: `url`, `normalized_url`, `title`, `description`, `source_type`, `source_id`, `channel_name`, `topic_inferred`, `context_snippet`, `domain`, `content_hash`.

### 4. Quality Gate Filtering
- **Ingest:** External links with context, substantive threads (>30 words), long-form posts (>100 words)
- **Skip:** Reactions/noise, too-short (<15 words), media-only posts
- **Flag:** Borderline cases for manual review

### 5. Storage (pgvector)
PostgreSQL + pgvector as canonical store. One system, one backup story. HNSW index for similarity. Schema: `items`, `item_embeddings`, `cluster_snapshots`, `cluster_memberships`, `item_edges`.

### 6. Graph Construction
Three edge types: similarity (cosine > 0.7), co-occurrence (same URL across sources), shared-channel (same container).

### 7. Emergent Clustering
HDBSCAN on embedding space. No preset k. Auto-label via TF-IDF. Recluster periodically, preserve snapshots for drift tracking.

### 8. Incremental Sync
Cron-based pagination with state tracking. Track known IDs. Rate-limit backoff. Quality filter each batch.

### 9. Dual-Path Access
- **Agent API:** `search()`, `get_item_detail()`, `get_similar()`, `get_topic_map()`
- **Human UI:** Force-directed graph, clickable nodes, search box, tier badges
- **Review Queue:** SLA-driven manual review with auto-archive after 7 days

## Pitfalls

1. Building extraction before validating — You'll build a crawl pipeline for content that's 80% paywalled.
2. Over-engineering storage — pgvector alone suffices for 10k-100k items.
3. Ignoring source organization — Channel names, folder structures, and tags are free first-class metadata.
4. Ingesting without quality gates — Social media bookmarks include reactions and noise.
5. Fixed taxonomies — Let HDBSCAN discover emergent structure.
6. Forgetting the human path — If agents can query it but humans can't browse it, you've built half a system.
7. Discord privileged intents — DM listening requires "Message Content Intent" enabled in Developer Portal.

## References

- `references/pgvector-macos-setup.md` — Compiling pgvector from source for PostgreSQL 16 on macOS
- `references/discord-bot-patterns.md` — Privileged intents, DM listening, rate limiting
- `references/hdbscan-clustering.md` — Emergent topic clustering patterns and noise floor expectations
