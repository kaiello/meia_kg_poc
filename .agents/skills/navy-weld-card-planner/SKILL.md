---
name: navy-weld-card-planner
description: Mandatory planning protocol and architectural drift auditor for Navy Weld / MEIA project milestone cards. Cross-references the 49-item Master Integration and Bakeoff List, enforces the 4-point drift audit against goal.md and architecture.md, and formats implementation plan artifacts with RequestFeedback: true before code execution.
---

# Navy Weld Card Planner Skill

This skill governs the disciplined planning and architectural validation of implementation milestone cards for the **Mission Engineering and Integration Activity (MEIA) Federated Tri-Graph POC**.

---

## 1. Trigger Conditions

Activate this skill whenever:
- The user requests `/plan` for a card or milestone (e.g., `/plan card 08`, `plan card 8`, `plan next card`).
- A new feature or subsystem milestone is initiated.
- A proposed architectural change or candidate bakeoff is evaluated.

---

## 2. Mandatory Master Register Cross-Reference

Before writing any card implementation plan, the agent **MUST** cross-reference the 49 integration candidates documented in:
👉 [`docs/NAVY_WELD_MASTER_INTEGRATION_AND_BAKEOFF_LIST_2026-10-18.md`](file:///C:/Users/kenai/meia_kg_poc/docs/NAVY_WELD_MASTER_INTEGRATION_AND_BAKEOFF_LIST_2026-10-18.md)

Identify and map all relevant candidates across the 8 categories:
1. **Extraction (`E01`–`E05`)**: Manifest schemas, PDF layout parsing, table structures, visual asset bounding, OCR.
2. **Retrieval & Context Assembly (`R01`–`R10`)**: Modality calibration, NativeScope structural scoping, functional context packets, Cross-Encoder reranking, SKOS query expansion.
3. **Visual Reading & Training (`V01`–`V03`, `L01`–`L02`)**: Loud-and-Clear (LoC) multi-arm inspection (Arm A full-page, Arm B focal crop, Arm C OCR callouts), diagram OCR.
4. **Semantic Representation & Validation (`S01`–`S06`)**: BFO-Lite ontology, SKOS concept schemes, dual-layer epistemic separation, Utopia review compatibility.
5. **Platform & Persistence (`P01`–`P07`)**: SQLite FTS5, NetworkX GraphML, local contextual vector store (WeKnora, CortexDB, GraphRAG deferred/challengers).
6. **Serving Optimization (`O01`–`O03`)**: Zero-daemon local serving, batch vector precomputation, headless CLI/API.
7. **Consumer Boundary & Inspection (`U01`–`U07`)**: Context-Bench format, decoupled evaluation harness, verifiable receipts, 100% citation completeness, 360° dossiers.
8. **Engineering Workflow & History (`D01`–`D06`)**: Phased verification gates, Git audit trail & clean remote sync, deterministic offline test protocol, ADR logs.

---

## 3. Mandatory 4-Point Drift Audit

Every card plan must execute and document a strict 4-point drift check against [`docs/goal.md`](file:///C:/Users/kenai/meia_kg_poc/docs/goal.md) and [`docs/architecture.md`](file:///C:/Users/kenai/meia_kg_poc/docs/architecture.md):

| Drift Dimension | Invariant Rule | Violation Check / Enforcement |
| :--- | :--- | :--- |
| **1. Infrastructure Drift** | **Zero External Database Daemons** | Strictly reject external DB servers, Neo4j/Milvus/Qdrant daemons, Docker clusters, or cloud database subscriptions. Enforce 100% local SQLite (`storage/meia_tri_graph_registry.db`), NetworkX GraphML (`storage/*.graphml`), and local BGE-Large vector projections. |
| **2. Epistemic Drift** | **Strict Non-Equivalence Firewall** | Enforce `VENDOR_SELF_ASSERTED` $\neq$ `LIVE_DEMONSTRATED`. Zero vendor capability assertions (`meia:CapabilityClaim`) may ever be promoted to empirical demonstration facts (`eval:DemonstrationEvent` / FPDS contract awards) without explicit proof. |
| **3. Retrieval / Modality Drift** | **Fair Multimodal Representation & 100% Citation** | Prevent text-token starvation. Diagram/schematic queries must balance visual chips (180 DPI / LoC focal crops) and tabular cell coordinates (`Sheet!Row:Col`). 100% of facts must maintain traceable source provenance. |
| **4. Scope / Capacity Drift** | **Single Bounded Challenger Arm** | Follow the "core ingestion plus one active experiment campaign" rule. Limit execution to one bounded challenger arm per milestone; reject concurrent platform rewrites or speculative multi-model bakeoffs. |

---

## 4. Required Implementation Plan Artifact Format

All plans generated under this skill must be written to:
`C:\Users\kenai\.gemini\antigravity-cli\brain\<conversation-id>\meia_<card_name>_plan.md`

With `ArtifactMetadata`:
```json
{
  "RequestFeedback": true,
  "UserFacing": true,
  "Summary": "Detailed multi-line summary of the card implementation plan..."
}
```

The artifact must include the following structural sections:
1. **Goal Description & Background**: Clear scope and relationship to preceding cards.
2. **Master Integration Register Cross-Reference**: Explicit table mapping card features to `NAVY_WELD_MASTER_INTEGRATION_AND_BAKEOFF_LIST_2026-10-18.md` candidate codes.
3. **Mandatory 4-Point Drift Assessment Table**: Explicit verification of Infrastructure, Epistemic, Modality, and Scope invariants.
4. **Proposed Changes**: Concrete code snippets, new/modified files (`[NEW]`, `[MODIFY]`), data models, and schemas.
5. **Verification Plan**: Exact commands for unit tests, regression tests, and benchmark scorers.
6. **Git Synchronization Protocol**: Pre- and post-execution push/commit/pull/merge verification steps.
