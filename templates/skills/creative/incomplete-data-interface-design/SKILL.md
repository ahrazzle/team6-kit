<!-- GENERICIZED: 5×{AMOUNT}, 2×{CLIENT}, 1×{RELATIONSHIP} | source: skills/creative/incomplete-data-interface-design/SKILL.md -->
---
name: incomplete-data-interface-design
description: Use when designing UI over sparse, partial, or sampled data.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ux, data, degradation, empty-states, dashboards, search, knowledge-base]
    related_skills: [html-report-design, data-essay-design, interaction-contract-design]
---

# Incomplete Data Interface Design

Use when building any view over a dataset that is **not uniformly populated** — search
results, card grids, catalogs, knowledge-base browsers, dashboards, graph visualisations.
Real corpora have missing fields and views have row caps, and both facts must be designed
for rather than discovered in production.

## Trigger

- Designing cards, lists, tables, or graph labels over records from a real store
- A dataset has optional fields — titles, descriptions, thumbnails, tags
- A view has a `LIMIT`, a page size, a top-N cap, or a layout budget
- Cluster names, tooltips, or snippets look wrong and the data looks fine
- Reviewing an existing interface for honesty about what it shows

## First Principle: Measure The Shape Before Designing The Component

Never design a card and then find out what fills it. **Count the render states first**, in
the store itself. One query changes the design:

```sql
select count(*) as total,
  count(*) filter (where title <> '' and description <> '')            as full_card,
  count(*) filter (where title <> '' and coalesce(description,'') = '') as title_only,
  count(*) filter (where coalesce(title,'') = '')                       as no_title
from items;
```

"28% of items are degraded" is not actionable. **"209 items need a substitute for the
missing description, and 40 have no text at all"** is — because those are two different
components, and one fallback for both looks broken in one case and wastes space in the
other.

## Design Every Tier Explicitly

For each field that can be absent, decide what takes its place. Rank tiers by what is
present, not by what is missing.

| Tier | Present | Treatment |
|---|---|---|
| Full | title + description | Normal component |
| Partial | title only | Promote a **derived** value into the gap — source domain, date, author, type. Never leave the region blank. |
| Bare | neither | Promote the identifier itself (domain as primary, path as secondary) plus an explicit "no metadata yet" state |

**Empty space where content belongs reads as a bug, not as absence.** A card with a title
and a blank paragraph region looks like a failed load; the user waits, then distrusts the
view. A card showing the title and `reddit.com` reads as complete information about an
incompletely-described thing. Same data, opposite feeling.

**Prefer derived over apologetic.** A domain, a timestamp, or a type label is real
information already in the record. "No description available" is an apology that occupies
the same pixels and tells the user nothing.

## Missing Metadata Propagates Into Every Derived Label

This is the failure that gets misdiagnosed most often. Any label computed *from* item text
inherits that text's gaps — cluster names, search snippets, tooltips, auto-tags, headings.

Concretely: a TF-IDF labeller over `title + description` will, on records where both are
empty, fall back to the only string available — the URL. Clusters then name themselves
after domains and URL fragments (`reddit / comments / www`, `twitter / https / com`), and
raw HTML entities that survived ingest show up as label tokens (`x27` from `&#x27;`).

**Two consequences for design work:**

1. When labels look wrong, **check field completeness before blaming the labelling
   algorithm.** They are frequently the same defect wearing a different costume.
2. Fixing labels without fixing the underlying metadata will not hold. Say so rather than
   shipping a cosmetic patch over a data gap.

Also strip HTML entities at ingest. `&#x27;` reaching an embedding or a label is upstream
noise that surfaces far from its origin.

## A Capped View Must Say So

Any view with a `LIMIT` is a **sample presenting itself as a map**, and the gap is usually
enormous:

```
items  500 / 882    = 57%
edges  {AMOUNT} / {AMOUNT} = 2.8%
```

The caps are typically correct — a force-directed layout with 72K edges will not stay
interactive. **This is a labelling problem, not a performance problem.** Do not remove the
cap; disclose it.

- **Cheapest honest fix, one line:** "500 most recent of 882 items · {AMOUNT} strongest of
  {AMOUNT} connections."
- **Better:** make the sample *intentional* — let the user choose the slice (recent, by
  cluster, by source) instead of silently always receiving `ORDER BY created_at DESC LIMIT N`.

Watch for **ordering bias** hiding inside a cap. `ingested_at DESC LIMIT 500` does not show
"the data" — it shows the newest 500 and silently omits the oldest 382. If the omission
correlates with anything the user cares about (age, source, quality), the view is not just
partial, it is skewed. Name the ordering alongside the count.

**Compounding is the real danger.** A capped view of a partially-clustered corpus is a
sample of a sample. If 74% of records fall outside every cluster and the view shows 57% of
records, a user navigating by cluster is seeing a small fraction of what exists and has no
way to know. Disclose each layer.

## A Headline Number Can Be True And Misleading

"17 emergent topic clusters" is accurate and hides that those clusters cover 226 of 882
items. Whenever a summary states a count of *groupings*, state the **coverage** beside it:

> 17 clusters covering 226 of 882 items (656 unclustered)

For a knowledge base or shared resource, this is the highest-value correction available:
its front page is what every future reader trusts first, and **a store that overstates its
own coverage is the one failure a knowledge store cannot afford.**

## Workflow

1. **Query the render-state distribution** before designing the component.
2. **Enumerate tiers** — one per combination of present fields that needs different treatment.
3. **Pick a derived substitute** for each gap from data already in the record.
4. **Find every cap** in the query layer (`LIMIT`, page size, top-N) and compute the ratio
   against the true totals.
5. **Write the disclosure line**, including the ordering, not just the count.
6. **Trace derived labels** back to the fields they are computed from; check those fields'
   completeness before touching the algorithm.
7. **State coverage next to any grouping count** in summaries and documentation.

## Pitfalls

- **Designing the card before counting the render states.** The component ends up assuming
  fields that a quarter of the corpus lacks.
- **One fallback for all degraded states.** Title-only and no-text-at-all need different
  components.
- **Leaving the gap blank.** Reads as a loading failure; costs trust, not just polish.
- **"No description available" as the fallback.** Occupies the same space as a real derived
  value and carries none.
- **Blaming a labelling algorithm for a metadata gap.** Check field completeness first.
- **Presenting a capped view as complete.** Especially a graph view — edge caps are commonly
  under 5% of the real edge set.
- **Disclosing the count but not the ordering.** `LIMIT 500` with `ORDER BY date DESC` is a
  recency-biased sample, not a neutral one.
- **Removing a cap to be honest.** Wrong fix — the cap keeps the view usable. Label it.
- **Quoting a grouping count without coverage.** True and misleading is worse than wrong,
  because nobody checks it.
- **Fixing derived labels cosmetically** while the source fields stay empty. It regresses on
  the next ingest.

## Designing Against A Locked Data Contract

Sometimes the data isn't just sparse — it's **frozen**. A locked `app.json` / schema /
exported fixture that a redesign may not change, with invariants that make certain naive
renderings *wrong* (a self-report affordance on a non-self-reportable field is a
correctness bug, not a UX shortcut). This is the strictest form of this class: the
render-state distribution isn't a query away, it's spelled out in a contract doc, and the
design must bind to real fields.

**Pull the real shapes, don't design from the contract's prose.** Read the contract AND
load the actual shipped artifact (JSON fixture, sample export) and inspect representative
records — exact field values, which fields are empty, the magnitude of the numbers. The
contract says "releasing channel may be empty"; the data says *how many are empty and how
big the numbers get* (e.g. a field documented as an edge case turns out to reach seven
digits in a real persona). Design against the measured magnitudes, not the described ones.

**Bind every decision to a field that exists in the contract.** If a design move needs a
field the contract doesn't have, mark it `[BACKEND]` and stop — don't let the UI invent
data that isn't there (clickable drill-down over a names-only list, an override button on
a `liftable:false` node). The contract's own sharp edges (filtered lists, clipped strings,
empty-guard-defaults) are the design constraints, not obstacles.

**Design the degenerate states FIRST.** The cases that break a naive component — frozen
with *no* remedy, frozen with *all four* remedies, seven-digit magnitudes — are not
afterthoughts; they are the honesty test. A component that renders "needs " with nothing
after it, or collapses `{AMOUNT}` to `1M`, has failed. Enumerate these branches before the
happy path and give each its own copy, not one fallback.

**One load-bearing component carries the product's reframe.** In contract-bound design
there is usually a single component that *is* the point (e.g. a "frozen SP + its remedy"
chip — the instruction the whole product exists to surface). Identify it early, make every
other component subordinate to it, and treat its degenerate branches as acceptance
criteria, not suggestions. A structure question (tabs vs. single-screen) is architecturally
neutral when the app is a stateless render over the locked fixture — confirm that with the
architect rather than treating it as a product gate.

**Honesty is the register, not a mood.** When the product is a capability instrument for
children, the sober un-gamified register is load-bearing integrity (guard families exist
to stop the system rewarding the wrong thing). Resist the pull toward celebration — a
level is a claim someone might check.

## Progressive Coverage: A Surface That Is Still Being Built

A distinct sub-class: not sparse fields *within* records, but whole regions of the data
that **do not exist yet** because content is populated progressively (juz-by-juz,
page-by-page, batch-by-batch). Two rules make this honest without trapping the user:

**1. Navigation must never be trapped by content coverage.** The user can jump anywhere
they want; the *content* shows an honest "not built yet" state, not a dead link or a
broken shell. Free navigation + honest empty state, never the reverse. Show the real
metadata the index already has (name, number, revelation type, page range, size) so the
empty state is informative, then one clear line that this region isn't built yet and
which region *is* the fully-populated reference.

**2. A progress strip turns the limitation into a roadmap.** "1 of 30 juz built · 3%"
with a bar reads as intent, not a bug. Compute it honestly — and that is where the
subtle failure hides.

### The coverage-count pitfall: derive from real data, not navigation metadata

A navigation index often lists a surah's **full** extent ("surah 2: pages 2–49, 286
ayahs") even when only one juz of it is populated (pages 2–21 in the actual file). If
you compute "what's built" from that index's page/surah spans, you overstate coverage —
I built a metric that counted 3 juz as built when only 1 was, because partially-built
surahs appeared in later juz's surah lists.

The honest signal is the **real loaded data**: track which pages/records actually appear
in the content files as they load (a `BUILT_PAGES`-style set populated from the files
themselves, not the index). A region is built only if every page it spans is in that
set. Eager-load the reference region at init so the first render is already accurate.

**Never claim coverage that isn't in the loaded data.** An inflated progress number is
the same failure as an overstated coverage count on a dashboard — true-looking and
misleading, and worse because nobody re-derives it.

**Never fake the pending regions either.** Don't ship empty content files to make a
region look covered; render the honest "not built yet" state with real metadata. Index
coverage (free navigation) and data coverage (actual content) are different things —
decide deliberately which one "navigate anywhere" means.

## References

- `references/{CLIENT}-kb-audit.md` — worked case: measured render-state distribution across an
  882-item knowledge base, the cluster-label degradation traced to empty text fields, and
  the graph view showing 2.8% of its edge set with no disclosure
- `references/contract-bound-design.md` — worked case: {CLIENT} redesign against a locked
  data contract (158-skill capability map) — the FrozenChip load-bearing component, the
  four degenerate branches, and binding every surface to a real field

## Related Skills

- **html-report-design** — visual energy and layout once the data shape is known
- **data-essay-design** — presenting analytical findings; pairs with the coverage-disclosure
  rule here
- **interaction-contract-design** — for the async/event side of the same interface
