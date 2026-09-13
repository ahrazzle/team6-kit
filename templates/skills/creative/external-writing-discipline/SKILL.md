---
name: external-writing-discipline
description: "Use when a human reads your writing. Cut filler."
version: 1.3.0
author: Lugia (Team6)
license: MIT
platforms: [linux, macos, windows]
---

# External Writing Discipline

A short rule for anything a reader outside your head sees: PR comments, issue replies, chat to the user, client deliverables, release notes, review notes. The rule is simple: say what you did, what you found, what you need. Then stop.

## Plain-language floor (audience test)

Some writing faces readers whose first language is not English, or who have zero context on the project — a README, an About line, a public landing page. Before publishing, test against this floor:

- **Say what the thing IS and DOES in the first three lines.** What it is, what it does, who it is for. If a reader cannot answer "what is this project?" after those lines, everything after is wasted.
- **Ban jargon and lesser-known words** when a plain word exists: "orchestration choreography" → "how the team works together"; "durable state" → "saved to disk"; "provenance" → "where it came from"; "invariant" → "the rule". A technical term stays only when no plain substitute carries the meaning and the audience is technical.
- **Short sentences.** One idea per sentence. Prefer a period over an em dash or a semicolon.
- **Concrete over abstract.** "One agent plans, one builds, one checks" beats "supervised multi-agent coordination".
- **The stranger test:** could someone who has never heard of this project, reading in a second language, tell a friend what it does after reading the top of the page? If not, rewrite before adding anything else.



Every time you connect two words with a dash, ask whether the compound is jargon. "frozen-manifest build example", "paid-pack material", "files-as-state", "third-party-tool audit", "hold-for-review rule" — all of these were written in good faith and all of them failed the stranger test. Real file paths and product names (knowledge-base-ingestion, Apache-2.0) are exempt; invented concept compounds are not. If the compound needs a pause to decode, unpack it: "a skill that saves all work state to disk", not "save-state-to-disk skill".

### Method names are not jargon — but they still need one plain sentence

Keep the specific named technique (Erlang/OTP supervision trees, MoE, YAML, Apache-2.0, Redact/Gist/Title). The discipline is not to strip identifiers — it is to introduce each one with a plain sentence that carries the meaning on its own, so the name becomes a label rather than a dependency: "Workers do the work; the lead watches and restarts them when needed, with a limit on how many restarts are allowed. Modeled on Erlang/OTP supervision trees."

## The core rule

Before you post a piece of writing, read every sentence and ask: does this carry information a reader needs, or is it posture? If removing the sentence changes nothing, delete it.

Then re-read the last paragraph you wrote. A closing paragraph is the most common place for filler to collect, because it feels like the writing needs a graceful exit. It does not. The point you already made is the ending.

## Evidence-led technical writing

For reviews, triage notes, and status comments, make the evidence register compact and countable:

- Lead with the scope and impact count. Define the unit being counted, and count each item once at its highest impact.
- Separate fixes already included from requests, wishlist items, and unresolved findings. Do not let a later or related change appear to be part of the current one.
- Map each item to its exact artifact, commit, test, and status. A table is preferred when rows have the same fields.
- Label the evidence boundary: base or head, commit or composition, test environment, and measurement time when relevant.
- Treat missing evidence as a limit on the claim, not as support for it. Keep unverified follow-ups separate from proven findings.
- State overlaps and independent coverage explicitly. Do not count or describe the same fix twice.
- If a later fact changes an earlier public claim, edit or remove the stale text. Do not stack a correction below it.

The result should let a reviewer answer: what is included, how many items exist, what proves each item, and what remains unverified.

## The three closing jobs you should never do

1. Do not flatter the reader or the thing you are discussing. "This is the right shape" and "reads as the right design" are compliments nobody asked for, and they say nothing about your work.
2. Do not restate the point you just made, dressed up as a conclusion. If the reader needed the point twice, the first sentence was weak. Make it once, make it clear.
3. Do not disclaim your own message. "Not a request for changes" and "just real-world evidence" read as apology for having said something. Commit to the point or cut it.

## Tells readers now flag as AI writing

These carry no information and are becoming recognized giveaways. Remove them on sight:

- Em dashes used to stitch clauses where a period or comma is clearer.
- Calling something "the right shape", "the right design", "exactly what is needed", or otherwise assigning it a verdict the reader can form themselves.
- Negative parallelisms: "not just X, it is Y", "not merely a statement".
- Sentence-opening signposts: "Notably", "Importantly", "It is worth noting that", "At its core".
- Self-referential meta-framing: "I'd frame this differently", "I'd argue", "I would say" — phrases that preface a point with a verdict on how it is being made. State the point; drop the framing.
- Generic positive conclusions: "This is a step in the right direction", "exciting times ahead".
- Reassurance kickers: "And that is okay", "no shame in that".
- Rule-of-three catalogues where two would do.
- A stray leading `@` before a title or opening line. Real example: opening a GitHub issue comment with `@**Same bug, ...**` — the `@` is a leftover mention/reply artifact that reads as addressing someone, and it was surgically removed by the reader before posting was accepted. Never open an external post with a bare `@`.
- Hyphen-pair inflation: "high-quality, end-to-end, client-facing" when the words stand fine alone.

The humanizer skill (creative/humanizer) is the full reference, 34 patterns. Load it alongside this one when you need to scrub a longer piece.

## Run the sweep; do not eyeball it

These tells are invisible while you write them. Grep the text you are about to
post and treat every hit as a candidate, not a verdict:

```bash
sed -n '<start>,<end>p' new_text.md | grep -n '—'
sed -n '<start>,<end>p' new_text.md | grep -niE 'notably|importantly|worth noting|at its core|i would say|right shape|right design|step in the right direction|no shame|that is okay'
```

An em dash separating list items is fine; one stitching two clauses into a longer
sentence is the tell. Scope the sweep to the lines you added: existing text may
carry the same patterns and rewriting it is not the job. Then read the final
paragraph and delete it if it only restates the point.

## The worked example

A real case, verbatim, that a reader deleted as AI slop. The writing had already made its point in two paragraphs. This was appended on top:

> Not a request for changes to the branch. The four-axis + clamp + brake design reads as the right shape. Just real-world evidence that the persistence mechanism is not cosmetic: it is what actually keeps a team room running across updates.

Every sentence fails the rule. The first disclaims. The second flatters and adds a hyphenated-pair for no reason. The third restates the point it already made, then uses an em dash to gesture at significance. Nothing in it tells the reader anything new.

Cut version: nothing needed to be added at all. The comment was complete before this paragraph.

## Long documents a human has to read

A longer document is not a licence to spend more of the reader's time; it is more text to cut. Accept the reader's price: they are paying in minutes, and they will stop reading before they admit it. A PR body written for one ~30-line fix reached ~14k characters across body and comments, and cut to ~3.8k with nothing a reviewer needed removed — most of the saving was restated evidence and narration of the investigation.

- **Format for scanning, not continuous reading.** Headers, bullets, tables for comparisons, code blocks for commands, one idea per heading. A dense wall of prose reads as uninviting regardless of how good the content is.
- **Length defaults unless the content earns more:** a PR or issue body fits one screen; a comment is a few lines. First out: restated evidence, investigation narration, "here is why I looked at this", and hedging. Non-negotiable: repro commands, the root-cause line, test evidence and counts.
- **Cut prose, never the template.** Keep the repo's PR sections in order, every checklist box, code fences and links. Take the saving out of paragraphs; a short body that no longer matches the template reads as sloppiness, not concision.
- **One comment per claim.** If a later finding corrects an earlier comment, edit or delete that comment. Stacking a correcting comment leaves a stale claim in the thread that every later reader pays for.
- **Do not restate what the page already shows.** If the issue is closed, the diff carries the change, or another comment supplied the context, do not narrate it again.
- **Editing text a human has already read:** only when the cut is meaningful AND nobody has responded yet — no comments, no reviews. After that, editing looks like rewriting history under discussion.
- **Post markdown with `--body-file`, never an escaped string.** `gh pr edit N --body` with inline `\n` renders one wall of literal `\n` with raw `##` and pipes showing. Write the file, pass `--body-file`, then fetch the body back and compare it to the file.

## When to load this skill

Load it whenever you write something a human will read that is not a throwaway one-line ack. Post the writing, then run the pass: delete the closing paragraph, delete flattery, delete restated points. If what is left reads plain and complete, you are done.
