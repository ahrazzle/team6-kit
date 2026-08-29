<!-- GENERICIZED: 4×{CLIENT}, 1×{RELATIONSHIP} | source: skills/research/document-analysis/SKILL.md -->
---
name: document-analysis
description: "Use when asked to analyze or review a report or document."
version: 1.0.0
author: {RELATIONSHIP}
license: MIT
platforms: [linux, macos, windows]
tags: [analysis, report, research, document, summary]
related_skills: [grounded-citations, blocked-page-recovery]
---

# Document Analysis

Structured workflow for analyzing documents, reports, papers, and linked content. Produces a three-phase deliverable: quick summary, thorough analysis, and written report.

## When to Use

- User provides a URL or file and asks to "analyze," "go through," "summarize and analyze," or "review" a document
- User wants both a quick overview and deep implications
- User explicitly asks for a report on findings and conclusions

## Workflow

### Phase {CLIENT}: Fetch

- Extract content from the provided URL or local file
- If direct fetch fails (404, paywall, block), try to find the correct URL via web search before escalating to blocked-page-recovery techniques
- For government/organizational sites: try alternate extensions (.htm vs .pdf), add/remove www, switch http→https
- Preserve source provenance (URL, date, archive snapshot if applicable)

### Phase {CLIENT}: Quick Summary

- Lead with a one-paragraph executive summary
- Include a quick-reference table of key metrics, decisions, or facts
- Keep this section scannable — the user wants the gist fast, not the full analysis

### Phase {CLIENT}: Thorough Analysis

- Break analysis into thematic sections based on the document's content
- For each theme: what happened/stated, what it means, what the risks are
- Include cross-theme interactions and second-order effects
- Assess scenarios with rough probability estimates where appropriate
- Note dissenting views, minority positions, or minority reports if present
- Explicitly address "implications" — what this means for stakeholders, markets, policy, etc.

### Phase {CLIENT}: Written Report

- Synthesize findings into a structured markdown report
- Write to the project workspace
- Include: primary findings, scenario analysis, strategic implications, conclusion
- Attribute the source clearly with URL and access date

## Report Structure

Use this structure unless the user specifies otherwise:

```
# [Document Title] Analysis
## Report ID: [project]-[date]-[topic]-[seq]

---

## 1. Executive Summary
[One paragraph + key metrics table]

## 2. Quick Summary
[Bullet points or table of main facts/decisions]

## 3. Thorough Analysis
### 3.1 [Theme 1]
### 3.2 [Theme 2]
...
[Each section: what → so what → risks]

## 4. Report: Findings & Conclusions
### 4.1 Primary Findings
### 4.2 Scenarios & Probabilities
### 4.3 Strategic Implications
### 4.4 Conclusion

---
*Analysis by: [agent]*
*Date: [date]*
*Source: [URL]*
```

## Pitfalls

- **404 / wrong URL:** Many sites (especially government) have multiple URL forms. If the direct link fails, search for the document title + site before assuming it's blocked. Federal Reserve sites commonly have both `.pdf` and `.htm` versions.
- **Long documents:** If web_extract truncates, save to a local file and use read_file with offset/limit to page through.
- **Data fidelity:** Preserve numerical data exactly as presented — the user may reference specific figures. Do not round unless asked.
- **Analysis depth:** The "thorough analysis" section should go beyond restating the document. Include your own synthesis, pattern recognition, and implication assessment. That's what the user is paying for.

## Support Files

- `templates/report-structure.md` — starter template for the report output
