<!-- GENERICIZED: 4×{CLIENT}, 1×{RELATIONSHIP} | source: skills/software-development/fullstack-monorepo-dev/SKILL.md -->
---
name: fullstack-monorepo-dev
description: Use when building Fastify/Prisma or Supabase/Edge Functions + Expo pnpm monorepos.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
metadata:
  hermes:
    tags: [monorepo, fastify, prisma, postgres, expo, tdd]
    related_skills: [test-driven-development, plan, spike, systematic-debugging]
---

# Full-stack monorepo development (Fastify/Prisma OR Supabase/Edge Functions + Expo)

Class-level workflow for this user's pnpm workspace + Turborepo stacks. Two backend
flavors: `apps/api` (Fastify 5 + Prisma 6 + zod + vitest) for {CLIENT}, or
Supabase (Auth, Postgres, Realtime, RLS) + Edge Functions for anything money, with
`apps/mobile` (Expo SDK), `apps/web` (Next 15), `packages/ui` (shared RN+web design
system). Both flavors run plan-driven with hard review checkpoints.

## Operating mode (user expectations)
- The plan file (attachments/finalplan.md) is the anchor. Execute phases in order; STOP at every REVIEW PAUSE; present a decision summary; use `clarify()` with the RECOMMENDED option FIRST; wait for the founder's verdict before continuing. Never slip past a pause.
- TDD (plan rule R3): write failing tests first (verify RED), then implement (verify GREEN).
- Each phase ends with the full gate — `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build` all green — then one meaningful commit.
- The founder tests on a physical phone (Expo Go over LAN) and wants dev friction removed: one-tap dev login, auto-fetched OTP codes, visible "API: <url>" hint. Never build "ceremony" around dev entry.
- Background-process notifications can arrive HOURS after execution (session restores replay historical transcripts — including destructive commands like `docker compose down -v`). Verify current state empirically (lsof / curl / docker ps / row counts) before reacting; never re-execute anything from a zombie transcript.
- LSP write-time diagnostics on this stack are frequently stale or wrong-context (node_modules d.ts noise, missing exports that exist). Trust real `pnpm --filter <pkg> typecheck` (tsc with skipLibCheck).

## Pitfalls quick map (details in references/)
| Area | Lesson | Reference |
|---|---|---|
| Prisma | `migrate dev` needs a TTY; NEVER `migrate diff --from-schema-datasource` with raw-SQL columns (generates DROPs); Prisma types come from schema.prisma, not the DB. A hand-written raw-SQL migration must be ADDITIVE-ONLY — if a bad diff wrote DROP statements into the file, rewrite it to add-only AND re-add the dropped columns via manual SQL (fresh DBs replay the file). **1:1 relations fail validation (P1012) unless the defining-side FK is `@unique` — nullable+unique is fine in PG and enforces one-redeem-per-account at the DB level; apply the extra index to the live DB too (applied migration won't re-run).** | references/prisma-migrations.md |
| Code-editing / TS | **Side-effect calls after `return` are dead code** — `return reply.status(201).send({x}); void analytics.record(...)` never fires; put side-effects BEFORE the return. **`ReturnType<Service["method"]>` of an async method is a Promise** — use `Awaited<ReturnType<...>>` (define `type FeedResult = Awaited<...>`) before indexing `.listings`. **Insert-clobber:** inserting a new `export const X = {` before an existing declaration via find-replace can swallow the existing header (orphan its body, `;` expected) — anchor old_string on the FULL existing declaration line to preserve the boundary. | references/fastify-plugin-zod.md |
| Fastify | fastify-plugin for decorations + `declare module "fastify"` augmentations; error handler must pass through `err.statusCode` (rate-limit 429 → 500 bug); swagger transform lives in `@fastify/type-provider-zod` | references/fastify-plugin-zod.md |
| Expo | device can't reach localhost — resolve API from Metro hostUri; reload bundle after code changes. EVERY fetch must use that single resolved base — a per-screen hardcoded `http://127.0.0.1:4000` fallback silently breaks device testing (an onboarding screen had one) | references/expo-dev-connectivity.md |
| Demo walkthroughs | dev-only login/OTP endpoints gated on NODE_ENV; demo account state must be LEDGER-BACKED with recent timestamps (a running `day` counter drifted all synthetic ledger dates 60+ days back — streak/league read as empty). One obvious CTA per screen — a redundant secondary link is "janky". | references/dev-demo-login.md |
| pnpm 11 | allowBuilds placeholder auto-injection blocks postinstall; store-dir drift → ERR_PNPM_UNEXPECTED_STORE. Expo/RN under pnpm also needs `shamefully-hoist=true` + a metro.config with watchFolders/nodeModulesPaths pointing at the workspace root so Metro can resolve `expo-modules-core` etc. | references/pnpm-workspace.md, references/supabase-edge-functions.md |
| Docker (pnpm) | `pnpm deploy --prod --legacy` strips gitignored `dist` AND the generated Prisma client ("did not initialize yet") — regenerate into /out after deploy. `rootDir "."` emits `dist/src`, but `cp -r dist/src /out/dist` flattens → container CMD is `node dist/server.js`. Run migrations in the deploy pipeline, never `npx prisma` in the container (fetches latest major → drift). | references/docker-pnpm-prisma.md |
| Env pollution | `terminal` persists exports across calls; `export $(grep .env)` can leak a corrupted `DATABASE_URL` (trailing `"` → `%22`), and dotenv does NOT override existing vars → every Prisma test fails "URL must start with postgresql://". Fix: `unset DATABASE_URL REDIS_URL JWT_SECRET` before `pnpm test`. | references/docker-pnpm-prisma.md |
| Vitest | idempotent FK-ordered fixture cleanup in beforeAll AND afterAll; parallel files share the DB — distinct email prefixes per file; poll for async delivery, never fixed sleeps. When distinct prefixes still race, harden with `test: { fileParallelism: false }`; adding a NEW user-linked table (e.g. {CLIENT}) breaks every existing cleanup — purge it in each file before `user.deleteMany`. Base tsconfig has `noUncheckedIndexedAccess` — use `rows[0]!`. | references/test-isolation.md |
| Supabase / Edge Functions | Edge runtime bundles ONLY inside `functions/` — it can't import monorepo packages; keep a lockstep Deno-safe mirror in `functions/_shared/`. Serve strips `/functions/v1/` from `req.url`, so `seg[1]`=id, `seg[2]`=action (not seg[3]/seg[4]); consolidate REST surface into one function dir per resource. Mock Stripe must be DB-backed (in-memory is per-worker). Grant SELECT to anon/authenticated on custom tables explicitly. | references/supabase-edge-functions.md |
| UI motion / dopamine | One RN `Animated` layer in `packages/ui` covers native+web; CSS keyframes (`page-in`, `rise-in`, `glow-pulse`, shimmer) live in web `globals.css`. className is NOT a valid prop on RN components (type error) — wrap animated bits in plain `<div className>` in web-only pages. Resolve the "no gamification vs dopamine" tension as WARM dopamine. Next 15 dynamic route `params` is a Promise — `await params`. | references/ui-motion-pass.md |

## Verification loop
1. Change code → 2. targeted test `pnpm --filter @{CLIENT} test` → 3. typecheck → 4. full gate → 5. commit. When a test fails: read the real assertion output (grep `AssertionError`), fix the cause or the wrong test premise, re-run. Never commit a red suite. NOTE: `grep -c` prints `0` AND exits 1 when nothing matches — chaining `grep -c error && next` aborts the chain on a CLEAN result; run checks as separate commands or use `grep -q`.

## Service lifecycle (Colima + docker)
Recovery after VM/container death: `colima start` (background) → wait `docker info` → `docker compose up -d` (background) → wait health via `docker inspect --format '{{.State.Health.Status}}' {CLIENT}` → verify API `/health/ready` (pings db+redis) → row-count the data. Named volumes survive VM restarts; only a real `down -v` wipes data — confirm with a count before assuming loss. Kill-by-port must be its own command (`lsof -ti :4000 | xargs kill`) — combined with a server-start command it trips the long-lived-process guard and the kill never runs.
