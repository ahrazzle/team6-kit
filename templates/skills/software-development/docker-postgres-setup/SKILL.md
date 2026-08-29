<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/software-development/docker-postgres-setup/SKILL.md -->
---
name: docker-postgres-setup
description: Set up Postgres in Docker with PostGIS and pgvector.
version: 0.1.0
author: {RELATIONSHIP}
license: MIT
tags: [docker, postgres, postgis, pgvector, dev-setup]
---

# Docker Postgres Setup (PostGIS + pgvector)

## When to Use

Setting up local PostgreSQL in Docker with specialized extensions (PostGIS for geospatial, pgvector for vector search). Needed when a project requires both capabilities in a single container.

## The Problem

Getting multiple PostgreSQL extensions into one Docker container is non-trivial:
- Official `postgres` image ships with no extensions.
- `postgis/postgis` does NOT include pgvector.
- `pgvector/pgvector` does NOT include PostGIS.
- `timescaledb/timescaledb-ha` may not exist for your PG version or requires auth.
- Building extensions from source is slow and fragile.

## The Working Pattern (PostgreSQL 16)

Use `pgvector/pgvector:pg16` as the base (pgvector pre-compiled), then install PostGIS via apt on top.

### Dockerfile

```dockerfile
FROM pgvector/pgvector:pg16

RUN apt-get update && apt-get install -y \
    postgresql-16-postgis-3 \
    postgresql-16-postgis-3-scripts \
    && rm -rf /var/lib/apt/lists/*

COPY scripts/init-db.sh /docker-entrypoint-initdb.d/init-db.sh
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh
```

### init-db.sh

```bash
#!/bin/bash
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-SQL
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS vector;
SQL
```

### docker-compose.yml

```yaml
services:
  postgres:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: project-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: db
    ports:
      - '5433:5432'
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U user']
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

## Why This Works

`pgvector/pgvector:pg16` comes with pgvector pre-installed. The Debian base has apt, so you install PostGIS via `postgresql-16-postgis-3`. Both extensions land in the same Postgres instance.

## Alternatives Considered

| Approach | Why It Fails |
|----------|--------------|
| `timescaledb/timescaledb-ha:pg16` | Image does not exist (pull access denied) |
| `postgres:16` + build both from source | Slow (~5+ min), needs build-essential + postgresql-server-dev |
| `postgis/postgis:16-3.4` + build pgvector | Same slow build, plus PostGIS pulls many heavy deps |
| `pgvector/pgvector:pg16` + apt install PostGIS | Works — cleanest, fastest path |

## Pitfalls

- **Port conflicts**: Local Postgres on 5432? Map container to 5433.
- **Colima disk space**: Docker builds inside Colima can hit disk limits. Run `docker system prune -af` and bump Colima disk (`colima start --disk 30`) if you see "no space left on device".
- **Extension path mismatch**: Match apt package to PG major version (`postgresql-16-postgis-3` for PG16). Mismatch = extension files not found.
- **Top-level await with tsx**: "Top-level await is not supported with CJS output" → add `"type": "module"` to package.json.

## Version Notes

- Match PostGIS package to PG version: `postgresql-16-postgis-3` for PG16, `postgresql-15-postgis-3` for PG15.
- pgvector version is pinned by base image tag (`pg16` → latest pgvector for PG16).
- To pin a specific pgvector version, build from source.

## Verification

```bash
docker exec project-postgres psql -U user -d db -c \
  "SELECT extname, extversion FROM pg_extension WHERE extname IN ('postgis', 'vector');"
```

Expected: `postgis | 3.6.4` and `vector | 0.8.6` (or current versions).

Test PostGIS:
```bash
docker exec project-postgres psql -U user -d db -c \
  "SELECT ST_Distance(ST_MakePoint(-73.9857, 40.6928)::geography, ST_MakePoint(-74.0060, 40.7128)::geography) / 1000;"
```

Test pgvector:
```bash
docker exec project-postgres psql -U user -d db -c \
  "SELECT '[1,2,3]'::vector <-> '[4,5,6]'::vector;"
```
