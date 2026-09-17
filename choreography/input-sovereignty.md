# Input Sovereignty Law

> Normative binding for all Protean software. Version 1.0.1. Effective immediately. Owner verdict from the EvoPet incident: "This class must be structurally impossible."

## 1. Preamble

On 2026-09-17, the EvoPet overlay seized the owner's pointer control by running a hover-expand polling loop that fought the user for mouse dominance. The overlay supervisor respawned the offender after kill attempts, denying the owner the ability to regain control of the machine. After relief was applied out-of-band, the owner issued the following verdict: **"This class must be structurally impossible."** This law enshrines that verdict into binding architecture. It applies to ALL Protean software — every window, overlay, and process the team builds or supervises, now and in perpetuity.

## 2. Clauses

### (a) No Input Coercion
**MUST NOT** call focus-steal, pointer-warp, input-grab, or reposition-under-pointer APIs. Overlays are purely passive render surfaces: they may draw and be interacted with only by the user's own uncoerced input.

### (b) Polling Loop Hysteresis and Cooldown
Any polling loop that affects UI (timer/poll-driven changes to anything visible) **MUST** have hysteresis AND cooldown so it cannot oscillate.

- **Hysteresis** means asymmetric entry/exit thresholds or state persistence such that a boundary-stationary condition cannot flip state every tick.
- **Cooldown** means a minimum interval between successive state flips.
- The **oscillation acceptance test**: an input held at the boundary produces at most one state flip.

### (c) User Kill-Switch for Supervisor-Managed Processes
Every supervisor-managed process **MUST** provide ONE documented command that:
1. Parks the process immediately,
2. Stops the supervisor from respawning it,
3. Yields an observable parked state.

Park is durable until the user explicitly un-parks.

### (d) Shaka QA Input-Sovereignty Proof
The Shaka QA checklist gains input-sovereignty proof for any overlay/window/supervisor work. QA **MUST** demonstrate:
- **Static proof**: the forbidden-API set is absent from the work (via the canonical grep set defined below), AND
- **Behavioral proof**: pointer position sampled before/during/after the QA window; no event capture or swallow of keyboard input reaching the foreground app.

Where behavioral probing is impossible in the QA environment, record it as an explicit LIMIT and fall back to static proof only.

## 3. Canonical Forbidden-API List (macOS / Python)

This is the enforcement baseline. A broader engineering pattern set may be used for audits; the law's list is the normative minimum.

| Category | API / Module / Pattern | Enforcement |
|----------|------------------------|-------------|
| Pointer warp | `CoreGraphics.CGDisplayMoveCursorToPoint`, `CGWarpMouseCursorPosition` | grep |
| Event post | `CoreGraphics.CGPostEvent`, `CGEventPost` | grep |
| Event tap | `CoreGraphics.CGEventTapCreate`, `CGEventTapCreate` | grep |
| Focus activation | `AppKit.NSApp.activate(ignoringOtherApps:)`, `NSApplication.activate(ignoringOtherApps:)`, `NSWindow.makeKeyAndOrderFront`, `NSWindow.makeKeyWindow` | grep |
| Input grab | `CoreGraphics.CGSetMouseCursorVisible`, `CGSetSystemCursorVisibility`, accessibility `AXUIElementSetAttributeValue` writes that drive input | grep |
| Synthetic input | `QuartzCore.NSSyntheticEvent`, `CGEventSourceCreate`, `CGEventCreate`, synthetic key/mouse events | grep |
| Reposition under pointer | `NSWindow.setFrame(_:display:)` when the frame origin is computed relative to the pointer position without user initiation | grep |
| Reposition (Tk) | Tk `.geometry(`, Tk `.place(` | grep |
| Reposition (Cocoa window geometry) | Cocoa `setFrame(:`, `setFrameOrigin(:`, `setFrameTopLeftPoint`, `orderFrontRegardless` | grep |

**Static check semantics**:
- Match must be against executable code API calls only (function/method invocations, not declarations, imports, docs, tests, or comments).
- Visibility-only APIs (e.g., `CGSetMouseCursorVisible` without input-driving writes) and observation-only event taps are not automatic violations; they require semantic review.
- Pointer-relative frame computation (any geometry that depends on the current pointer position without user-initiated gesture) requires either:
  - A manual code-review to verify user-initiation semantics, OR
  - A behavioral check that no reposition occurs under pointer hover/movement.
- Static absence from the canonical baseline **does not** prove semantic compliance for pointer-relative geometry; pointer-relative semantics must be reviewed separately.

**Static check**: For any overlay/window/supervisor work, grep the codebase for the exact patterns above. Absence = static proof passed.

## 4. Enforcement Mapping

| Clause | Enforcement Mechanism | Proof Type | Result State |
|--------|----------------------|------------|--------------|
| (a) No Input Coercion | Static grep against forbidden-API list in every overlay/window/supervisor diff | Static | STATIC PASS / BEHAVIORAL LIMIT |
| (b) Polling Loop Hysteresis/Cooldown | Code review + behavioral probe (boundary input held; verify ≤1 flip) | Mixed (static + behavioral) | BEHAVIORAL PASS / BEHAVIORAL LIMIT |
| (c) User Kill-Switch | Verify documented command exists and parks process + stops respawn per evidence record below | Behavioral | STATIC PASS / UNVERIFIED/BLOCKED |
| (d) Shaka QA Proof | QA checklist: static grep + behavioral probe or explicit LIMIT entry | Mixed | STATIC PASS / BEHAVIORAL PASS / BEHAVIORAL LIMIT / UNVERIFIED/BLOCKED |

### (c) Evidence Record for Kill-Switch Compliance
For every supervisor-managed process, the following evidence must be present and verifiable:

1. **Supported user command**: One documented shell command or supervisor command that:
   - Parks the process immediately,
   - Stops the supervisor from respawning it (e.g., by disabling the launchd job, supervisor config, or child-manage respawn flag),
   - Yields an observable parked state.
2. **Durable anti-respawn action**: The command must modify state at the launchd/supervisor/child layer that persists across reboots or service restarts.
3. **Observable parked-state read-back**: A distinct command or query that returns an unambiguous boolean (parked/unparked) or state enum; this read-back must be independent of the park command and verifiable without executing the park command.
4. **Explicit unpark command**: A distinct command to restore the process with the same durability guarantees.

The following are **NOT** acceptable proof:
- `overlay stop` (unless the full evidence chain above is demonstrated),
- hide/show visibility toggles,
- install-time opt-outs (they do not constitute a user-facing park command),
- an unexecuted host command (the command must be documented and operational).

A single user-facing command may cover all managed layers only if the evidence proves it satisfies all four requirements across all layers.

## 5. Binding Note

This law binds ALL Protean software: past, present, and future. Any new work that violates any clause is non-compliant by definition. Compliance is checked at the PR gate (static grep) and at the QA gate (behavioral proof or documented LIMIT).
