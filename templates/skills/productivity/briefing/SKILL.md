<!-- GENERICIZED: 2×{RELATIONSHIP} | source: skills/productivity/briefing/SKILL.md -->
---
name: briefing
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
triggers:
  - "brief"
  - "brief me"
description: Generate a project status briefing for the user on demand.
metadata:
  hermes:
    tags: [productivity, status, briefing, project-management]
    related_skills: []
---

# Briefing

When the user says "brief" or "brief me", generate a structured project status update and deliver it.

## When to Use

Trigger when the user says "brief" or "brief me" in any chat context.

## Steps

1. **Scan session history** to identify the current project state.
2. **Categorize** all items into the four buckets below.
3. **Format** using the template.
4. **Deliver** to the user.

## Output Template

```
📋 PROJECT BRIEF

✅ COMPLETED
- [item]
- [item]

🔄 IN PROGRESS
- [item] — @owner
- [item] — @owner

⏸️ BLOCKED / WAITING
- [item] — waiting on [what/who]
- [item] — blocked by [reason]

❓ INPUT NEEDED FROM YOU
- [decision or input required]
- [decision or input required]

📌 NEXT STEPS
- [what happens next]
```

## Rules

- Only include items that have actually been discussed or worked on in this session. Do not invent or assume.
- If governance or decision-rights are established, include a one-line note on the current governance state.
- If nothing has happened yet (fresh session), say so — don't pad.
- Keep it scannable. Use short lines. The user fatigues easily.

## Delivery

- In a group chat: deliver to the room. All messages are visible to chat participants.
- For private delivery: tell the user to use {RELATIONSHIP}'s 1:1 chat, or use `send_message` if a separate DM session is available.
