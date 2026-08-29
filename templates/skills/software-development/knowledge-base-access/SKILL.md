<!-- GENERICIZED: 1×{AMOUNT}, 1×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/knowledge-base-access/SKILL.md -->
---
name: knowledge-base-access
description: "Build access interfaces for knowledge consolidation systems."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [knowledge-base, access-layer, visualization, rag, metadata, quality-gate]
---

# Knowledge Base Access Systems

> Design and maintain the interface layer for knowledge consolidation — where heterogeneous sources (bookmarks, notes, chat exports) become a searchable, browsable index for both agents and humans.

## When to Use

- Building an access layer over a vector DB / knowledge index
- Designing visualization for knowledge graphs or topic cluster maps
- Adding quality filtering for ingested content
- Fixing silent-failure modes in QA/review queues
- Handling metadata-poor items (many items lack title/description)

## Core Principles

### 1. Metadata-First, Not Deep Extraction

Pull url + title + description + tags + surrounding context first. Deep page crawl is deferred.

### 2. Three-Tier Card Degradation

| State | What Exists | What to Show |
|-------|-------------|--------------|
| Full | title + description | Title (linked) + description |
| Title only | title, no description | Title + source domain as substitute |
| Bare URL | neither | Domain as primary, path as secondary |

Never render empty space — an empty region reads as a loading failure.

### 3. Coverage Labeling for Sampled Views

Always label what is shown vs total:
```
"500 most recent of 919 items - 2000 strongest of {AMOUNT} connections"
```

### 4. Quality Gate Disconnection Detection

A QA gate that reports clean while disconnected is worse than no gate. Fix order:
1. Add schema constraints first
2. Ingest only genuinely missing items
3. Then reconnect the gate

### 5. Source Tier Alignment

Lookup tables must use exact same keys as the database. Default tier should be unknown, not curated — an unmapped source should be visibly unmapped.

### 6. Review Queue SLA

Flagged items without deadline accumulate forever. Auto-archive items past 7 days. Show queue count prominently.

### 7. Dimensionality Before Clustering

High noise rates (74% unclustered) often indicate dimensionality problem, not clustering failure. Reduce dimensions (UMAP 384 to 15) before tuning HDBSCAN.

## Procedure: Building an Access Layer

1. Unify schema - every source feeds same table
2. Quality gate at ingest - classify before embedding
3. Dual-path access - agent (Python) + human (HTML) simultaneously
4. Enrich with tier and status fields
5. Sample with metadata - always return counts
6. Three-tier rendering in UI

## Pitfalls

**Silent QA disconnect.** Review queue reads from empty column while items wait in JSONL file. Always verify gate reads from where items actually are.

**Lookup key drift.** DB stores plural, code keys singular. Nothing looks broken because default happens to be correct.

**Clustering noise panic.** 74% noise sounds like failure. Often just high-dimensional sparse embeddings.

**Empty space as loading failure.** Substitute domain for missing description. Empty card reads as broken.

**Re-reviewing already-ingested items.** needs_review.jsonl may contain items already in DB. Ingest only genuinely missing.

## Verification

- Search returns results with similarity scores
- All source types map to correct tiers
- Empty-title items render with domain as label
- Topic map shows coverage note
- Review queue matches actual flagged items in DB

## Related

- {CLIENT} - for absorbing knowledge into consciousness system
