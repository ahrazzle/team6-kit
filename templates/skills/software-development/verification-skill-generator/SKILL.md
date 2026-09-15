---
name: verification-skill-generator
description: "Use when a project has no scripted way to prove its behavior. Interviews the project and writes a project-local verification skill plus a feature map."
version: 1.0.0
author: {RELATIONSHIP}
license: Apache-2.0
metadata:
  hermes:
    tags: [verification, qa, generator, feature-map, testing]
    related_skills: [web-build-verification, verify-deployed-artifacts, systematic-debugging]
---

# Verification-Skill Generator

Interview one project and write a **project-local** verification skill that drives
the real app the way a user does: launch it, exercise a feature, and capture proof.
The output is a skill the next agent reads cold, mid-task, on an app it has never
seen. This generator ships in the kit. The skill it writes is project-local, at
`<project>/.hermes/skills/verify-<app>/`.

The generated skill is self-contained. It runs without this generator and without
the interview that produced it.

## 1. Interview the project, not the user

Answer each question from the codebase. Ask the user only for what you cannot
observe. A skill written against assumptions it never checked is a draft.

- **Surface:** what does a user touch? A web UI, a CLI or TUI, a desktop app, an
  API, a mobile app, or a library? A project can have several. Pick the primary one
  and name the rest.
- **Run:** how does it start locally? Prefer the project's own documented dev
  command: a package script, a Makefile target, or a README quickstart. Note ports,
  env vars, seed data, and auth.
- **Drive:** how can an agent interact with it? Reuse existing harnesses first:
  Playwright or Cypress specs, expect scripts, PTY helpers, callable endpoints, or a
  debug port. Reach for a generic recipe only when none exists.
- **Observe:** what proof can you capture? Screenshots, terminal transcripts,
  response bodies, logs, exit codes, or database state.
- **Isolate:** can two instances run side by side on separate ports, data dirs, or
  profiles? If not, say so in the generated skill. Refusing to double-drive one
  shared instance is safer than corrupting a live session.

If the checkout does not build or start as written, fix that first, or report it
precisely. A skill built on a broken base teaches wrong steps.

## 2. Write the generated skill

Create `<project>/.hermes/skills/verify-<app>/SKILL.md` with YAML frontmatter. The
frontmatter needs `name: verify-<app>` and a `description` that names the app, the
surface, and when to reach for it. Without frontmatter the skill never registers.
Fill every section from what the interview actually found. Leave no placeholders.
Required sections:

- **Launch:** the exact command that starts the app, and how to tell it is ready. A
  ready signal is a log line, a port answering, or a prompt. Include teardown. For a
  short-lived CLI or TUI there is no server to keep up: build once, then run each
  drive in its own isolated session.
- **Doctor:** one read-only check that answers "is this instance worth driving?".
  Process up, correct build, port held by us, auth valid. An agent runs this first
  whenever anything looks off.
- **Drive:** the harness recipe with real selectors and commands from this project,
  not generic ones. Prefer stable handles: ARIA labels, data attributes, prompt
  strings, or route paths. Avoid coordinates and tab order.
- **Evidence:** what to capture, and where it goes. State the proof standard:
  - Exercise the real user path, not internal setters or test-only endpoints.
  - Capture the action and the resulting state, not just the final screen.
  - Verify side effects alongside what is visible: files written, rows inserted,
    messages sent.
  - Use a mock only where a production boundary already isolates the external
    system.
  - When the safe path is a dry run or test mode, verify what it actually skips by
    observation, not by trusting its name.
- **Cleanup:** how to tear down the instances the run created. Kill what you
  started, never by process name. Cleanup removes scratch state, never the proof.
  Evidence survives teardown, in a location the skill names.
- **Helpers:** any script the skill ships is executable, and its exact invocation is
  shown in the body. A helper the reader must reverse-engineer is not a helper.

## 3. Seed the feature map

Create `<project>/.hermes/skills/verify-<app>/feature-map.md` following
`references/feature-map.md`. List the top three to five user-facing features you can
identify, drawn from routes, commands, menus, or docs. Every listed feature must
carry a `verification_method`. The map is the project's maintained verification
source. A proof that drives one convenient entry point is incomplete when the map
lists others.

## 4. Prove the generated skill before handoff

Run the generated skill's own instructions end to end once: launch, doctor, drive
one mapped feature, capture evidence, and clean up. After cleanup, confirm the
evidence still exists at the named location. A cleanup that eats the proof fails
this step. Fix what breaks. Run the generated cleanup after every failed attempt
too, so a broken attempt leaves no stranded process or port. An unexecuted
generator is a draft, not a deliverable. The run is the proof.

## 5. Offer the maintenance loop

Point the user at keeping the feature map honest as the app changes. Suggest a
review cadence only when they ask.
