<!-- GENERICIZED: 1×{AMOUNT}, 4×{CLIENT}, 1×{RELATIONSHIP} | source: skills/research/project-takeover-recon/SKILL.md -->
---
name: project-takeover-recon
description: Use when taking over incomplete project from another agent.
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
metadata:
  hermes:
    tags: [recon, handoff, takeover, verification, baseline]
    related_skills: [read-only-system-audit, web-build-verification, org-tech-stack-reconnaissance]
---

# Project Takeover Recon

When the user hands you a workspace of files from another agent ("was being worked on by X, not complete, take it across the finish line"), the first task is NOT to build. It is to reconstruct what exists, where it stopped, what "done" means per the handoff — then establish a verified baseline. Plan before touching anything.

## When to Use

- User points at a directory of prior working files and asks you to understand the project and plan completion.
- Another agent (Claude CoWork, a subagent, a prior session) left a handoff package, briefs, or an unfinished build.
- You inherit a codebase whose "current state" is asserted in docs but never verified by execution.

## Workflow

1. **Map the tree first.** search_files (target='files') excluding node_modules/dist/.git, or terminal `find` when you need mtimes. Identify versioned directory families (v1, v16, "webapp v10 - animations"). List mtimes — the newest write tells you where work stopped, which is not where the docs say it stopped.
2. **Read handoff docs BEFORE code.** Look for README.md, handoff/, *-BRIEF.md, STATE.md, DEPLOY.md. They are the highest-density context; code is the lowest. A good handoff names: the locked layer vs the open surface, the states that must exist, the correctness gates, and the "done when" criteria. Extract those four before anything else.
3. **Establish the stop point on disk.** No git repo? design/ dir empty? build/ stale relative to src? Empty handoff artifacts and un-run steps (git init, npm install of new deps) are fingerprints of where the previous agent actually stopped.
4. **Check portability.** grep for old absolute paths (a different home or Documents location). In CODE it is a real risk; in markdown it is cosmetic — say which.
5. **Run the documented gates BEFORE planning — never trust doc claims about data.** Handoff fixture tables ("state X never occurs", "worst case is N") drift from the actual generated data. Execute verify/validate/personas/build scripts and diff the output against the claims. Expect discrepancies; report each with confidence level.
6. **git init + .gitignore audit before any baseline commit.** If the plan deletes a prototype file and there is no repo, the tree is a one-way door. Audit .gitignore for junk it misses: stale build dirs, temp files (vite timestamp-*.mjs), .DS_Store.
7. **License audit when reusing the stack.** One pass over the dependency tree: MIT/Apache fine, GPL infects, CC BY-NC kills commercial use. Report the obligation, not just "open source".
8. **Report: what it is / where it stopped / what is green (by execution, with gate outputs) / what is unknown / the documented finish line.** Distinguish found vs inferred vs unverifiable. Hand to the director for routing — planning the build is not the recon agent's job.

## Pitfalls

- Documented or remembered workspace paths are stale by default — projects get renamed (nutrition-app → nutrak) and canonical trees move into `wrk/<id>/` while historical snapshots stay behind in `vers/`. Re-discover the tree on disk (search_files/find) before reporting state; a memory path is a hint, not a fact.
- A handoff table listing "states not in the fixture" is a CLAIM, not a fact. Re-run the persona/generator scripts: execution can reveal worse degenerate states than the docs' worst case (2.16M stranded SP vs documented {AMOUNT}) and states the docs call untriggered that a persona actually triggers.
- "Not under version control" is the highest-risk sentence in any handoff. The build brief's step 1 is often git init — verify it actually ran before anything gets deleted.
- Gate scripts exist for a reason: run them AT TAKEOVER, not just at the end. Green-at-takeover is the baseline that makes "you broke the model, not the test" meaningful later.
- Check node_modules presence in each package before assuming an install step — often already present.
- Documented known-drift ("25/27 match, 2 known drifts") is a feature: a third mismatch means breakage, zero means someone "fixed" a documented defect. Say this in the report so nobody "fixes" it later.
- A validate script may tolerate missing optional inputs (slice dirs) and still pass — verify whether the gate actually exercised what you think it did.

## Support files

- `references/{CLIENT}-{CLIENT}` — worked example: {CLIENT} {CLIENT} takeover; gate commands, results, doc-vs-execution discrepancies, infra facts.
