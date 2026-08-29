<!-- GENERICIZED: 9×{CLIENT} | source: skills/software-development/web-build-verification/references/{CLIENT} -->
# {CLIENT} contact-info round (v6.17 / v6.17.1) — LLM contact access + phone swap

Session: {CLIENT}, {CLIENT} gateway + division pages, staging-first loop.

## User asks

1. Give the terminal LLM access to the firm's email and phone.
2. Site phone number → `tel:416-500-4462` (then corrected to `tel:289-928-9554` — first number was wrong).

## What shipped (verified against served bytes)

### 1. LLM contact access — in the system prompt

`api/ask.mjs` SYSTEM_PROMPT line:

```
'- Contact: email info@{CLIENT}, phone +1-289-928-9554 (tel:289-928-9554). When asked for contact details, give these exactly.',
```

Live POST asking "what is your email and phone?" returned: `info@{CLIENT}` and `+1-289-928-9554`.

### 2. `/call` command — target lives in the SERVED COMPONENT FILE, not the HTML mount

The landing HTML mounts the shared component with a minimal config:

```js
{CLIENT}({
  root: document.getElementById('askterm'),
  api: '/api/ask',
  intro: '{CLIENT} deploy --emerging-tech --funded',
  readyLine: 'capability demo ready'
});
```

No command map there. The full map — including `/call` — lives inside the served `assets/js/{CLIENT}`:

```js
{cmds:['/call','/phone','call','phone'], action:'tel', target:'289-928-9554', label:'call us directly'}
```

Dispatch: `window.location.href='tel:'+target`.

**Lesson: to verify any command behavior, fetch the served component JS with a cache-buster and read the map there. Reading the HTML mount config proves nothing.**

### 3. Three-surface phone swap verification

After the correction to 289-928-9554:

| Surface | Old `416-500-4462` | New `289-928-9554` |
|---|---|---|
| `git grep '416-500-4462' HEAD` (whole tree) | **0** | — |
| served `digital/` page | 0 | 1 (`tel:289-928-9554` Call us button) |
| served `physical/` page | 0 | 1 (`tel:289-928-9554` Call us button) |
| served landing page | 0 | 0 (no static phone — terminal `/call` is its surface, correct) |
| served `{CLIENT}` | 0 | `target:'289-928-9554'` |
| `api/ask.mjs` prompt (HEAD) | 0 | `+1-289-928-9554 (tel:289-928-9554)` |

`git grep '<old>' HEAD` returning 0 across the tree is the strongest single evidence — it proves the old value is excised from source, not just hidden in served output.

## Repeated verification notes from this round

- The old number had ALSO to be purged from the LLM prompt or the assistant would answer with the stale contact.
- The landing page correctly has no static phone button — its phone surface is the `/call` slash command; verify surfaces per design, not uniformly.
- Blocked-command recovery used repeatedly this session: oversized inline shell payloads → saved to `~/.hermes/profiles/<profile>/cache/blocked-scripts/blocked-*.sh` → run `bash <path>` (never retry inline).
