<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/autonomous-ai-agents/project-initializer/SKILL.md -->
---
name: project-initializer
description: "Use when the user asks to create a new project."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
---

# Project Initializer

Creates a new Hermes Project when starting a new group chat or workspace.

## When to Use

- The user asks to "create a project" or "set up a workspace"
- A new group chat starts and needs a workspace anchor
- Starting work in a new repo/folder

## Process

1. User provides:
   - **Name**: Human-readable project name
   - **Directory**: Absolute path to the workspace folder

2. Create the project:
   ```
   project_create(name="...", path="...")
   ```

3. Confirm with the project ID and anchored path.

## Rules

- Both name and path are provided by the user. Do not ask for them — create immediately.
- Path must be absolute.
- If a project with the same name exists, warn before overwriting.

## Group Chat Workflow

When a new group chat starts:
1. User provides name and directory
2. Create the project immediately — do not ask for clarification or a brief
3. Set workspace to that directory
4. Then proceed with task delegation
