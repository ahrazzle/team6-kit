<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/creative/game-ux-architecture/SKILL.md -->
---
name: game-ux-architecture
description: "Design input systems and feedback for input-driven games."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [game-design, ux, feedback, input-system, rhythm, typing, plugin-architecture, gamification, timing]
    related_skills: [claude-design, sketch, interactive-data-simulation, design-tone-domain]
---

# Game UX Architecture

Use this skill when designing **input-driven games** — games where the player's primary action (typing, pressing, clicking, swinging) IS the gameplay, not a means to an end. Covers rhythm games, typing games, music games, reaction-time games, and gamified learning tools where input precision is the core loop.

Load this when the user says things like "design a typing game," "rhythm game mechanics," "gamify this input task," "plugin architecture for games," "make pressing keys feel satisfying," or when the deliverable is a game's input/feedback architecture rather than a static UI.

## When NOT to use this

- The game is not input-driven (strategy, exploration, narrative) — use `claude-design` for the UI
- The user wants a static prototype or mockup — use `sketch`
- The user wants a data visualization or simulation — use `interactive-data-simulation`
- The user wants game art/graphics, not game feel — this skill covers the UX architecture, not the visual production

## Core Principle: The Input IS the Game

In input-driven games, the fundamental design question is: **"Why does performing this physical action feel good?"** If the answer is only "because you get points," the design has failed. The input itself must be satisfying — the feedback loop between action and response is the entire game.

This is the critical distinction from other game genres:
- In a racing game, you steer to win a race. The steering is a means to an end.
- In Guitar Hero, pressing the fret button at the right time IS the game. There is no higher-level goal that justifies the input — the input precision itself is the entertainment.

When designing for input-driven games, every design decision serves the moment-to-moment satisfaction of performing the action.

## The Three-Layer Architecture

Every input-driven game needs three decoupled layers. This is the foundational architecture:

### Layer 1: Input (Keystroke/Action Bus)

Captures raw player input and transforms it into structured events.

```
RawBus → NormalizedBus → Judge → PluginHooks
```

- **RawBus:** Captures hardware events with high-resolution timestamps (`performance.now()`, NOT `Date.now()`). Captures BOTH `keydown` AND `keyup` — press duration and inter-key interval are needed for intensity visualization and adaptive difficulty.
- **NormalizedBus:** Handles shift, caps lock, locale, and other transformations. Produces clean character/action events. Do this once in the framework — never force plugins to reimplement normalization.
- **Judge:** Evaluates input against expected targets (timing windows, correct keys, sequence order). Emits judgment events (Perfect/Great/Good/Miss), not raw correctness.

**Critical:** Timestamps must be captured in the raw `keydown` listener itself, not after normalization or judgment. Event-loop jitter eats precision if you capture late. For rhythm games targeting ±25ms "Perfect" windows, this is non-negotiable.

### Layer 2: Feedback (The "Feel" Layer)

The animated response system that makes input satisfying. This is NOT cosmetic — it is the bridge between "I did the thing" and "I want to do it again."

**Design rules for feedback:**

1. **Scale feedback to performance quality.** Not just correct/incorrect — degrees of correctness mapped to degrees of satisfaction. A Perfect hit should feel fundamentally different from a Good hit. This is the dopamine engine.

2. **Make the input device itself the feedback surface.** The keyboard is not just an input tool — it becomes the score display, the combo meter, the progress indicator. Keys pulse, glow, depress, and react. The player sees their performance reflected in the instrument they're playing.

3. **Combo feedback escalates.** The longer the streak, the more the environment transforms:
   - 10x: subtle aura on the keyboard
   - 25x: scene intensity shift (color saturation, particle density)
   - 50x: full light show
   - The world rewards mastery visibly.

4. **Wrong input gets deliberately underwhelming feedback.** Not silent (feels broken — the player thinks their keyboard is broken) and not punishing (breaks flow). A gentle shake, a muted flash — the UX equivalent of a head-shake, not a failure screen.

5. **The input device should be "alive" even before input.** Keys pulse on the beat, subtle glow syncs to tempo. The instrument breathes. This gives rhythm context without requiring reading.

6. **Stuck-player nudges.** If the expected action hasn't been performed within a reasonable window, subtly highlight the expected target. This prevents freezing and doubles as implicit teaching. At higher difficulties, this nudge can be disabled.

### Layer 3: Game (Plugins / Game Logic)

Consumes judged events and renders game-specific scenes on top. Plugins never see raw events — they consume judgments only.

**Rendering architecture:** Stack independent canvas layers:
- Bottom: shared feedback layer (keyboard + effects) — managed by the framework
- Top: per-plugin canvas with `pointer-events: none` so input always reaches the input layer

**Theme descriptors, not raw access:** Plugins say "cyberpunk" or "pastel" via a theme descriptor — the framework renders the appropriate visual treatment. Direct DOM/canvas access from multiple plugins causes theme conflicts.

## Input Model Fork: The Critical Decision

The most important architectural decision for any input-driven game is: **what happens when the player performs the wrong action?**

### Model A: Rhythm-Forward (Guitar Hero model)
Wrong actions advance the beat. The game continues regardless. The song never stops.
- **Risk:** Players learn to mash keys. Accuracy doesn't matter. Pedagogy collapses.
- **Best for:** Pure entertainment games where the goal is engagement, not learning.

### Model B: Accuracy-Forward (Traditional typing model)
Wrong actions block progress. The player cannot advance until the correct action is performed.
- **Risk:** Flow is constantly interrupted. The rhythm stutters. The thing that makes rhythm games satisfying (continuous flow) dies.
- **Best for:** Pure learning tools where the goal is accuracy, not engagement.

### Model C: Correct Key + Timing Window (osu! model) — RECOMMENDED SYNTHESIS
Wrong actions are **ignored** by the game logic — they don't advance the target, don't break the combo, don't trigger game feedback. The player simply cannot progress until the correct action is performed. **But timing judgment applies whenever the correct action arrives.**

- Correct action within Perfect window → Perfect + full feedback
- Correct action within Great window → Great + moderate feedback
- Correct action late/early (outside windows) → Good + minimal feedback
- Wrong action → nothing from game logic (subtle feedback only — see Layer 2 rule #4)
- Never performing the correct action → the target sits there until you do

**Why this works:**

| Concern | How it's solved |
|---|---|
| Action mashing | Mashing hits the right key by chance, but with terrible timing. Combo breaks, score stays low. Optimal strategy is still "read ahead, time it right." |
| Flow preservation | The music/beat never stops. Background pulses on beat. No jarring interruption from wrong keys. |
| Accuracy enforcement | You literally cannot advance without the correct key. No correct press = no progress. |
| Rhythm satisfaction | Timing still matters enormously. A correct action on beat gives the full burst. Late is underwhelming. |

**When to use which model:**
- Model C is the default for any game that combines learning with engagement
- Model A for pure entertainment (Nitro Type-style racing)
- Model B for pure assessment/testing

## Timing Windows (Reference Values)

| Judgment | Window | Feedback intensity |
|---|---|---|
| Perfect | ±25–40ms (tight) / ±80ms (medium) / ±150ms (easy) | Full particle burst, key depression, screen-edge glow |
| Great | ±40–80ms (tight) / ±120ms (medium) / ±200ms (easy) | Moderate flash, smaller particles |
| Good | Outside Great but correct key | Minimal flash |
| Miss | Wrong key or never pressed | Gentle shake (wrong key) or nothing (never pressed) |

**Age/skill scaling:** Start with generous windows (±150ms Perfect for young children) and tighten with difficulty. The existence of a tight Perfect window at higher levels is what makes mastery feel real.

## Scoring Architecture (Guitar Hero model, refined)

- **Base points per action:** 50 pts × multiplier
- **Combo multiplier:** 1x → 2x → 3x → 4x, stepping every N consecutive hits
- **Overdrive/Star Power:** Doubles the active combo multiplier (4x → 8x at max) — triggered by streak thresholds
- **Sustains (hold actions):** 25 pts/beat — relevant for long vowels, double-letter patterns
- **Chords (multi-action):** 50 pts × number of simultaneous actions

**Why this works for learning:** Combo multipliers reward *accuracy*, not just speed. A player who acts slowly but accurately outscores one who speed-blurs with mistakes. Accuracy first, speed emerges naturally.

## Plugin Contract (Draft)

```typescript
interface GamePlugin {
  // Lifecycle
  onGameStart(config: GameConfig)    // BPM, beat-map, difficulty, age band
  onGameEnd(results: GameResults)    // accuracy, max combo, WPM/APM, stars earned
  
  // Timing events (the core loop)
  onHit(judgment: 'perfect' | 'great' | 'good', key: string, timingDelta: number)
  onMiss(key: string, expectedKey: string)
  onCombo(count: number, multiplier: number)
  
  // Progression
  onStreakThreshold(count: number)   // every N hits — triggers overdrive/star power
  onTargetStale(target: Note)        // target exceeded its window without correct input
  onSongComplete(results: GameResults)
  
  // Rendering
  getCanvasContext(): CanvasRenderingContext2D  // plugin draws its scene here
  getThemeDescriptor(): ThemeDescriptor          // plugin says "what vibe," framework renders it
}
```

**Key design points:**
- Plugins consume **judgments only** — never raw events. The judge evaluates timing windows and emits `onHit(judgment, key, delta)` / `onMiss`.
- `onTargetStale` is a feedback-layer feature — the framework uses it to trigger stuck-player nudges. Plugins can also use it for game-specific reactions.
- `getThemeDescriptor()` prevents theme conflicts between plugins.

## Beat-Map Schema (The Content Format)

A beat-map is the data structure that turns lesson content into playable rhythm patterns:

```typescript
interface BeatMap {
  id: string
  bpm: number                         // tempo
  difficulty: 'easy' | 'medium' | 'hard'
  timeSignature: [number, number]     // e.g., [4, 4]
  notes: Note[]
}

interface Note {
  beat: number                        // position in beats (float for subdivisions)
  key: string                         // target key/action
  type: 'tap' | 'hold'
  duration?: number                   // in beats, for hold notes
}
```

**Critical design point:** Note density is independent of BPM. A beginner beat-map at 80 BPM might have a note every 2 beats (sparse), while an expert map at 140 BPM might have 4 notes per beat (dense). This separates *tempo* from *complexity* — two distinct difficulty axes.

**BPM → WPM mapping:** At 1 note per action with 5 chars/word: 60 BPM ≈ 12 WPM, 120 BPM ≈ 24 WPM, 180 BPM ≈ 36 WPM.

## Accessibility (Core, Not Plugin)

Accessibility must be in the core architecture from day one. Retrofitting it loses contracts and excludes users.

- Full keyboard navigation for all menus (no mouse required)
- ARIA live regions announcing combo milestones and progress
- High-contrast mode for the keyboard and note indicators
- One-handed mode: beat-maps that avoid simultaneous multi-action presses
- Adjustable timing windows as an accommodation (not just a difficulty setting — this is a legal requirement in educational contexts)
- `prefers-reduced-motion` support for all animations

## Failure State Design

The failure state is a design choice, not a default:

| Mode | Failure state | Best for |
|---|---|---|
| No Fail | Music never stops, scene gets quieter/monochrome until recovery | Young kids, casual play |
| Soft Fail | Scene dims, Rock Meter drops, but song continues | Intermediate players |
| Hard Fail | Song ends, results screen | Competitive/older players |

**Design principle:** Failure should feel like "the world got quieter," not "you are punished." The music dimming is more effective than a red X.

## Age/Skill Scaling

Scale along these axes independently:

| Setting | Easy (age 6-7) | Medium (age 8-9) | Hard (age 10+) |
|---|---|---|---|
| Timing window (Perfect) | ±150ms | ±80ms | ±40ms |
| BPM range | 40–70 | 70–110 | 110–180 |
| Actions used | Home row only | Home + top row | Full keyboard |
| Fail state | None (No Fail) | Soft (scene dims) | Rock Meter |
| Session length | 1–2 min | 2–3 min | 3–5 min |
| Stuck nudge | Always on | On for first 3 misses | Off |

## Anti-Patterns

- **Cosmetic-only feedback:** Adding particles and glow without scaling feedback to performance quality. If a Perfect hit and a Good hit look the same, the feedback system is decorative, not functional.
- **Silent wrong input:** Zero feedback on wrong actions makes the player think their hardware is broken. Always give a minimal "that wasn't it" signal.
- **Blocking the beat on wrong actions:** This kills rhythm flow. Use the osu! model (wrong = ignored) rather than the traditional typing model (wrong = blocked).
- **Separating the score from the input device:** If the player has to look away from the keyboard to see their score, the feedback loop is broken. The keyboard itself should communicate performance.
- **One-size-fits-all difficulty:** "Kids" is not a demographic. A 6-year-old and a 12-year-old need fundamentally different timing windows, content complexity, and reward cadence.
- **Accessibility as an afterthought:** WCAG compliance cannot be a plugin. It must be in the core input and feedback layers from day one.

## References

- `references/rhythm-game-mechanics.md` — timing windows, scoring, beat-map patterns from Guitar Hero, DDR, Beat Saber, osu!
- `references/rhythm-game-approach-patterns.md` — approach ring and note highway patterns from osu! and Stepmania, with implementation checklist
- `references/canvas-animation-pitfalls.md` — canvas rendering bugs (negative radius, dead animations, double-subscription, stale cache) encountered in interactive HTML game development

## Pitfalls

- **Cosmetic-only feedback:** Adding particles and glow without scaling feedback to performance quality. If a Perfect hit and a Good hit look the same, the feedback system is decorative, not functional.
- **Silent wrong input:** Zero feedback on wrong actions makes the player think their hardware is broken. Always give a minimal "that wasn't it" signal.
- **Blocking the beat on wrong actions:** This kills rhythm flow. Use the osu! model (wrong = ignored) rather than the traditional typing model (wrong = blocked).
- **Separating the score from the input device:** If the player has to look away from the keyboard to see their score, the feedback loop is broken. The keyboard itself should communicate performance.
- **One-size-fits-all difficulty:** "Kids" is not a demographic. A 6-year-old and a 12-year-old need fundamentally different timing windows, content complexity, and reward cadence.
- **Accessibility as an afterthought:** WCAG compliance cannot be a plugin. It must be in the core input and feedback layers from day one.
- **No approach notes:** If the game shows only a static highlight on the expected key with no sense of motion or anticipation, it's a flashcard, not a rhythm game. See "Rhythm Game Approach Patterns" reference for the minimum viable approach system.
- **Timing mismatch from stale startTime:** If the judge's `_startTime` is never set before judging begins, `delta = timestamp - startTime` becomes billions of ms, registering every correct key as a miss. Always call `judge.setStartTime(performance.now())` immediately before the game begins.
- **Stale nudge highlights:** Nudge highlights must be cleared on game end AND on game restart, not just on natural timeout. Otherwise the last expected key from the previous game stays highlighted indefinitely.
- **Over-shaking feedback:** Using CSS `text-shadow` + `transform` transition on rapidly-updating text (like combo counters) creates motion blur. Remove glow from text that updates frequently, or promote to compositor layer with `will-change: transform`.
- **Canvas negative radius from future-dated animations:** Creating effects with `startTime: performance.now() + delay` causes negative elapsed time → negative radius → `IndexSizeError`. Clamp progress: `Math.max(0, Math.min(1, elapsed / duration))`. Never create future-dated animations.
- **Double-subscription on start:** Start function must guard with `if (gameActive) return;` to prevent duplicate judges/buses/subscriptions.
- **Feedback layer starting before game state:** Don't call `feedbackLayer.start()` on page load — only inside game start function after judge exists.
- **Browser cache serving stale bundle:** Add cache-control meta + version query param on imports. Verify live version with curl before debugging further.
- **Notes at time 0 (no lead-in):** If the first note is at `time: 0`, the player must press the instant the game starts — impossible — and approach rings have no preempt window to appear before the first beat. Add a `LEAD_IN_MS` offset (e.g. 3000ms) to every generated note time (`time: LEAD_IN_MS + i * beatInterval`). Align the ring preempt time so rings appear ~1.5s before the first note.
- **Key-ID / character mismatch (e.g. spacebar):** The beat-map emits notes with the literal character (`key: " "`), but the keyboard renderer names keys by DOM id (`id: "space"`). Any visual lookup via `getKeyElement(note.key)` silently fails for the spacebar — no approach ring, no expected-key highlight. Always normalize the character to the key id before `getKeyElement()`: map `" "` → `"space"`, handle both cases.
- **Debug overlay vs. gameplay stats:** A raw event-log readout (judgment log, combo circle, debug counts) is a development tool and must be hidden by default (`showDebugUI = false`), NOT shipped visible to players. But the live Perfect/Great/Good/Miss counters are gameplay feedback, not debug — they belong in the feedback layer as a core always-visible element, independent of the debug plugin. Never couple player-facing stats to a debug component you might hide.
- **Verify the served bundle before announcing a fix:** In a multi-agent loop with a deployed artifact, local source ≠ what the browser loads. Before telling the user "fix is live," confirm the fix actually exists in the served file (curl the raw GitHub URL / deploy endpoint and grep for the change). Repeating "hard refresh" when the fix was never pushed erodes trust fast. When unit tests pass but the app breaks, the gap is almost always integration wiring — write ONE integration test that drives the full pipeline end-to-end (input → bus → judge → feedback) and asserts a correctly-timed input registers as the right judgment. That single test catches regressions that isolated unit tests miss.
