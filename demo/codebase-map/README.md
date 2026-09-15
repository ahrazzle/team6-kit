# Codebase-map proof — static treemap viewer (Slices 2–3)

A self-contained, zero-dependency static treemap viewer for the Team6
codebase-map snapshot contract (`choreography/codebase-map.md`) and its
interaction contract (`choreography/codebase-map-interaction.md`). It renders
**one local fixture** as rectangles, lets you focus and search it, and reports
a read-back receipt.

## Boundaries (read these first)

- **Snapshot, not a live view.** The viewer draws a fixture. It does not
  watch, crawl, parse, or index any repository.
- **No external anything.** No fonts, scripts, styles, images, analytics, or
  network calls. The only fetch is the local fixture, same-origin.
- **Area is a declared measure**, never importance, risk, or quality. **Color
  is a display token**, never a grade.
- **Read-only and metadata-only.** No repository command, no source ingestion,
  no second state store. **No source text, syntax highlighting, dependency
  edges, entity definitions, or live source search are available** — those are
  explicitly out of scope and shown as an unavailable state.

## Run

Serve the repository root over a local static server and open the page (the
fixture is fetched relative to the repository root, so the page needs an
origin — opening the file directly shows a visible error):

```bash
python3 -m http.server 8899          # from the repository root
# then open  http://127.0.0.1:8899/demo/codebase-map/index.html
```

## Selected algorithm

`t6-squarified-v1` — a squarified treemap layout applied to the snapshot's
**declared child order** (it does not re-sort, because child order is part of
the snapshot). This is a Team6 experiment baseline, not a claim about any
other tool's default. An unknown `rendering.algorithm` is rejected; the viewer
never falls back to a default mode.

## Fixture identity

| Field | Value |
|---|---|
| fixture | `examples/codebase-map.valid.json` |
| `source_kind` | `synthetic` |
| sha256 | `3c56bf83cf0555946eee9f0dd888b6431a2d11b2a653c56e88a57bd9c20d5bbb` |
| viewport | 1000 × 640 (fixed logical viewBox) |
| serialization precision | 3 decimal places |

## Interaction (Slice 3)

- **Overview** — the default view shows the directory-level hierarchy of the
  whole snapshot (root focus, `focus_path: ""`).
- **Focus** — select a directory rectangle (click, or Enter/Space when it is
  keyboard-focused) to re-root the viewport to that directory and expose its
  descendants. A breadcrumb (`root / app / core`) shows the focus path.
- **Back / Fit** — `Back` returns focus to the parent directory; `Fit to root`
  resets to the root. Keyboard: `Backspace` = back, `Escape` = fit.
- **Search** — the search box matches normalized relative identities and
  display labels. A hit focuses the containing directory and selects the
  entity, showing its **path, kind, size, color, provenance, and algorithm** in
  the side panel. A miss shows a `no result` state and issues no request.
- **Reload reconstruction** — focus and query are written to the URL fragment
  (`#path=…&q=…`). Reloading reconstructs the same focus from the snapshot
  alone, e.g. `#path=app/core` or `#q=routes.py`.
- **Keyboard & accessibility** — every entity is reachable (`tabindex="0"`,
  `role="button"`, an `aria-label`); the focused entity has a visible focus
  ring; the selected item has an announced text alternative in the side panel.

## Browser verification (read-back)

Serve the root, then capture the post-JavaScript DOM with headless Chrome:

```bash
python3 -m http.server 8899 &
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --user-data-dir=/tmp/cm-profile \
  --virtual-time-budget=6000 --dump-dom \
  "http://127.0.0.1:8899/demo/codebase-map/index.html"
```

Expected read-back (measured):

- Footer receipt names `algorithm t6-squarified-v1`, the fixture, its sha256,
  `viewport 1000x640`, `precision 3`, `rect_count 8` (nodes 3, leaves 5),
  `focus_path ""`, `selected_path null`.
- The SVG carries 11 `<rect>` elements (3 node-box + 3 node-band + 5 leaf) and
  8 text labels; two renders at the same viewport are byte-identical.
- `#path=app/core` → `rect_count 3`, `focus_path "app/core"`.
- `#q=routes.py` → `match_count 1`, `selected_path "app/web/routes.py"`.
- Console: no uncaught errors. Server log shows only same-origin requests —
  **external-request count 0**.

### Diagnostic mode

`?selftest=1` loads the real fixture, then runs the interaction and boundary
cases through the same code paths and prints a `SELF-TEST` block: overview,
focus, back, fit, search hit, search miss, one-leaf, nested nodes,
empty-children fail-closed, unknown algorithm, and a malicious-label check
(labels render as text and cannot execute markup). All 11 cases pass.

`?fixture=<relative path>` points the viewer at another local snapshot — e.g.
`?fixture=../../examples/codebase-map.invalid.json` shows the visible rejection
panel. Absolute or scheme URLs are refused: the viewer only reads relative,
same-origin paths.

## Known limitations

- One algorithm only. `Classic`, `SquarifiedNoSort`, and the ordered variants
  remain comparison candidates in the contract, not implemented modes.
- The layout is a proof, not a production promise: skewed trees may show poor
  aspect ratios. No usability claim is made.
- Search is metadata-only (labels and paths). It never reads source text,
  dependency edges, or entity definitions.
- Nothing here measures importance, quality, or task improvement.
