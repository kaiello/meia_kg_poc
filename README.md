# MEIA Knowledge Graph POC (`meia_kg_poc`)

**Federated Tri-Graph Multimodal Natural Language Query (NLQ) & Epistemic Decision Prototype**  
**Target:** OUSD(R&E) Mission Engineering and Integration Activity (MEIA) — Technology Scouting, Assessment & Procurement Pathway Intelligence  
**Architectural Reference:** [`kaiello/aws-a30-prototype`](https://github.com/kaiello/aws-a30-prototype/tree/main/docs)  

---

## 1. Core Documentation

- **[System Architecture](docs/architecture.md)**: Tri-graph domain separation (`Org-KG`, `Tech-KG`, `CRM-Graph`), shared multimodal evidence graph, BFO-Lite + SKOS ontology profile, SQLite FTS5 + GraphML storage substrates, active pre-retrieval routing, and claim-vs-demonstration epistemic verification.
- **[Project Goal](docs/goal.md)**: Executive objectives, client verification tests, multimodal corpus boundaries, quantitative success criteria, and fail-closed gates.
- **[Implementation Plan](docs/plan.md)**: Phased execution plan (`Cards 01–08`), declarative manifest specification (`config/meia_poc_manifest.json`), zero-truncation chunking, and evaluation protocols.
- **[78 Federated Competency Questions](docs/MEIA_Federated_78_Competency_Questions.md)**: Complete benchmark question catalog across all 8 routing profiles (`ROUTE_ORG`, `ROUTE_TECH`, `ROUTE_CRM`, pairwise joins, 360° compound dossiers, and fail-closed gates).

---

## 2. Architectural Pillars

1. **Three Federated Domain Graphs over One Epistemic Spine**: Keeps Organization, Technology, and CRM data distinct while enabling deterministic cross-graph joins (`[:DEVELOPS_OFFERING]`, `[:SUBMITTED_BY_ORG]`, `[:EVALUATES_OFFERING]`, `[:VALIDATED_BY_CONTRACT]`).
2. **Declarative Source Manifest**: Every Excel workbook, vendor PDF, raster scan, and USASpending receipt is fingerprinted by SHA-256 with exact coordinate bindings.
3. **Zero Silent Token Truncation**: Semantic field-boundary chunking ($\le 400$ tokens) paired with active 1024-dim `BAAI/bge-large-en-v1.5` contextual embeddings.
4. **Active Pre-Retrieval Intent Router**: Classifies queries into minimum-sufficient routing profiles *before* vector search or LLM generation.
5. **Claim-vs-Demonstration Non-Equivalence**: Enforces an unbroken epistemic bridge between vendor self-assertions and empirical demonstration events (AFSIM, live exercises, FPDS award obligations).
