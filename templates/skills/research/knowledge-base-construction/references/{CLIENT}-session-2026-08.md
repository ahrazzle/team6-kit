<!-- GENERICIZED: 6×{AMOUNT}, 10×{CLIENT}, 1×{RELATIONSHIP} | source: skills/research/knowledge-base-construction/references/{CLIENT}-session-2026-08.md -->
# {CLIENT} Knowledge Base — Session Learnings (2026-08)

Consolidated from a real multi-source knowledge consolidation project. These patterns emerged from building the {CLIENT} knowledge base for a single user with heterogeneous sources.

## Metadata-First Principle (Path Over Payload)

**User's exact words:** "With how fast technological and namely agentic capabilities are progressing, always backload the work... This system is for agents to retrieve from who will only become more capable with time. All we need to do is draw as clear of a path for them to follow as possible."

**Rule:** When consolidating knowledge from heterogeneous or unknown sources, pull metadata first (URL + title + description + tags + surrounding context). Defer full page content extraction.

**Why:** Extraction obstacles that exist today (paywalls, rate limits, JS-rendered pages) will crumble to ash in the face of future agentic capabilities.

## Source Archaeology Protocol

Before designing any ingestion architecture:
1. Map the full source landscape (every platform holding knowledge)
2. Check platform status — alive, dead, merged, deprecated
3. Verify API/export availability
4. Rank by value density (items × quality × uniqueness)

**{CLIENT} example:** Discovered Pocket was dead (exports disabled {CLIENT}, data deleted). Discovered Discord has no native export. Discovered browser bookmarks are local files (Chrome JSON, Safari plist). These facts re-shaped the entire architecture.

## Knowledge Incorporation Patterns

Don't just store knowledge — incorporate it into team knowledge systems. Classification schema:

| Category | Destination | Criteria |
|----------|-------------|----------|
| **Operational** | {CLIENT} patterns/skills | "Would this change how an agent operates or makes decisions?" |
| **Environmental** | Memory | Facts about our stack, setup, or current state |
| **Strategic** | Soul.md or venture docs | Direction, decisions, long-term thinking |
| **Noise** | Stays in local KB only | Everything else — searchable but not elevated |

**When to run:** Automatically as items are ingested, not as a retroactive sweep.

**Pattern inflation guard:** Not every observation from a source becomes a team pattern. The bar is: "Would this change a decision on a future venture we haven't imagined yet?" If it's useful context for the current setup, save it as an experience, not a universal rule.

## Platform Status (2026-08)

| Platform | Status | Notes |
|----------|--------|-------|
| **Pocket** | Dead | Shut down {CLIENT}. Exports disabled {CLIENT}. All data deleted. |
| **X/Twitter** | Active, pay-per-use | Owned reads {AMOUNT}/resource. Public reads {AMOUNT}/resource. Rate limits: 15-min windows. |
| **Discord** | Active, no native export | API requires bot token. No bookmark feature. Manual export via DiscordChatExporter or bot. |
| **Apple Notes** | Active | Access via `memo` CLI. Folders provide free metadata. |
| **Raindrop.io** | Active | API + Pocket-import compatible. Visual bookmark organization. |
| **Notion** | Active | API available. `ntn` skill covers it. |
| **Readwise Reader** | Active | Syncs to Obsidian/Notion/Logseq. API available. |

## X/Twitter Specific Learnings

### API Endpoints for Knowledge Ingestion

| Endpoint | Cost | Notes |
|----------|------|-------|
| `GET /2/users/{id}/bookmarks` | {AMOUNT}/resource | Owned reads rate. Requires user-context OAuth. |
| Activity API (`/2/activity/subscriptions`) | Free delivery | Real-time events. **Requires app-only bearer token auth** — OAuth 2.0 user-context tokens return 403. |
| `GET /2/users/{id}/likes` | {AMOUNT}/resource | Owned reads. Noisy signal (social signaling, humor, passive agreement). |
| `GET /2/users/{id}/followers` | {AMOUNT}/resource | Owned reads. Follow-graph is stronger knowledge signal than likes. |

### X Data Archive Export

If API access is too expensive/restricted, the X data archive download includes bookmarks in `bookmarks.js`. This is a different ingestion path (file parse vs. API), but gets the same data.

### Content Type Distribution in Bookmarks

In the {CLIENT} project, 87% of X bookmarks were tweets/posts (content IS the bookmark), 13% were external URLs (GitHub, arxiv, HuggingFace). This varies by user — bookmark-heavy users may have more external links.

### Quality Filtering for Social Bookmarks

For reaction-heavy sources (social media), classify before ingest:
- **Substantive** (explains concepts, step-by-step) → ingest
- **Reactions/opinions** ("great take," "🔥") → skip
- **External links with commentary** → link as primary, context as metadata

Use engagement metrics as quality signals: a tweet with {AMOUNT} bookmarks is almost certainly substantive; one with 2 is probably a reaction.

## Discord-Specific Learnings

### Bot Token Security

Discord bot tokens are NOT the same as X API tokens. The Discord bot needs "Privileged Gateway Intents" enabled in the Discord Developer Portal to read messages. Two intents are critical:
- **Server Members Intent** — for reading member lists
- **Message Content Intent** — for reading message content (required for DM ingestion)

### DM as Ingest Path

Once privileged intents are enabled, the user can DM the bot a link → bot extracts metadata → ingests into the knowledge base → replies with confirmation. Zero new infrastructure beyond enabling intents.

### Channel Organization = Free Taxonomy

If Discord channels are deliberately organized by content category (as in {CLIENT}'s "{RELATIONSHIP}" server), channel names provide a free taxonomy — no ML needed. Map channel names to topics.

## Retrieval Score Interpretation

Cosine similarity ranges for `all-MiniLM-L6-v2` (384 dims) on metadata-only embeddings:

| Score | Meaning | Action |
|-------|---------|--------|
| **0.7+** | Strong — exact phrase match | Precise retrieval, high confidence |
| **0.5-0.7** | Good — semantic match | Useful retrieval |
| **0.3-0.5** | Decent — loosely related | Finding aid, not reasoning engine |
| **Below 0.3** | Noise | Not what was asked for |

**Key insight:** Pure vector search is a finding aid, not a reasoning engine. It retrieves well when the query mirrors content verbatim. It fails on abstract/conceptual queries — that's expected behavior, not a bug.

**For higher-confidence matches:** Use richer embedding text (combine title + description + context snippet) or a higher-dimensional model (`all-mpnetbase-v2` at 768 dims).

## Audit Patterns

Common failure modes in knowledge bases:
1. **Review queue disconnected** — QA gate reports "0 pending" while items wait unreviewed. Worse than no gate because it produces false confidence.
2. **Source tier key mismatch** — Pipeline writes `x_bookmarks`, lookup keys `x_bookmark`. All items fall through to default silently.
3. **Documentation overstates coverage** — Front page of a knowledge base that lies about its own state is the one failure mode a knowledge base cannot afford.
4. **No unique constraint** — Duplicate URLs silently corrupt the corpus. Schema-level enforcement is required.
5. **No version control** — An ever-evolving, multi-agent resource needs history and rollback.

**Fix order matters:** Add unique constraint BEFORE ingesting missing rows. Otherwise you insert duplicates into a table that cannot then be constrained without a second cleanup pass.

## Validation Queries

Always define 5-10 real queries BEFORE building. Examples from {CLIENT}:
- "Free token inference serving" → returned FreeToken arxiv paper at result #3 (0.43)
- "Stripe payment integration" → returned matching note (0.71)
- "Hermes team routing rules" → returned noise (0.26) because it spans multiple notes but never appears as a phrase

If top-3 results surface what the user would have found manually, the pipeline works. If not, fix the foundation before adding sources.
