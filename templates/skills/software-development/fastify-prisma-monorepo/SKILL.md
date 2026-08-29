<!-- GENERICIZED: 1×{CLIENT} | source: skills/software-development/fastify-prisma-monorepo/SKILL.md -->
---
name: fastify-prisma-monorepo
description: Fastify/Prisma/pnpm monorepo builds, migrations, Docker.
---

# Fastify + Prisma + pnpm monorepo (backend)

Recurring traps when building a TypeScript pnpm-workspace backend with Fastify,
Prisma, Postgres, and Docker.

## Prisma migrations
- `prisma migrate dev` **refuses to create a migration without a real TTY** (non-interactive shells silently no-op it). Workaround: hand-write a migration dir (`prisma/migrations/<ts>_<name>/migration.sql`) + `prisma migrate deploy`. Alternative: `prisma migrate diff` but beware its direction — diffing live-DB→schema when raw-SQL columns exist emits DROPs for them.
- **Schema-first, never column-first:** raw SQL adds a column that Prisma's generated client can't see — the client types come from `schema.prisma`, not the live DB. Add the field to the schema, THEN migrate. If you need geo/vector types Prisma can't model (PostGIS `geography`, pgvector `vector`), keep them in raw-SQL migrations and mark them so later `migrate diff` doesn't drop them (hand-write additive-only migrations).
- After applying, always `prisma generate` (client lives in the `.pnpm` store path, not a committed location).

## pnpm 11 build-script approval
pnpm 11 uses `allowBuilds:` (a boolean map) in `pnpm-workspace.yaml` to approve postinstall scripts. The old `onlyBuiltDependencies:` list is **ignored**. If `prisma`, `@prisma/client`, `@prisma/engines`, `esbuild`, or `sharp` aren't listed as `true` under `allowBuilds`, a fresh install (e.g. in Docker) fails with `ERR_PNPM_IGNORED_BUILDS`. A local install may "work" only because the store already has them built.

## Docker multi-stage (pnpm monorepo)
- Use `pnpm --filter <pkg> deploy --prod --legacy /out` to assemble a self-contained prod tree (`--legacy` needed when the package has no injected workspace deps). Then regenerate the Prisma client INTO the deploy output:
  ```
  RUN pnpm --filter @{CLIENT} deploy --prod --legacy /out \
      && cp -r apps/api/dist/src /out/dist \
      && cp -r apps/api/prisma /out/prisma \
      && cd /out && /repo/apps/api/node_modules/.bin/prisma generate --schema prisma/schema.prisma
  ```
  Without the regenerate, `@prisma/client did not initialize yet` at runtime (the generated client is a build artifact pnpm deploy strips).
- **`rootDir: "."`** in tsconfig makes tsc emit `dist/src/server.js`, not `dist/server.js`. The Docker `CMD` and `start:prod` must match the actual output path.
- **Don't run `prisma migrate deploy` in the container** — `npx prisma` without a local CLI fetches the LATEST prisma (e.g. 7.x) which mismatches a v6 schema. Run migrations in the CI/promotion pipeline before the container starts.

## Vitest with a shared real DB
- Multiple test files hitting the same Postgres race each other; set `fileParallelism: false` in `vitest.config.ts` to serialize files (each file's tests still run in parallel).
- Fixture cleanup must purge generated rows (ledger, skills, media, referrals) or the next run hits unique-constraint conflicts on `create`. Cleanup is the failure point — dependency-ordered deletes, and delete by unique email/slug patterns, not counts.

## Env gotcha
Tests load `.env` via dotenv, which does NOT override already-set process env vars. If you ever `export $(grep ... .env)` into the session shell (e.g. for a Docker test), that polluted value leaks into test runs and can break `DATABASE_URL` validation. `unset DATABASE_URL REDIS_URL JWT_SECRET` before running tests.
