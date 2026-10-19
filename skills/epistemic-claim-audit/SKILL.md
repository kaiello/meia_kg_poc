---
name: epistemic-claim-audit
description: Audits epistemic authority and enforces strict separation between vendor self-asserted claims (Graph 1), live demonstration trial telemetry (Graph 2), and obligated FPDS contract awards (Graph 3).
route_profiles:
  - D1_ORGANIZATIONAL_IDENTITY
  - D2_TECHNICAL_READINESS
  - D3_PROCUREMENT_TELEMETRY
  - D4_CROSS_GRAPH_SYNTHESIS
  - ROUTE_ORG
  - ROUTE_TECH
  - ROUTE_CRM
  - ROUTE_ORG_TECH
  - ROUTE_CRM_ORG
  - ROUTE_CRM_TECH
  - ROUTE_ALL_TRI_STORE
require_epistemic_tags: true
ban_unsupported_promotions: true
---

# Epistemic Claim Audit & Authority Verification Skill

## Purpose
Guarantees that no vendor marketing or self-asserted claim is presented as a verified government test result or an active procurement obligation, and validates that every generated claim is anchored to a verified locator (`Sheet!Row:Col`, `chunk_id`, `award_id`, `claim_id`).

## Inputs
- `retrieved_evidence`: Context packets containing Tri-Graph facts with explicit `epistemic_status` tags:
  - `VENDOR_SELF_ASSERTED`: Marketing materials, initial Vulcan submissions, self-reported TRLs.
  - `LIVE_DEMONSTRATED`: Event trial observations, measured flight tests, physical test environments.
  - `FPDS_OBLIGATED`: Federal Procurement Data System records, obligated dollar amounts, contract IDs.
  - `DERIVED_ANALYTIC`: Tri-Graph multi-hop cross-referencing or calculated ratios.
- `generated_text`: Candidate synthesis text from the reader model.

## Outputs
- `epistemic_audit`: Structured audit object with `status` (`VERIFIED`, `CONFLATION_DETECTED`, `UNANCHORED_CLAIM`), list of inspected claims, and violations.
- `sanitized_answer`: Answer text with strict epistemic qualifiers and corrected claim attributions.

## Guardrails
- **No Conflation**: An answer must NEVER describe a self-reported TRL (e.g. "Vendor asserts TRL 8") as an independently demonstrated fact unless supported by a Graph 2 `LIVE_DEMONSTRATED` trial record.
- **Mandatory Caveats**: Any vendor assertion lacking corresponding live demonstration data MUST include an explicit caveat: `"[CAVEAT: Vendor self-asserted; not independently observed in government trials]"`.
- **Strict Citation**: Every factual statement regarding numbers, dates, locations, or contract amounts must include an inline locator citation: `[Source: <locator>]`.

## Workflow
1. **Fact Tagging**: For each statement in the generated answer, identify the underlying Tri-Graph source and verify its epistemic tag.
2. **Authority Boundary Check**:
   - If text says "Vendor demonstrated capability X at Key West", verify that a Graph 2 trial record exists.
   - If only Graph 1 Vulcan text exists, rewrite statement to: "In Vulcan submission VULCAN-XXX, the vendor asserts capability X...".
3. **Obligation Integrity Check**:
   - Ensure contract ceiling and obligated amounts are not conflated.
   - Verify that award numbers match actual FPDS records from Graph 3.
4. **Epistemic Badge Generation**: Produce the final audit badge (`Epistemic Status: VERIFIED (Graph 1 + Graph 2 + Graph 3)`).

## Success Metrics
- 0% epistemic conflation errors across Competency Questions CQ-73, CQ-74, and CQ-75.
- 100% resolution of source citations against the retrieved context packet.
