<!-- GENERICIZED: 11×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/project-foundation-scaffold/SKILL.md -->
---
name: project-foundation-scaffold
description: "Use when scaffolding a new project. Monorepo, infra, CI."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
tags: [monorepo, scaffold, turborepo, pnpm, project-setup, phase-0]
---

# Project Foundation Scaffold

## When to Use

- Starting a new project from a detailed execution plan (locked decisions + open questions)
- Standing up a TypeScript monorepo with mobile + web + API
- Setting up infrastructure-as-code (Docker Compose, CI) from day one
- Creating shared packages (types, design tokens, db client) that multiple apps consume

## The Pattern

Given a detailed plan, execute Phase {CLIENT} (Foundations) as a single coherent pass:

1. **Parse the plan** — identify locked decisions, open questions, tech stack, package topology
2. **Create open-decision list** — flag anything the user must confirm before Phase {CLIENT}+
3. **Scaffold monorepo** — pnpm + Turborepo with `apps/*` and `packages/*`
4. **Wire infrastructure** — Docker Compose (PostgreSQL + extensions, Redis), CI workflow
5. **Create shared packages** — types/db/design/ui/config per the plan's topology
6. **Apply first migration** — prove the database + Prisma pipeline works
7. **Run stack spike** — verify each extension/tech actually works, paste outputs to user
8. **Commit** — one commit per logical unit, clear messages

## Decision Triage

Before scaffolding, classify every decision in the plan:

| Type | Action |
|------|--------|
| **Locked** (user confirmed) | Build to it exactly |
| **Open** (user must decide) | Build the infra to support either answer; flag at REVIEW PAUSE |
| **Plan default** (recommendation) | Build to the default; note it can change at REVIEW PAUSE |

Never proceed past a REVIEW PAUSE without user confirmation.

## Monorepo Structure

Default topology (adjust per plan):

```
apps/
  mobile/          # Expo (React Native)
  web/             # Next.js (App Router)
  api/             # Fastify
packages/
  shared/          # Zod schemas + TS types
  design/          # Design tokens (no components)
  ui/              # Component primitives (depends on design)
  db/              # Prisma client singleton
  config/          # Shared tooling configs
```

Keep `design` and `ui` separate — tokens are the foundation layer; components consume them. This unblocks design work while components are still being specified.

## Package Conventions

Every package gets:
- `package.json` with `name`, `version`, `private`, `main`, `types`, `scripts`
- `tsconfig.json` extending root `../../tsconfig.json`
- Workspace dependencies via `workspace:*`

For ESM packages (`"type": "module"`), top-level await works in tsx. For CJS, wrap in async IIFE.

## Infrastructure

### Docker Compose

- Use a pre-built image when possible (`pgvector/pgvector:pg16` + apt PostGIS)
- Map to non-default ports if local services occupy them (e.g., `5433:5432` when local PG is on 5432)
- Always add healthchecks
- One-time extension setup via `/docker-entrypoint-initdb.d/` scripts

See `docker-postgres-setup` skill for the full Docker pattern.

### CI (GitHub Actions)

```yaml
name: CI
on:
  push: { branches: [main, develop] }
  pull_request: { branches: [main] }
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm typecheck
      - run: pnpm lint
      - run: pnpm test
      - run: pnpm build
```

## Stack Spike Verification

Verify each piece of new infrastructure works before declaring Phase {CLIENT} done:

| Component | Verification |
|-----------|-------------|
| PostgreSQL + PostGIS | `ST_Distance()` returns expected km between two points |
| pgvector | Cosine distance between two vectors; top-k search |
| Fastify API | `/health` endpoint returns JSON |
| Prisma | Migration applies clean; client generates |
| Docker | `docker ps` shows healthy containers |

Paste the actual outputs to the user — never claim "it works" without evidence.

## Shared Package Content

### @{CLIENT}/shared

Start with Zod schemas for core domain types. Export from `src/index.ts`, one file per schema:

```typescript
// schemas/access-policy.ts
import { z } from 'zod';
export const AccessMode = z.enum(['MERIT', 'CASH', 'HYBRID']);
export const AccessPolicySchema = z.object({ ... });
export type AccessPolicy = z.infer<typeof AccessPolicySchema>;
```

### @{CLIENT}/design

Tokens as typed TypeScript constants (not CSS variables) for full type safety across Expo and Next.js:

```typescript
export const colors = { primary: '#1a1a2e', ... } as const;
export const spacing = { xs: 4, sm: 8, ... } as const;
export const typography = { fontFamily: { ... }, fontSize: { ... } } as const;
```

Include domain-specific tokens (e.g., access-badge colors) in the design package — they're a design concern, not a component concern.

### @{CLIENT}/db

Singleton Prisma client export:

```typescript
import { PrismaClient } from '@prisma/client';
export const prisma = new PrismaClient({ ... });
export * from '@prisma/client';
```

## Pitfalls

- **Port conflicts**: Local Postgres on 5432? Use 5433 for Docker. Always check with `lsof -i :5432`.
- **Colima disk space**: Docker builds inside Colima hit disk limits. Run `docker system prune -af` and `colima start --disk 30` before large builds.
- **Top-level await with tsx**: Add `"type": "module"` to package.json or wrap in async IIFE.
- **Extension version mismatch**: Match apt packages to PG major version (`postgresql-16-postgis-3` for PG16).
- **Workspace protocol**: Use `workspace:*` for intra-monorepo dependencies, not version numbers.
- **First migration before code**: Apply a placeholder migration immediately to prove the DB → Prisma → migration pipeline works, then expand the schema in Phase {CLIENT}.

## References

- [{CLIENT} session files](references/{CLIENT}) — complete Phase {CLIENT} scaffold from {CLIENT} project (Aug 2026)
