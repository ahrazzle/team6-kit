<!-- GENERICIZED: 3×{CLIENT}, 1×{RELATIONSHIP} | source: skills/research/knowledge-base-consolidation/SKILL.md -->
---
name: knowledge-base-consolidation
description: "Build a unified knowledge base from heterogeneous sources."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [knowledge-base, ingestion, consolidation, rag, multi-source, metadata]
    related_skills: [xurl, {CLIENT}]
---

# Knowledge Base Consolidation

> Unify chaotic, multi-platform knowledge sources into a single queryable and browsable system with automated quality filtering and classification.

## When to Use

- User wants to consolidate bookmarks, notes, files, or messages from multiple platforms into one knowledge base
- Sources are heterogeneous (social media, chat platforms, document stores, local files)
- The goal is agent-accessible + human-browsable retrieval
- Metadata-first extraction is preferred over deep content crawling

## Architecture

```
Sources → Ingestion → Embedding Store → Access Layer
              ↓                           ↓
        Quality Filter              Agent Tools + Human Viz
              ↓
        Classification → Team6 Knowledge Systems
```

### Storage Layer
- **Vector DB**: pgvector with HNSW index for semantic search
- **Graph**: item edges from similarity + shared-source co-occurrence
- **Clusters**: HDBSCAN emergent clustering (no fixed taxonomy)
- **Mirror**: Markdown files for human browsing

### Access Layer (Dual-Path)
- **Agent path**: Python module with `search()`, `get_item_detail()`, `get_topic_map()`
- **Human path**: HTML force-directed graph visualization
- Both query the same underlying data

## Methodology

### 1. Source Archaeology (before building anything)
- Map ALL sources: platform status (alive/dead), API availability, export friction
- Rank by value density, not volume
- Identify auth requirements and rate limits early
- Check for folder/category metadata availability — many APIs don't return it

### 2. Metadata-First Extraction
- Pull titles, URLs, descriptions, tags, surrounding context first
- Defer deep content crawling to future agentic capabilities
- Cost scales linearly with source size; metadata is cheaper than full content

### 3. Quality Filtering
Apply before embedding to avoid polluting the index:

| Signal | Action |
|--------|--------|
| Substantive threads (explanations, breakdowns) | Ingest with full embedding |
| Reactions/opinions ("great take", "lol", "🔥") | Skip or metadata-only |
| External links with commentary | URL as primary, tweet as context |
| Media-only posts | Skip |
| Too short (<15 words) | Skip |

### 4. Classification Schema ({CLIENT} → Team6)

| Category | Criteria | Destination |
|----------|----------|-------------|
| **Operational** | Affects how agents work, tools to use, patterns to apply | {CLIENT} patterns/skills |
| **Environmental** | Facts about stack, setup, dependencies | Memory |
| **Strategic** | Direction, decisions, long-term bets | Soul.md / venture docs |
| **Noise** | Interesting but not actionable | Stays in KB only |

### 5. Automated Pipeline
- Cron jobs for volatile sources (daily bookmark sync)
- DM/listener triggers for human-initiated ingestion
- Auto-classify on ingest using keyword heuristics
- Review queue with SLA (auto-archive after 7 days)

## Quality Tiers

| Tier | Meaning | Embedding |
|------|---------|-----------|
| `curated` | Explicitly saved, high-signal | Full embedding |
| `inferred` | Auto-categorized with confidence | Full embedding |
| `noise` | Flagged for review or low-signal | Skip or minimal |

## Pitfalls

### Credentials in Chat
**Never** paste tokens, API keys, or secrets into group chat. Once in chat history, they are compromised. Use env vars or `.env` files only. Flag any exposure immediately — even if the user dismisses the risk.

### API Metadata Limitations
Many APIs don't return user-created metadata (e.g., X bookmarks endpoint returns `text`, `author`, `metrics` but NOT folder/category labels). Don't assume folder data exists — verify with a sample pull first.

### Rate Limit Management
Social media APIs enforce 15-minute window limits. Build in sleep intervals (6s between requests for read endpoints). Handle 403/429 with backoff, not hard stops.

### Experience Inflation
Not every observation from a knowledge sweep is a universal pattern. Apply filters:
1. "Would this have changed a decision on a previous venture?" If no → experience, not pattern
2. "Is this a principle or implementation detail?" If implementation → memory, not pattern

### Retrieval Quality Baseline
Cosine similarity 0.4-0.5 is normal for metadata-only embeddings. Don't optimize embedding strategy until validated against real user queries.

## Support Files

- [references/x-bookmark-extraction.md](references/x-bookmark-extraction.md) — X API bookmarks endpoint, pagination, rate limits, cost
- [references/social-media-quality-filtering.md](references/social-media-quality-filtering.md) — Heuristic filters for Twitter/Discord content
- [references/discord-bot-setup.md](references/discord-bot-setup.md) — Bot creation, privileged intents, DM listener architecture

## Verification

- Semantic search returns results for known queries
- Cluster count stabilizes (not everything in one basket)
- Review queue processes within SLA
- No credentials in chat history
- Cost monitoring for pay-per-use APIs
