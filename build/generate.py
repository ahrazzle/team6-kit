#!/usr/bin/env python3
"""
generate.py — The generator (build step 3). Manifest → instantiated kit.

THE ONLY ASSEMBLY PATH. A kit that cannot be built by this script from
templates/ + a parameter file does not exist.

Contract (spec section 4):
  - Declarative: reads the manifest; each TEMPLATE row maps to a template
    target with {PLACEHOLDER} substitutions. No hand-edited output.
  - One engine, two products: open core = engine + generic templates;
    vertical packs = parameter file fed through the SAME generator.
  - Cross-class seams emit provenance comments in the output.

USAGE
  python3 generate.py --out <kit-dir> [--params <parameter-file.yaml>]
    --params optional: vertical-pack parameter file (persona set, skill
            bundle, choreography). Without it, generates the generic open
            core (default persona archetypes).

Preconditions (enforced):
  sweep-gate.py  == 0   (source clean + fully classified)
  review-gate.py == 0   (semantic sign-off complete)

Placeholder scheme: every {PLACEHOLDER} in templates/ resolves from:
  1. the parameter file (vertical pack), or
  2. DEFAULT_PARAMS (open core), or
  3. a per-row override table below.
"""

import os
import re
import sys
import shutil
import subprocess

from genericize import sanitize_path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_SOURCE = os.path.expanduser("~/.hermes/profiles")
TEMPLATES = os.path.join(ROOT, "templates")
MANIFEST = os.path.join(HERE, "manifest.tsv")
MANIFEST_FROZEN = os.path.join(HERE, "manifest.frozen.tsv")
REVIEW_FROZEN = os.path.join(HERE, "REVIEW.frozen.md")

DEFAULT_PARAMS = {
    "TEAM_NAME": "Your Team",
    "DIRECTOR_NAME": "Director",
    "AGENT_NAME": "{ROLE_NAME}",
    "PROFILE_NAME": "{AGENT_NAME}",
    "MODEL_PROVIDER": "nous",
    "MODEL_NAME": "nous/deepseek/deepseek-v4-flash-0731",
    "BASE_URL": "",
}

# Source relpath → template target (mirrors templates/MANIFEST.md)
def target_path(rel):
    base = os.path.basename(rel)
    if base == "profile.yaml":
        return os.path.join("personas", "profile.yaml.tmpl")
    if base in ("SOUL.md", "AGENTS.md", "USER.md", "HERMES.md"):
        return os.path.join("personas", f"{base}.tmpl")
    if rel.startswith("skills/"):
        # Apply the SAME path sanitization genericize.py uses, so the template
        # is found at its sanitized location (instance tokens stripped from
        # filenames/dirs before they can ship in the committed tree).
        return os.path.join("skills", sanitize_path(rel[len("skills/"):]))
    return rel


def load_manifest():
    """Live-fleet manifest if present, else the committed frozen one — a fresh
    clone has no fleet, so instantiation falls back to the frozen shipped
    surface (self-contained)."""
    path = MANIFEST if os.path.isfile(MANIFEST) else MANIFEST_FROZEN
    rows = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("relpath"):
                continue
            parts = line.split("\t")
            if len(parts) < 5:
                continue
            rows[parts[0]] = (parts[1], parts[4])
    return rows


def parse_review():
    """REVIEW.md -> {relpath: (ticked, total)} across all profile copies.
    Used as the pass-gate for KEEP-REVIEW rows: only fully-signed rows ship.
    Falls back to the frozen committed review on a fresh clone."""
    signed = {}
    path = REVIEW_FROZEN if not os.path.isfile(os.path.join(HERE, "REVIEW.md")) \
        else os.path.join(HERE, "REVIEW.md")
    cur = None
    ticked = total = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            m = re.match(r"^### ([^ ]+?)/(.+?)(?:\s+\*\(.*\)\*)?$", line)
            if m:
                if cur is not None:
                    signed[cur] = (ticked, total)
                body = re.sub(r"\s+\*\(.*\)\*$", "", line[4:])
                _, cur = body.split("/", 1)
                ticked = total = 0
                continue
            cm = re.match(r"^- \[( |x)\] \d+\.", line)
            if cm and cur is not None:
                total += 1
                if cm.group(1) == "x":
                    ticked += 1
    if cur is not None:
        signed[cur] = (ticked, total)
    return signed


def find_source(rel):
    """Locate the first on-disk copy of a source relpath across the live
    profiles (used to copy signed KEEP-REVIEW content into keep-review/)."""
    for prof in sorted(os.listdir(DEFAULT_SOURCE)):
        if prof.startswith("."):
            continue
        full = os.path.join(DEFAULT_SOURCE, prof, rel)
        if os.path.isfile(full):
            return full
    return None


def dest_path(out, rel):
    """THE ONLY destination-path constructor in the generator.

    Every path the generator writes — template, skill, OR keep-review —
    passes through sanitize_path() here, by construction. No output surface
    can carry a raw instance-token name, because there is no other way to
    compute a destination. Same discipline as the S8 network-egress rule:
    the generator cannot write a raw path, the way the agent cannot reach
    the network. (sanitize_path is idempotent on already-sanitized paths —
    placeholders like {CLIENT} contain no instance tokens — so routing an
    already-sanitized template path through it again is safe.)"""
    return os.path.join(out, sanitize_path(rel))


def load_pack_schema(params_path):
    """Read the vertical pack's declared placeholder contract from its
    kit.yaml (placeholders: [A, B]). Returns set or None if absent."""
    if not params_path:
        return None
    # The pack's kit.yaml sits next to the parameter file.
    d = os.path.dirname(os.path.abspath(params_path))
    kit = os.path.join(d, "kit.yaml")
    if not os.path.isfile(kit):
        return None
    try:
        with open(kit, encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return None
    m = re.search(r"placeholders\s*:\s*\[([^\]]*)\]", text, re.I)
    if not m:
        return None
    return {p.strip() for p in m.group(1).split(",") if p.strip()}


def validate_schema(declared, resolved, unresolved, strict):
    """Asymmetric declared-schema check (T-001 team contract):
      - declared ∖ resolved = FAIL (pack promised a placeholder, didn't
        deliver — the typo case). Always fails, regardless of strict.
      - resolved ∖ declared = WARN (extra tokens like {BK} are legit code
        literals or template drift — review, don't fail).
      - unresolved (tokens with no param at all) — WARN in open-core mode
        (generic state), FAIL under --strict (paid tier can't ship mangled).
    Returns (fail_list, warn_list)."""
    fails, warns = [], []
    if declared is not None:
        missing_declared = declared - resolved
        if missing_declared:
            fails.append(
                f"DECLARED PLACEHOLDER(S) NOT RESOLVED: {sorted(missing_declared)} "
                f"— pack promised them; check the parameter file for typos")
        extra = resolved - declared
        if extra:
            warns.append(
                f"RESOLVED-BUT-UNDECLARED TOKENS: {sorted(extra)} — "
                f"template drift or code literals; review")
    if unresolved:
        msg = f"UNRESOLVED PLACEHOLDERS: {sorted(unresolved)}"
        if strict:
            fails.append(msg + " — strict mode: paid kit cannot ship mangled")
        else:
            warns.append(msg + " — open core ships generic by design")
    return fails, warns


def load_params(path):
    """Minimal YAML-subset reader: key: value lines. Full YAML not required
    for parameter files (flat keys)."""
    params = dict(DEFAULT_PARAMS)
    if path and os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or ":" not in line:
                    continue
                k, v = line.split(":", 1)
                params[k.strip()] = v.strip().strip("'\"")
    return params


def instantiate(template_rel, params):
    """Read a template file, substitute {PLACEHOLDER}s."""
    src = os.path.join(TEMPLATES, template_rel)
    if not os.path.isfile(src):
        return None, None
    with open(src, encoding="utf-8") as fh:
        text = fh.read()
    missing = sorted(set(re.findall(r"\{([A-Z_0-9]+)\}", text)) - set(params))
    for k, v in params.items():
        text = text.replace("{" + k + "}", v)
    return text, missing


def main():
    args = sys.argv[1:]
    out = None
    params_path = None
    strict = "--strict" in args
    if "--out" in args:
        out = args[args.index("--out") + 1]
    if "--params" in args:
        params_path = args[args.index("--params") + 1]
    if not out:
        out = os.path.join(ROOT, "dist", "open-core")
    out = os.path.abspath(out)

    # Preconditions — the gates run first. Nothing assembles on failure.
    # Gate mode is decided by artifact presence, not by params: if the live
    # fleet manifest is absent (fresh clone), sweep-gate runs --frozen against
    # the committed artifacts so instantiation is self-contained. If the live
    # manifest exists, the live path runs (with review-gate's staleness check
    # protecting buyer-side builds).
    use_frozen = not os.path.isfile(MANIFEST)
    sweep_cmd = [sys.executable, os.path.join(HERE, "sweep-gate.py"),
                 "--kit-scope"] + (["--frozen"] if use_frozen else [])
    review_cmd = [sys.executable, os.path.join(HERE, "review-gate.py")]
    if params_path and os.path.isfile(params_path):
        review_cmd += ["--params", params_path]
    for cmd in (sweep_cmd, review_cmd):
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(r.stdout)
        if r.returncode != 0:
            print(f"✗ {os.path.basename(cmd[1])} FAILED — assembly blocked.")
            return 1
        print(f"✓ {os.path.basename(cmd[1])} passed")

    params = load_params(params_path)
    manifest = load_manifest()
    declared = load_pack_schema(params_path)

    # Cross-class seam provenance lines (spec section 4)
    SEAM_REASON = {
        ("SHIPPABLE", "DROP"): "instance-bound content dropped despite shippable class",
        ("REDACTABLE", "TEMPLATE"): "redactable config surface templated at instantiation",
    }

    # Wipe and rebuild the output dir
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)

    provenance = []
    shipped = 0
    skipped_unsigned = 0
    resolved_union = set()   # every placeholder actually resolved across rows
    unresolved_union = set() # every placeholder left unresolved
    schema_fails, schema_warns = [], []
    # Signed REVIEW entries (4/4) — the pass-gate for KEEP-REVIEW rows.
    review = parse_review()
    for rel, (cls, verdict) in manifest.items():
        if verdict == "DROP":
            continue
        if verdict not in ("TEMPLATE", "KEEP-REVIEW"):
            continue
        tpl = target_path(rel)
        if verdict == "TEMPLATE":
            text, missing = instantiate(tpl, params)
            if text is None:
                provenance.append(f"# SKIP: {rel} — no template at {tpl}")
                continue
            if missing:
                unresolved_union.update(missing)
                provenance.append(
                    f"# WARN: {rel} — unresolved placeholders: {missing}")
            dst = dest_path(out, tpl)
        else:  # KEEP-REVIEW — ship as-is ONLY if the semantic pass signed it.
            signed = review.get(rel, (0, 0))
            if signed[0] < signed[1]:
                # Not fully signed — neither copy nor count (the pass-gate
                # rule: an unverified claim in provenance is the leak class
                # the sweep surface exists to catch).
                skipped_unsigned += 1
                provenance.append(
                    f"# KEEP-REVIEW SKIPPED (unsigned): {rel} — "
                    f"no ship, no count")
                continue
            src = find_source(rel)
            if src is None:
                provenance.append(
                    f"# KEEP-REVIEW SKIPPED (no source): {rel}")
                continue
            text = open(src, encoding="utf-8", errors="replace").read()
            # Sanitize the dest path EXACTLY like the template path — instance
            # tokens live in source filenames (client-asset-audit.md) and the
            # raw rel would ship them in the committed tree. The semantic pass
            # signs content; the path needs the same treatment.
            dst = dest_path(out, os.path.join("keep-review", rel))
            provenance.append(
                f"# KEEP-REVIEW: {rel} — ships as-is (signed {signed[0]}/{signed[1]})")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if text is not None:
            with open(dst, "w", encoding="utf-8") as fh:
                fh.write(text)
        shipped += 1
        seam = SEAM_REASON.get((cls, verdict))
        if seam:
            with open(dst, "a", encoding="utf-8") as fh:
                fh.write(f"\n# Provenance: {cls}→{verdict} — {seam}\n")

    # ---- Declared-schema contract check (team, asymmetric) ----
    # resolved = params keys used in at least one template
    resolved_union = set()
    for rel, (cls, verdict) in manifest.items():
        if verdict != "TEMPLATE":
            continue
        tpl = target_path(rel)
        src = os.path.join(TEMPLATES, tpl)
        if not os.path.isfile(src):
            continue
        with open(src, encoding="utf-8") as fh:
            resolved_union.update(re.findall(r"\{([A-Z_0-9]+)\}", fh.read()))
    resolved_union &= set(params)
    schema_fails, schema_warns = validate_schema(
        declared, resolved_union, unresolved_union, strict)
    for w in schema_warns:
        print(f"  ⚠ {w}")
    if schema_fails:
        print("FAIL — declared-schema contract violated:")
        for f in schema_fails:
            print(f"  ✗ {f}")
        print("remediation: fix the parameter file / pack kit.yaml, then re-run.")
        return 1

    # Write the audit trail
    with open(os.path.join(out, "AUDIT.md"), "w", encoding="utf-8") as fh:
        fh.write("# Kit Assembly Audit\n\n")
        fh.write(f"- source manifest: {MANIFEST}\n")
        fh.write(f"- parameter file: {params_path or '(open core defaults)'}\n")
        fh.write(f"- rows shipped: {shipped} (files actually written)\n")
        fh.write(f"- KEEP-REVIEW skipped (unsigned): {skipped_unsigned}\n")
        fh.write(f"- generated by: build/generate.py (the only assembly path)\n\n")
        fh.write("## Provenance notes\n\n")
        fh.write("\n".join(provenance) + "\n")

    print(f"\n✓ Kit assembled at {out}")
    print(f"  shipped rows: {shipped} (files actually written; "
          f"{skipped_unsigned} unsigned KEEP-REVIEW skipped)")
    print(f"  audit trail : {os.path.join(out, 'AUDIT.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
