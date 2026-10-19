---
name: executive-dossier-composer
description: Synthesizes 360-degree Executive Business & Capability Dossiers across Tri-Graph dimensions using Functional Evidence Units and strict inline citations.
route_profiles:
  - D4_CROSS_GRAPH_SYNTHESIS
  - D1_ORGANIZATIONAL_IDENTITY
  - D2_TECHNICAL_READINESS
  - D3_PROCUREMENT_TELEMETRY
  - ROUTE_ALL_TRI_STORE
  - ROUTE_ORG
  - ROUTE_TECH
  - ROUTE_CRM
  - ROUTE_ORG_TECH
  - ROUTE_CRM_ORG
  - ROUTE_CRM_TECH
citation_style: INLINE_LOCATOR
functional_units_enabled: true
max_tokens: 1500
---

# Executive Dossier Composer Skill

## Purpose
Synthesizes professional, decision-ready 360° Executive Business & Capability Dossiers that integrate organizational lineage (Graph 1), technical readiness and physical trial telemetry (Graph 2), and federal procurement history (Graph 3) into an authoritative, structured report.

## Inputs
- `query_str`: User query or executive research prompt.
- `functional_evidence_units`: Structured `ContextPacket` units containing:
  - `entity_anchor`: Vendor canonical name, CAGE, Vulcan ID, CRM status.
  - `readiness_unit`: Claimed TRL, live demonstrated trial results, test environments, and caveats.
  - `procurement_unit`: Contract numbers, agency obligations, ceiling values, and NAICS/PSC codes.
  - `visual_unit`: LoC `ARM_C_HYBRID_OCR` diagrams and architectural schematics.

## Outputs
- `executive_dossier`: Markdown-formatted executive report containing:
  - **1. Executive Summary & Epistemic Posture**: High-level verdict with explicit authority separation.
  - **2. Organizational Lineage & Identity**: Corporate registry, CAGE code, CRM stage, and Vulcan submission.
  - **3. Technical Readiness & Demonstration Telemetry**: Claimed vs demonstrated TRL, test dates, locations, and limitations.
  - **4. Federal Procurement & Obligation History**: Cumulative DoD obligations, active vehicles, and agency distribution.
  - **5. Multimodal Architecture & Visual Telemetry**: Inspection notes on relevant system schematics.
  - **6. Risk Assessment & Recommendations**: Bounded analyst notes on capability gaps or unverified claims.

## Guardrails
- **Evidence Boundary**: Only make claims backed by the supplied `functional_evidence_units`. If data is missing (e.g. no FPDS contract awards found), explicitly state "No active federal contract awards found in FPDS telemetry for CAGE [XXXXX]".
- **No Inferred Truth**: Do not infer operational suitability from corporate marketing descriptions.
- **Locator Citations**: Every section must cite exact source locators (e.g. `[Source: MEIA_TEM_Vulcan_Export.xlsx!Sheet1#Row12]`, `[Source: usaspending_awards.jsonl#AWARD-102]`).

## Workflow
1. **Analyze Evidence Units**: Unpack the functional units and verify that all three graph dimensions are represented.
2. **Draft Executive Sections**: Follow the 6-section dossier template, maintaining clear epistemic boundaries in each section.
3. **Embed Visual Telemetry**: Reference the LoC `ARM_C_HYBRID_OCR` diagrams where applicable.
4. **Final Fact-Check**: Ensure every factual metric has an exact source bracket citation.

## Success Metrics
- 100% adherence to the 6-section executive dossier structure for D4 queries.
- Zero uncited numerical metrics or contract figures.
