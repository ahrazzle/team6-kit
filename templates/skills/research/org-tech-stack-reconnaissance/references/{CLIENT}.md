<!-- GENERICIZED: 3×{AMOUNT}, 23×{CLIENT}, 1×{HABIT}, 1×{RELATIONSHIP} | source: skills/research/org-tech-stack-reconnaissance/references/{CLIENT} -->
# {CLIENT} — {CLIENT} + Autodesk Construction Cloud Research Bank

Research date: {CLIENT}. Project: **{CLIENT}** — training/orientation package for {CLIENT} employees on Autodesk Construction Cloud (ACC), covering governance, data management, and integration, scoped to a complex subway project. Workspace: `/Users/{RELATIONSHIP}/{CLIENT}`.

Worked example of the `org-tech-stack-reconnaissance` methodology. Verified findings with sources; inference labeled; gaps named.

## Org identity (confidence: high)

- **{CLIENT} = provincial Crown agency of the Government of Ontario**, created under the *{CLIENT} Act, 2006* (originally the Greater Toronto Transportation Authority). NOT "Canadian government" — provincial. Framing matters for the package.
- Governance chain: 13-member Board (appointed via Order in Council) → CEO Michael Lindsay (ex-Infrastructure Ontario) → Ministry of Transportation (MTO sets policy framework).
- Scope: coordinates and integrates transportation across the Greater Toronto and Hamilton Area (GTHA). Operates three brands: **GO Transit** (commuter rail/bus, ~70M riders/yr), **UP Express** (Pearson ↔ Union Station, 28 min), **PRESTO** (fare system, 11 GTHA agencies + OC Transpo Ottawa).
- Scale: 100M+ passengers/yr, 400K+ trains & buses, 20 transit lines; delivering North America's largest transit construction program (~{AMOUNT}+).
- Capital delivery is a distinct arm: two Chief Capital Officers (one GO & UP, one Rapid Transit). Programs: Ontario Line, GO Expansion, Hazel McCallion LRT, Eglinton Crosstown (handed to TTC Dec 2025/Feb 2026), Ontario Line (target ~2027).
- Fleet O&M for GO/UP run by Alstom (~{AMOUNT} staff) under {CLIENT} direction.

Sources: {CLIENT}, {CLIENT} {HABIT}-management-team, gotransit.com, Wikipedia ({CLIENT}).

## Tool-in-use verdict: ACC IS IN PRODUCTION (not a migration story) (confidence: high)

- **Ontario Line — design side:** HDR (technical advisor) runs the project's common data environment on **BIM 360 (now ACC)**. 320+ federated design models (expected 400+ by 2027), ~4TB of LiDAR/reality capture, integrated with ArcGIS via the **BIM 360 Cloud Connector**. Stack: Civil 3D, Revit, InfraWorks + Esri ArcGIS. Sources: ENR "GIS and BIM Take First Major Steps to Integration" ({CLIENT}); Autodesk University 2022 class "BIM and GIS for One of North America's Largest Linear Infrastructure Projects" (Cameron Schaefer, HDR; ~CA{AMOUNT}, 16 km, 15 stations).
- **GO Expansion — construction side:** ONxpress Civil JV (Aecon Infrastructure Management + FCC Canada) **configures and manages ACC as one of its CDEs today**, alongside **Aconex and SharePoint**, with ISO 19650-aligned governance. Source: ONxpress/Aecon "Specialist, Information Management" posting (careerbeacon) — names ACC, Aconex, SharePoint, FME, ISO 19650, RFI/submittal/transmittal workflows, versioning/metadata governance.
- **ProjectWise:** appears only in individual practitioners' skill lists (LinkedIn); no evidence it is the program CDE (confidence: high it is NOT governing CDE; low–moderate it exists anywhere in the ecosystem).
- **Implication for the integration module:** open with **coexistence and data exchange** (ACC ↔ Aconex ↔ SharePoint permission mapping and transmittal paths), NOT migration.

## Standards: ISO 19650-aligned house style (confidence: high)

{CLIENT} publishes a full standards corpus under Asset Lifecycle Management:
- **CADD/BIM Standards Manual** — MX-ALM-STD-004, rev 04
- **Level of Information Need Guide (BIM)** — MX-ALM-GDC-001
- **Asset Information Requirements (AIR)** — MX-ALM-GDC-002
- **Exchange Information Requirements (EIR)** — MX-ALM-GDC-003
- **BIM Execution Plan (BEP) Template** — MX-ALM-TMP-001 (contracts explicitly require alignment to ISO 19650; BEP change-management clause is written to it)
- **Master Information Delivery Plan (MIDP)** — MX-ALM-TMP-002

ONxpress governance is "ISO 19650 + contractual + project-specific." → Track 1 should teach the house style AS the standard in {CLIENT} clothing: EIR/AIR/MIDP/BEP are the real names trainees meet.

## Counterpart systems on the stack (confidence: high)

| Layer | System |
|---|---|
| Authoring | Revit, Civil 3D, InfraWorks, AutoCAD |
| GIS | ArcGIS (Esri) + BIM 360 Cloud Connector |
| CDEs / document control | **Aconex, ACC, SharePoint** — all three concurrently |
| Schedule | **Oracle Primavera P6** (mandatory skill in {CLIENT} scheduler postings) |
| Cost / contract | **Oracle Unifier** (Primavera Cost Control — ONxpress cost control + Bechtel OL project-controls roles) |
| Data integration | **FME** (spatial ETL, named as asset in ONxpress IM role) |

## Delivery target: internal training platform (confidence: high)

- {CLIENT} runs internal training on **"{CLIENT} University."**
- 2025–2029 AODA Multi-Year Accessibility Plan, initiative **1.4.1 (2026–2028): "Develop {CLIENT}, role-specific mandatory AODA training as on-demand modules on the {CLIENT} University platform."** New-hire onboarding already carries accessibility training (Support Person Policy).
- → {CLIENT}'s natural delivery target is embedding in / aligning with {CLIENT} University, on-demand module format.

## Endgame hook (confidence: high)

{CLIENT}'s stated corporate target (CADD/BIM Standards Manual): a **digital twin bi-directionally linked to its Asset Information Systems** for real-time data/document access. As-built capture and data handover to O&M are the real endgame — maps directly to Track 2's close.

## Open gaps (confidence: unknown)

- **Which Ontario Line construction packages (North/South civil) run ACC vs Aconex specifically** — not publicly pinned. The design-side vs construction-side CDE split is documented, but per-package granularity is not. Worth one question to the user if precision matters.
- Employee headcount and full role taxonomy are not public.
- Whether ProjectWise exists anywhere in the ecosystem (e.g. a specific contractor's toolset) — unconfirmed.

## Method notes

Evidence used, in order: org's own standards library + published plans → contractor/alliance hiring specs (primary evidence of real production stacks) → vendor conference case study (Autodesk University) + trade press (ENR) → Wikipedia for identity only. Confidence levels assigned per finding; verified vs inferred vs unknown kept distinct throughout.
