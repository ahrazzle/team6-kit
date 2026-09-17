# Codebase-map interaction contract (v1)

> This contract governs how a viewer interacts with a codebase-map snapshot
> (`choreography/codebase-map.md`). Interaction is **metadata-only**: it may
> navigate labels and normalized identities already present in the snapshot,
> and must never ingest source text, execute a repository command, fetch a
> remote resource, or infer structure the snapshot does not contain.
>
> **Why:** `choreography/artifact-contract.md` requires that state be
> reconstructable from durable evidence rather than a hidden live process. A
> focus, a search, and a reload must all resolve to the same immutable input —
> the snapshot plus a selected identity or query. No second state store, no
> session database, no watcher.
>
> **Provenance:** this is a fresh Team6 interaction contract. It reimplements a
> narrow progressive-disclosure idea; it copies no navigation, search, minimap,
> controller, or UI text from any external project. The module names in a public
> visualizer are evidence of decomposition, not a template.

## Model

Three inputs fully determine the view:

1. the snapshot (`choreography/codebase-map.md`),
2. `focus_path` — the entity whose subtree fills the viewport (default: the
   root, `""`),
3. `query` — an optional metadata search string.

Nothing else. `selected_path` and the detail read-back are **derived** from
those three and are announced back in the receipt.

## Behaviours

| Behaviour | Rule |
|---|---|
| **Overview** | The default view (`focus_path: ""`) shows the directory-level hierarchy of the whole snapshot. |
| **Focus / zoom** | Selecting a `Node` re-roots the viewport to that node and exposes its descendants **only when they are present in the snapshot**. Selecting a `Leaf` selects it; it has no descendants to reveal. |
| **Back** | Returns focus to the parent of the current `focus_path`; at the root it is a no-op. |
| **Fit** | Resets `focus_path` to the root (`""`). |
| **Search** | Matches the query against **normalized relative identities and display labels** (case-insensitive substring). A match focuses the matching entity's containing directory and selects the entity, showing its normalized path, kind, size, and provenance. |
| **No result** | A query with no match shows an explicit no-result state. It issues **no** repository or network request. |
| **Unavailable detail** | Source text, syntax highlighting, dependency edges, entity definitions, and live source search are **out of scope** and shown as an explicit unavailable state. The viewer never infers or fabricates them. |
| **Keyboard** | Every entity is keyboard-reachable (`tabindex`, `role="button"`, an `aria-label`). Enter/Space selects and focuses; the focused entity has a visible focus indication. The selected item has a text alternative (an announced detail region). |
| **Reload reconstruction** | Focus and query are serialized into the URL (`#path=…&q=…`) — these two forms are the only persisted state. Reloading with that fragment reconstructs the same focus and the same query-derived selection from the snapshot alone. A leaf click-selection (`selected_path` set by activating a `Leaf`) is **not** persisted: it is derived view state, and a reload restores the focus, not the leaf. |

## Rendering safety

- Labels are written as **text**, never as markup. A label containing HTML or
  script characters renders verbatim and cannot execute.
- Tooltips and the detail pane use the snapshot's **declared** semantics for
  size and color. Unknown semantics stay unknown.

## Receipt

An interaction receipt records, at minimum:

| Field | Rule |
|---|---|
| `fixture_sha256` | SHA-256 of the snapshot bytes (the durable input) |
| `focus_path` | the current focus identity |
| `selected_path` | the currently selected identity (or `null`) |
| `query` | the current search string |
| `match_count` | number of metadata matches for the query |
| `algorithm` / `viewport` | echoed from the rendering receipt |

The receipt proves the view is derived from the snapshot plus a selected
identity/query — not from an in-memory-only event. It is **not** a claim that
the map is live or that any task is improved.

## Explicitly out of scope for this slice

Code thumbnails, semantic/syntax highlighting, dependency graph, architecture
parser, entity database, big-grep index, live source search, live repository
watching, and any hosted/telemetry surface. If a request needs one of these,
stop: that is a new architecture decision, not an interaction detail.
