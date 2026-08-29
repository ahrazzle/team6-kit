<!-- GENERICIZED: 9×{CLIENT}, 2×{RELATIONSHIP} | source: skills/software-development/fullstack-ts-monorepo/references/{CLIENT} -->
# {CLIENT} instance — stack reference

Repo: `/Users/{RELATIONSHIP}/{CLIENT}{CLIENT}` (git, branch `main`).

Runbook (governing plan with REVIEW PAUSE checkpoints): `~/.hermes/profiles/{RELATIONSHIP}/attachments/finalplan.md`. Phases: 0 foundations+spike → 1 PRD+brand+clickable prototype → 2 data model/auth/API core → 3 discovery app MVP → 4 {CLIENT} economy (ledger/levels/streaks) → 5 AI matching → 6 hardening → 7 launch.

## Commands (from repo root unless noted)
- Install: `pnpm install` (pnpm 11.21.0 via standalone installer, PATH at `~/.local/share/pnpm/bin`).
- Services: `docker compose up -d` (db={CLIENT} :5433, redis={CLIENT} :6379). PostGIS image is custom (`pgvector/pgvector:pg16` + apt-get postgis at build).
- Migrate/seed (api): `pnpm exec prisma migrate deploy`; `pnpm exec tsx prisma/seed.ts`. NOTE: `migrate dev` needs a TTY; create migrations by hand + deploy.
- Run API: `cd apps/api && pnpm start` (tsx, :4000). Swagger at `http://localhost:4000/docs`.
- Run Metro: `cd apps/mobile && EXPO_NO_TELEMETRY=1 CI=0 pnpm start --port 8081`.
- Gate (root): `pnpm lint && pnpm typecheck && pnpm test && pnpm build`.

## Auth / identity (MVP = built-in passwordless OTP; Clerk is a documented drop-in)
- `POST /auth/otp/request` (204, never leaks account existence) → code stored in Redis `otp:<email>` (TTL 600s, 5-attempt lockout) → `POST /auth/otp/verify` → `{accessToken, refreshToken, user}`.
- Dev-only (404 when `NODE_ENV=production`): `GET /auth/otp/dev-code?email=` (returns pending code) and `POST /auth/dev-login` (creates user + returns tokens, no OTP).
- Sessions: HS256 JWT access (15m) + opaque refresh token stored hashed, rotated on every use.
- Demo account: `demo@{CLIENT}` / "Demo Seeker" / **Level 4** (unlocks DISCOUNT + L3/L4 merit doors; L5 stays locked to demo rejection).

## Access-policy engine (the locked mechanic — port to any consumer 1:1)
`PolicyService.evaluate(policy, learnerLevel)` in `apps/api/src/services/policy.service.ts`. Modes: MERIT (level gate), CASH (pay), HYBRID with combinator AND | EITHER | DISCOUNT. Instant-book split per payment type: `instantBookCash` / `instantBook{CLIENT}` (default false → request/accept/decline flow). 11-case spec test: `apps/api/test/policy.service.test.ts`. Price snapshot + `policySnapshot` JSON on the Booking at creation.

## Schema & services
- 14 domain models + enums; `AccessPolicy` carries mode/combinator/meritLevelRequired/priceCents/discountPercent/instantBook*. `User.kycStatus` (NONE/PENDING/VERIFIED), `Listing.format` (IN_PERSON/VIRTUAL/EITHER), `MentorProfile.proofs` (LINKEDIN/VIDEO/PRESS/TESTIMONIAL).
- Services (decorated on Fastify, all `fastify-plugin`): policy, discovery (PostGIS feed + pgvector semantic search + filters), booking (policy enforcement + payment provider interface + lifecycle + notifications), reviews (value-confirmed = {CLIENT} seed), chat (Socket.io realtime + REST), notifications (booking/message/review triggers).
- Dev providers behind interfaces (drop-in later): DevPaymentProvider (records refs, Stripe Connect later), HashEmbeddingProvider (token-overlap vectors, real provider later), built-in OTP (Clerk later).

## Watch-outs hit on this project
- Zod 4 was installed (`z.string().email()` etc. still fine). `@fastify/type-provider-zod` (not `fastify-type-provider-zod`); swagger transform is `createJsonSchemaTransform` from the type-provider package.
- `fastify` types the error-handler `err` as `unknown` in some spots — cast before `.message`.
- Mobile `ListingDetail` contract: must include `stats {rating, reviewCount, totalSessions}`, `mentor {rating, sessions, verified, ...}`, top-level `headline`/`bio`, proofs with `id`. Lock it with an API test so it can't drift.
- Detail endpoint returns `{ user: publicUser }` at `/me`; the app reads `.user`.
- Phone dev connectivity: resolve base from `Constants.expoConfig?.hostUri` → `http://<host>:4000` (see umbrella skill pitfall 8).
