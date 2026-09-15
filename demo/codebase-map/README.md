# Codebase-map proof — static treemap viewer (Slice 2)

A self-contained, zero-dependency static treemap viewer for the Team6
codebase-map snapshot contract (`choreography/codebase-map.md`). It renders
**one local fixture** as rectangles and reports a geometry receipt.

## Boundaries (read these first)

- **Snapshot, not a live view.** The viewer draws a fixture. It does not
  watch, crawl, parse, or index any repository.
- **No external anything.** No fonts, scripts, styles, images, analytics, or
  network calls. The only fetch is the local fixture, same-origin.
- **Area is a declared measure**, never importance, risk, or quality. **Color
  is a display token**, never a grade.
- **Read-only.** No repository command, no source ingestion, no second state
  store.

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

## Browser verification (read-back)

Serve the root, then capture the post-JavaScript DOM with headless Chrome:

```bash
python3 -m http.server 8899 &
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --user-data-dir=/tmp/cm-profile \
  --virtual-time-budget=6000 --dump-dom \
  "http://127.0.0.1:8899/demo/codebase-map/index.html"
```

Expected read-back (Slice 2 measured): footer receipt line names
`algorithm t6-squarified-v1`, the fixture, its sha256, `viewport 1000x640`,
`rect_count 8` (nodes 3, leaves 5); the SVG carries 11 `<rect>` elements
(3 node-box + 3 node-band + 5 leaf) and 8 text labels; two renders at the same
viewport are byte-identical. Console: no uncaught errors. Server log shows
only same-origin requests — **external-request count 0**.

### Edge cases (diagnostic mode)

`?selftest=1` runs the contract's boundary cases through the same render path
(inline objects only, no files, no network) and prints a `SELF-TEST` block:
one-leaf renders, nested nodes render, an empty-children snapshot fails closed
with no partial map, and an unknown algorithm is rejected.
`?fixture=<relative path>` points the viewer at another local snapshot — e.g.
`?fixture=../../examples/codebase-map.invalid.json` shows the visible rejection
panel. Absolute or scheme URLs are refused: the viewer only reads relative,
same-origin paths.

## Known limitations

- Slice 2 renders the **whole** tree at once (every depth). Progressive focus
  and metadata search are Slice 3.
- One algorithm only. `Classic`, `SquarifiedNoSort`, and the ordered variants
  remain comparison candidates in the contract, not implemented modes.
- The layout is a proof, not a production promise: skewed trees may show poor
  aspect ratios. No usability claim is made.
- Nothing here measures importance, quality, or task improvement.
