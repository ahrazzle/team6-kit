<!-- GENERICIZED: 5×{CLIENT}, 1×{RELATIONSHIP} | source: skills/research/knowledge-base-construction/SKILL.md -->
---
name: knowledge-base-construction
description: Build searchable knowledge bases from heterogeneous sources.
trigger: "Use when the user wants to aggregate knowledge from multiple heterogeneous sources (notes, bookmarks, files, cloud docs, social saves) into a searchable personal/team knowledge base."
version: 1
author: {RELATIONSHIP}
license: MIT
metadata:
  hermes:
    tags: [knowledge-base, ingestion, embeddings, vector-database, RAG]
    related_skills: [product-discovery, grounded-citations, session-librarian]
---

# Knowledge Base Construction

Build searchable knowledge bases from heterogeneous sources. Validated against a real multi-source aggregation session (project "{CLIENT}", {CLIENT}).

## When to Use

Use this skill when the user wants to:
- Aggregate knowledge from multiple platforms (Apple Notes, Google Drive, X bookmarks, browser bookmarks, local files) into a searchable index
- Build a RAG-enabled knowledge base for AI agents to query
- Migrate from chaotic distributed storage to a unified semantic search system

Do NOT use this skill for:
- Single-source organization (just use that source's native tools)
- Real-time collaboration features (this is personal/team knowledge archival)
- Public-facing knowledge bases (this is for private/team use)

## Core Methodology: Validate Simplest First

Never scaffold infrastructure before validating the simplest version works. The pattern that works:

1. **Source inventory** — Map every platform holding knowledge. Check for dead data *before* building connectors (e.g., Pocket shut down {CLIENT}, exports disabled {CLIENT} — data is gone if not exported beforehand).
2. **Value ranking** — Identify the 20% of sources that yields 80% of value. Ask the user to rank sources by importance.
3. **Export a sample** — 20-30 items from the highest-value source. Manual export, no automation.
4. **Embed and test** — Embed the sample, run 5-10 *real* queries the user actually needs answered.
5. **Measure score distribution** — Interpret cosine similarity scores:
   - **0.6+**: Strong — precise match, useful retrieval
   - **0.4-0.6**: Decent — related but not exact
   - **Below 0.4**: Noise — loosely related, not what was asked
6. **Validate or abandon** — If results are useful, THEN automate and scale. If not, fix embedding/chunking strategy before adding sources.

## Architecture: Hybrid (Live + Centralized)

- **Live-pull** for volatile sources (Apple Notes, Google Drive, X/Twitter) — cron-scheduled, upsert on `modified_at`. Access via existing skills/CLIs (`memo`, `gws`, `xurl`).
- **File-parse** for static sources (browser bookmarks JSON/plist, local markdown/txt/PDF) — one-time ingestion with optional manual re-trigger.
- **Centralized vector index** for cross-source semantic search. One index, multiple connectors.

## Tooling Choices (with reasoning)

| Choice | Recommendation | Why |
|---|---|---|
| **Vector DB** | ChromaDB (embedded) | Pure Python, no server, fastest path to working system. Migrate to pgvector later only if scale demands it. |
| **Embeddings** | `sentence-transformers` with `all-MiniLM-L6-v2` (local) | Data never leaves the machine — non-negotiable for sensitive content. Quality is strong for retrieval. |
| **Chunking** | Paragraph-level with overlap for prose; whole-note for short notes; section headers as metadata | Balances granularity with context preservation. |
| **Agent interface** | MCP server wrapping the vector DB (eventually) | Single `knowledge_search(query, source_filter?, limit?)` tool all agents share. Not for the first prototype — validate first. |

## Metadata Schema

Every chunk must carry:

```
{
  source,           // "apple-notes" | "google-drive" | "x" | "browser-bookmarks" | "local-file"
  source_id,        // original ID from the source system
  title,            // note title / doc name / bookmark title
  chunk_index,      // 0-based index within the source document
  total_chunks,     // total chunks for this source
  word_count,       // chunk word count
  ingested_at,      // ISO timestamp
  folder?,          // Apple Notes folder name (free metadata, improves filtering)
  url?              // original URL if applicable
}
```

Do not drop free metadata (folders, tags, dates) — it improves retrieval filtering at zero cost.

## Connector Inventory (macOS)

| Source | Access Tool | Blocker |
|---|---|---|
| Apple Notes | `memo` CLI (`brew install antoniorodr/memo/memo`) | Install needed |
| Google Drive/Docs | `gws` CLI + OAuth | Google OAuth client setup (~5 min user time) |
| X/Twitter | `xurl` CLI (`brew install --cask xdevplatform/tap/xurl`) | Paid X Developer account + auth |
| Chrome Bookmarks | JSON at `~/Library/Application Support/Google/Chrome/Default/Bookmarks` | Direct file read, no tool needed |
| Safari Bookmarks | plist at `~/Library/Safari/Bookmarks.plist` | Direct file read, plist parser needed |
| Local files | Terminal / `read_file` | None |

## Critical Pitfalls

1. **Don't build connectors for dead data.** Verify the platform still exists and exports are still possible before writing a connector.
2. **Don't declare victory on self-validation.** The builder testing their own system is worthless. The user must run the queries and confirm results are useful.
3. **Don't abstract before you have two implementations.** Storage abstraction layers for a migration that will never happen are speculation, not architecture. YAGNI.
4. **Don't build on a weak foundation.** If phrase-matched lookups work (0.6+) but conceptual queries fail (0.4-), that's expected behavior for embedding retrieval. Know what your system is good at before scaling.
5. **Browser bookmarks are near-zero knowledge value.** The value is in the *linked content*, not the bookmark metadata. Ingesting bookmarks means crawling each URL — a completely different and harder problem.

## Validation Criteria (define BEFORE building)

Ask the user for 5-10 real queries they've recently searched for. Examples of good validation queries:
- Specific: "Xplorr logo decisions — rejected options and rationale"
- Cross-cutting: "Hermes team routing rules — who handles what?"
- Conceptual: "{CLIENT} scholar inclusion criteria"

Run these exact queries against the embedded sample. If top-3 results surface what the user would have found manually, the pipeline works. If not, fix the foundation before adding sources.

## Reference Files

- `references/platform-status-2026-08.md` — dead platforms, active export paths, macOS file locations, embedding score interpretation
