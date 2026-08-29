<!-- GENERICIZED: 4×{CLIENT} | source: skills/software-development/fullstack-ts-monorepo/SKILL.md -->
---
name: fullstack-ts-monorepo
description: Build/extend a pnpm+Turborepo TS monorepo.
version: 1.0.0
author: hermes-curator
license: MIT
metadata:
  hermes:
    tags: [typescript, monorepo, expo, fastify, prisma, postgres, postgis, pgvector, tdd]
    related_skills: [test-driven-development, systematic-debugging]
---

# Full-stack TypeScript monorepo (pnpm + Turborepo)

## When to Use
- Scaffolding a new app/service/package in this stack (pnpm+Turborepo, Expo, Next, Fastify, Prisma, Postgres/PostGIS/pgvector, Redis, Colima).
- Extending or debugging the API (Fastify plugins/routes), Prisma schema/migrations, or the Expo app against the live API.
- Integration tests that need DB/Redis fixtures, or any docker/Colima / mobile↔API dev-loop work.

Used to build the founder's marketplace products ({CLIENT}, {CLIENT}). Layout: `apps/mobile` (Expo SDK 57), `apps/web` (Next 15), `apps/api` (Fastify 5 + Prisma 6), `packages/design` + `packages/config`. macOS host, **Colima** (not Docker Desktop) for docker, test-first throughout.

## Workflow anchors
- **TDD (RED→GREEN)**: write the failing test first, run it (expect the module-missing RED), then implement, then confirm GREEN. Tests live under each package's `test/` and run via vitest.
- **Trust the REAL toolchain, not the LSP.** The diagnostics attached to file writes (`.ts`/`.tsx`) are frequently stale or noisy — node_modules `.d.ts` errors, `TS18028 Private identifiers`, "Cannot find module" for installed packages, `#types/hmrPayload` — from a different tsconfig context. Always confirm with `pnpm --filter <pkg> typecheck` / `tsc`. Do not chase LSP noise; do fix real `tsc` errors.
- **Port hygiene**: `:3000` is owned by the founder's other backend. API `:4000`, web `:3001`, Postgres host `:5433`, Redis `:6379`, Metro `:8081`.
- **fastify-plugin for every decoration** (db, redis, services, config). A plain plugin's decorations are invisible to siblings. Also declare custom decorations in a `declare module "fastify"` block so typed routes (`app.config`, `app.chatService`, …) resolve.
- Build order that works: schema+migration → db/redis/errors/rate-limit plugins → auth service+routes → domain services (policy, discovery, booking, reviews, chat, notifications) → routes → integration tests → mobile app against the live API.

## Durable pitfalls
1. **pnpm store-dir drift** → `ERR_PNPM_UNEXPECTED_STORE` ("Unexpected store location"). `node_modules/.modules.yaml` records a `storeDir` that differs from the current store path; `pnpm add` / `expo install` then fail. Fix: `pnpm config set store-dir <the path written in .modules.yaml>` and retry. Align, don't wipe `node_modules`.
2. **`prisma migrate dev` needs a real TTY to CREATE migrations** — in a non-interactive shell it refuses/does nothing. Bypass: hand-write `prisma/migrations/<yyyymmddhhmmss>_<name>/migration.sql`, then `prisma migrate deploy` (applies + records it). CI uses `migrate deploy`.
3. **NEVER use `prisma migrate diff` when schema.prisma omits raw-SQL columns** (PostGIS `geography` column, pgvector `vector` column). diff sees the DB-only columns as drift and generates **DROP** statements for them — it will delete that infra when applied. Only add raw columns via explicit hand-written migration files.
4. **Raw-SQL columns aren't in Prisma types.** A column added only via a raw-SQL migration stays off the generated client until it's also in `schema.prisma`; adding to the schema without a matching migration creates drift. Keep schema.prisma and the migration history in lockstep.
5. **PostGIS/pgvector in dev**: bake extensions into a custom image (`pgvector/pgvector:pg16` + `apt-get install postgis` at build time) — initdb runs as non-root `postgres`, so apt-get inside init scripts fails. Use a generated `geography` column + GIST index for distance (`ST_DWithin`, `ST_Distance`); HNSW index on a `vector(1536)` column for semantic search (`1 - (emb <=> $vec::vector)`). For test-fixture embeddings use UNIQUE tokens so `ORDER BY sim DESC LIMIT 1` can't tie between a fixture skill and a seeded skill.
6. **Integration-test fixture cleanup**: delete in FK dependency order (reviews → sessions → bookings → proofs → accessPolicies → listings → mentorProfiles → refreshTokens → conversations → users → skills) in BOTH beforeAll and afterAll, keyed by a shared test-email suffix (`@test.dev`). Otherwise parallel test files delete each other's rows (FK violations) and reruns collide on unique keys.
7. **Background-process zombie notifications**: after session restore, an old process's completion can surface LATE with a transcript showing a destructive command (`docker compose down -v`, `rm -rf`, `colima start`, `brew install`). It usually EXECUTED long ago, before the current data existed. Before reacting, verify empirically (table/user counts, `/health/ready`). A fresh wipe would show zero tables, not healthy data.
8. **Expo Go phone can't reach `127.0.0.1:4000`** — that's the phone's own loopback. Resolve the dev API base from `Constants.expoConfig?.hostUri` (Metro's LAN host) → `http://<host>:4000`, falling back to `10.0.2.2` (Android emu) / `127.0.0.1` (iOS sim). Never hardcode localhost inside a screen. Sanity-check phone↔Mac with `http://<LAN-IP>:4000/health` from the phone browser.
9. **Dev login bypass** (founder walkthroughs): add production-gated dev endpoints — `GET /auth/otp/dev-code?email=` and `POST /auth/dev-login` (both 404 when `NODE_ENV=production`). App surfaces a "Dev mode: enter without a code" button. Keeps prod secure, one-tap entry in dev.
10. **Colima restart**: VM down → containers gone → `docker compose up -d`. The foreground guard may flag compose-up as a long-lived server; run it with `background=true` then poll health. Named volumes persist across the recreation — data survives.
11. **Expo in a pnpm monorepo**: Metro can't see pnpm's isolated layout. Three fixes together: `shamefully-hoist=true` in `.npmrc`, a `metro.config.js` with `watchFolders`+`nodeModulesPaths` pointing at the workspace root (and `.pnpm/node_modules`), and `"main": "index.js"` (NOT `node_modules/expo/AppEntry.js`). Add `@babel/runtime` explicitly. Full sequence in `references/expo-pnpm-metro.md`.
12. **Supabase Edge Functions can't import monorepo packages** — the bundler is restricted to `functions/`. Keep pure logic in `packages/core` (tested), mirror it in `supabase/functions/_shared/`, have functions import the mirror. Mock Stripe must be DB-backed (per-worker memory isn't shared across functions). Path parsing: the runtime strips `/functions/v1/`, so `seg[1]=id` not `seg[3]`. `createClient(url, serviceRoleKey)` resolves to `authenticated` role for `.from().insert()` — use raw REST fetch with the SR token for server-side writes. Details in `references/supabase-edge-functions.md`.
13. **Dedicated env var for DB scripts**: a stray generic `DATABASE_URL` (from another project) silently breaks seeders (`getaddrinfo ENOTFOUND`). Use `SOFRA_DATABASE_URL`-style names with a local fallback.

## Mobile UI conventions (founder preference)
"Look up standard design principles and apply them." Use platform-standard layout, not hand-rolled spacing:
- `react-native-safe-area-context`: `insets.top` on the top bar (below the status bar), `insets.bottom` on the tab bar.
- Touch targets ≥ **44pt** (Apple HIG); back chevron visually left-aligned but with a generous hit area and the title kept centered by a symmetric right slot.
- Buttons: horizontal padding (min `space(4)`), `minHeight ≈ 52`, `textAlign: center` so labels never touch edges and stay centered in two-up rows.
- Persistent **Message/coordinate affordances** on profile (Message button beside Book) and booking ("Message <mentor> to coordinate") — wired to real conversation start + thread navigation, not dead placeholders.

## References
- `references/{CLIENT}` — the {CLIENT} instance: repo path, exact commands, schema/service wiring, the access-policy engine contract, demo accounts.
- `references/supabase-edge-functions.md` — Supabase-backed backend inside a pnpm monorepo: Edge Functions bundle only inside `functions/` (mirror `packages/core` into `_shared/`), DB-backed mock Stripe for cross-worker money loops, service-role token + raw REST fetch gotchas, RLS patterns, idempotent deadline job, vitest `fileParallelism:false`, dedicated `SOFRA_DATABASE_URL`.
- `references/expo-pnpm-metro.md` — Expo inside a pnpm monorepo: `shamefully-hoist=true`, `metro.config.js` with `watchFolders`+`nodeModulesPaths`, `"main":"index.js"` not expo's AppEntry, explicit `@babel/runtime`.
