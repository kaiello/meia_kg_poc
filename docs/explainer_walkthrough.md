# MEIA Architecture Explainer Walkthrough: Core Concepts & Systems Deep-Dive

This document provides a comprehensive, component-by-component technical walkthrough of the **MEIA Architecture Explainer** (`http://127.0.0.1:8000/explainer`). It details the formal data models, algorithmic pipelines, epistemic boundaries, and runtime execution paths across the four foundational pillars of the system:
1. **Federated Tri-Graph Knowledge Architecture & Formal Ontologies**
2. **Pre-Retrieval Policy Routing, NativeScope & Fail-Closed Gateways**
3. **Trident Multimodal Search, ColPali Late-Interaction & LoC Reader Arms**
4. **Epistemic Authority Firewall & Reified Claim Ledger**
5. **Dual-Engine Synthesis & Active Domain Skill Orchestration**

---

## 1. System Overview & The Explainer Interface

The **MEIA Interactive Explainer** is accessible live at **`http://127.0.0.1:8000/explainer`**. Built on an interactive, dark-mode architecture inspired by GitHub systems documentation, it enables evaluators, ontologists, and system architects to:
- **Inspect System State in Real Time:** Review live counts of nodes, edges, claims, and active models across the federated repository.
- **Trace Guided Execution Steps:** Step through sequential data transformations (Ingest $\to$ Graph Partitioning $\to$ Link Bridges $\to$ Evidence Spines).
- **Interact with High-Definition Diagrams:** Pan and zoom SVG Mermaid-rendered architectural schematics.
- **Audit Live Source Excerpts:** Inspect real repository code side-by-side with architectural claims via [`/api/explainer/source`](file:///C:/Users/kenai/meia_kg_poc/src/explainer_service.py#L475-L524).

```mermaid
flowchart LR
    accTitle: MEIA Explainer High-Level System Partitioning
    accDescr: Shows the five major functional panels and their operational domains within the MEIA architecture.

    P1["🏛️ Panel 1: Federated Tri-Graph<br/>(ORG-KG + TECH-KG + CRM-KG + Spine)"] --> P2["🛡️ Panel 2: Pre-Retrieval & Policy<br/>(D1-D4 Profiles + CQ-76/77/78 Gates)"]
    P2 --> P3["🖼️ Panel 3: Trident Visual Search<br/>(ColQwen2.5 MaxSim + LoC 3-Arm)"]
    P3 --> P4["⚖️ Panel 4: Epistemic Firewall<br/>(Tier Hierarchy + Reified Claims)"]
    P4 --> P5["⚡ Panel 5: Dual Engine & Skills<br/>(Deterministic Proof + Local 8B Ollama)"]

    classDef panel fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    class P1,P2,P3,P4,P5 panel;
```

---

## 2. Pillar 1: Federated Tri-Graph Architecture & Formal Ontology

### 2.1 The Need for Federated Graph Partitioning
Government capability evaluation suffers when commercial marketing, corporate registration, and procurement awards are collapsed into a single monolithic graph. Commercial claims taint official contract records, and financial accounting relationships pollute technical readiness evaluations.

MEIA resolves this through **formal tri-graph domain isolation**:
- **Organization Graph (`ORG-KG`):** Contains corporate identities, legal entities, CAGE codes, UEI numbers, SAM.gov registration states, and FPDS procurement award histories.
- **Technology Graph (`TECH-KG`):** Contains hardware and software offerings, technical specifications, subsystem components, demonstrated readiness levels (TRL/MRL/IRL), and operational problems solved.
- **CRM & Submissions Graph (`CRM-KG`):** Tracks commercial Vulcan intakes, 48-hour SLA review milestones, rough-order-of-magnitude (ROM) funding requests (Q5), and unit costs (Q6).

```mermaid
graph TD
    accTitle: Federated Tri-Graph Partitioning and Multimodal Evidence Spine
    accDescr: Illustrates the three isolated domain graphs connected via bidirectional inverse bridges to the shared multimodal evidence spine.

    subgraph OrgDomain ["🏢 ORG-KG (Organization Domain)"]
        OrgNode["Node: org:albacore<br/>CAGE: 8H3K9 | UEI: W7J8K9<br/>Lynnwood, WA | Small Business"]
        AwardNode["Node: award:CONT_AWD_M0026411P0469<br/>Value: $740,000 | DoD USMC"]
        OrgNode -->|"has_procurement_history"| AwardNode
    end

    subgraph TechDomain ["⚙️ TECH-KG (Technology Domain)"]
        TechNode["Node: tech:ghostfin_uuv<br/>TRL: 6 | Range: 1000 nmi<br/>Payload: 250 lbs modular"]
        SKOSNode["SKOS: c5isr:tactical_undersea<br/>Broader: c5isr:undersea_warfare"]
        TechNode -->|"skos:broader"| SKOSNode
    end

    subgraph CRMDomain ["📋 CRM-KG (Submission Domain)"]
        SubNode["Node: crm:submission_26705<br/>Vulcan TEM #26705<br/>Q5 Funding: $5M-10M | Q6 Cost: $500K"]
        StageNode["Node: crm:stage:technical_evaluation<br/>SLA Status: REVIEW_COMPLETED"]
        SubNode -->|"has_pipeline_stage"| StageNode
    end

    subgraph Spine ["🔗 Multimodal Evidence Spine (Immutable Anchor)"]
        CellAnchor["Cell: MEIA_TEM_Vulcan_Export.xlsx!R2C59"]
        DocAnchor["Doc: doc:klas_c5isr_truetactical#p1"]
        FigAnchor["Raster: MEIA_Charter_2026_p2.png<br/>BBox: [0.12, 0.08, 0.88, 0.92]"]
    end

    %% Cross-Graph Typed Bridges
    OrgNode <===>|"[:DEVELOPS_OFFERING]<br/>[:OFFERED_BY_ORGANIZATION]"| TechNode
    SubNode <===>|"[:EVALUATES_OFFERING]<br/>[:HAS_CAPABILITY_SUBMISSION]"| TechNode
    SubNode <===>|"[:SUBMITTED_BY_ORG]<br/>[:SUBMITTED_CAPABILITY]"| OrgNode

    %% Evidence Anchor Connections
    TechNode -.->|"has_evidence_locator"| CellAnchor
    TechNode -.->|"illustrated_by"| FigAnchor
    AwardNode -.->|"has_evidence_locator"| DocAnchor

    classDef org fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef tech fill:#1e293b,stroke:#34d399,stroke-width:2px,color:#f8fafc;
    classDef crm fill:#1e293b,stroke:#fbbf24,stroke-width:2px,color:#f8fafc;
    classDef spine fill:#1e1b4b,stroke:#a855f7,stroke-width:2px,color:#f8fafc;

    class OrgNode,AwardNode org;
    class TechNode,SKOSNode tech;
    class SubNode,StageNode crm;
    class CellAnchor,DocAnchor,FigAnchor spine;
```

### 2.2 Formal OWL 2 DL Ontology & Inverse Object Properties
The knowledge model is formally defined in [`ontology/meia_ontology.ttl`](file:///C:/Users/kenai/meia_kg_poc/ontology/meia_ontology.ttl) using **W3C OWL 2 DL** and anchored to **Basic Formal Ontology 2020 (ISO/IEC 21838-2)**.

Key ontological structural guarantees include:
- **21 Formal BFO Classes:** Explicitly mapping entities to BFO primitives (`bfo:MaterialEntity`, `bfo:GenericallyDependentContinuant`, `bfo:Process`).
- **13 Bidirectional Inverse Object Property Pairs (26 total predicates):** Ensures traversability across domain boundaries without graph directionality bias:
  - `meia:developsOffering` $\iff$ `meia:offeredByOrganization`
  - `meia:evaluatesOffering` $\iff$ `meia:evaluatedInSubmission`
  - `meia:submittedByOrg` $\iff$ `meia:submittedCapability`
  - `meia:addressesProblem` $\iff$ `meia:problemAddressedBy`
  - `meia:hasEvidenceLocator` $\iff$ `meia:locatorEvidences`
- **4,188 Exported W3C RDF Turtle Triples:** Serialized with standard prefix mappings (`bfo:`, `skos:`, `dcterms:`, `meia:`, `prov:`).
- **Automated Reasoner Validation:** Validated via [`src/ontology_service.py`](file:///C:/Users/kenai/meia_kg_poc/src/ontology_service.py) with zero owl-disjointness violations.

---

## 3. Pillar 2: Pre-Retrieval Policy, NativeScope & Fail-Closed Gateways

### 3.1 Minimum-Sufficient Routing Profiles (D1–D4 & 360°)
Before searching or querying any index, queries pass through the **Pre-Retrieval Router** ([`src/pre_retrieval.py`](file:///C:/Users/kenai/meia_kg_poc/src/pre_retrieval.py)), which classifies intent into **minimum-sufficient routing profiles**:
- **`D1_CORPORATE_PAST_PERFORMANCE`:** Scopes search strictly to `ORG-KG` (CAGE, UEI, SAM status, past performance awards). Bypasses technical indices entirely.
- **`D2_TECHNICAL_READINESS`:** Scopes search strictly to `TECH-KG` (TRL, specs, modular payload, SKOS taxonomies).
- **`D3_OPERATIONAL_FIT`:** Crosses `TECH-KG` and `CRM-KG` to evaluate mission operational problems against commercial solution readiness.
- **`D4_CROSS_GRAPH_SYNTHESIS`:** Multi-graph traversal joining `ORG-KG`, `TECH-KG`, and `CRM-KG` along verified cross-graph spine bridges.
- **`ROUTE_ALL_TRI_STORE`:** Triggered for exhaustive 360° Executive Dossiers, joining corporate history, full Vulcan submission fields (Q1–Q14), and multimodal schematics.

```mermaid
sequenceDiagram
    accTitle: Pre-Retrieval Policy and Fail-Closed Gateway Sequence
    accDescr: Sequence diagram illustrating how a user query is evaluated against RBAC clearance, scope rules, and domain routing.

    autonumber
    actor User as Evaluator / Caller
    participant Router as Pre-Retrieval Router
    participant RBAC as CQ-77 RBAC/ABAC Gate
    participant Guard as CQ-78 Boundary Gate
    participant CTE as SKOS Recursive CTE
    participant Hybrid as Scoped Hybrid Retriever

    User->>Router: query("What is Ghostfin TRL?"), CallerContext(SECRET)
    Router->>RBAC: verify_clearance(caller_level="SECRET", target_data="CUI/Proprietary")
    alt Clearance Insufficient (UNCLASSIFIED caller on CUI)
        RBAC-->>User: Refusal: ACCESS_DENIED [policy:meia_rbac_gate#CQ-77] (0 tokens generated)
    else Clearance Authorized
        RBAC->>Guard: check_empirical_parameters(query)
        alt Query seeks unrecorded specs (e.g. crush depth at 40 knots)
            Guard-->>User: Refusal: OUT_OF_SCOPE [CQ-78 Truthful Abstention]
        else Query within recorded domain
            Guard->>CTE: expand_concepts("ghostfin", "uuv")
            CTE-->>Router: Expanded: ["unmanned undersea vehicle", "submersible", "c5isr:undersea"]
            Router->>Hybrid: dispatch(route="D2_TECHNICAL_READINESS", modules=["TECH-KG"])
        end
    end
```

### 3.2 Recursive SKOS Taxonomy Expansion via SQL CTEs
Domain queries frequently use shorthand acronyms (`UUV`, `C5ISR`, `LFAM`). To ensure comprehensive recall without ungrounded LLM query expansion, MEIA utilizes **Recursive Common Table Expressions (CTEs)** directly in SQLite:

```sql
WITH RECURSIVE skos_hierarchy AS (
    -- Anchor: find exact concept match
    SELECT concept_id, pref_label, broader_id, 0 AS depth
    FROM skos_concepts
    WHERE pref_label MATCH :query_token
    UNION ALL
    -- Recursive Step: walk up and down broader/narrower edges
    SELECT c.concept_id, c.pref_label, c.broader_id, h.depth + 1
    FROM skos_concepts c
    JOIN skos_hierarchy h ON c.broader_id = h.concept_id OR c.concept_id = h.broader_id
    WHERE h.depth < 3
)
SELECT DISTINCT concept_id, pref_label FROM skos_hierarchy;
```

### 3.3 Fail-Closed Gateways (CQ-76, CQ-77, CQ-78)
In high-stakes defense intelligence, **failing closed** is strictly preferable to generating hallucinated extrapolations:
- **CQ-76 (Node Capability Dependency Gate):** If a query requests a domain module not deployed on the air-gapped node (e.g. foreign export registry), execution halts with status `INSUFFICIENT_DEPLOYED_CAPABILITY`.
- **CQ-77 (Mandatory RBAC/ABAC Gate):** If the caller's cryptographic `CallerContext` has clearance `UNCLASSIFIED`, all CUI, proprietary pricing (Q5 ROM funding, Q6 unit cost), and classified observations are withheld. The system cites `policy:meia_rbac_gate#CQ-77` without executing graph traversal.
- **CQ-78 (Truthful Abstention on Operational Boundaries):** If a user asks for unrecorded empirical specifications (e.g., *"What is Ghostfin's crush depth and acoustic signature decibel rating at 40 knots?"*), the composer inspects the ground truth evidence ledger. Recognizing that no empirical trial recorded acoustic decibels, it **truthfully abstains** with `OUT_OF_SCOPE` rather than allowing an LLM to invent military figures.

---

## 4. Pillar 3: Trident Visual Search, ColPali Late-Interaction & LoC Arms

### 4.1 Trident Visual Architecture (arXiv:2610.11816)
Text-only retrieval is blind to engineering diagrams, electrical schematics, propulsion layouts, and slide memos. The Trident subsystem indexes document visuals natively:
- **180 DPI / 300 DPI Lossless Rasterization:** Every PDF page is rasterized to high-density RGB images.
- **Docling & PyMuPDF Spatial Segmentation:** Figures and diagrams are detected and cropped into normalized coordinates `[ymin, xmin, ymax, xmax]`.
- **Bypassing Image Extraction Limits:** Rather than extracting embedded raster thumbnails (which often fail or cap out), Trident operates directly on full-resolution rendered page coordinate patches.

```mermaid
flowchart TD
    accTitle: Trident Visual Search and Loud-and-Clear (LoC) Cropping Pipeline
    accDescr: Shows the transformation of PDF documents into 180 DPI rasters, ColPali multi-vector patch embeddings, and LoC reader arm perspectives.

    PDF["📄 Document Corpus (PDFs & Slides)"] --> Raster["🖼️ 180 DPI Rasterization Engine"]
    Raster --> Layout["📐 PyMuPDF & Docling Spatial Bounding"]
    
    Layout --> ArmA["🔭 LoC Arm A: Full-Page Raster<br/>(Macro topography & slide context)"]
    Layout --> ArmB["🔬 LoC Arm B: 300 DPI Focal Crop<br/>(High-zoom propulsion/schematic detail)"]
    Layout --> ArmC["⚡ LoC Arm C: Multimodal Callout<br/>(Focal crop + GLM-OCR extracted chips)"]

    Raster --> ColPali["🧠 Vidore / ColQwen2.5-v0.2<br/>Vision Transformer (ViT)"]
    ColPali --> Patches["🧩 1024 Multi-Vector Patch Embeddings<br/>(per page image)"]
    
    Query["🔍 Text Query: 'propulsion layout'"] --> QTokens["🔤 Query Tokens (BERT/Qwen Tokenizer)"]
    
    QTokens & Patches --> MaxSim["∑ MaxSim Late Interaction<br/>Score = ∑_i max_j (q_i · p_j)"]
    
    MaxSim --> TopFigs["🏆 Top-Scoring Visual Figures & Chips"]
    ArmC --> TopFigs
    TopFigs --> Packets["📦 Functional Context Packet"]

    classDef proc fill:#1e293b,stroke:#0ea5e9,stroke-width:2px,color:#f8fafc;
    classDef arm fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#f8fafc;
    classDef math fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;

    class PDF,Raster,Layout proc;
    class ArmA,ArmB,ArmC arm;
    class ColPali,Patches,QTokens,MaxSim math;
```

### 4.2 ColPali Late-Interaction MaxSim Scoring
Instead of relying on lossy text OCR, **ColPali / ColQwen2.5** maps page images into a grid of **1,024 ViT patch token vectors**. When a query $Q = \{q_1, q_2, \dots, q_m\}$ is executed, ColPali computes the **MaxSim** late-interaction operator:

$$\text{Score}(Q, \text{Page}) = \sum_{i=1}^{m} \max_{j=1}^{1024} \left( \frac{q_i \cdot p_j}{\|q_i\| \|p_j\|} \right)$$

This allows visual features (arrows, propulsion manifolds, chassis pinouts) to match textual queries with high spatial precision, even when OCR text is degraded or absent.

### 4.3 Loud-and-Clear (LoC) 3-Arm Inspection Strategy
To support both visual language models and text-only synthesis engines, the LoC subsystem ([`src/figure_inspectors.py`](file:///C:/Users/kenai/meia_kg_poc/src/figure_inspectors.py)) provides three distinct arms:
1. **`ARM_A_FULL_PAGE`:** Serves the full-page raster (resized to $512 \times 512$ JPEG in-memory) for high-level topographic slide reasoning.
2. **`ARM_B_FOCAL_CROP`:** Crops tightly around the primary technical diagram at 300 DPI, eliminating surrounding headers and disclaimers.
3. **`ARM_C_MULTIMODAL_CALLOUT` *(Default)*:** Combines the focal crop with structured text callouts extracted via `glm-ocr` and bounding-box chip annotations. This delivers **maximum extraction accuracy in only 3 seconds** without saturating the LLM's visual context window.

---

## 5. Pillar 4: Epistemic Authority Firewall & Reified Claim Ledger

### 5.1 Three-Tier Normative Authority Hierarchy
The central doctrine of the MEIA Knowledge Graph is: **Never treat vendor self-assertions as government-validated facts.**

Evidence is strictly triaged into three sovereign authority tiers ([`src/epistemic_verifier.py`](file:///C:/Users/kenai/meia_kg_poc/src/epistemic_verifier.py)):

| Tier | Epistemic Classification | Authority Sources | Weight / Priority |
| :--- | :--- | :--- | :--- |
| **Tier 1** | `FPDS_OBLIGATED` / `GOVERNMENT_AWARD` | Executed federal procurement contracts, FPDS notices, SAM.gov registrations | **Sovereign Authority (1.0)** — Overrules all lower tiers |
| **Tier 2** | `LIVE_DEMONSTRATED` / `GOVERNMENT_TRIAL` | NATO exercise test logs (REPMUS, SONIC SPEAR), military range evaluation telemetry | **Empirical Ground Truth (0.9)** — Verifies technical readiness |
| **Tier 3** | `VENDOR_SELF_ASSERTED` | Vulcan Excel TEM submissions, commercial whitepapers, marketing brochures | **Asserted Claim (0.5)** — Subject to audit & firewall isolation |

### 5.2 Conflict Detection & Reified Statements
When an asserted claim contradicts an empirical observation, the Epistemic Firewall triggers **CQ-74 Conflict Handling**:
- **Scenario:** Albacore marketing materials assert Ghostfin achieves **TRL 7**. However, official NATO REPMUS 26 exercise results demonstrate field maturity at **TRL 6**.
- **System Action:** The system does not average or silently overwrite the values. Instead, it generates a high-visibility warning banner:
  > `> [!WARNING] Epistemic Conflict Detected (CQ-74): Conflicting records exist between vendor claims and independent test/evaluation evidence.`
- Both perspectives are preserved side-by-side with exact provenance locators (`Sheet1!R2C59` vs `demo:repmus_26_trial_log`).

Every triple is stored in SQLite using **W3C RDF Statement Reification**:
```text
Claim Statement: [tech:ghostfin_uuv] -> [:has_readiness_trl] -> "6"
  - Reified Subject:    tech:ghostfin_uuv
  - Reified Predicate:  has_readiness_trl
  - Reified Object:     6
  - Epistemic Status:   LIVE_DEMONSTRATED
  - Confidence:         1.0
  - Evidence Locator:   MEIA_TEM_Vulcan_Export.xlsx!Vulcan Submissions!R2C59
  - Handling Privilege: SECRET
```

---

## 6. Pillar 5: Dual-Engine Synthesis & Active Skill Orchestration

```mermaid
flowchart TD
    accTitle: Dual-Engine Synthesis with Domain Skill Ingress
    accDescr: Illustrates how an AnswerRouteBundle is evaluated either deterministically or through live local Ollama open-weight models.

    Bundle["📦 AnswerRouteBundle<br/>(Entities, Claims, Chunks, Visual Chips)"] --> Switch{"Engine Selector Switch<br/>(Caller Preference)"}

    subgraph EngineA ["⚙️ Engine A: Pure Graph Proof Engine"]
        DetComposer["Deterministic Grounded Composer<br/>(< 35ms Latency, Zero Hallucination)"]
        DetFactMap["Strict Fact-to-Locator Matrix<br/>(Extracts GroundedFact list)"]
        DetComposer --> DetFactMap
    end

    subgraph EngineB ["🖥️ Engine B: Local Open-Weight Stack (Ollama + CUDA:0)"]
        Client["LiveLLMClient.generate()<br/>(Ollama Native /api/chat)"]
        Skills["Active SKILL.md Prompt Injection<br/>(tri-graph-routing, epistemic-claim-audit)"]
        QwenVL["ollama:qwen3-vl:8b-instruct<br/>(5.91 GB VRAM, num_ctx=4096)"]
        Hermes["ollama:hermes3:8b<br/>(4.80 GB VRAM, num_ctx=4096)"]

        Client --> Skills
        Skills --> QwenVL & Hermes
    end

    Switch -->|"engine = 'deterministic'"| EngineA
    Switch -->|"engine = 'ollama:qwen3-vl:8b-instruct'"| EngineB
    Switch -->|"engine = 'ollama:hermes3:8b'"| EngineB

    EngineA --> Verifier["⚖️ Epistemic Verifier<br/>(Audits facts & checks citations)"]
    EngineB --> Verifier

    Verifier --> FinalDossier["📄 Final Executive Grounded Dossier<br/>(VERIFIED_GROUNDED + Cell Citations)"]

    classDef bundle fill:#312e81,stroke:#6366f1,stroke-width:2px,color:#ffffff;
    classDef ea fill:#1e293b,stroke:#0ea5e9,stroke-width:2px,color:#ffffff;
    classDef eb fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#ffffff;
    classDef audit fill:#3b0764,stroke:#a855f7,stroke-width:2px,color:#ffffff;

    class Bundle bundle;
    class DetComposer,DetFactMap ea;
    class Client,Skills,QwenVL,Hermes eb;
    class Verifier,FinalDossier audit;
```

### 6.1 Engine A: Pure Graph Proof Engine (< 35ms)
Engine A operates without an LLM. It directly traverses the SQLite FTS5 index, follows cross-graph foreign keys, and assembles formatted Markdown dossiers strictly from validated claim assertions.
- **Latency:** **15–35 milliseconds**.
- **Reproducibility:** **100.0% deterministic**, mathematical certainty.
- **Ideal For:** Automated regression test suites, batch CI/CD pipelines, and air-gapped embedded hardware lacking GPU acceleration.

### 6.2 Engine B: Local Open-Weight Models (Ollama Stack)
Engine B leverages modern open-weight language models hosted 100% locally on your machine via **Ollama on NVIDIA GeForce RTX 3080 Ti (CUDA:0)**:
- **`qwen3-vl:8b-instruct` *(Default)*:** 8-billion parameter vision-language model. Running through Ollama's native `/api/chat` with `num_ctx=4096` and `think=False`, it occupies **5.91 GB of VRAM (zero CPU swap spillover)** and synthesizes structured executive dossiers in seconds.
- **`hermes3:8b`:** High-speed general instruction model based on Llama 3.1. Achieves ~73 tokens/sec for rapid technical summarization.
- **`gemma4:e4b`:** Ultra-lightweight edge model for low-latency queries.

### 6.3 Active SKILL.md Prompt Orchestration
Before calling the LLM, the system dynamically scans the active domain skills registered in [`src/skill_loader.py`](file:///C:/Users/kenai/meia_kg_poc/src/skill_loader.py) and injects their mandatory operational rules into the LLM system prompt:
1. **`tri-graph-routing`:** Enforces domain isolation and prevents cross-domain entity confusion.
2. **`trident-colpali-visual`:** Directs attention to attached visual figures and bounding-box OCR callouts.
3. **`epistemic-claim-audit`:** Mandates that every assertion cite an exact locator (`[Source: Sheet1!R2C5]`) and demands explicit epistemic labeling.
4. **`executive-dossier-composer`:** Structures output into formal executive sections (Executive Summary, Technical Readiness, Commercial Terms, Risk Factors).

---

## 7. Interactive Tour & Verification Checklist

When navigating the Explainer at **`http://127.0.0.1:8000/explainer`**, verify the following key features:

| Explainer Section | Visual / Interactive Element to Inspect | Expected Architectural Insight |
| :--- | :--- | :--- |
| **Panel 1: Tri-Graph Federation** | Guided Steps 1–4, Diagram 1 SVG, Source Excerpt `config/meia_poc_manifest.json` | Verifies SHA-256 declarative ingestion, ORG/TECH/CRM segregation, and BFO 2020 class mapping. |
| **Panel 2: Pre-Retrieval Policy** | Guided Steps 1–4, Diagram 2 SVG, Source Excerpt `src/pre_retrieval.py` | Shows how `CallerContext` aborts unauthorized queries in < 1ms and how recursive SQL CTEs expand SKOS concepts. |
| **Panel 3: Trident Visual Search** | Guided Steps 1–4, Diagram 3 SVG, Source Excerpt `src/visual_retriever.py` | Demonstrates 180 DPI rasterization, ColPali 1024-patch ViT MaxSim alignment, and LoC 3-Arm cropping. |
| **Panel 4: Epistemic Firewall** | Guided Steps 1–4, Diagram 4 SVG, Source Excerpt `src/epistemic_verifier.py` | Illustrates Tier 1 vs Tier 3 authority triage, CQ-74 conflation gating, and RDF statement reification. |
| **Panel 5: Dual-Engine & Skills** | Guided Steps 1–4, Diagram 5 SVG, Source Excerpt `src/grounded_answer.py` | Contrasts < 35ms deterministic graph proofs with live Ollama 8B generation with active SKILL.md rules. |
| **Source Inspector Modal** | Click **"Inspect Source Code"** tab on any panel | Verifies that architectural claims link directly to real lines in repository code without broken paths. |

---

## 8. Summary of Key Files

| Architectural Component | File Path | Description |
| :--- | :--- | :--- |
| **Explainer Service & IR Catalog** | [`src/explainer_service.py`](file:///C:/Users/kenai/meia_kg_poc/src/explainer_service.py) | Guided steps, diagram mappings, source excerpt extractor |
| **Interactive Explainer HTML/JS** | [`docs/meia_architecture_explainer.html`](file:///C:/Users/kenai/meia_kg_poc/docs/meia_architecture_explainer.html) | Standalone Archify responsive HTML application |
| **Pre-Retrieval & Policy Engine** | [`src/pre_retrieval.py`](file:///C:/Users/kenai/meia_kg_poc/src/pre_retrieval.py) | Route profiles (D1–D4), NativeScope, CQ-76/77/78 gates |
| **Scoped Hybrid Retriever** | [`src/hybrid_retriever.py`](file:///C:/Users/kenai/meia_kg_poc/src/hybrid_retriever.py) | BM25 + BGE 1024d + CrossEncoder + Modality RRF |
| **Trident Visual Retriever** | [`src/visual_retriever.py`](file:///C:/Users/kenai/meia_kg_poc/src/visual_retriever.py) | ColQwen2.5 ViT patch MaxSim + LoC 3-Arm crops |
| **LoC Figure Inspectors** | [`src/figure_inspectors.py`](file:///C:/Users/kenai/meia_kg_poc/src/figure_inspectors.py) | Arm A, B, C cropping and GLM-OCR callout generation |
| **Epistemic Verifier & Firewall** | [`src/epistemic_verifier.py`](file:///C:/Users/kenai/meia_kg_poc/src/epistemic_verifier.py) | Three-tier authority triage & CQ-74 conflict gating |
| **Grounded Answer Composer** | [`src/grounded_answer.py`](file:///C:/Users/kenai/meia_kg_poc/src/grounded_answer.py) | Deterministic baseline & Live LLM dispatch orchestrator |
| **Local LLM Client** | [`src/llm_client.py`](file:///C:/Users/kenai/meia_kg_poc/src/llm_client.py) | Native Ollama `/api/chat` integration with VRAM controls |
| **Formal OWL 2 DL Ontology** | [`ontology/meia_ontology.ttl`](file:///C:/Users/kenai/meia_kg_poc/ontology/meia_ontology.ttl) | BFO 2020 + SKOS OWL 2 DL ontology & 13 inverse pairs |
| **Ontology Reasoner Service** | [`src/ontology_service.py`](file:///C:/Users/kenai/meia_kg_poc/src/ontology_service.py) | SQL CTE hierarchy resolvers and OWL consistency validator |
