<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/productivity/task-execution/SKILL.md -->
---
name: task-execution
description: "Stop when no tool path exists. Don't brute-force."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [task-execution, efficiency, dead-ends, honest-reporting]
---

# Task Execution

Use when approaching any task where tool availability, API capability, or environment constraints are uncertain. Governs the decision to continue searching, attempt, or stop and report honestly.

## Core Principle

**When there is no path forward, say so immediately. Do not substitute effort for capability.**

Brute-forcing through repeated tool calls, reworded searches, or alternative approaches when the capability genuinely does not exist wastes tokens, delays the user, and erodes trust. The user prefers an honest "cannot do" delivered early over a plausible-looking attempt delivered late.

## Decision Framework

For every task, assess in this order:

1. **Capability Check** — Do I have a tool, command, or API that can accomplish this? If the catalog search returns no match, the answer is no.
2. **Efficient Attempt** — Make ONE focused attempt with the best available tool. If it fails with an unambiguous signal (404, "not found", empty result, unsupported operation), do NOT retry the same path with different parameters.
3. **Honest Stop** — If step 1 is negative or step 2 fails conclusively, report the blocker and stop. Tell the user what's missing and what they can do instead.

## Explicit Rules

- **One tool call per logical attempt.** If `tool_search` returns no matches for "create group chat," that is a signal. Do not follow up with `web_extract` on documentation hoping the answer hides there.
- **404 / not-found = dead end.** A missing CLI subcommand, an undocumented API, a tool catalog miss — these are not invitations to dig deeper. They are the answer.
- **"I cannot do X with available tools" is a valid deliverable.** It is not failure. It is honest reporting.
- **Never loop search → miss → search differently → miss → search again.** This is the exact pattern the user flagged.
- **If you realize you are in a loop, stop mid-loop.** Do not finish the "planned" sequence of attempts just because you queued them.

## Common Traps

- **The documentation rabbit hole:** Hoping that reading more docs will reveal a capability that the tool catalog search already confirmed doesn't exist.
- **The "maybe if I try X" fallacy:** After exhausting obvious paths, inventing increasingly speculative approaches to avoid admitting the task is impossible.
- **Confirmation bias in search:** Rewording a query when the first search returned nothing, hoping different phrasing will conjure a nonexistent tool.

## Reporting Blockers

When you stop, report in this shape:

```
There is no [tool/command/capability] available to [accomplish X].
The [tool catalog / CLI / API] does not support this.
To proceed, you would need to [create it yourself / install Y / use Z surface instead].
```

## Pitfalls

- **Looping when the tool catalog says no.** User explicitly flagged this: "if there's no way to do that, just say so when you realize it instead of going into a loop of trying to brute force your way into doing it through repetition and raw effort." This is the primary trigger for this skill.
- **Substituting effort for capability.** More tool calls do not create new capabilities. They only burn tokens and delay honest reporting.
