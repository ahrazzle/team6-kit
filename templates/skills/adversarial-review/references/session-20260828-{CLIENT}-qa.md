<!-- GENERICIZED: 5×{CLIENT}, 1×{RELATIONSHIP} | source: skills/adversarial-review/references/session-20260828-{CLIENT}-qa.md -->
# Session {CLIENT} — {CLIENT}/Asset QA ({CLIENT} contact-sheet vote)

Live demonstration of adversarial review attack vector 7 (visual asset vetting) on the {CLIENT} monster-starter-pack vote. Sequence: vision pass on the contact sheet → pixel-level verification → taxonomy correction → gated vote.

## Scenario

{RELATIONSHIP} shipped a spike (http://127.0.0.1:8770/spike/index.html) with a 51-monster contact sheet, motion-recipe demo, and a first-draft taxonomy table. The QA gate: which monsters read as monsters vs noise blobs for ages 7–10, and which archetype labels are wrong. Vision pass alone would have misled — several reads were wrong.

## Step 1 — Vision pass (hypothesis, not verdict)

`vision_analyze` on the contact sheet PNG returned: ~70% recognizable, ~30% noise; "ID 41 looks like a coat", "ID 51 looks like a sombrero", "serpent×large is a dumping ground". Pixel-art object reads by vision are unreliable — these became hypotheses to verify, never verdicts.

**Tooling retry pattern:** vision_analyze returned HTTP 404 on the original path (`.../OUTPUTS/spike-pose-motion-{CLIENT}.png` — contains spaces). Fix: `cp` to a clean path (`/tmp/spike-contact-sheet.png`) and retry; succeeded immediately. Before concluding an image can't be read, retry from a space-free path.

## Step 2 — Pixel-level verification (no image libraries)

Minimal PNG parser in pure Python (struct + zlib): read IHDR dims, concat IDAT, decompress, undo scanline filters 0–4 (assume RGBA), then compute:
- **opaque ratio** = pixels with alpha > 40 / total pixels
- **alpha bounding box** = min/max x,y of opaque pixels

No PIL/numpy dependency — runs anywhere. Key code shape:

```python
import struct, zlib
def png_info(path):  # -> (w, h, opaque_ratio, bbox)
    data = open(path,'rb').read()
    pos = 8; w = h = None; idat = b""
    while pos < len(data):
        n = struct.unpack(">I", data[pos:pos+4])[0]
        ct = data[pos+4:pos+8]; chunk = data[pos+8:pos+8+n]
        if ct == b"IHDR": w,h = struct.unpack(">II", chunk[:8])
        elif ct == b"IDAT": idat += chunk
        pos += 12 + n
        if ct == b"IEND": break
    raw = zlib.decompress(idat); stride = w*4
    # undo filters 0-4 (Sub/Up/Average/Paeth) line by line, then alpha-scan
```

## Step 3 — Measured data (100×100 sprites)

| id | opaque% | bbox | read |
|---|---|---|---|
| 38 | 4% | 30×28 | **dot** — invisible at battle scale |
| 10, 7 | 5–6% | ~30×38 | sparse — noise at scale |
| 44 | 6.5% | 56×37 | wide flat — plausible quad, needs eye |
| 34, 55 | 7–8% | ~30–49 wide | sparse; 55 labeled serpent×large at 8% = contradiction |
| 19 | 50% | 90×96 | dense but dark — **contrast problem, not exclusion** |
| 18 | 12% | 56×71 | dark purple — contrast pass needed |

**Generalized thresholds (battle scale, 100×100):**
- <5% opaque → invisible dot: exclude or auto-rescale
- 5–8% → suspect: sparse shapes read as noise blobs at target scale
- high density but dark/low contrast → contrast-boost, NOT exclusion
- bbox geometry refutes archetype: vertical column (35×46) is not a "serpent"; two near-identical bboxes (52, 53: 58×73) are the same family → same bucket
- a taxonomy bucket that is a dumping ground (serpent held coats/horses/birds per vision, confirmed geometrically) must be re-bucketed by eye

## Step 4 — Artifact self-consistency

The spike contradicted itself: demo tiles labeled `opmon-41` as quad×large and `opmon-53` as biped×large, but the TAXONOMY table (in-page JS object) listed both as serpent×large. **A vote cannot run on an artifact that disagrees with itself** — label set fixed first.

## Step 5 — Deliverable decisions

- Exclude 38 outright (4% density, dot).
- Contrast-boost 18/19 (dark, not broken).
- Re-bucket serpent category by eye on the contact sheet.
- Recommend a per-pose `scale` hint in the asset manifest derived from bbox — monsters under ~15% bbox area auto-scale to battle size or are excluded. Keeps the taxonomy machine-driven instead of eyeball-driven.

## Lesson

Visual quality gates for kid-facing games need data, not vibes: vision pass narrows the candidate set, pixel metrics decide, geometry checks taxonomy, and the artifact must agree with itself before the vote runs.
