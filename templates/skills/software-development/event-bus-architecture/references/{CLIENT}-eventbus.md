<!-- GENERICIZED: 2×{CLIENT} | source: skills/software-development/event-bus-architecture/references/{CLIENT} -->
# {CLIENT} Event Bus — Concrete Implementation

## Overview

The {CLIENT} framework uses a layered event bus to capture keystrokes with high precision, normalize them, evaluate timing against a beat-map, and dispatch judgments to plugins. This is the reference implementation for the `event-bus-architecture` skill.

## Architecture

```
DOM keydown/keyup
    ↓
RawBus (captures performance.now() at source)
    ↓
NormalizedBus (handles shift/caps/lock, filters repeats)
    ↓
BeatClockJudge (evaluates timing windows, maintains combo/cursor)
    ↓
FeedbackLayer (renders SVG keyboard + canvas particles)
    ↓
DebugPlugin / GamePlugins (consume judgments, render scenes)
```

## Key Components

### RawBus (`src/RawBus.ts`)
- Captures `keydown`/`keyup` from a DOM target (default: window)
- Stamps each event with `performance.now()` **inside the DOM handler itself**
- Exposes `onKeyDown(fn)` and `onEvent(fn)` subscription methods
- Includes `inject(key, code, type, timestamp?)` for headless testing
- Fallback no-op target for non-DOM environments

### NormalizedBus (`src/NormalizedBus.ts`)
- Consumes raw events via `rawBus.onEvent(fn)`
- Normalizes using US QWERTY layout mapping
- Handles shift XOR caps lock for letters
- Filters out key repeats (`e.repeat`)
- Emits `NormalizedEvent { char, raw, phase }` where phase is 'press' | 'release'

### BeatClockJudge (`src/BeatClockJudge.ts`)
- Consumes normalized events via `attach(normalizedBus)`
- Evaluates timing delta = pressedTime - expectedTime
- Classifies judgments: perfect / great / good / miss
- Maintains combo counter and multiplier (1x → 2x → 4x → 8x)
- **Wrong keys are silently ignored** — no judgment, no cursor advance, no combo break
- Stale note detection via `tick(currentSongTime)`
- Emits to subscribers via `onJudgment(fn)` and to plugin hooks

### BeatMap (`src/BeatMap.ts`)
- Read-only infrastructure — notes are immutable once constructed
- Defensive copy + sort by time
- `getNote(index)`, `getNotesInRange(startMs, endMs)`

### BeatMapGenerator (`src/beatmap-generator.ts`)
- Converts typing content into rhythmic note arrays
- BPM → WPM mapping: `bpm = WPM × 5`
- Difficulty-based density filtering (medium skips spaces)
- Hard difficulty: doubled notes for common letters at half-beat offset
- Hand-alternation shuffle: detects 3+ consecutive same-hand notes and swaps

### FeedbackLayer (`src/feedback-layer.ts`)
- Hybrid rendering: SVG keyboard + Canvas particle system
- Three visual channels: right key + good timing (full burst), right key + bad timing (muted flash), wrong key (gentle shake)
- Combo escalation: subtle (10x), moderate (25x), intense (50x)
- Nudge hints for stale notes (pulsing glow on expected key)
- ARIA live regions for accessibility announcements
- Theme descriptor system for plugin customization

### SVGKeyboardRenderer (`src/svg-keyboard.ts`)
- Full QWERTY layout with finger hints
- Hardware-accelerated CSS transitions
- ARIA labels on every key (e.g., "Key F, home row, index left finger")
- High-contrast mode support
- Home row indicators

### ParticleSystem (`src/particle-system.ts`)
- Canvas-based particle effects
- 5 particle styles: spark, ring, star, confetti, none
- Screen shake with decay
- Edge glow with radial gradients
- Reduced-motion support

### DebugPlugin (`src/debug-plugin.ts`)
- Minimal contract validator — exercises every hook
- Visual: combo circle, progress bar, judgment log
- Proves the plugin contract works end-to-end

## Timing Precision

For ±25ms precision at expert difficulty:
- Timestamp captured in raw DOM handler (not downstream)
- `performance.now()` used throughout
- No re-capture of time in normalization or judgment layers

## Testing

- 29 event bus tests (RawBus → NormalizedBus → BeatClockJudge → PluginRegistry)
- 48 beat-map generator tests (BPM intervals, difficulty density, hand alternation)
- All tests use `inject()` for deterministic, headless execution

## Demo

`demo.html` — self-contained browser validation page:
- Wires RawBus → NormalizedBus → BeatClockJudge → FeedbackLayer + DebugPlugin
- Controls for content, BPM (40–180), difficulty
- Generates beat-map, starts game, renders feedback through real framework
