# templates/ MANIFEST — row → template mapping + provenance

Generated from `manifest.tsv` (locked). One row per UNIQUE source path.

- **TEMPLATE rows: 261** — become generic templates with {PLACEHOLDER} substitution
- **KEEP-REVIEW rows: 173** — ship as-is after semantic sign-off (not in templates/)
- **DROP rows: 122** — never ship; provenance only (filtered by build/)
- **Cross-class seams: 4** — carry explicit one-line reasons below

## TEMPLATE rows (source → template target)

| source path | class | #profiles | hits | → template target |
|---|---|---|---|---|
| `SOUL.md` | SHIPPABLE | 8 | 338 | `templates/personas/SOUL.md.tmpl` |
| `skills/model-config-skill/SKILL.md` | SHIPPABLE | 5 | 225 | `templates/skills/model-config-skill/SKILL.md` |
| `profile.yaml` | REDACTABLE | 6 | 69 | `templates/personas/profile.yaml.tmpl` |
| `skills/software-development/{CLIENT}-absorption/SKILL.md` | SHIPPABLE | 1 | 68 | `templates/skills/software-development/{CLIENT}-absorption/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-19-{CLIENT}.md` | SHIPPABLE | 1 | 62 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-19-{CLIENT}.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-{CLIENT}-phase-3.md` | SHIPPABLE | 1 | 48 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-{CLIENT}-phase-3.md` |
| `skills/coordination/model-config-skill/SKILL.md` | SHIPPABLE | 1 | 45 | `templates/skills/coordination/model-config-skill/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/SKILL.md` | SHIPPABLE | 1 | 44 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/SKILL.md` |
| `skills/custom-domain-publishing/references/{CLIENT}-live-state.md` | SHIPPABLE | 1 | 44 | `templates/skills/custom-domain-publishing/references/{CLIENT}-live-state.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-22-{CLIENT}-phase-10.md` | SHIPPABLE | 1 | 38 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-22-{CLIENT}-phase-10.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-22-{CLIENT}-phase-9.md` | SHIPPABLE | 1 | 34 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-22-{CLIENT}-phase-9.md` |
| `skills/software-development/quran-{CLIENT}-platform/SKILL.md` | SHIPPABLE | 1 | 34 | `templates/skills/software-development/quran-{CLIENT}-platform/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-{CLIENT}-phase-4.md` | SHIPPABLE | 1 | 33 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-{CLIENT}-phase-4.md` |
| `skills/deployment/vercel-deployment/references/{CLIENT}-subdomains.md` | SHIPPABLE | 1 | 32 | `templates/skills/deployment/vercel-deployment/references/{CLIENT}-subdomains.md` |
| `skills/software-development/fullstack-ts-monorepo/references/{CLIENT}-stack.md` | SHIPPABLE | 3 | 30 | `templates/skills/software-development/fullstack-ts-monorepo/references/{CLIENT}-stack.md` |
| `skills/software-development/quran-{CLIENT}-platform/references/{CLIENT}-sources-api.md` | SHIPPABLE | 1 | 30 | `templates/skills/software-development/quran-{CLIENT}-platform/references/{CLIENT}-sources-api.md` |
| `skills/autonomous-ai-agents/multi-agent-coordination/SKILL.md` | SHIPPABLE | 1 | 28 | `templates/skills/autonomous-ai-agents/multi-agent-coordination/SKILL.md` |
| `skills/software-development/{CLIENT}-maintenance/SKILL.md` | SHIPPABLE | 1 | 28 | `templates/skills/software-development/{CLIENT}-maintenance/SKILL.md` |
| `skills/autonomous-ai-agents/hermes-profile-management/SKILL.md` | SHIPPABLE | 1 | 26 | `templates/skills/autonomous-ai-agents/hermes-profile-management/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-orchestration/references/{CLIENT}-case-study.md` | SHIPPABLE | 1 | 26 | `templates/skills/autonomous-ai-agents/multi-agent-orchestration/references/{CLIENT}-case-study.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-team-registry-formalization.md` | SHIPPABLE | 1 | 26 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-team-registry-formalization.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-21-team6-operations.md` | SHIPPABLE | 1 | 26 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-21-team6-operations.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-{CLIENT}-phase-7.md` | SHIPPABLE | 1 | 25 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-{CLIENT}-phase-7.md` |
| `skills/deployment/github-pages-deployment/references/{CLIENT}-pages-deploy.md` | SHIPPABLE | 1 | 25 | `templates/skills/deployment/github-pages-deployment/references/{CLIENT}-pages-deploy.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-{CLIENT}-phase-5.md` | SHIPPABLE | 1 | 24 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-{CLIENT}-phase-5.md` |
| `skills/macos-harness/SKILL.md` | SHIPPABLE | 8 | 24 | `templates/skills/macos-harness/SKILL.md` |
| `skills/software-development/web-build-verification/references/{CLIENT}-terminal-interactive-rounds.md` | SHIPPABLE | 1 | 24 | `templates/skills/software-development/web-build-verification/references/{CLIENT}-terminal-interactive-rounds.md` |
| `skills/autonomous-ai-agents/hermes-session-model-migration/SKILL.md` | SHIPPABLE | 1 | 23 | `templates/skills/autonomous-ai-agents/hermes-session-model-migration/SKILL.md` |
| `skills/software-development/quranic-arabic-data/references/{CLIENT}-sources.md` | SHIPPABLE | 1 | 23 | `templates/skills/software-development/quranic-arabic-data/references/{CLIENT}-sources.md` |
| `skills/static-site-production/SKILL.md` | SHIPPABLE | 1 | 23 | `templates/skills/static-site-production/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-21-workflow-overhaul.md` | SHIPPABLE | 1 | 22 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-21-workflow-overhaul.md` |
| `skills/software-development/deploy-artifact-verification/references/{CLIENT}-github-pages.md` | SHIPPABLE | 1 | 22 | `templates/skills/software-development/deploy-artifact-verification/references/{CLIENT}-github-pages.md` |
| `skills/autonomous-ai-agents/hermes-session-model-overrides/references/state-db-recipe.md` | SHIPPABLE | 1 | 21 | `templates/skills/autonomous-ai-agents/hermes-session-model-overrides/references/state-db-recipe.md` |
| `skills/research/org-tech-stack-reconnaissance/references/{CLIENT}.md` | SHIPPABLE | 1 | 21 | `templates/skills/research/org-tech-stack-reconnaissance/references/{CLIENT}.md` |
| `skills/software-development/agent-consciousness-architecture/references/session-journal.md` | SHIPPABLE | 1 | 21 | `templates/skills/software-development/agent-consciousness-architecture/references/session-journal.md` |
| `skills/software-development/quranic-arabic-data/SKILL.md` | SHIPPABLE | 1 | 21 | `templates/skills/software-development/quranic-arabic-data/SKILL.md` |
| `skills/software-development/web-build-verification/SKILL.md` | SHIPPABLE | 1 | 21 | `templates/skills/software-development/web-build-verification/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-19-the-search.md` | SHIPPABLE | 1 | 20 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-19-the-search.md` |
| `skills/research/agent-consciousness-architecture/references/{CLIENT}-session-2026-08-19.md` | SHIPPABLE | 1 | 20 | `templates/skills/research/agent-consciousness-architecture/references/{CLIENT}-session-2026-08-19.md` |
| `skills/research/model-validation/references/fomc-simulator-case-study.md` | SHIPPABLE | 1 | 20 | `templates/skills/research/model-validation/references/fomc-simulator-case-study.md` |
| `skills/software-development/web-build-verification/references/{CLIENT}-v6-13-16-disputes-and-tone.md` | SHIPPABLE | 1 | 20 | `templates/skills/software-development/web-build-verification/references/{CLIENT}-v6-13-16-disputes-and-tone.md` |
| `skills/autonomous-ai-agents/multi-agent-orchestration/SKILL.md` | SHIPPABLE | 1 | 19 | `templates/skills/autonomous-ai-agents/multi-agent-orchestration/SKILL.md` |
| `skills/research/agent-consciousness-architecture/references/tension-lifecycle-examples.md` | SHIPPABLE | 1 | 18 | `templates/skills/research/agent-consciousness-architecture/references/tension-lifecycle-examples.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-{CLIENT}-phase-6.md` | SHIPPABLE | 1 | 17 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-20-{CLIENT}-phase-6.md` |
| `skills/software-development/drift-monitoring/SKILL.md` | SHIPPABLE | 1 | 17 | `templates/skills/software-development/drift-monitoring/SKILL.md` |
| `skills/autonomous-ai-agents/project-handoff-takeover/references/3f-metamap-case.md` | SHIPPABLE | 1 | 16 | `templates/skills/autonomous-ai-agents/project-handoff-takeover/references/3f-metamap-case.md` |
| `skills/consciousness-architecture-design/SKILL.md` | SHIPPABLE | 1 | 16 | `templates/skills/consciousness-architecture-design/SKILL.md` |
| `skills/creative/excalidraw/references/examples.md` | SHIPPABLE | 8 | 16 | `templates/skills/creative/excalidraw/references/examples.md` |
| `skills/devops/agent-profile-extraction/references/{CLIENT}-t001-session.md` | SHIPPABLE | 1 | 16 | `templates/skills/devops/agent-profile-extraction/references/{CLIENT}-t001-session.md` |
| `skills/mlops/evaluation/evaluating-llms-harness/SKILL.md` | SHIPPABLE | 8 | 16 | `templates/skills/mlops/evaluation/evaluating-llms-harness/SKILL.md` |
| `skills/software-development/knowledge-drift-monitoring/SKILL.md` | SHIPPABLE | 1 | 16 | `templates/skills/software-development/knowledge-drift-monitoring/SKILL.md` |
| `skills/adversarial-review/references/session-20260820-metabot-path-b.md` | SHIPPABLE | 1 | 15 | `templates/skills/adversarial-review/references/session-20260820-metabot-path-b.md` |
| `skills/autonomous-ai-agents/agent-pager/SKILL.md` | SHIPPABLE | 3 | 15 | `templates/skills/autonomous-ai-agents/agent-pager/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-orchestration/references/{CLIENT}-mvp-case-study.md` | SHIPPABLE | 1 | 15 | `templates/skills/autonomous-ai-agents/multi-agent-orchestration/references/{CLIENT}-mvp-case-study.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-19-{CLIENT}-mvp.md` | SHIPPABLE | 1 | 15 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-19-{CLIENT}-mvp.md` |
| `skills/hermes/custom-openai-endpoint-registration/SKILL.md` | SHIPPABLE | 1 | 15 | `templates/skills/hermes/custom-openai-endpoint-registration/SKILL.md` |
| `skills/software-development/agent-consciousness-architecture/SKILL.md` | SHIPPABLE | 1 | 15 | `templates/skills/software-development/agent-consciousness-architecture/SKILL.md` |
| `skills/software-development/fullstack-monorepo-dev/SKILL.md` | SHIPPABLE | 3 | 15 | `templates/skills/software-development/fullstack-monorepo-dev/SKILL.md` |
| `skills/software-development/{CLIENT}-plugin-development/SKILL.md` | SHIPPABLE | 1 | 15 | `templates/skills/software-development/{CLIENT}-plugin-development/SKILL.md` |
| `skills/software-development/web-app-deployment/references/{CLIENT}-deployment.md` | SHIPPABLE | 1 | 15 | `templates/skills/software-development/web-app-deployment/references/{CLIENT}-deployment.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-22-{CLIENT}-portfolio-overview.md` | SHIPPABLE | 1 | 14 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-22-{CLIENT}-portfolio-overview.md` |
| `skills/creative/book-creation/SKILL.md` | SHIPPABLE | 1 | 14 | `templates/skills/creative/book-creation/SKILL.md` |
| `skills/software-development/{CLIENT}-plugin-dev/SKILL.md` | SHIPPABLE | 1 | 14 | `templates/skills/software-development/{CLIENT}-plugin-dev/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-consciousness/SKILL.md` | SHIPPABLE | 1 | 13 | `templates/skills/autonomous-ai-agents/multi-agent-consciousness/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-22-xplor-absorption.md` | SHIPPABLE | 1 | 13 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-22-xplor-absorption.md` |
| `skills/creative/consciousness-architecture/references/{CLIENT}-case-study.md` | SHIPPABLE | 1 | 13 | `templates/skills/creative/consciousness-architecture/references/{CLIENT}-case-study.md` |
| `skills/multi-agent-consciousness-architecture/SKILL.md` | SHIPPABLE | 1 | 13 | `templates/skills/multi-agent-consciousness-architecture/SKILL.md` |
| `skills/productivity/training-package-design/references/{CLIENT}-acc-case-study.md` | SHIPPABLE | 1 | 13 | `templates/skills/productivity/training-package-design/references/{CLIENT}-acc-case-study.md` |
| `skills/software-development/browser-game-development/SKILL.md` | SHIPPABLE | 1 | 13 | `templates/skills/software-development/browser-game-development/SKILL.md` |
| `skills/software-development/fullstack-ts-monorepo/SKILL.md` | SHIPPABLE | 3 | 12 | `templates/skills/software-development/fullstack-ts-monorepo/SKILL.md` |
| `skills/software-development/verify-deployed-artifacts/references/{CLIENT}-session-example.md` | SHIPPABLE | 1 | 12 | `templates/skills/software-development/verify-deployed-artifacts/references/{CLIENT}-session-example.md` |
| `skills/software-development/web-build-verification/references/{CLIENT}-env-swap-incident.md` | SHIPPABLE | 1 | 12 | `templates/skills/software-development/web-build-verification/references/{CLIENT}-env-swap-incident.md` |
| `skills/software-development/web-build-verification/references/{CLIENT}-gh-pages-case.md` | SHIPPABLE | 1 | 12 | `templates/skills/software-development/web-build-verification/references/{CLIENT}-gh-pages-case.md` |
| `skills/adversarial-review/references/session-20260820-{CLIENT}-architecture.md` | SHIPPABLE | 1 | 11 | `templates/skills/adversarial-review/references/session-20260820-{CLIENT}-architecture.md` |
| `skills/autonomous-ai-agents/hermes-session-model-migration/references/upstream-bug-notes.md` | SHIPPABLE | 1 | 11 | `templates/skills/autonomous-ai-agents/hermes-session-model-migration/references/upstream-bug-notes.md` |
| `skills/deployment/vercel-deployment/SKILL.md` | SHIPPABLE | 1 | 11 | `templates/skills/deployment/vercel-deployment/SKILL.md` |
| `skills/educational-html-book/references/{CLIENT}-project.md` | SHIPPABLE | 1 | 11 | `templates/skills/educational-html-book/references/{CLIENT}-project.md` |
| `skills/github/open-source-project-packaging/references/{CLIENT}-packaging-pass.md` | SHIPPABLE | 1 | 11 | `templates/skills/github/open-source-project-packaging/references/{CLIENT}-packaging-pass.md` |
| `skills/research/product-discovery/references/{CLIENT}-case-study.md` | SHIPPABLE | 1 | 11 | `templates/skills/research/product-discovery/references/{CLIENT}-case-study.md` |
| `skills/software-development/rhythm-typing-game-framework/SKILL.md` | SHIPPABLE | 1 | 11 | `templates/skills/software-development/rhythm-typing-game-framework/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-21-{CLIENT}.md` | SHIPPABLE | 1 | 10 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-21-{CLIENT}.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-27-knowledge-routing-and-entropy.md` | SHIPPABLE | 1 | 10 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-27-knowledge-routing-and-entropy.md` |
| `skills/deployment/github-pages-deployment/SKILL.md` | SHIPPABLE | 1 | 10 | `templates/skills/deployment/github-pages-deployment/SKILL.md` |
| `skills/devops/staging-first-web-deployment/references/{CLIENT}-playbook.md` | SHIPPABLE | 1 | 10 | `templates/skills/devops/staging-first-web-deployment/references/{CLIENT}-playbook.md` |
| `skills/software-development/browser-game-development/references/{CLIENT}-lessons.md` | SHIPPABLE | 1 | 10 | `templates/skills/software-development/browser-game-development/references/{CLIENT}-lessons.md` |
| `skills/software-development/static-brand-site-launch/references/{CLIENT}-gateway-terminal.md` | SHIPPABLE | 1 | 10 | `templates/skills/software-development/static-brand-site-launch/references/{CLIENT}-gateway-terminal.md` |
| `skills/adversarial-review/references/session-20260819-subtractive-fragility.md` | SHIPPABLE | 1 | 9 | `templates/skills/adversarial-review/references/session-20260819-subtractive-fragility.md` |
| `skills/autonomous-ai-agents/hermes-profile-fleet-operations/SKILL.md` | SHIPPABLE | 1 | 9 | `templates/skills/autonomous-ai-agents/hermes-profile-fleet-operations/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-18-command-centre.md` | SHIPPABLE | 1 | 9 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-18-command-centre.md` |
| `skills/hermes/hermes-profile-distribution/SKILL.md` | SHIPPABLE | 1 | 9 | `templates/skills/hermes/hermes-profile-distribution/SKILL.md` |
| `skills/productivity/user-preference-capture/SKILL.md` | SHIPPABLE | 1 | 9 | `templates/skills/productivity/user-preference-capture/SKILL.md` |
| `skills/research/agent-consciousness-architecture/SKILL.md` | SHIPPABLE | 1 | 9 | `templates/skills/research/agent-consciousness-architecture/SKILL.md` |
| `skills/software-development/deploy-artifact-verification/references/{CLIENT}-gate-loop.md` | SHIPPABLE | 1 | 9 | `templates/skills/software-development/deploy-artifact-verification/references/{CLIENT}-gate-loop.md` |
| `skills/software-development/nodejs-project-bringup/references/metamap-3f-bringup.md` | SHIPPABLE | 1 | 9 | `templates/skills/software-development/nodejs-project-bringup/references/metamap-3f-bringup.md` |
| `skills/software-development/source-verification/SKILL.md` | SHIPPABLE | 1 | 9 | `templates/skills/software-development/source-verification/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-19-xplor-kickoff.md` | SHIPPABLE | 1 | 8 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-19-xplor-kickoff.md` |
| `skills/creative/excalidraw/SKILL.md` | SHIPPABLE | 8 | 8 | `templates/skills/creative/excalidraw/SKILL.md` |
| `skills/deployment-verification-discipline/references/{CLIENT}-deployment-incidents.md` | SHIPPABLE | 1 | 8 | `templates/skills/deployment-verification-discipline/references/{CLIENT}-deployment-incidents.md` |
| `skills/software-development/web-build-verification/references/{CLIENT}-contact-swap-round.md` | SHIPPABLE | 1 | 8 | `templates/skills/software-development/web-build-verification/references/{CLIENT}-contact-swap-round.md` |
| `skills/concurrent-agent-file-coordination/SKILL.md` | SHIPPABLE | 1 | 7 | `templates/skills/concurrent-agent-file-coordination/SKILL.md` |
| `skills/creative/marketing-site-delivery/SKILL.md` | SHIPPABLE | 1 | 7 | `templates/skills/creative/marketing-site-delivery/SKILL.md` |
| `skills/research/knowledge-base-drift-monitoring/SKILL.md` | SHIPPABLE | 1 | 7 | `templates/skills/research/knowledge-base-drift-monitoring/SKILL.md` |
| `skills/research/project-takeover-recon/references/3f-metamap-takeover.md` | SHIPPABLE | 1 | 7 | `templates/skills/research/project-takeover-recon/references/3f-metamap-takeover.md` |
| `skills/software-development/rhythm-game-development/SKILL.md` | SHIPPABLE | 1 | 7 | `templates/skills/software-development/rhythm-game-development/SKILL.md` |
| `skills/software-development/static-brand-site-launch/references/{CLIENT}site-case.md` | SHIPPABLE | 1 | 7 | `templates/skills/software-development/static-brand-site-launch/references/{CLIENT}site-case.md` |
| `skills/creative/consciousness-architecture/SKILL.md` | SHIPPABLE | 1 | 6 | `templates/skills/creative/consciousness-architecture/SKILL.md` |
| `skills/creative/marketing-site-delivery/references/session-findings.md` | SHIPPABLE | 1 | 6 | `templates/skills/creative/marketing-site-delivery/references/session-findings.md` |
| `skills/creative/web-design-component-catalog/SKILL.md` | SHIPPABLE | 1 | 6 | `templates/skills/creative/web-design-component-catalog/SKILL.md` |
| `skills/research/org-tech-stack-reconnaissance/SKILL.md` | SHIPPABLE | 1 | 6 | `templates/skills/research/org-tech-stack-reconnaissance/SKILL.md` |
| `skills/software-development/agent-kit-extraction/references/{CLIENT}-t001-case.md` | SHIPPABLE | 1 | 6 | `templates/skills/software-development/agent-kit-extraction/references/{CLIENT}-t001-case.md` |
| `skills/software-development/framework-handoff-package/SKILL.md` | SHIPPABLE | 1 | 6 | `templates/skills/software-development/framework-handoff-package/SKILL.md` |
| `skills/software-development/knowledge-base-ingestion/SKILL.md` | SHIPPABLE | 1 | 6 | `templates/skills/software-development/knowledge-base-ingestion/SKILL.md` |
| `skills/software-development/rhythm-typing-game-framework/references/{CLIENT}-debug-session.md` | SHIPPABLE | 1 | 6 | `templates/skills/software-development/rhythm-typing-game-framework/references/{CLIENT}-debug-session.md` |
| `skills/software-development/static-brand-site-launch/SKILL.md` | SHIPPABLE | 1 | 6 | `templates/skills/software-development/static-brand-site-launch/SKILL.md` |
| `skills/software-development/web-build-verification/references/{CLIENT}-font-and-button-rounds.md` | SHIPPABLE | 1 | 6 | `templates/skills/software-development/web-build-verification/references/{CLIENT}-font-and-button-rounds.md` |
| `skills/software-development/web-deployment-safety/references/terminal-llm-assistant.md` | SHIPPABLE | 1 | 6 | `templates/skills/software-development/web-deployment-safety/references/terminal-llm-assistant.md` |
| `skills/github/open-source-project-packaging/SKILL.md` | SHIPPABLE | 1 | 5 | `templates/skills/github/open-source-project-packaging/SKILL.md` |
| `skills/software-development/agent-kit-extraction/SKILL.md` | SHIPPABLE | 1 | 5 | `templates/skills/software-development/agent-kit-extraction/SKILL.md` |
| `skills/software-development/event-driven-web-ui-lifecycle/SKILL.md` | SHIPPABLE | 1 | 5 | `templates/skills/software-development/event-driven-web-ui-lifecycle/SKILL.md` |
| `skills/software-development/external-tool-vetting/SKILL.md` | SHIPPABLE | 1 | 5 | `templates/skills/software-development/external-tool-vetting/SKILL.md` |
| `skills/software-development/integration-testing/SKILL.md` | SHIPPABLE | 1 | 5 | `templates/skills/software-development/integration-testing/SKILL.md` |
| `skills/software-development/web-deployment-safety/references/vercel-cloudflare-staging.md` | SHIPPABLE | 1 | 5 | `templates/skills/software-development/web-deployment-safety/references/vercel-cloudflare-staging.md` |
| `skills/adversarial-review/SKILL.md` | SHIPPABLE | 1 | 4 | `templates/skills/adversarial-review/SKILL.md` |
| `skills/autonomous-ai-agents/distributed-coordination/SKILL.md` | SHIPPABLE | 1 | 4 | `templates/skills/autonomous-ai-agents/distributed-coordination/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-knowledge-systems/SKILL.md` | SHIPPABLE | 1 | 4 | `templates/skills/autonomous-ai-agents/multi-agent-knowledge-systems/SKILL.md` |
| `skills/creative/agent-consciousness-design/references/{CLIENT}-case-study.md` | SHIPPABLE | 1 | 4 | `templates/skills/creative/agent-consciousness-design/references/{CLIENT}-case-study.md` |
| `skills/creative/interactive-html-publication/references/{CLIENT}-build-notes.md` | SHIPPABLE | 1 | 4 | `templates/skills/creative/interactive-html-publication/references/{CLIENT}-build-notes.md` |
| `skills/creative/interactive-training-design/SKILL.md` | SHIPPABLE | 1 | 4 | `templates/skills/creative/interactive-training-design/SKILL.md` |
| `skills/creative/source-agnostic-design/SKILL.md` | SHIPPABLE | 1 | 4 | `templates/skills/creative/source-agnostic-design/SKILL.md` |
| `skills/devops/agent-profile-extraction/SKILL.md` | SHIPPABLE | 1 | 4 | `templates/skills/devops/agent-profile-extraction/SKILL.md` |
| `skills/productivity/briefing/SKILL.md` | SHIPPABLE | 2 | 4 | `templates/skills/productivity/briefing/SKILL.md` |
| `skills/productivity/training-package-design/SKILL.md` | SHIPPABLE | 1 | 4 | `templates/skills/productivity/training-package-design/SKILL.md` |
| `skills/research/knowledge-base-management/SKILL.md` | SHIPPABLE | 1 | 4 | `templates/skills/research/knowledge-base-management/SKILL.md` |
| `skills/research/oss-reuse-license-audit/SKILL.md` | SHIPPABLE | 1 | 4 | `templates/skills/research/oss-reuse-license-audit/SKILL.md` |
| `skills/sales-enablement/SKILL.md` | SHIPPABLE | 1 | 4 | `templates/skills/sales-enablement/SKILL.md` |
| `skills/software-development/browser-game-development/references/deployment-verification.md` | SHIPPABLE | 1 | 4 | `templates/skills/software-development/browser-game-development/references/deployment-verification.md` |
| `skills/software-development/deploy-artifact-verification/SKILL.md` | SHIPPABLE | 1 | 4 | `templates/skills/software-development/deploy-artifact-verification/SKILL.md` |
| `skills/software-development/rhythm-game-development/references/{CLIENT}-session-details.md` | SHIPPABLE | 1 | 4 | `templates/skills/software-development/rhythm-game-development/references/{CLIENT}-session-details.md` |
| `skills/autonomous-ai-agents/hermes-agent-contributing/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/autonomous-ai-agents/hermes-agent-contributing/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-knowledge-coordination/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/autonomous-ai-agents/multi-agent-knowledge-coordination/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-21-{CLIENT}-phase-8.md` | SHIPPABLE | 1 | 3 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-21-{CLIENT}-phase-8.md` |
| `skills/autonomous-ai-agents/project-drift-monitoring/references/{CLIENT}-case-study.md` | SHIPPABLE | 1 | 3 | `templates/skills/autonomous-ai-agents/project-drift-monitoring/references/{CLIENT}-case-study.md` |
| `skills/autonomous-ai-agents/project-handoff-takeover/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/autonomous-ai-agents/project-handoff-takeover/SKILL.md` |
| `skills/creative/interactive-documents/references/{CLIENT}-recipe-book.md` | SHIPPABLE | 1 | 3 | `templates/skills/creative/interactive-documents/references/{CLIENT}-recipe-book.md` |
| `skills/deployment-verification-discipline/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/deployment-verification-discipline/SKILL.md` |
| `skills/devops/staging-first-web-deployment/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/devops/staging-first-web-deployment/SKILL.md` |
| `skills/framework-plugin-development/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/framework-plugin-development/SKILL.md` |
| `skills/github/github-project-publication/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/github/github-project-publication/SKILL.md` |
| `skills/marketing-site-production/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/marketing-site-production/SKILL.md` |
| `skills/productivity/client-review-package/SKILL.md` | SHIPPABLE | 3 | 3 | `templates/skills/productivity/client-review-package/SKILL.md` |
| `skills/research/knowledge-base-consolidation/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/research/knowledge-base-consolidation/SKILL.md` |
| `skills/research/product-discovery/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/research/product-discovery/SKILL.md` |
| `skills/research/project-takeover-recon/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/research/project-takeover-recon/SKILL.md` |
| `skills/software-development/deploy-gate-discipline/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/software-development/deploy-gate-discipline/SKILL.md` |
| `skills/software-development/event-bus-architecture/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/software-development/event-bus-architecture/SKILL.md` |
| `skills/software-development/inherited-project-takeover/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/software-development/inherited-project-takeover/SKILL.md` |
| `skills/software-development/inherited-project-takeover/references/{CLIENT}-handoff-api-audit.md` | SHIPPABLE | 1 | 3 | `templates/skills/software-development/inherited-project-takeover/references/{CLIENT}-handoff-api-audit.md` |
| `skills/software-development/open-source-reuse-licensing/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/software-development/open-source-reuse-licensing/SKILL.md` |
| `skills/software-development/project-foundation-scaffold/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/software-development/project-foundation-scaffold/SKILL.md` |
| `skills/software-development/{CLIENT}-plugin-development/references/demo-ux-word-content.md` | SHIPPABLE | 1 | 3 | `templates/skills/software-development/{CLIENT}-plugin-development/references/demo-ux-word-content.md` |
| `skills/software-development/verify-deployed-artifacts/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/software-development/verify-deployed-artifacts/SKILL.md` |
| `skills/software-development/web-app-integration-debugging/SKILL.md` | SHIPPABLE | 1 | 3 | `templates/skills/software-development/web-app-integration-debugging/SKILL.md` |
| `skills/adversarial-review/references/session-20260828-typemon-contract-verification.md` | SHIPPABLE | 1 | 2 | `templates/skills/adversarial-review/references/session-20260828-typemon-contract-verification.md` |
| `skills/autonomous-ai-agents/agent-consciousness-architecture/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/autonomous-ai-agents/agent-consciousness-architecture/SKILL.md` |
| `skills/autonomous-ai-agents/agent-persistence-layers/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/autonomous-ai-agents/agent-persistence-layers/SKILL.md` |
| `skills/autonomous-ai-agents/hermes-bot-mode-troubleshooting/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/autonomous-ai-agents/hermes-bot-mode-troubleshooting/SKILL.md` |
| `skills/autonomous-ai-agents/hermes-desktop-app-internals/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/autonomous-ai-agents/hermes-desktop-app-internals/SKILL.md` |
| `skills/autonomous-ai-agents/hermes-session-model-overrides/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/autonomous-ai-agents/hermes-session-model-overrides/SKILL.md` |
| `skills/autonomous-ai-agents/multi-agent-orchestration/references/{CLIENT}-feedback-mechanics.md` | SHIPPABLE | 1 | 2 | `templates/skills/autonomous-ai-agents/multi-agent-orchestration/references/{CLIENT}-feedback-mechanics.md` |
| `skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-21-the-search.md` | SHIPPABLE | 1 | 2 | `templates/skills/autonomous-ai-agents/multi-agent-team-orchestration/references/session-2026-08-21-the-search.md` |
| `skills/creative/analytical-report-design/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/creative/analytical-report-design/SKILL.md` |
| `skills/creative/game-ux-architecture/references/{CLIENT}-debugging-patterns.md` | SHIPPABLE | 1 | 2 | `templates/skills/creative/game-ux-architecture/references/{CLIENT}-debugging-patterns.md` |
| `skills/creative/interactive-documents/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/creative/interactive-documents/SKILL.md` |
| `skills/creative/interactive-educational-books/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/creative/interactive-educational-books/SKILL.md` |
| `skills/creative/interactive-term-definitions/references/{CLIENT}-implementation.md` | SHIPPABLE | 1 | 2 | `templates/skills/creative/interactive-term-definitions/references/{CLIENT}-implementation.md` |
| `skills/creative/user-design-aesthetic/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/creative/user-design-aesthetic/SKILL.md` |
| `skills/creative/visual-report-design/SKILL.md` | SHIPPABLE | 2 | 2 | `templates/skills/creative/visual-report-design/SKILL.md` |
| `skills/custom-domain-publishing/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/custom-domain-publishing/SKILL.md` |
| `skills/deployment-verification-discipline/references/curiokids-visual-regression.md` | SHIPPABLE | 1 | 2 | `templates/skills/deployment-verification-discipline/references/curiokids-visual-regression.md` |
| `skills/game-feedback-animations/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/game-feedback-animations/SKILL.md` |
| `skills/long-run-deployment-discipline/SKILL.md` | SHIPPABLE | 2 | 2 | `templates/skills/long-run-deployment-discipline/SKILL.md` |
| `skills/productivity/knowledge-base-consolidation/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/productivity/knowledge-base-consolidation/SKILL.md` |
| `skills/research/classical-arabic-text-research/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/research/classical-arabic-text-research/SKILL.md` |
| `skills/research/knowledge-base-construction/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/research/knowledge-base-construction/SKILL.md` |
| `skills/research/knowledge-base-construction/references/arif-session-2026-08.md` | SHIPPABLE | 1 | 2 | `templates/skills/research/knowledge-base-construction/references/arif-session-2026-08.md` |
| `skills/research/read-only-system-audit/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/research/read-only-system-audit/SKILL.md` |
| `skills/research/source-evaluation/references/egis-au2024-provenance-example.md` | SHIPPABLE | 1 | 2 | `templates/skills/research/source-evaluation/references/egis-au2024-provenance-example.md` |
| `skills/research/tool-adoption-audit/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/research/tool-adoption-audit/SKILL.md` |
| `skills/software-development/browser-game-demos/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/software-development/browser-game-demos/SKILL.md` |
| `skills/software-development/discord-bot-development/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/software-development/discord-bot-development/SKILL.md` |
| `skills/software-development/event-bus-architecture/references/{CLIENT}-eventbus.md` | SHIPPABLE | 1 | 2 | `templates/skills/software-development/event-bus-architecture/references/{CLIENT}-eventbus.md` |
| `skills/software-development/event-driven-web-ui-lifecycle/references/{CLIENT}-lifecycle-bugs.md` | SHIPPABLE | 1 | 2 | `templates/skills/software-development/event-driven-web-ui-lifecycle/references/{CLIENT}-lifecycle-bugs.md` |
| `skills/software-development/event-driven-web-ui-lifecycle/references/{CLIENT}-mvp-polish-checklist.md` | SHIPPABLE | 1 | 2 | `templates/skills/software-development/event-driven-web-ui-lifecycle/references/{CLIENT}-mvp-polish-checklist.md` |
| `skills/software-development/fastify-prisma-monorepo/SKILL.md` | SHIPPABLE | 2 | 2 | `templates/skills/software-development/fastify-prisma-monorepo/SKILL.md` |
| `skills/software-development/integration-testing/references/{CLIENT}-integration-patterns.md` | SHIPPABLE | 1 | 2 | `templates/skills/software-development/integration-testing/references/{CLIENT}-integration-patterns.md` |
| `skills/software-development/knowledge-base-access/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/software-development/knowledge-base-access/SKILL.md` |
| `skills/software-development/nodejs-project-bringup/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/software-development/nodejs-project-bringup/SKILL.md` |
| `skills/software-development/static-webapp-verification/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/software-development/static-webapp-verification/SKILL.md` |
| `skills/software-development/threejs-webgl-development/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/software-development/threejs-webgl-development/SKILL.md` |
| `skills/software-development/{CLIENT}-plugin-development/references/audio-pipeline.md` | SHIPPABLE | 1 | 2 | `templates/skills/software-development/{CLIENT}-plugin-development/references/audio-pipeline.md` |
| `skills/software-development/verify-deployed-artifacts/references/{CLIENT}-phase3-polish.md` | SHIPPABLE | 1 | 2 | `templates/skills/software-development/verify-deployed-artifacts/references/{CLIENT}-phase3-polish.md` |
| `skills/software-development/web-app-deployment/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/software-development/web-app-deployment/SKILL.md` |
| `skills/software-development/web-deployment-safety/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/software-development/web-deployment-safety/SKILL.md` |
| `skills/static-site-production/references/bundle-deploy-case-study.md` | SHIPPABLE | 1 | 2 | `templates/skills/static-site-production/references/bundle-deploy-case-study.md` |
| `skills/web-app-debugging/SKILL.md` | SHIPPABLE | 1 | 2 | `templates/skills/web-app-debugging/SKILL.md` |
| `skills/web-release-gates/references/{CLIENT}-site-incident-log.md` | SHIPPABLE | 1 | 2 | `templates/skills/web-release-gates/references/{CLIENT}-site-incident-log.md` |
| `skills/adversarial-review/references/session-20260828-sprite-qa.md` | SHIPPABLE | 1 | 1 | `templates/skills/adversarial-review/references/session-20260828-sprite-qa.md` |
| `skills/autonomous-ai-agents/distributed-coordination/references/{CLIENT}-debugging-2026-08-26.md` | SHIPPABLE | 1 | 1 | `templates/skills/autonomous-ai-agents/distributed-coordination/references/{CLIENT}-debugging-2026-08-26.md` |
| `skills/autonomous-ai-agents/hermes-profile-fleet-operations/references/session-db-forensics.md` | SHIPPABLE | 1 | 1 | `templates/skills/autonomous-ai-agents/hermes-profile-fleet-operations/references/session-db-forensics.md` |
| `skills/autonomous-ai-agents/multi-agent-model-tiering/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/autonomous-ai-agents/multi-agent-model-tiering/SKILL.md` |
| `skills/autonomous-ai-agents/project-initializer/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/autonomous-ai-agents/project-initializer/SKILL.md` |
| `skills/autonomous-ai-agents/skill-library-curation/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/autonomous-ai-agents/skill-library-curation/SKILL.md` |
| `skills/client-deliverables/references/{CLIENT}-case-study.md` | SHIPPABLE | 1 | 1 | `templates/skills/client-deliverables/references/{CLIENT}-case-study.md` |
| `skills/collaborative-knowledge-systems/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/collaborative-knowledge-systems/SKILL.md` |
| `skills/copywriting/website-copy/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/copywriting/website-copy/SKILL.md` |
| `skills/creative/agent-consciousness-design/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/creative/agent-consciousness-design/SKILL.md` |
| `skills/creative/client-brand-collateral/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/creative/client-brand-collateral/SKILL.md` |
| `skills/creative/data-essay-design/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/creative/data-essay-design/SKILL.md` |
| `skills/creative/design-tone-domain/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/creative/design-tone-domain/SKILL.md` |
| `skills/creative/game-ux-architecture/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/creative/game-ux-architecture/SKILL.md` |
| `skills/creative/html-report-authoring/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/creative/html-report-authoring/SKILL.md` |
| `skills/creative/html-report-design/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/creative/html-report-design/SKILL.md` |
| `skills/creative/incomplete-data-interface-design/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/creative/incomplete-data-interface-design/SKILL.md` |
| `skills/creative/interaction-contract-design/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/creative/interaction-contract-design/SKILL.md` |
| `skills/creative/interactive-data-simulation/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/creative/interactive-data-simulation/SKILL.md` |
| `skills/creative/interactive-html-publication/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/creative/interactive-html-publication/SKILL.md` |
| `skills/creative/interactive-simulation/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/creative/interactive-simulation/SKILL.md` |
| `skills/creative/interactive-term-definitions/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/creative/interactive-term-definitions/SKILL.md` |
| `skills/creative/print-material-design/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/creative/print-material-design/SKILL.md` |
| `skills/devops/logo-asset-pipeline/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/devops/logo-asset-pipeline/SKILL.md` |
| `skills/educational-html-book/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/educational-html-book/SKILL.md` |
| `skills/educational-html-book/references/{CLIENT}-lessons.md` | SHIPPABLE | 1 | 1 | `templates/skills/educational-html-book/references/{CLIENT}-lessons.md` |
| `skills/github/github-pr-audit/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/github/github-pr-audit/SKILL.md` |
| `skills/knowledge-base-ingestion/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/knowledge-base-ingestion/SKILL.md` |
| `skills/learning-design/training-module-design/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/learning-design/training-module-design/SKILL.md` |
| `skills/multi-page-html-design/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/multi-page-html-design/SKILL.md` |
| `skills/productivity/task-execution/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/productivity/task-execution/SKILL.md` |
| `skills/productivity/training-package-design/references/egis-hsr-acc-case-study.md` | SHIPPABLE | 1 | 1 | `templates/skills/productivity/training-package-design/references/egis-hsr-acc-case-study.md` |
| `skills/research/document-analysis/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/research/document-analysis/SKILL.md` |
| `skills/research/model-validation/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/research/model-validation/SKILL.md` |
| `skills/research/primary-source-discovery/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/research/primary-source-discovery/SKILL.md` |
| `skills/research/source-evaluation/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/research/source-evaluation/SKILL.md` |
| `skills/software-development/code-review-verification/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/code-review-verification/SKILL.md` |
| `skills/software-development/docker-postgres-setup/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/docker-postgres-setup/SKILL.md` |
| `skills/software-development/drift-monitoring/references/{CLIENT}-bundle-drift.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/drift-monitoring/references/{CLIENT}-bundle-drift.md` |
| `skills/software-development/git-remote-troubleshooting/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/git-remote-troubleshooting/SKILL.md` |
| `skills/software-development/hermes-desktop-plugin-storage/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/hermes-desktop-plugin-storage/SKILL.md` |
| `skills/software-development/hermes-desktop-update-repair/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/hermes-desktop-update-repair/SKILL.md` |
| `skills/software-development/interactive-web-game-development/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/interactive-web-game-development/SKILL.md` |
| `skills/software-development/knowledge-base-consolidation/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/knowledge-base-consolidation/SKILL.md` |
| `skills/software-development/licensed-asset-reuse/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/licensed-asset-reuse/SKILL.md` |
| `skills/software-development/multi-agent-knowledge-base/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/multi-agent-knowledge-base/SKILL.md` |
| `skills/software-development/python-venv-repair/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/python-venv-repair/SKILL.md` |
| `skills/software-development/rhythm-typing-game-framework/references/game-shipping-license-deployment.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/rhythm-typing-game-framework/references/game-shipping-license-deployment.md` |
| `skills/software-development/static-webapp-verification/references/{CLIENT}-bug-log.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/static-webapp-verification/references/{CLIENT}-bug-log.md` |
| `skills/software-development/{CLIENT}-plugin-development/references/handoff-api-truth.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/{CLIENT}-plugin-development/references/handoff-api-truth.md` |
| `skills/software-development/web-build-fix-verification/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/web-build-fix-verification/SKILL.md` |
| `skills/software-development/web-deployment-safety/references/grid-layout-recovery.md` | SHIPPABLE | 1 | 1 | `templates/skills/software-development/web-deployment-safety/references/grid-layout-recovery.md` |
| `skills/web-development/interactive-terminal-assistant/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/web-development/interactive-terminal-assistant/SKILL.md` |
| `skills/web-release-gates/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/web-release-gates/SKILL.md` |
| `skills/writing/argument-analysis/SKILL.md` | SHIPPABLE | 1 | 1 | `templates/skills/writing/argument-analysis/SKILL.md` |

## Cross-class seams (provenance)

| source path | class→verdict | reason |
|---|---|---|
| `profile.yaml` | REDACTABLE→TEMPLATE | redactable config surface templated at instantiation — profile.yaml |
| `skills/.hub/index-cache/browse_sh_catalog.json` | SHIPPABLE→DROP | shippable content dropped anyway — instance-bound, no generic form |
| `skills/.hub/index-cache/hermes-index.json` | SHIPPABLE→DROP | shippable content dropped anyway — instance-bound, no generic form |
| `skills/.usage.json` | SHIPPABLE→DROP | shippable content dropped anyway — instance-bound, no generic form |

## KEEP-REVIEW rows (semantic gate — not in templates/)

173 rows ship only after REVIEW.md sign-off (4/4). See `build/REVIEW.md`.

## DROP rows (never ship)

122 rows are filtered by `build/` before assembly. Provenance kept in `manifest.tsv`.
