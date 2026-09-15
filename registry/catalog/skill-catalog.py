#!/usr/bin/env python3
"""
skill-catalog.py — compact skill catalog router (read-on-demand).

WHAT IT DOES
  Serves compact candidate cards from a generated catalog. A card carries
  metadata and an exact local read path to the skill's SKILL.md — never the
  body. Resolution is read-on-demand: the body is loaded only when the caller
  asks for it with `--open`.

ENGINES (both deterministic and bounded)
  fts   in-memory SQLite FTS5 candidate retrieval, then the shared scorer
  json  full deterministic JSON scoring (the fallback)
  auto  FTS5 when available and safe to represent, else json (default)

  Both engines apply the SAME scorer, over the SAME tokenization, so the
  top-N ordering and exact-name behavior are identical (see the `fallback`
  fixture). The FTS path exists to bound candidate retrieval on large
  catalogs; it is a prefilter, never a different ranking.

FAIL-CLOSED (an entry is NOT router-visible when:)
  - a required provenance field (pack/source/license/provenance/id/read_path)
    is missing or empty
  - its pack is not declared under the packs directory
  - its funnel is not declared by the pack
  - its read_path escapes the root or does not resolve on disk (stale)
  - the lock exists and the entry is absent from it, or the catalog digest
    does not match the lock (tampered)
  Excluded entries never appear in results; `--audit` lists them with reasons.

USAGE
  skill-catalog.py search <funnel|all> "<query>" [--format json|text]
                          [--limit N] [--engine auto|fts|json] [--open]
  skill-catalog.py audit
  skill-catalog.py list-funnels

EXIT
  0 = ran (search may legitimately return zero results)
  1 = fail-closed configuration error (unreadable catalog/pack)
  2 = usage error

Standard library only. No network, no third-party dependency.
"""

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DEFAULT_CATALOG = os.path.join(SCRIPT_DIR, "catalog.json")
DEFAULT_PACKS_DIR = os.path.join(SCRIPT_DIR, "packs")

TOKEN_RE = re.compile(r"[a-z0-9]+")
# Query-side only: single characters and English function words carry no
# routing signal and, under prefix matching, match almost every entry. They
# are dropped from the QUERY, never from the indexed fields (so scoring stays
# a pure function of the query and the entry).
STOPWORDS = frozenset((
    "a", "an", "the", "of", "to", "in", "on", "for", "and", "or", "is",
    "be", "do", "it", "at", "by", "as", "my", "we", "i", "me", "us",
))
REQUIRED_ENTRY_FIELDS = ("id", "name", "funnel", "pack", "source",
                         "license", "provenance", "read_path")
DEFAULT_LIMIT = 5
MAX_LIMIT = 20
CANDIDATE_CAP = 100

# Field weights — a query token scores the MAX weight of any field it matches.
FIELD_WEIGHTS = {
    "name": 5,
    "id": 4,
    "aliases": 4,
    "tags": 3,
    "capabilities": 3,
    "description": 2,
    "funnel": 1,
}
# Fixed order for deterministic "why" reporting.
FIELD_ORDER = ("name", "id", "aliases", "tags", "capabilities",
               "description", "funnel")


def tokenize(text):
    return TOKEN_RE.findall(str(text).lower())


def query_tokens(text):
    """Tokens that carry routing signal (>=2 chars, non-stopword)."""
    return [t for t in tokenize(text) if len(t) >= 2 and t not in STOPWORDS]


def field_tokens(entry):
    return {
        "name": tokenize(entry.get("name", "")),
        "id": tokenize(entry.get("id", "").replace("/", " ")),
        "aliases": [t for a in entry.get("aliases", []) for t in tokenize(a)],
        "tags": [t for tag in entry.get("tags", []) for t in tokenize(tag)],
        "capabilities": [t for c in entry.get("capabilities", [])
                         for t in tokenize(c)],
        "description": tokenize(entry.get("description", "")),
        "funnel": tokenize(entry.get("funnel", "")),
    }


def token_matches(query_token, tokens):
    """Exact token, or prefix — the same predicate FTS5 'tok*' applies."""
    for t in tokens:
        if t == query_token or t.startswith(query_token):
            return True
    return False


def score_entry(entry, query_tokens, fields=None):
    """Return (score, matched_field_names). Deterministic; no I/O."""
    if not query_tokens:
        return 0, []
    fields = fields or field_tokens(entry)
    total = 0
    matched = set()
    for qt in query_tokens:
        best = 0
        for field in FIELD_ORDER:
            if token_matches(qt, fields[field]):
                matched.add(field)
                if FIELD_WEIGHTS[field] > best:
                    best = FIELD_WEIGHTS[field]
        total += best
    # Exact-name bonus (whole normalized query equals the entry name).
    if "".join(query_tokens) == "".join(fields["name"]):
        total += 10
        matched.add("name")
    return total, [f for f in FIELD_ORDER if f in matched]


def rank(entries, query, funnel="all"):
    """Return the ranked, bounded candidate list for a query."""
    qtokens = query_tokens(query)
    if not qtokens:
        return []
    scored = []
    for entry in entries:
        if funnel not in ("all", None) and entry["funnel"] != funnel:
            continue
        score, why = score_entry(entry, qtokens)
        if score > 0:
            scored.append((score, why, entry))
    scored.sort(key=lambda row: (-row[0], row[2]["id"]))
    return scored


def make_card(score, why, entry, n_tokens):
    confidence = round(min(1.0, score / (5.0 * max(1, n_tokens))), 3)
    return {
        "id": entry["id"],
        "name": entry["name"],
        "description": entry.get("description", ""),
        "funnel": entry["funnel"],
        "pack": entry.get("pack"),
        "source": entry.get("source"),
        "license": entry.get("license"),
        "provenance": entry.get("provenance"),
        "read_path": entry["read_path"],
        "tags": entry.get("tags", []),
        "capabilities": entry.get("capabilities", []),
        "score": score,
        "confidence": confidence,
        "why": why,
    }


def fts_available():
    try:
        con = sqlite3.connect(":memory:")
        con.execute("CREATE VIRTUAL TABLE _probe USING fts5(x)")
        con.close()
        return True
    except sqlite3.Error:
        return False


def fts_candidates(entries, query_tokens):
    """Return the set of entry ids FTS5 matches, or raise on failure.

    The FTS columns carry the SAME tokens the shared scorer uses, and the
    query is a prefix OR over the query tokens — so the candidate set equals
    the scorer's positive set (parity by construction)."""
    con = sqlite3.connect(":memory:")
    try:
        con.execute(
            "CREATE VIRTUAL TABLE skill USING fts5("
            "id UNINDEXED, name, id_tok, aliases, tags, capabilities, "
            "description, funnel)")
        rows = []
        for e in entries:
            f = field_tokens(e)
            rows.append((
                e["id"],
                " ".join(f["name"]),
                " ".join(f["id"]),
                " ".join(f["aliases"]),
                " ".join(f["tags"]),
                " ".join(f["capabilities"]),
                " ".join(f["description"]),
                " ".join(f["funnel"]),
            ))
        con.executemany(
            "INSERT INTO skill (id, name, id_tok, aliases, tags, "
            "capabilities, description, funnel) VALUES "
            "(?, ?, ?, ?, ?, ?, ?, ?)", rows)
        match = " OR ".join('"{}"*'.format(t) for t in query_tokens)
        cur = con.execute(
            "SELECT id FROM skill WHERE skill MATCH ?", (match,))
        return {row[0] for row in cur.fetchall()}
    finally:
        con.close()


class Router:
    def __init__(self, catalog_path, packs_dir, root):
        self.root = os.path.abspath(root)
        self.packs_dir = packs_dir
        with open(catalog_path, encoding="utf-8") as fh:
            self.catalog = json.load(fh)
        self.pack_name = self.catalog.get("pack")
        self.pack = self._load_pack(self.pack_name)
        self.lock = self._load_lock(catalog_path)
        self.visible, self.excluded = self._classify()

    def _load_pack(self, name):
        path = os.path.join(self.packs_dir, f"{name}.json")
        if not os.path.isfile(path):
            raise ValueError(f"unknown pack '{name}' (no {path})")
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    def _load_lock(self, catalog_path):
        lock_path = os.path.join(os.path.dirname(catalog_path), "locks",
                                 f"{self.pack_name}.lock.json")
        if not os.path.isfile(lock_path):
            return None
        with open(lock_path, encoding="utf-8") as fh:
            return json.load(fh)

    def _declared_funnels(self):
        return set(self.pack.get("funnels", {}).keys())

    def _lock_state(self):
        """(digest_ok, provenance_ids) — empty set when no lock is present."""
        if self.lock is None:
            return True, None
        canonical = json.dumps(
            self.catalog.get("entries", []), sort_keys=True,
            separators=(",", ":")).encode("utf-8")
        digest = "sha256:" + hashlib.sha256(canonical).hexdigest()
        digest_ok = digest == self.lock.get("catalog_digest")
        prov = {e.get("provenance") for e in self.lock.get("entries", [])}
        return digest_ok, prov

    def _classify(self):
        visible, excluded = [], []
        funnels = self._declared_funnels()
        digest_ok, prov_ids = self._lock_state()
        for entry in self.catalog.get("entries", []):
            eid = entry.get("id", "<no-id>")
            missing = [f for f in REQUIRED_ENTRY_FIELDS if not entry.get(f)]
            if missing:
                excluded.append((eid, "missing-field",
                                 "required provenance field(s): "
                                 + ", ".join(missing)))
                continue
            if entry.get("pack") != self.pack_name:
                excluded.append((eid, "unknown-pack",
                                 f"pack '{entry.get('pack')}' is not the "
                                 f"catalog pack '{self.pack_name}'"))
                continue
            if entry.get("funnel") not in funnels:
                excluded.append((eid, "unclassified",
                                 f"funnel '{entry.get('funnel')}' is not "
                                 f"declared by pack '{self.pack_name}'"))
                continue
            if not self._resolves(entry["read_path"]):
                excluded.append((eid, "stale",
                                 f"read_path does not resolve: "
                                 f"{entry['read_path']}"))
                continue
            if not digest_ok:
                excluded.append((eid, "lock-digest-mismatch",
                                 "catalog digest does not match the lock "
                                 "(tampered catalog)"))
                continue
            if prov_ids is not None and entry.get("provenance") not in prov_ids:
                excluded.append((eid, "unprovenanced",
                                 "provenance id is absent from the lock"))
                continue
            visible.append(entry)
        return visible, excluded

    def _resolves(self, read_path):
        if not read_path or os.path.isabs(read_path):
            return False
        full = os.path.abspath(os.path.join(self.root, read_path))
        if not full.startswith(self.root + os.sep):
            return False
        return os.path.isfile(full)

    def resolve(self, read_path):
        return os.path.join(self.root, read_path)

    def search(self, query, funnel, limit, engine):
        qtokens = query_tokens(query)
        used = "json"
        candidates = None
        if engine in ("auto", "fts") and qtokens:
            try:
                ids = fts_candidates(self.visible, qtokens)
                if len(ids) <= CANDIDATE_CAP:
                    candidates = ids
                    used = "fts"
                elif engine == "fts":
                    raise ValueError("candidate cap saturated")
            except (sqlite3.Error, ValueError) as exc:
                if engine == "fts":
                    raise ValueError(f"FTS unavailable/unsafe: {exc}")
                used = "json"
        pool = self.visible
        if candidates is not None:
            pool = [e for e in self.visible if e["id"] in candidates]
        ranked = rank(pool, query, funnel)
        cards = [make_card(s, w, e, len(qtokens))
                 for s, w, e in ranked[:limit]]
        return {"used": used, "cards": cards, "ranked_total": len(ranked)}


def build_arg_parser():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--catalog", default=DEFAULT_CATALOG)
    ap.add_argument("--packs-dir", default=DEFAULT_PACKS_DIR)
    sub = ap.add_subparsers(dest="cmd")

    s = sub.add_parser("search", help="search the catalog")
    s.add_argument("funnel", help="funnel name or 'all'")
    s.add_argument("query", help="search query")
    s.add_argument("--format", choices=("json", "text"), default="text")
    s.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    s.add_argument("--engine", choices=("auto", "fts", "json"), default="auto")
    s.add_argument("--open", action="store_true",
                   help="print the selected skill body (read-on-demand)")

    sub.add_parser("audit", help="list fail-closed (non-visible) entries")
    sub.add_parser("list-funnels", help="list declared funnels")
    return ap


def text_card(card):
    return (f"  {card['name']}  [{card['funnel']}]  conf={card['confidence']}\n"
            f"      id={card['id']}\n"
            f"      pack={card['pack']} license={card['license']} "
            f"prov={card['provenance']}\n"
            f"      why={','.join(card['why'])}\n"
            f"      read_path={card['read_path']}")


def main(argv=None):
    args = build_arg_parser().parse_args(argv)
    if not args.cmd:
        build_arg_parser().print_help()
        return 2

    try:
        router = Router(args.catalog, args.packs_dir, args.root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL — {exc}", file=sys.stderr)
        return 1

    if args.cmd == "list-funnels":
        for name, spec in router.pack.get("funnels", {}).items():
            print(f"{name}\t{spec.get('title', '')}\t{spec.get('purpose', '')}")
        return 0

    if args.cmd == "audit":
        print(f"catalog: {router.catalog.get('catalog_id')}  "
              f"visible={len(router.visible)} excluded={len(router.excluded)}")
        for eid, kind, reason in router.excluded:
            print(f"  ✗ [{kind}] {eid}: {reason}")
        if not router.excluded:
            print("  (no excluded entries)")
        return 0

    # search
    limit = max(1, min(args.limit, MAX_LIMIT))
    try:
        result = router.search(args.query, args.funnel, limit, args.engine)
    except ValueError as exc:
        print(f"FAIL — {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        payload = {
            "query": args.query,
            "funnel": args.funnel,
            "engine": result["used"],
            "limit": limit,
            "count": len(result["cards"]),
            "ranked_total": result["ranked_total"],
            "excluded": len(router.excluded),
            "results": result["cards"],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=True))
    else:
        print(f"search funnel={args.funnel} engine={result['used']} "
              f"limit={limit} matches={result['ranked_total']}")
        for card in result["cards"]:
            print(text_card(card))
        if not result["cards"]:
            print("  (no matches)")

    if args.open and result["cards"]:
        top = result["cards"][0]
        body = open(router.resolve(top["read_path"]), encoding="utf-8").read()
        print(f"\n--- open {top['id']} ({top['read_path']}) ---")
        print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
