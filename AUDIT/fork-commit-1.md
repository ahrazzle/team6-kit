# Fork Commit 1 — Cleanliness Evidence

Generated: 2026-08-29T16:58:38

This tree was verified clean across multiple independent checks before
the first commit. Every later commit can diff against this as baseline.

## 1. Surface Matrix Scan (surface-scan.py)

```
============================================================
SURFACE MATRIX — leak scan (N surfaces, N detectors)
============================================================
S7-generic-service (WARN): 24 hit(s)
    templates/skills/creative/interactive-documents/SKILL.md: api.unsplash.com
    templates/skills/creative/interactive-documents/references/{CLIENT}-recipe-book.md: api.unsplash.com
    templates/skills/creative/interactive-html-publication/SKILL.md: api.unsplash.com
    templates/skills/creative/interactive-html-publication/references/{CLIENT}-build-notes.md: api.unsplash.com
    templates/skills/creative/user-design-aesthetic/SKILL.md: quran.com
    templates/skills/custom-domain-publishing/SKILL.md: .vercel.app
    templates/skills/custom-domain-publishing/SKILL.md: vercel.app
    templates/skills/deployment/github-pages-deployment/references/{CLIENT}-pages-deploy.md: .vercel.app
    templates/skills/deployment/github-pages-deployment/references/{CLIENT}-pages-deploy.md: vercel.app
    templates/skills/deployment/vercel-deployment/SKILL.md: .vercel.app
    templates/skills/deployment/vercel-deployment/SKILL.md: vercel.app
    templates/skills/deployment/vercel-deployment/references/{CLIENT}-subdomains.md: .vercel.app
S1-content: clean
S2-filenames: clean
S3-headers: clean
S4-script-paths: clean
S5-config-defaults: clean
S6-gitignore: clean
S7-reachability: clean
------------------------------------------------------------
WARN — 24 generic-service mention(s) (review, not blocking).
PASS — 0 instance leaks across all 7 surfaces.
```

## 2. Staged-tree manifest (what this commit contains)

**276 files.**

- `.gitignore`
- `LICENSE`
- `README.md`
- `build/build-manifest.py`
- `build/extraction-inventory.py`
- `build/fork-dryrun.sh`
- `build/generate.py`
- `build/genericize.py`
- `build/identifiers.yaml.example`
- `build/review-gate.py`
- `build/surface-scan.py`
- `build/sweep-gate.py`
- `choreography/funnel/SOP-SPINOFF.md`
- `choreography/funnel/viability-pass.md`
- `choreography/governance.md`
- `choreography/orchestration.md`
- `registry/kit.yaml`
- `registry/packs/README.md`
- `templates/personas/SOUL.md.tmpl`
- `templates/personas/profile.yaml.tmpl`
- `templates/skills/adversarial-review/SKILL.md`
- `templates/skills/adversarial-review/references/session-20260819-{CLIENT}.md`
- `templates/skills/adversarial-review/references/session-20260820-{CLIENT}-architecture.md`
- `templates/skills/adversarial-review/references/session-20260820-{CLIENT}-path-b.md`
- `templates/skills/adversarial-review/references/session-20260828-{CLIENT}-contract-verification.md`
- `templates/skills/adversarial-review/references/session-20260828-{CLIENT}-qa.md`
- `templates/skills/autonomous-ai-agents/agent-consciousness-architecture/SKILL.md`
- `templates/skills/autonomous-ai-agents/agent-pager/SKILL.md`
- `templates/skills/autonomous-ai-agents/agent-persistence-layers/SKILL.md`
- `templates/skills/autonomous-ai-agents/distributed-coordination/SKILL.md`
- `templates/skills/autonomous-ai-agents/distributed-coordination/references/{CLIENT}-debugging-2026-08-26.md`
- `templates/skills/autonomous-ai-agents/hermes-agent-contributing/SKILL.md`
- `templates/skills/autonomous-ai-agents/hermes-bot-mode-troubleshooting/SKILL.md`
- `templates/skills/autonomous-ai-agents/hermes-desktop-app-internals/SKILL.md`
- `templates/skills/autonomous-ai-agents/hermes-profile-fleet-operations/SKILL.md`
- `templates/skills/autonomous-ai-agents/hermes-profile-fleet-operations/references/session-db-forensics.md`
- `templates/skills/autonomous-ai-agents/hermes-profile-management/SKILL.md`
- `templates/skills/autonomous-ai-agents/hermes-session-model-migration/SKILL.md`
- `templates/skills/autonomous-ai-agents/hermes-session-model-migration/references/upstream-bug-notes.md`
- `templates/skills/autonomous-ai-agents/hermes-session-model-overrides/SKILL.md`
- `templates/skills/autonomous-ai-agents/hermes-session-model-overrides/references/state-db-recipe.md`
- `templates/skills/autonomous-ai-agents/multi-agent-consciousness/SKILL.md`
- `templates/skills/autonomous-ai-agents/multi-agent-coordination/SKILL.md`
- `templates/skills/autonomous-ai-agents/multi-agent-knowledge-coordination/SKILL.md`
- `templates/skills/autonomous-ai-agents/multi-agent-knowledge-systems/SKILL.md`
- `templates/skills/autonomous-ai-agents/multi-agent-model-tiering/SKILL.md`
- `templates/skills/autonomous-ai-agents/multi-agent-orchestration/SKILL.md`
- `templates/skills/autonomous-ai-agents/multi-agent-orchestration/references/{CLIENT}-case-study.md`
- `templates/skills/autonomous-ai-agents/multi-agent-orchestration/references/{CLIENT}-feedback-mechanics.md`
- `templates/skills/autonomous-ai-agents/multi-agent-orchestration/references/{CLIENT}-mvp-case-study.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/SKILL.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-18-{CLIENT}.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-19-the-search.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-19-{CLIENT}-kickoff.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-19-{CLIENT}-mvp.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-19-{CLIENT}.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-team-registry-formalization.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-{CLIENT}-phase-3.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-{CLIENT}-phase-4.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-{CLIENT}-phase-5.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-{CLIENT}-phase-6.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-{CLIENT}-phase-7.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-21-team6-operations.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-21-the-search.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-21-workflow-overhaul.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-21-{CLIENT}-phase-8.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-21-{CLIENT}.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-22-{CLIENT}-absorption.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-22-{CLIENT}-phase-10.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-22-{CLIENT}-phase-9.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-22-{CLIENT}-portfolio-overview.md`
- `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-27-knowledge-routing-and-entropy.md`
- `templates/skills/autonomous-ai-agents/project-drift-monitoring/references/{CLIENT}-case-study.md`
- `templates/skills/autonomous-ai-agents/project-handoff-takeover/SKILL.md`
- `templates/skills/autonomous-ai-agents/project-handoff-takeover/references/{CLIENT}-case.md`
- `templates/skills/autonomous-ai-agents/project-initializer/SKILL.md`
- `templates/skills/autonomous-ai-agents/skill-library-curation/SKILL.md`
- `templates/skills/client-deliverables/references/{CLIENT}-case-study.md`
- `templates/skills/collaborative-knowledge-systems/SKILL.md`
- `templates/skills/concurrent-agent-file-coordination/SKILL.md`
- `templates/skills/consciousness-architecture-design/SKILL.md`
- `templates/skills/coordination/model-config-skill/SKILL.md`
- `templates/skills/copywriting/website-copy/SKILL.md`
- `templates/skills/creative/agent-consciousness-design/SKILL.md`
- `templates/skills/creative/agent-consciousness-design/references/{CLIENT}-case-study.md`
- `templates/skills/creative/analytical-report-design/SKILL.md`
- `templates/skills/creative/book-creation/SKILL.md`
- `templates/skills/creative/client-brand-collateral/SKILL.md`
- `templates/skills/creative/consciousness-architecture/SKILL.md`
- `templates/skills/creative/consciousness-architecture/references/{CLIENT}-case-study.md`
- `templates/skills/creative/data-essay-design/SKILL.md`
- `templates/skills/creative/design-tone-domain/SKILL.md`
- `templates/skills/creative/excalidraw/SKILL.md`
- `templates/skills/creative/excalidraw/references/examples.md`
- `templates/skills/creative/game-ux-architecture/SKILL.md`
- `templates/skills/creative/game-ux-architecture/references/{CLIENT}-debugging-patterns.md`
- `templates/skills/creative/html-report-authoring/SKILL.md`
- `templates/skills/creative/html-report-design/SKILL.md`
- `templates/skills/creative/incomplete-data-interface-design/SKILL.md`
- `templates/skills/creative/interaction-contract-design/SKILL.md`
- `templates/skills/creative/interactive-data-simulation/SKILL.md`
- `templates/skills/creative/interactive-documents/SKILL.md`
- `templates/skills/creative/interactive-documents/references/{CLIENT}-recipe-book.md`
- `templates/skills/creative/interactive-educational-books/SKILL.md`
- `templates/skills/creative/interactive-html-publication/SKILL.md`
- `templates/skills/creative/interactive-html-publication/references/{CLIENT}-build-notes.md`
- `templates/skills/creative/interactive-simulation/SKILL.md`
- `templates/skills/creative/interactive-term-definitions/SKILL.md`
- `templates/skills/creative/interactive-term-definitions/references/{CLIENT}-implementation.md`
- `templates/skills/creative/interactive-training-design/SKILL.md`
- `templates/skills/creative/marketing-site-delivery/SKILL.md`
- `templates/skills/creative/marketing-site-delivery/references/session-findings.md`
- `templates/skills/creative/print-material-design/SKILL.md`
- `templates/skills/creative/source-agnostic-design/SKILL.md`
- `templates/skills/creative/user-design-aesthetic/SKILL.md`
- `templates/skills/creative/visual-report-design/SKILL.md`
- `templates/skills/creative/web-design-component-catalog/SKILL.md`
- `templates/skills/custom-domain-publishing/SKILL.md`
- `templates/skills/custom-domain-publishing/references/{CLIENT}-live-state.md`
- `templates/skills/deployment-verification-discipline/SKILL.md`
- `templates/skills/deployment-verification-discipline/references/{CLIENT}-deployment-incidents.md`
- `templates/skills/deployment/github-pages-deployment/SKILL.md`
- `templates/skills/deployment/github-pages-deployment/references/{CLIENT}-pages-deploy.md`
- `templates/skills/deployment/vercel-deployment/SKILL.md`
- `templates/skills/deployment/vercel-deployment/references/{CLIENT}-subdomains.md`
- `templates/skills/devops/agent-profile-extraction/SKILL.md`
- `templates/skills/devops/agent-profile-extraction/references/{CLIENT}-t001-session.md`
- `templates/skills/devops/logo-asset-pipeline/SKILL.md`
- `templates/skills/devops/staging-first-web-deployment/SKILL.md`
- `templates/skills/devops/staging-first-web-deployment/references/{CLIENT}-playbook.md`
- `templates/skills/educational-html-book/SKILL.md`
- `templates/skills/educational-html-book/references/{CLIENT}-lessons.md`
- `templates/skills/educational-html-book/references/{CLIENT}-project.md`
- `templates/skills/framework-plugin-development/SKILL.md`
- `templates/skills/game-feedback-animations/SKILL.md`
- `templates/skills/github/github-pr-audit/SKILL.md`
- `templates/skills/github/github-project-publication/SKILL.md`
- `templates/skills/github/open-source-project-packaging/SKILL.md`
- `templates/skills/github/open-source-project-packaging/references/{CLIENT}-packaging-pass.md`
- `templates/skills/hermes/custom-openai-endpoint-registration/SKILL.md`
- `templates/skills/hermes/hermes-profile-distribution/SKILL.md`
- `templates/skills/knowledge-base-ingestion/SKILL.md`
- `templates/skills/learning-design/training-module-design/SKILL.md`
- `templates/skills/long-run-deployment-discipline/SKILL.md`
- `templates/skills/macos-harness/SKILL.md`
- `templates/skills/marketing-site-production/SKILL.md`
- `templates/skills/mlops/evaluation/evaluating-llms-harness/SKILL.md`
- `templates/skills/model-config-skill/SKILL.md`
- `templates/skills/multi-agent-consciousness-architecture/SKILL.md`
- `templates/skills/multi-page-html-design/SKILL.md`
- `templates/skills/productivity/briefing/SKILL.md`
- `templates/skills/productivity/client-review-package/SKILL.md`
- `templates/skills/productivity/knowledge-base-consolidation/SKILL.md`
- `templates/skills/productivity/task-execution/SKILL.md`
- `templates/skills/productivity/training-package-design/SKILL.md`
- `templates/skills/productivity/training-package-design/references/{CLIENT}-acc-case-study.md`
- `templates/skills/productivity/user-preference-capture/SKILL.md`
- `templates/skills/research/agent-consciousness-architecture/SKILL.md`
- `templates/skills/research/agent-consciousness-architecture/references/tension-lifecycle-examples.md`
- `templates/skills/research/agent-consciousness-architecture/references/{CLIENT}-session-2026-08-19.md`
- `templates/skills/research/classical-arabic-text-research/SKILL.md`
- `templates/skills/research/document-analysis/SKILL.md`
- `templates/skills/research/knowledge-base-consolidation/SKILL.md`
- `templates/skills/research/knowledge-base-construction/SKILL.md`
- `templates/skills/research/knowledge-base-construction/references/{CLIENT}-session-2026-08.md`
- `templates/skills/research/knowledge-base-drift-monitoring/SKILL.md`
- `templates/skills/research/knowledge-base-management/SKILL.md`
- `templates/skills/research/model-validation/SKILL.md`
- `templates/skills/research/model-validation/references/{CLIENT}-simulator-case-study.md`
- `templates/skills/research/org-tech-stack-reconnaissance/SKILL.md`
- `templates/skills/research/org-tech-stack-reconnaissance/references/{CLIENT}.md`
- `templates/skills/research/oss-reuse-license-audit/SKILL.md`
- `templates/skills/research/primary-source-discovery/SKILL.md`
- `templates/skills/research/product-discovery/SKILL.md`
- `templates/skills/research/product-discovery/references/{CLIENT}-case-study.md`
- `templates/skills/research/project-takeover-recon/SKILL.md`
- `templates/skills/research/project-takeover-recon/references/{CLIENT}-takeover.md`
- `templates/skills/research/read-only-system-audit/SKILL.md`
- `templates/skills/research/source-evaluation/SKILL.md`
- `templates/skills/research/tool-adoption-audit/SKILL.md`
- `templates/skills/sales-enablement/SKILL.md`
- `templates/skills/software-development/agent-consciousness-architecture/SKILL.md`
- `templates/skills/software-development/agent-consciousness-architecture/references/session-journal.md`
- `templates/skills/software-development/agent-kit-distribution/SKILL.md`
- `templates/skills/software-development/agent-kit-distribution/references/{CLIENT}-fork-decision.md`
- `templates/skills/software-development/agent-kit-extraction/SKILL.md`
- `templates/skills/software-development/agent-kit-extraction/references/{CLIENT}-t001-case.md`
- `templates/skills/software-development/browser-game-demos/SKILL.md`
- `templates/skills/software-development/browser-game-development/SKILL.md`
- `templates/skills/software-development/browser-game-development/references/deployment-verification.md`
- `templates/skills/software-development/browser-game-development/references/{CLIENT}-lessons.md`
- `templates/skills/software-development/code-review-verification/SKILL.md`
- `templates/skills/software-development/deploy-artifact-verification/SKILL.md`
- `templates/skills/software-development/deploy-artifact-verification/references/{CLIENT}-gate-loop.md`
- `templates/skills/software-development/deploy-artifact-verification/references/{CLIENT}-github-pages.md`
- `templates/skills/software-development/deploy-gate-discipline/SKILL.md`
- `templates/skills/software-development/discord-bot-development/SKILL.md`
- `templates/skills/software-development/docker-postgres-setup/SKILL.md`
- `templates/skills/software-development/drift-monitoring/SKILL.md`
- `templates/skills/software-development/drift-monitoring/references/{CLIENT}-bundle-drift.md`
- `templates/skills/software-development/event-bus-architecture/SKILL.md`
- `templates/skills/software-development/event-bus-architecture/references/{CLIENT}-eventbus.md`
- `templates/skills/software-development/event-driven-web-ui-lifecycle/SKILL.md`
- `templates/skills/software-development/event-driven-web-ui-lifecycle/references/{CLIENT}-lifecycle-bugs.md`
- `templates/skills/software-development/event-driven-web-ui-lifecycle/references/{CLIENT}-mvp-polish-checklist.md`
- `templates/skills/software-development/external-tool-vetting/SKILL.md`
- `templates/skills/software-development/fastify-prisma-monorepo/SKILL.md`
- `templates/skills/software-development/framework-handoff-package/SKILL.md`
- `templates/skills/software-development/fullstack-monorepo-dev/SKILL.md`
- `templates/skills/software-development/fullstack-ts-monorepo/SKILL.md`
- `templates/skills/software-development/fullstack-ts-monorepo/references/{CLIENT}-stack.md`
- `templates/skills/software-development/git-remote-troubleshooting/SKILL.md`
- `templates/skills/software-development/hermes-desktop-plugin-storage/SKILL.md`
- `templates/skills/software-development/hermes-desktop-update-repair/SKILL.md`
- `templates/skills/software-development/inherited-project-takeover/SKILL.md`
- `templates/skills/software-development/inherited-project-takeover/references/{CLIENT}-handoff-api-audit.md`
- `templates/skills/software-development/integration-testing/SKILL.md`
- `templates/skills/software-development/integration-testing/references/{CLIENT}-integration-patterns.md`
- `templates/skills/software-development/interactive-web-game-development/SKILL.md`
- `templates/skills/software-development/knowledge-base-access/SKILL.md`
- `templates/skills/software-development/knowledge-base-consolidation/SKILL.md`
- `templates/skills/software-development/knowledge-base-ingestion/SKILL.md`
- `templates/skills/software-development/knowledge-drift-monitoring/SKILL.md`
- `templates/skills/software-development/licensed-asset-reuse/SKILL.md`
- `templates/skills/software-development/multi-agent-knowledge-base/SKILL.md`
- `templates/skills/software-development/nodejs-project-bringup/SKILL.md`
- `templates/skills/software-development/nodejs-project-bringup/references/{CLIENT}-bringup.md`
- `templates/skills/software-development/open-source-reuse-licensing/SKILL.md`
- `templates/skills/software-development/project-foundation-scaffold/SKILL.md`
- `templates/skills/software-development/python-venv-repair/SKILL.md`
- `templates/skills/software-development/quran-{CLIENT}-platform/SKILL.md`
- `templates/skills/software-development/quranic-arabic-data/SKILL.md`
- `templates/skills/software-development/rhythm-game-development/SKILL.md`
- `templates/skills/software-development/rhythm-game-development/references/{CLIENT}-session-details.md`
- `templates/skills/software-development/rhythm-typing-game-framework/SKILL.md`
- `templates/skills/software-development/rhythm-typing-game-framework/references/game-shipping-license-deployment.md`
- `templates/skills/software-development/rhythm-typing-game-framework/references/{CLIENT}-debug-session.md`
- `templates/skills/software-development/source-verification/SKILL.md`
- `templates/skills/software-development/static-brand-site-launch/SKILL.md`
- `templates/skills/software-development/static-brand-site-launch/references/{CLIENT}-gateway-terminal.md`
- `templates/skills/software-development/static-brand-site-launch/references/{CLIENT}site-case.md`
- `templates/skills/software-development/static-webapp-verification/SKILL.md`
- `templates/skills/software-development/static-webapp-verification/references/{CLIENT}-bug-log.md`
- `templates/skills/software-development/threejs-webgl-development/SKILL.md`
- `templates/skills/software-development/verify-deployed-artifacts/SKILL.md`
- `templates/skills/software-development/verify-deployed-artifacts/references/{CLIENT}-phase3-polish.md`
- `templates/skills/software-development/verify-deployed-artifacts/references/{CLIENT}-session-example.md`
- `templates/skills/software-development/web-app-deployment/SKILL.md`
- `templates/skills/software-development/web-app-deployment/references/{CLIENT}-deployment.md`
- `templates/skills/software-development/web-app-integration-debugging/SKILL.md`
- `templates/skills/software-development/web-build-fix-verification/SKILL.md`
- `templates/skills/software-development/web-build-verification/SKILL.md`
- `templates/skills/software-development/web-build-verification/references/{CLIENT}-contact-swap-round.md`
- `templates/skills/software-development/web-build-verification/references/{CLIENT}-env-swap-incident.md`
- `templates/skills/software-development/web-build-verification/references/{CLIENT}-font-and-button-rounds.md`
- `templates/skills/software-development/web-build-verification/references/{CLIENT}-gh-pages-case.md`
- `templates/skills/software-development/web-build-verification/references/{CLIENT}-terminal-interactive-rounds.md`
- `templates/skills/software-development/web-build-verification/references/{CLIENT}-v6-13-16-disputes-and-tone.md`
- `templates/skills/software-development/web-deployment-safety/SKILL.md`
- `templates/skills/software-development/web-deployment-safety/references/grid-layout-recovery.md`
- `templates/skills/software-development/web-deployment-safety/references/terminal-llm-assistant.md`
- `templates/skills/software-development/web-deployment-safety/references/vercel-cloudflare-staging.md`
- `templates/skills/software-development/{CLIENT}-absorption/SKILL.md`
- `templates/skills/software-development/{CLIENT}-maintenance/SKILL.md`
- `templates/skills/software-development/{CLIENT}-plugin-dev/SKILL.md`
- `templates/skills/software-development/{CLIENT}-plugin-development/SKILL.md`
- `templates/skills/software-development/{CLIENT}-plugin-development/references/audio-pipeline.md`
- `templates/skills/software-development/{CLIENT}-plugin-development/references/demo-ux-word-content.md`
- `templates/skills/software-development/{CLIENT}-plugin-development/references/handoff-api-truth.md`
- `templates/skills/static-site-production/SKILL.md`
- `templates/skills/static-site-production/references/bundle-deploy-case-study.md`
- `templates/skills/web-app-debugging/SKILL.md`
- `templates/skills/web-development/interactive-terminal-assistant/SKILL.md`
- `templates/skills/web-release-gates/SKILL.md`
- `templates/skills/web-release-gates/references/{CLIENT}-site-incident-log.md`
- `templates/skills/writing/argument-analysis/SKILL.md`

## 3. Invariant check (mid-word clobbers)

The post-substitution invariant (no `{PLACEHOLDER}` splitting an ordinary
lowercase word) was verified against this exact staged tree. Zero clobbers
outside the invariant's own docstring examples (which use neutral `w{CLIENT}rd`).

## 4. Residual evidence

- Live third-party integration name: 0 in staged tree (quarantined build moved to `OUTPUTS/`)
- Project-name filenames: 0 (the 4 'hits' were the word 'registry')
- `dist/`: empty — poisoned build at `OUTPUTS/open-core-QUARANTINED-20260829`
- Dry-run (fork-dryrun.sh): committed kits/ destroyed by update, gitignored survives

## Verification lineage

- Fixer-side evidence (all three residuals resolved)
- Independent re-check (integration=0, ventures=0 visible, 8 legit classes)
- Independent scan (dist empty, quarantine intact, staged tree = 7 surfaces)
- Gate-holder, executed on verified evidence
