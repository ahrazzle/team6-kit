<!-- GENERICIZED: 4×{AMOUNT}, 3×{CLIENT}, 3×{RELATIONSHIP} | source: skills/research/knowledge-base-management/SKILL.md -->
---
name: knowledge-base-management
description: "Knowledge base patterns for multi-source consolidation."
version: 1.0.0
author: {RELATIONSHIP}
platforms: [macos, linux]
metadata:
  hermes:
    tags: [knowledge-base, ingestion, consolidation, metadata, extraction]
    related_skills: [llm-wiki, {CLIENT}, xurl, apple-notes, google-workspace]
---

# Knowledge Base Management

> Cross-venture patterns for extracting, organizing, and querying knowledge from heterogeneous sources.

## Trigger Conditions

Use this skill when:
- The user wants to consolidate knowledge from multiple platforms into a central store
- Building a knowledge base, wiki, or structured reference system
- Extracting links, notes, bookmarks, or documents from a specific platform
- Evaluating ingestion architectures (centralized vs. distributed vs. hybrid)

## Core Principles

### 1. Metadata-First, Path Over Payload

**Definition:** When consolidating knowledge from heterogeneous or unknown sources, extract metadata first (URL + title + description + tags + surrounding context) and defer deep content extraction.

**Why:** Current extraction obstacles (paywalls, rate limits, dead links) are temporary. Future agentic capabilities will handle deep extraction when the structure is in place. The path matters more than the payload.

**Application:**
- Pull titles, URLs, descriptions, tags, and surrounding context — not full page content
- Store source metadata for every item: origin, extraction timestamp, transformation history
- Design the data structure so that deep extraction can be layered on top later
- The 20% that yields 80% of value is the metadata structure itself

### 2. Validate Before Scale

**Definition:** Before building an elaborate multi-layer architecture, prove value at the simplest possible level first.

**Sequence:**
1. Sample 50-100 items from the source
2. Categorize by domain heuristics
3. Validate content quality (paywall rate, signal-to-noise, content types)
4. Test retrieval against real queries
5. THEN decide whether to automate and scale

**Why:** Every venture exhibits the same pattern: plan grand systems, build elaborate infrastructure, validate late or never. The correct sequence is: design the interface → mock it up → test it against real queries → THEN build the backend.

**Application:**
- One source → real data → real queries → THEN decide whether to scale
- Do NOT default to PostgreSQL + pgvector + knowledge graph + MCP server before validating that a simpler solution won't serve the need
- A well-organized directory of markdown files with consistent naming + SQLite FTS index may be sufficient

### 3. Source Archaeology Before Architecture

**Definition:** Before designing any ingestion architecture, map the full source landscape: platform status (alive/dead/merged), API availability, export friction, rate limits, and pricing.

**Why:** These facts re-shape the entire architecture. Discovering Pocket is dead with data permanently deleted, Discord has no native export, or browser bookmarks are local files — these change the priority order and feasibility.

**Application:**
- Enumerate all sources before choosing architecture
- Rank sources by value density, not just volume
- Check API tier pricing and endpoint availability before committing to a path
- Document platform status (alive, dead, merged, deprecated) for future reference

### 4. Capture Source Organization as Structure

**Definition:** When the source has inherent organization (Discord channels, Notion databases, folder structures), capture that organization as metadata rather than imposing an external taxonomy.

**Why:** Source organization often encodes the creator's mental model. Discord channels labeled by content category, Apple Notes folders by topic, browser bookmark folders by project — these are pre-built taxonomies that require no ML to extract.

**Application:**
- Store `channel_name` for Discord items
- Store `folder_path` for file-based sources
- Store `database_id` for Notion items
- Use these as initial topic clusters before applying algorithmic clustering

### 5. Knowledge Provenance Chain

**Definition:** Every knowledge item carries an audit trail: origin source, extraction timestamp, transformation history.

**Why:** Provenance enables verification, updating, and retraction. Without it, the knowledge base becomes an untrusted black box.

**Application:**
- Every item stores: source platform, source ID, extraction timestamp, transformation steps
- Raw API responses are preserved alongside normalized data
- Cross-source duplicates are collapsed with provenance tracking (so we know an item came from both Chrome bookmarks and Discord)

## Architecture Patterns

### Centralized RAG Pipeline

- Per-source ingestion scripts
- Chunks + embeddings stored in vector DB (pgvector or ChromaDB)
- Exposed via MCP for agent querying
- ~94% answer accuracy on complex queries per research
- Tradeoff: engineering effort + embedding maintenance

### Distributed Live Access

- Query sources through existing skills in real-time
- No sync lag, zero engineering
- Tradeoff: rate limits, no cross-source semantic search

### Hybrid (Recommended)

- Live access for volatile sources (Notes, Drive, X)
- Centralized vector index for static/reference knowledge (bookmarks, curated documents)
- Periodic re-sync of live sources into the index

## Extraction Workflows

### X/Twitter Bookmarks via xurl

**Endpoint:** `/2/users/{user_id}/bookmarks?max_results=100&tweet.fields=...&expansions=...`

**Key facts:**
- The `bookmarks` shortcut doesn't expose pagination tokens — use raw API access
- Rate limit: 6 seconds between requests (~10 req/min)
- Pricing: {AMOUNT} per owned read (bookmarks, followers, likes)
- 500 bookmarks = {AMOUNT} {AMOUNT} = {AMOUNT}
- **API does NOT return folder/category metadata** — only: id, text, author_id, created_at, entities, public_metrics, lang, possibly_sensitive, referenced_tweets

**Content vs. context:**
- Most X bookmarks ARE the content (tweets themselves)
- External links (GitHub, arxiv) are the minority but high-value
- Surrounding tweet text provides context for why the link was saved

### Discord via Bot Token

**Setup:**
1. Create app at https://discord.com/developers/applications
2. Add bot, enable Message Content Intent (privileged)
3. OAuth2 URL Generator → bot scope → Read Messages/View Channels + Read Message History
4. Invite bot to server(s)
5. Store token as environment variable — NEVER in chat or files

**Extraction pattern:**
- List all channels via API
- Pull messages from categorized channels
- Extract URLs with surrounding context (message text, author, timestamp)
- Skip channels flagged as irrelevant (motivational, off-topic)

**Metadata to capture:**
- Channel name (often encodes topic)
- Message text (commentary + context)
- Author
- Timestamp
- Attachments/embeds

### Apple Notes via memo CLI

- `memo list` — list all notes
- `memo show <id>` — get note content
- Export to markdown for ingestion

### Browser Bookmarks

- Chrome: `~/Library/Application Support/Google/Chrome/Default/Bookmarks` (JSON)
- Safari: `~/Library/Safari/Bookmarks.plist` (plist)
- Dedup via URL normalization before ingestion

## Topic Clustering

### Emergent Clusters (HDBSCAN)

- No predefined categories — topics emerge from the data itself
- Map evolves as material accumulates
- Dynamic subject map reorganizes as new items are added

### Source-Derived Tags

- Use existing channel names, folder structures, or labels as initial tags
- Supplement with hashtag extraction from tweet text
- Cross-reference domains (e.g., `github.com` → code, `arxiv.org` → research)

## Security Conventions

**NO CREDENTIALS IN CHAT.** This is a first-class rule, not a guideline.

- Tokens, API keys, passwords → environment variables or `.env` files only
- If a credential appears in chat, it's considered compromised
- Even "low-risk" tokens (read-only, links-only servers) expose message history, channel lists, and member lists
- Violation protocol: flag immediately, rotate, document the incident

## Deduplication Strategy

- Normalize URLs before comparison
- Content-hash text items to find duplicates across sources
- When duplicates are found, collapse to single canonical item with provenance tracking
- Cross-channel duplicates in Discord reveal topic clusters

## Human vs. Agent Access

**Dual-path access principle:** Every knowledge system must serve both agents and humans from day one.

- Agent-facing: MCP tools for semantic + structured queries
- Human-facing: Browsable markdown mirror or simple UI
- If you design a data structure that's only queryable via API or only browsable via UI, you've failed

## Critical Pitfalls from {CLIENT} Implementation

### API Metadata Verification
**Always inspect actual API response JSON before claiming what fields it returns.** X's `/bookmarks` endpoint returns: `id`, `text`, `author_id`, `created_at`, `entities`, `public_metrics`, `lang`, `possibly_sensitive`, `referenced_tweets`. It does **NOT** return folder/category metadata or user-created labels. Don't approximate inaccessible metadata from tweet text and present it as ground truth. If you need folder data, the only path is the user's data archive export — not the API.

### Pattern Inflation Filters ({RELATIONSHIP}'s Rules)
**Before elevating any finding to a universal pattern, apply these filters:**
1. "Would this have changed a decision on a *previous* venture?" If it only applies going forward → save as experience, not universal rule.
2. "Is this a principle or an implementation detail?" Technology choices (pgvector, HDBSCAN) are implementation details. Strategic approaches (metadata-first, validate-before-scale) are principles.

**Team self-correction pattern:** When one agent ({RELATIONSHIP}) flags pattern inflation or inaccuracies, the others must accept the filter and demote over-elevated items. This is not conflict — it's the QA gate functioning correctly.

### System Boundary Clarity
**Never conflate permissions across platforms.** Discord privileged intents (Message Content Intent for reading DMs) are a Discord Developer Portal setting — they have no relationship to X API permissions. Full read/write access on X does NOT grant a Discord bot the ability to read DMs. State this clearly and separately for each platform.

### Source Tier Key Accuracy
**Verify lookup table keys match DB values exactly.** The database stores `x_bookmarks` (plural) but the code keyed it as `x_bookmark` (singular), causing all 341 items to fall through to a default tier. This is a silent correctness failure — the items happened to land on the correct tier (`curated`) by coincidence, but the moment a `noise` or `inferred` type was added it would also default to `curated`. Fix by normalizing keys at ingest or in the lookup table. Recommended hardening: make the default `unknown` rather than `curated`, so an unmapped source is visibly unmapped instead of silently trusted.

### Documentation Reflects Actual State
**Never write "all items processed" or "0 pending" based on assumption.** Always query the live database. In {CLIENT}, `ORIENTATION.md` stated "55 items pending" while the database had 0 rows with a `review_status` key — a disconnected review loop. The correct pattern: regenerate front-page documentation from actual DB metrics (counts, source tiers, review queue status) before publishing it. A knowledge base that certifies bugs as finished features is the one failure mode a knowledge base cannot afford.

### Specific Updates Only
**When reporting changes, state what specifically changed.** Saying "Agent Ecosystem Intelligence pattern updated with Hermes-specific operational signals" is a claim without evidence. A one-line diff or specific bullet of what changed is required. Address the finding directly: "Added X bookmark extraction reference and quality filtering thresholds" — specific, verifiable, honest.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| High paywall rate (>50%) | Source requires subscriptions | Pivot to metadata-only; deep extraction is temporary obstacle |
| 429 rate limits | Too many API requests | Add sleep intervals (6s for X, varies by platform) |
| Most items uncategorized | Auto-categorizer needs training | User samples 20-30 items to train the classifier |
| Duplicate items across sources | Same link shared multiple times | URL normalization + content hashing before ingestion |
| Token/credential exposed in chat | User pasted secret | Rotate immediately; never paste again; use env vars |
| Review queue shows 0 pending | Ingestion pipeline didn't write review_status key | Verify raw_metadata exists in DB, not just JSONL files |
| Source tier all defaulting to same value | Key mismatch between DB values and lookup table | Normalize source_type keys or use ON CONFLICT DO UPDATE |
