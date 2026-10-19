---
name: tri-graph-routing
description: Classifies query intent into MEIA Tri-Graph route profiles (D1-D4), extracts NativeScope structural anchors, and plans composed multi-hop graph traversals.
route_profiles:
  - D1_ORGANIZATIONAL_IDENTITY
  - D2_TECHNICAL_READINESS
  - D3_PROCUREMENT_TELEMETRY
  - D4_CROSS_GRAPH_SYNTHESIS
native_scope_enabled: true
composed_graph_ops: true
---

# Tri-Graph Routing & NativeScope Anchor Resolution Skill

## Purpose
Directs queries to the correct epistemic graph partition (Graph 1: Vulcan/Charter, Graph 2: Technical Demonstration, Graph 3: FPDS Awards, or Federated Tri-Graph) and resolves NativeScope structural anchors (`vulcan_id`, `cage_code`, `doc_id`, `Sheet!Row:Col`) to narrow candidate retrieval scopes before ranking.

## Inputs
- `query_str`: Raw user query string.
- `extracted_entities`: Pre-extracted entity tokens (company names, CAGE codes, Vulcan IDs, TRL values).
- `tri_graph_metadata`: Graph topology metrics and available relation types.

## Outputs
- `route_profile`: Selected route (`D1_ORGANIZATIONAL_IDENTITY`, `D2_TECHNICAL_READINESS`, `D3_PROCUREMENT_TELEMETRY`, `D4_CROSS_GRAPH_SYNTHESIS`).
- `native_anchors`: Dictionary of resolved structural anchors (e.g. `{"vulcan_id": "VULCAN-001", "cage_code": "8A3B2"}`).
- `anchor_confidence`: Float between 0.0 and 1.0 indicating structural anchor certainty.
- `traversal_plan`: Bounded sequence of graph hops (e.g. `Vendor -> DemonstratedAt -> Event`, `Vendor -> Awarded -> Contract`).

## Guardrails
- **NativeScope Fallback**: If `anchor_confidence < 0.75` or scoped candidate retrieval returns fewer than 3 chunks, automatically fall back to global hybrid retrieval.
- **Scope Order**: Document physical structure (`Sheet!Row:Col`) is source order, not epistemic causality. Do not infer organizational parentage from sheet adjacency.
- **Bounded Traversal**: Multi-hop graph traversals must not exceed 3 hops to avoid combinatorial explosion and hallucinated transitive relationships.

## Workflow
1. **Entity Extraction**: Match known vendor names (Klas, Fluor, Prometheus), CAGE codes (5-character alphanumeric), and Vulcan submission IDs (`VULCAN-XXX`).
2. **Anchor Resolution**: Identify if the query targets an exact row in `MEIA_TEM_Vulcan_Export.xlsx` or a specific section of `MEIA_Charter_2026.pdf`.
3. **Route Determination**:
   - If query asks about leadership, headquarters, CAGE code, CRM accounts -> `D1_ORGANIZATIONAL_IDENTITY`.
   - If query asks about TRL, flight trials, demonstrations, sensor architectures, figures -> `D2_TECHNICAL_READINESS`.
   - If query asks about obligated amounts, ceiling, award IDs, contracting agencies -> `D3_PROCUREMENT_TELEMETRY`.
   - If query spans multiple dimensions (e.g., "compare Klas TRL vs contract obligations") -> `D4_CROSS_GRAPH_SYNTHESIS`.
4. **Graph Operator Composition**: Formulate composed graph operations (intersection of vendors demonstrating in Florida with active DoD obligations).

## Success Metrics
- 100% correct route classification across the 24 Competency Questions (CQ-61 to CQ-84).
- Zero unhandled exceptions when queries lack structural anchors.
