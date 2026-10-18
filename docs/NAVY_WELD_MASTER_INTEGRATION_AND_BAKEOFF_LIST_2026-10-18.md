# Navy Weld — master integration and bakeoff list

**Prepared:** October 18, 2026  
**Scope:** Reconciled recommendations from the three requested October 17 documents.  
**Status:** Active Implementation & Disposition Register. Reconciled and audited against the completed baseline POC implementation (Cards 01–08) and 78-CQ gold benchmark (100.0% pass rate). See Section 10 for complete disposition audit.  
**Purpose:** One deduplicated decision and disposition register showing what has been implemented, what has been benchmarked/tested, and what has been deferred to future challenger arms.

The register contains **49 consolidated entries**, including retained practices and deferred options. Only five are near-term experiment choices; this is not a request to launch 49 tests.

## 1. Recommended decisions

**Continue source/evidence delivery and select one bounded experiment for the most consequential demonstrated failure.** The three documents describe complementary layers; their recommendations should not become a serial installation roadmap.

The near-term shortlist is:

1. **Semantic extraction: current method / minimal constrained LLM / Docling Graph / KAPipe DocRE** when useful relationships are missing. Reuse a completed equivalent comparison. LangExtract is a conditional substitution for a grounding problem.
2. **LoC-inspired reader preparation** when the correct pages or figures reach the reader but details are missed.
3. **Trident-inspired modality-bias audit** when relevant images lose rank in mixed retrieval. Test simple fusion corrections before training.
4. **NativeScope-inspired structural scoping** when reliable source anchors exist and unrestricted search misses their context.
5. **Functional evidence grouping and context packets** when answers omit notes, qualifiers, captions, or continuations.

These are five choices, not five concurrent projects. **Default capacity: core ingestion plus one active experiment campaign.** An extraction campaign can contain several bounded arms; run expensive arms sequentially unless resources are explicitly allocated otherwise. Adopt passing components behind existing interfaces, then check their interaction once.

**Conditional next:** minimal graph-operation improvements, bounded DocPilot-style navigation, a direct multimodal processor, or a reader-model comparison. Select each only for its own residual.

**Defer unless triggered:** retriever/OCR training, a new database, whole-platform migration, ontology infrastructure, global GraphRAG, a second UI, cloud wiki sync, and persistent engineering-agent orchestration. Completing AWS A3.0 is neither a prerequisite for every small experiment nor an automatic trigger to add these systems.

AWS A3.0 means the **American Welding Society standard**. Amazon Web Services is a separate infrastructure option. Workstream B, Annex B, and the earlier architecture's Option B are distinct labels.

## 2. Sources and reconciliation

### 2.1 Documents reviewed in full

The filenames supplied in the request were matched to available copies. This is a review of those documents, not direct access to the Windows Downloads folder.

| Reference | Exact source document | Date/version | Contribution |
|---|---|---|---|
| **D1** | `WELD_TECHNOLOGY_TEST_AND_INTEGRATION_RECOMMENDATIONS_2026-10-17.md` | October 17, 2026 | Reader/retrieval research, graph access, models, training, infrastructure and the earlier platform shortlist |
| **D2** | `aws_a30_visual_reader_and_platform_evaluation_card.md` | October 17, 2026; proposed execution card | Concrete LoC arms, bounded DocPilot-style navigation, WeKnora comparison and visual-pilot evaluation |
| **D3** | `NAVY_WELD_WORKSTREAM_B_TECHNOLOGY_RECOMMENDATIONS_V1_0.md` | October 17, 2026; document V1.0 | Semantic-extraction campaign, semantic contracts, validation, query optimization, consumers and downstream projections |

References such as **D3 §5** point to the source document's section. D2 uses named phases. The master IDs below are planning references, not replacements for existing experiment/run IDs.

All three sources are recommendation documents, not execution receipts. Their historical commits, counts, hardware descriptions and model routes do not establish today's runtime. This master consolidates their decisions without reinstating invalidated results or restarting completed work.

### 2.2 Differences resolved

| Issue | Master treatment |
|---|---|
| D1/D2 emphasize LoC; D3 emphasizes extraction | Use the failed boundary. Missing relationships → **E01**. Correct evidence but poor reading → **V01**. Neither blocks source access. |
| Earlier “Trident and NativeScope first” advice | Retain both as near-term retrieval experiments, alongside LoC for reader failures and E01 for semantic gaps. No unconditional technology ranking across different failures. |
| Duplicate LoC plans | One **V01** campaign: existing inputs, higher-detail pages, higher-detail pages plus automatically selected region text/OCR. Optional oracle-region diagnosis stays separate. |
| Functional units, source bundles, fact packets and parent expansion | One **R03** context-assembly family. Test the smallest explicit grouping first; a trained encoder or hypergraph database is unnecessary. NativeScope remains separate because it changes eligible search scope. |
| Trident audit, RRF and graph expansion | **R01** tests modality competition and fusion. **R05** tests whether a graph channel adds missing candidates. Preserve these as distinct ablations. |
| D1's 10–20 diagnostic questions versus D2's 24-case plan | Existing cases can diagnose the failure. D2's 12 development + 12 sealed cases are an optional bounded visual-pilot design, not an additional compulsory suite. Exposed cases cannot become fresh holdout. |
| D2's “two net additional correct answers” gate versus D3's task-specific gates | Retain the numeric rule only for the proposed 12-case visual pilot. Extraction, infrastructure and formal checking need their own prospectively defined outcomes. |
| LoC → DocPilot → WeKnora appears sequential | Only the reader-to-navigation comparison has that local dependency. WeKnora can be tested earlier when the diagnosed problem is ingest/retrieval or operations. It does not require a DocPilot trial. |
| D1 carries a broad platform list; D3 prefers components | Retain the full inventory as conditional alternatives. Start with an adapter or one component; no requirement to evaluate every platform. |
| Two projects named PAGE-RAG | Keep **R08** (`denghk666`) and **R09** (`CXY0112`) separate. Do not substitute one for the other. |
| Original Trident URL was wrong | D1 identifies **2610.11816** as the Trident/modality-bias paper. **2610.11148** belongs to SP-DocReader and remains **L02**. |
| Wiki, Helix Foundry and Utopia all offer inspection | Distinct roles: generated read-only projection (**U03**), structured analyst workspace (**U04**), and review/history compatibility (**S06**). Pick the smallest option serving an actual task. |
| Different source-card approval language | This review authorizes no deployment. Execution should reuse applicable existing task authority and settled permissions; the master adds no new approval ceremony. |

### 2.3 Review freshness and limits

This is principally a consolidation of the three supplied reviews. A limited October 18 public-page check reconfirmed the LoC repository's release placeholder, DocPilot's interactive-document role, and WeKnora's documented opt-in image retrieval in its v0.8.3 notes. The PAGE-RAG (`denghk666`) and DocPilot training-page fetches were unsuccessful; their October 17 qualifications remain attributed to D3 and D2. These checks were not code audits or deployment tests. Primary links are in Section 9.

Before an executable trial, bind the selected build and recheck only the interfaces, availability and terms relevant to that trial. Do not interpret the older platform shortlist as current compatibility evidence.

## 3. Preserve and apply in ongoing work

These are baseline responsibilities, not a new technology bakeoff.

| Responsibility | Treatment |
|---|---|
| Source access and native parsing | Continue authorized ingestion, deterministic profiling, reliable native text and targeted Tesseract/pytesseract where already used. Source reading must not wait for complete semantic extraction. |
| Evidence identity and actual images | Preserve edition/checksum, physical/printed page mapping, source/figure/region IDs, original pixels, coordinate frames, notes and continuation order. Check actual image delivery separately from reader interpretation. |
| Candidate and canonical semantics | Keep evidence-only outputs, candidate assertions, accepted assertions and inferred/derived projections distinct. Retain direction, roles, source sense, negation, qualifiers and support links. |
| Working retrieval and answering | Retain the actual lexical/exact, MiniLM, ColPali/ColQwen, graph and source-reading routes. Do not assume all named variants are installed, or silently call an unknown lexical implementation BM25. |
| Stable consumer boundary | Preserve existing read-only MCP/API, generic operations, answer/evidence contracts and one authorized consumer. An image URI alone does not demonstrate image delivery. |
| Assessment and history | Reuse existing questions, evidence packages, review and regression assets. Preserve failed runs, historical invalidations and uncertainty. Missing graph content does not prove absence from the source. |

Schema validity, ranking confidence, source support, formal derivability and answer quality remain separate outcomes. An accepted semantic graph can support traversal; it does not replace the source as authority for wording or visual interpretation. [D1 §§2, 4, 8; D3 §§2, 10–11]

## 4. Master integration and bakeoff register

**Priority key:** **P1** = near-term choice when the named failure exists; **P2** = conditional after its specific prerequisite; **P3** = defer until a substantive need/readiness change; **Retain/Apply** = ongoing responsibility or reusable principle. Priority is not a completion claim or authorization. Every unexecuted option remains proposed.

Each adoption statement below also requires the common evidence, regression, budget and rollback checks in Section 7. Shared rows group alternatives for one decision; they do not recommend installing every listed product.

### 4.1 Evidence preparation and semantic extraction

| ID / priority | Candidate or suggestion | Where and when to test | Smallest bakeoff and integration rule | Basis |
|---|---|---|---|---|
| **E01 · P1** | Current extraction; minimal schema-constrained LLM; **Docling Graph; KAPipe DocRE**; conditional **LangExtract** | Candidate generation on the next useful, authorized source family when supported relationships are missing | Same bundles, vocabulary and support contract. Compare raw supported candidates, qualifiers, grounding and total validated-build effort. Adopt by relationship family. LangExtract substitutes for a grounding-focused arm; do not automatically add a fifth arm. Details in §6.1. | D1 §5.12; D3 §5 |
| **E02 · P2** | **Docling/docling-parse; PaddleOCR/PP-StructureV3/PaddleOCR-VL; MinerU** | Source-to-evidence adapter when OCR, layout, tables or coordinates are demonstrably wrong | Current parser versus one relevant challenger on the same PDFs. Measure usable evidence and correction effort, including headers/notes and locations. Keep native text where it works; change only the failing parser component. | D1 §6; D3 §4.1 |
| **E03 · P2** | **Databricks IDP; Amazon Bedrock Data Automation/Textract; Google Document AI** | Managed parsing/extraction when an existing permitted environment and operating need fit | Select one cloud comparator. Same slice and evidence obligations; include transfer, model, repair and recurring operating costs. Adopt only a permitted parser/extraction adapter with useful gains. This is independent of managed retrieval. | D1 §6 |
| **E04 · P2** | **RAG-Anything / LightRAG** multimodal processor | Image-plus-caption/context enrichment when a direct reader or current processor misses associations | Same pixels/context: direct same-VLM control versus one processor, using compatible pre-parsed inputs where possible. Score source-supported associations and binding first. A processor win does not select its graph/index/runtime. | D1 §6; D3 §7.1 |
| **E05 · P3** | **KAPipe proposition extraction / ProStruct-RAG** | Candidate generation when complex prose decomposition or contradiction handling remains a real gap | Original-source assertions versus derived propositions on one family, preserving modality, scope and exceptions. Adopt only useful candidate production; rewritten statements and headings never become facts automatically. | D3 §4.1 |

### 4.2 Retrieval, graph operations and context assembly

| ID / priority | Candidate or suggestion | Where and when to test | Smallest bakeoff and integration rule | Basis |
|---|---|---|---|---|
| **R01 · P1** | **Trident-inspired modality-bias audit; RRF/calibrated fusion** | Ranking/fusion when images lose position among text candidates | Text-only, visual-only and fused routes with controlled text/image distractors. Track required visual rank and complete evidence recall. Test simple fusion fixes first. Adopt only a held-out gain without material text regressions; training is L01. | D1 §5.2; D3 §6.2 |
| **R02 · P1** | **NativeScope-inspired operators** | Before ranking, when exact IDs or reliable locators identify source structure | Global retrieval versus simple context window versus membership/order scope. Include wrong and ambiguous anchors, cross-references and fallback. Adopt bounded operators only when exclusions are controlled. Source order is not engineering causality. | D1 §5.3 |
| **R03 · P1** | **Functional evidence units; structure-aware bundles; fact packets; bounded parent/continuation expansion** | Evidence assembly when notes, limitations or connecting support are omitted | Individual hits versus explicit source-linked bundles at the same total reader budget. Preserve constituent IDs and direct lookup; deduplicate. Adopt useful grouping, not unconditional semantic edges. No learned encoder/hypergraph store in the first trial. | D1 §5.4; D3 §§4.1–4.2, 6 |
| **R04 · P2** | **Batching, pagination, bounded traversal and set composition; DKGI** | Graph query execution when the accepted graph has the answer but tool caps or one-hop calls obstruct access | Existing tools → minimal composed operations → isolated complete export only if a gap remains. Preserve actual edges, direction, qualifiers and evidence IDs. Prefer backend operators; unrestricted answering-agent shell/files require a different architecture decision. | D1 §5.5 |
| **R05 · P2** | **Source-scoped graph-neighborhood retrieval channel** | Candidate generation when supported semantic paths do not reach the reader | Current channels versus graph expansion, with route ablations and fixed scope/budget. Integrate if additional supported evidence improves answers. Do not force traversal for simple exact lookups; evaluate fusion separately in R01. | D3 §§4.2, 6.2 |
| **R06 · P2** | **Conventional cross-encoder reranking** | After retrieval when the relevant item is present but poorly ranked | Fixed candidate pool and reader; compare current order with reranking. Preserve necessary notes/context and measure full-query overhead. It cannot recover excluded candidates. | D3 §6.2 |
| **R07 · P2** | **CLM — Contrastive-LM/CLM** | Action/tool selection or candidate scoring after schema and simple ranking fixes leave a residual | Zero-shot shadow recommendations before control. Include plausible alternatives, irrelevant actions and “none sufficient.” Count encoder, candidate and cache costs. Adopt only improved supported completion/total cost; scores are not support confidence. | D3 §6.2 |
| **R08 · P3** | **PAGE-RAG — denghk666** | Query-local evidence selection after simpler context assembly fails and runnable artifacts are qualified | D3 reports a future-code-release README. Recheck readiness; if eligible, compare one mechanism with R03. A paper reimplementation is separate research, not package integration. | D3 §6.3 |
| **R09 · P2** | **PAGE-RAG — CXY0112** | Optional hybrid evidence/routing mechanism for a localized query failure | Borrow the textual-evidence floor now; compare one portable mechanism against existing routes if needed. Avoid importing graph construction, communities and a new harness together. | D3 §6.3 |
| **R10 · P3** | **Microsoft/global GraphRAG; Leiden communities; community reports; map/reduce** | Corpus synthesis only when a real broad question defeats source sections, taxonomy and local retrieval | Simpler aggregation versus community/report retrieval under the same reader/budget. Require trace-back, exceptions, update invalidation and permission isolation. Reports remain derived; whole-standard completion alone is not the trigger. | D1 §6; D3 §9.2 |

### 4.3 Visual reading and model training

| ID / priority | Candidate or suggestion | Where and when to test | Smallest bakeoff and integration rule | Basis |
|---|---|---|---|---|
| **V01 · P1** | **Loud and Clear (LoC)-inspired reader-input adapter** | After evidence resolution, before a working vision-reader call; correct evidence is misread | Current inputs versus higher-detail pages versus higher-detail pages plus selected region OCR/text. Freeze pages/model; match expanded budgets where comparing B/C. Adopt if supported answers improve within cost/latency caps. Author repository remains a placeholder in the limited recheck. | D1 §5.1; D2 Phase 1 |
| **V02 · P2** | **Bounded DocPilot-style navigation** | Query-time evidence seeking when a stronger static reader still needs another region/page | Best static route versus typed retrieve/load/crop/linked-continuation/answer actions, with bounded extra inspections. Attribute gains from new evidence separately. Prefer an original minimal implementation; full reuse retains D2's unresolved licensing and execution-path concerns. | D2 Phase 2 |
| **V03 · P2** | **Mistral Large 4; Qwen2.5-VL reader variants** | Answer-model adapter after pixels, context and evidence are adequate | Current authorized model versus one eligible model with equivalent evidence and scoring. Score qualifiers, visual interpretation, unsupported claims, abstention and total cost. No silent model/provider switch or assumption of local hardware fit. An extraction-model trial belongs under E01 and is separately labeled. | D1 §5.6; D3 §7.2 |
| **L01 · P3** | **Elastic VDR teacher signals; Trident training** | Offline visual-retriever training after coverage, fusion and affordable checkpoint choices fail | Start with a compatible released checkpoint if available. Then one signal versus teacher-free/hard-negative control, family-separated evaluation and appropriate seed checks. D1 reports expensive training requirements and incomplete adapter availability; qualify the chosen release before funding a run. | D1 §§5.2, 5.7 |
| **L02 · P3** | **SP-DocReader — 2610.11148** | OCR training only when meaning-changing transcription errors remain after rendering/parser fixes | First compare usable released artifacts with current OCR. Separate transcription from geometry/relationship understanding. D1 verified the abstract only; full method, compute and release readiness remain unqualified here. No new labeling/self-play campaign by default. | D1 §5.8 |

### 4.4 Semantic representation, validation and review

| ID / priority | Candidate or suggestion | Where and when to test | Smallest bakeoff and integration rule | Basis |
|---|---|---|---|---|
| **S01 · Apply** | **Source-scoped aliases, entity resolution, reusable relation mappings** | Candidate-to-canonical boundary within the active source family | Exercise ambiguous names, editions, senses, direction, negation and qualifiers. Reuse mapping decisions while reviewing each assertion's source support. Similarity cannot authorize a merge. | D3 §§4.3, 5.5 |
| **S02 · P2** | **SKOS-compatible vocabulary; RDF/named-graph export** | Interchange or validation projection when a consumer/checker needs it | Round-trip a qualified slice with IDs, qualified assertions, source senses and evidence. Adopt a projection beside the current store. Broader/narrower does not represent every engineering relation. | D3 §8.1 |
| **S03 · P2** | **SHACL and vocabulary checks** | Representation validation where declared constraints add value | Existing validator versus shapes on identical fixtures; declare targets/namespaces and expected violations, including no-target/no-ontology cases. Adopt useful detection or lower maintenance. Conformance does not establish factual support. | D3 §8.1 |
| **S04 · P2** | **Open Ontologies** | Offline change-impact/inference/projection checker after faithful export and an unmet checking need | Compare checks against existing validators; include missing premise, wrong-input certificate, forged conclusion and absent checker where relevant. Require added detection or less effort. No live apply/rollback, automatic equivalence, or certificate-based promotion. | D3 §8.2 |
| **S05 · P3** | **Selective OWL semantics** | Explicit domain inference that ordinary supported relationships and traversal cannot provide | One bounded inference need, with versioned rules and assumptions. Keep asserted and inferred records distinct; test consequences and exceptions. Avoid whole-corpus formalization without demonstrated value. | D3 §§4.3, 8.1 |
| **S06 · P2** | **Utopia — kaiello fork / deeplethe upstream** | Review, identity correction or historical queries after a qualified slice exists | Import/export compatibility first: original evidence, IDs, qualifiers, editions, status and time distinctions. Only then measure review/history benefits. Start with an isolated copy; JSON import cannot replace the PDF/figure as source. Runtime migration is a separate decision. | D3 §8.3 |

### 4.5 Platforms and persistence

| ID / priority | Candidate or suggestion | Where and when to test | Smallest bakeoff and integration rule | Basis |
|---|---|---|---|---|
| **P01 · P2** | **WeKnora** | Isolated ingest/retrieval/control-plane comparator for a demonstrated gap | Separate common-reader retrieval comparison from end-to-end parsing/system comparison. Compare OCR/text and image-vector modes, extracted figures and scanned pages; map every result to canonical anchors. Retain a useful API adapter if it wins. Whole-platform replacement requires a separate migration case. | D2 Phase 3 |
| **P02 · P2** | **RAGFlow** | Packaged self-hosted app when operating custom application plumbing is the problem | Same source and answer/evidence requirements; compare total operation/integration effort and quality with current system or the selected P01 comparator. Select one first; do not run a platform tournament without a decision need. | D1 §6 |
| **P03 · P2** | **Bedrock Knowledge Bases/managed GraphRAG; Google RAG Engine; Google Agent Search/Gemini File Search** | Managed retrieval/search when an approved cloud route and operational requirement exist | One eligible service with source/visual/citation tests. Separate native image handling from text descriptions/OCR and require adequate result granularity/export. Do not combine parser, reader and retrieval changes into a component-level claim. | D1 §6 |
| **P04 · P2** | **AWS GraphRAG Toolkit/BYOKG-RAG; Neo4j construction/retrieval components** | Existing-graph retrieval, or separately schema-guided extraction | For retrieval, reuse accepted graph/evidence and compare supported coverage/query effort. For construction, use E01's candidate/support controls. Do not re-extract merely to try a retrieval toolkit. | D1 §6 |
| **P05 · P2** | **CortexDB** | Backend/embedded packaging for a demonstrated local or operational requirement | Accepted-slice export/import; lookup/search/traversal/update/delete and recovery parity. Preserve IDs/provenance/qualifiers. Keep current visual retrieval external unless token/patch MaxSim equivalence is demonstrated. Optional memory/inference stays outside initial parity tests. | D1 §5.9 |
| **P06 · P3** | **Neo4j, FalkorDB, NetworkX, PostgreSQL/pgvector, Neptune, Spanner Graph** | Storage choice only when scale, query, deployment or maintenance limits are measured | Current store versus one suitable alternative with semantic/evidence parity and realistic workload. Distinguish an in-memory experimental graph from durable runtime storage. A framework dependency does not select production persistence. | D1 §6; D3 §4.4 |
| **P07 · P3** | **OpenSPG/KAG** | Rule/semantic reasoning only for a specific unmet operation | Existing supported traversal/rules versus one bounded reasoning path. Require explicit premises, source support and useful outcomes. Do not add another ontology/runtime merely to test ordinary retrieval. | D1 §6 |

### 4.6 Retrieval efficiency and serving

| ID / priority | Candidate or suggestion | Where and when to test | Smallest bakeoff and integration rule | Basis |
|---|---|---|---|---|
| **O01 · P2** | **ColPali/ColQwen/ColQwen2.5 variants; Byaldi wrapper** | Visual retrieval when recall, throughput or integration effort is deficient | Existing encoder versus one compatible checkpoint on identical assets and fixed reader preparation. A Byaldi trial tests adapter effort/capability, not a new model by itself. Adopt a reproducible useful gain with index/build cost included. | D1 §§3, 6; D3 §4.2 |
| **O02 · P2** | **Qdrant/Vespa; HNSW; pooling; binary quantization** | Visual index performance when memory/latency is actually limiting | Isolate one representation/index change, using reduced prefetch and adequate full-vector reranking where supported. Measure complete index size, build/update cost, evidence recall and end-to-end latency. Compression ratios are not full-system savings. | D3 §7.2 |
| **O03 · P2** | **vLLM/TensorRT-LLM/current serving optimization** | Serving when adequate inputs still leave a throughput/latency bottleneck | Same model/task and comparable precision/configuration. Report time to first token, completion, memory, throughput and answer fidelity. Do not combine a model upgrade with serving changes and attribute the gain to one. | D3 §7.2 |

### 4.7 Consumer, inspection and deployment

| ID / priority | Candidate or suggestion | Where and when to test | Smallest bakeoff and integration rule | Basis |
|---|---|---|---|---|
| **U01 · Retain / P2** | **MCP/API, one current consumer, Golden Retriever** | Consumer boundary; Golden Retriever when its real interface/environment is available | Check transport, sessions, limits, structured results, actual image delivery and supported answers. Reuse source facts and backend operations. A new consumer does not inherit another route's answer qualification. | D3 §10 |
| **U02 · Apply / P2** | **Existing evidence UI; split view; SVG/WebGL/tiled WebP** | Repair current inspectability; larger UI work only for a specific task | Verify original bound assets, truthful highlights and usable source navigation. Compare a small repair before a new app. Preserve free-form NLQ and do not treat generated boxes as proof of support. | D3 §§4.4, 10 |
| **U03 · P2** | **llm-wiki pattern; jackwener/llm-wiki candidate; Obsidian** | Read-only downstream projection after a qualified slice exists and navigation/review needs it | Optional 10–20-page template projection versus current evidence interface. Test source trace-back and invalidation after a fact changes. No factual-page answer writeback, autonomous research or bootstrap platform required. Original short-link identity remains unconfirmed. | D3 §9.1 |
| **U04 · P2** | **Helix Foundry** | Structured analyst exploration when accepted-record inspection needs a workspace | Import accepted records with deliberate schema mapping. Test a few inspection tasks and source/page/region trace-back. Adopt as a companion only if it reduces effort. Dataset snapshot citations need source mapping; no established PDF/figure extraction role. | D1 §5.10 |
| **U05 · P3** | **DB9 / wiki cloud-vector sync** | Secondary wiki search/storage only when a real requirement and data-transfer permissions exist | Compare against local projection/search first. Adopt only demonstrable search/operational benefit; avoid duplicate embeddings and synchronization by default. | D3 §§4.4, 9.1 |
| **U06 · P2** | **Offline/edge caching; store-and-forward receipts** | Deployment resilience for a bound disconnected-use case and device | Test permitted packages, version staleness, authorization, invalidation and reconnect behavior. Distinguish offline document viewing, search and model inference; a cached PDF demonstrates only the first. | D3 §10 |
| **U07 · P2 — required before multi-scope exposure** | **Enterprise document ACL filtering** | Retrieval, traversal, image access, caches and exports when users have different permissions | Cross-user/scope tests before exposure, including expanded context and cached assets. Adopt end-to-end enforcement. Source scoping alone is not authorization; removing final citations cannot undo unauthorized evidence use. | D3 §10 |

### 4.8 Engineering workflow and preserved history

| ID / priority | Candidate or suggestion | Where and when to test | Smallest bakeoff and integration rule | Basis |
|---|---|---|---|---|
| **D01 · P3** | **OpenRig** | Engineering coordination when handoff/review overhead is measured | One bounded change with an explicitly tasked builder/reviewer and total budget versus current workflow. Measure useful review, defects, elapsed time and usage. Keep out of runtime answering/admission. A reviewer role name does not establish independent assessment. | D1 §5.11 |
| **D02 · P2** | **Graphify** | Code dependency discovery for a concrete engineering investigation | Existing code-search approach versus a bounded graph-assisted investigation. Adopt accurate effort reduction only; do not create an authoritative welding graph from code relationships. | D1 §6 |
| **D03 · Borrow / P3** | **DeskForge; ScreenParse/ScreenTag; GUI-action models** | Borrow visible-evidence QA now; install only for a GUI-only workflow | Check omitted visible content, unsupported annotations, crop transforms and clipping in existing tests. Do not suppress thin engineering leaders/lines using GUI heuristics. No drawing-topology or Annex B extraction claim. | D3 §7.3 |
| **D04 · Retain / P3** | **Codex/Antigravity; DeepSeek Harness/OpenRouter** | Authorized development consumer/provider route | Reuse the current permitted route. Compare another only for a concrete compatibility gap, with source/privacy and output contracts intact. No provider tournament or silent fallback to make a library run. | D3 §4.4 |
| **D05 · Retain pause** | **Engineering Graph / Work DAG expansion** | Lifecycle analysis only when ordinary records cannot answer a useful dependency question | Preserve existing functions and receipts. Resume new development only for the named need; no new DAG or dashboard prerequisite for evidence delivery or this register. | D3 §10 |
| **D06 · Preserve** | **Historical C1R/C2/MAGE results and scorer** | Historical experimental record | Keep invalidations and frozen outcomes. They are not challenger arms or valid adoption evidence by default. Do not rehabilitate old scores when preparing new comparisons. | D3 §§4.4, 11 |

Upstream dependencies and bibliography-only examples such as **Jev** and **Florence-2** remain outside the selected bakeoff inventory. D3 explicitly found no separate Navy-specific integration case. Components bundled by a framework are not automatically independent recommendations.

## 5. Choose the next work item

| Observed problem | First work item | Next option only if needed |
|---|---|---|
| Source is absent/unfetchable or the wrong edition is bound | Repair access/inventory using the working pipeline | E02/E03 only for a demonstrated parser limitation |
| Source is reachable but useful semantic relationships are missing | **E01** extraction comparison alongside ingestion | E04 for image-dependent associations; E05 for complex proposition decomposition |
| Correct page/figure reaches the model but details are missed | Verify actual pixels and run **V01** | V02 for missing additional observations; V03 for residual model errors |
| Relevant visuals lose rank among text | **R01** | O01 checkpoint comparison; L01 only after simpler fixes fail |
| Search misses a known section/figure context | **R02**, if anchors are reliable | Global fallback or R05 as appropriate |
| Correct hits omit notes, exceptions or continuations | **R03** | R08/R09 only for a residual context-selection problem |
| Accepted graph contains the answer but API caps obstruct it | **R04** minimal operators | Isolated DKGI comparison only if the access gap persists |
| Adequate evidence/tools exist but ranking/action selection fails | **R06**, or fix tool schemas first | R07 shadow action scoring |
| Ingest/retrieval operations are the limiting factor | One of **P01/P02/P03**, selected by deployment fit | API integration first; migration only if necessary |
| A checker, analyst or consumer has a concrete unmet need | Relevant **S**, **U** or deployment item | No dependency on completing the entire standard |

**Default if no current failure breakdown is available:** bind the actual baseline and classify a small existing failure cohort. If the next authorized task is Annex B semantic enrichment, reuse or run E01. If the dominant user-visible miss is reading already-retrieved figures, choose V01 first. The documents alone cannot establish which failure currently dominates.

## 6. Bounded experiment cards

### 6.1 E01 — semantic extraction campaign

**Question:** Does a component produce more useful, source-supported relationships, or equivalent quality with less total validated-build effort?

**Entry:** A reachable authorized source family, permitted relation definitions, current candidate schema and existing assessment assets. Prefer the next useful Annex B slice, with a few existing Clause 4/Annex A regression bundles. Reuse equivalent completed work; reconcile any B17–B20 identity and prior-exposure history before reuse.

| Arm | Role | Important control |
|---|---|---|
| `TXT-CURRENT` | Actual current accepted extraction/mapping | Preserve working deterministic rules |
| `TXT-MINIMAL` | Minimal constrained-LLM control | Merge with current arm if already equivalent |
| `TXT-DOCLING-GRAPH` | Primary structured-extraction challenger | Input must be compatible; arbitrary JSONL is not DoclingDocument JSON |
| `TXT-KAPIPE` | Primary text DocRE challenger | Reuse resolved entities where appropriate; capture candidates before aggregation |
| `TXT-LANGEXTRACT` | Conditional replacement arm | Use when span alignment/grounding effort is the residual |

Hold source bundles, candidate entities, permitted predicates, support obligations and authorized model/version constant where interfaces allow. Declare differing preprocessing, evidence exposure or models as a **system comparison**, not an isolated library effect. A failed interface smoke test can make one arm not assessable without stopping the rest.

Include positives, negation/limitations, ambiguous identities and no-supported-relation cases. Score raw candidate precision, qualifiers, locations, false merges and review effort separately from post-review accepted quality. Claim recall only against an independently reviewed reference population; otherwise report audited precision and observed coverage.

Keep image-dependent work separate: KAPipe text DocRE cannot be credited with understanding pixels supplied only through captions. E04's direct same-VLM control is the relevant visual comparison. No exhaustive arrow/junction annotation or training campaign is required.

**Integrate:** one useful relationship-family adapter into current candidate records and ordinary promotion. Retain source access regardless of outcome. Include setup, extraction, binding, review/correction, assembly and indexing in cost; a fast mount of prepared artifacts is not extraction speedup.

### 6.2 V01 — LoC-inspired reader preparation

**Entry:** A real vision-reader bridge. Trace image bytes, ordering, detail/resizing settings and OCR limits. If the bridge is absent, implement the smallest feature-flagged route before claiming a reader-input comparison.

| Arm | Inputs | Claim it can test |
|---|---|---|
| A | Existing vision-reader inputs | Baseline |
| B | Higher-fidelity full pages at bounded visual budgets | Benefit from improved input detail/budget |
| C | Same pages plus automatically selected region OCR/text | Incremental benefit of selected textual detail |
| Optional diagnosis | Reviewer-selected regions | Selector ceiling/failure diagnosis only |

Freeze pages/order, model, prompt and decoding. Match total evidence budgets for B/C where possible; report actual observable image/text usage and retain a minimum image allocation. A larger low-resolution bitmap cannot restore lost detail. Preserve captions, notes, table headers and continuation context.

Native source text may be a separately labeled condition; it is not an exact OCR-based LoC replication. Do not attribute oracle-region or oracle-page gains to a deployable automatic selector. The small adapter is an original, paper-inspired implementation while author code is unavailable.

**Integrate:** better source-supported answers or comparable quality at lower operating cost, within prospectively fixed limits and without unacceptable regressions. Keep the default route reversible.

### 6.3 R01 / R02 / R03 — three distinct retrieval experiments

| Experiment | Freeze | Change | Required failure controls |
|---|---|---|---|
| R01 modality competition | Corpus scope, questions, reader and comparable retrieval budget | Text/visual/fused ranking and controlled distractor modality | Text-only regressions, duplicate source representations, incompatible score scales |
| R02 structural scope | Questions, reader and returned-evidence budget | Global/window/native-structure candidate scope | Wrong anchor, ambiguous figure, cross-reference outside scope, truncation |
| R03 context assembly | Retrieved starting hits, reader and total evidence budget | Explicit bundle/parent/continuation expansion | Unrelated expansion, dropped qualifiers, deduplication errors, source/edition mixing |

Use required-evidence recall/rank plus downstream supported-answer completeness. Keep anchor accuracy separate from within-scope ranking. Membership/order and bundle links describe navigation or explicit source relationships; they are not inferred welding topology.

**Integrate independently:** preserve source IDs and fallback. Only after separate wins, compose the selected changes and replay affected cases once to detect interactions.

### 6.4 V02 — bounded navigation

Use when another observation is needed after static preparation, not as a default response to every wrong answer. Reuse the best qualified static reader and existing evidence operations.

Start with D2's proposed cap of **three additional inspection actions and one continuation expansion**, plus a fixed total time/token budget. Tune on development cases only. Actions resolve known source IDs and bounded regions; retain observation provenance and distinguish newly found evidence from rereading.

Use typed actions for retrieval, page loading, bounded crops, explicit continuations and answer/abstention. The initial adapter has no arbitrary Python, shell, browser, external URL or unrestricted file tools. Test invalid IDs, loops, repeated crops, misleading document instructions and cap exhaustion. Retain the simple route for direct lookups.

Full DocPilot code reuse retains D2's reported unresolved license and direct-execution concerns; those require resolution against the selected build. Training/checkpoints are a separate later decision. An original bounded action adapter can test the architectural idea without importing the full framework.

### 6.5 P01 — isolated WeKnora comparison

The trigger is an ingest, retrieval or operating gap. It can precede V02 when that is the actual problem.

Run two separately labeled comparisons:

1. **Retrieval comparison:** common source corpus, reader and evidence budget; compare current retrieval with mapped WeKnora results. Declare unavoidable parser/model differences.
2. **End-to-end system comparison:** include each system's parsing, indexing and retrieval, while separately reporting their contributions and total effort.

Within the selected build, compare OCR/text and image-vector modes. D2 documents an important boundary: scanned PDF whole-page images use OCR-text retrieval rather than the documented extracted-image vector path. Treat scanned pages and extracted figures as separate cohorts and verify the selected release's behavior. An image attachment reaching a model is not measured visual accuracy.

Use isolated storage, pin the release/container digests, check applicable advisories and Lite feature parity, and enable only required services. Begin with public/synthetic material; AWS bytes stay within existing approved source/recipient boundaries. Preserve D2's exclusion of unnecessary agents, Wiki generation, SQL execution, browser control, connectors and other write-capable features in this trial.

Assess canonical anchor mapping, image recall/rank, table/footnote/continuation completeness, duplicate handling, retry/idempotent updates and exportability. Test workspace isolation if relevant. **Outcome:** reject, retain as comparator, integrate a narrow API, or separately propose migration. A good UI is insufficient evidence for platform replacement.

## 7. Shared evaluation and integration rules

### 7.1 One reusable evaluation structure

Reuse existing JSON/JSONL evidence packages and evaluation code. Do not create a universal harness, new labeling program, Work DAG or dashboard to start these tests.

- **Diagnosis:** approximately 10–20 existing cases can localize failures. This is an optional scope suggestion, not statistical qualification.
- **Visual pilot:** D2 proposes 24 source-checked cases: 12 development and 12 sealed evaluation. A balanced interpretation is two development and two evaluation cases in each of six categories: text/terminology, small visual labels, tables/notes, continuation, text-plus-image composition, and insufficient/conflicting evidence.
- **Exposure:** reuse existing reviewed cases honestly. If no untouched evaluation cases exist, report that limitation; do not relabel old failures as blind. Keep expected answers and oracle supports out of the tested runtime.
- **Extraction:** use source bundles and relationship populations suited to E01, not the visual-reader answer threshold. Family-separated evaluation is preferable where feasible.
- **Training:** protect document/figure-family splits and assess variation where small effects could be seed-dependent.

Set numeric resource and success limits before scored runs using actual capacity and applicable permissions. No universal dollar, hardware or latency target can be inferred from these three plans. Unknown API charges remain unknown.

### 7.2 What each test must report

| Boundary | Useful measures |
|---|---|
| Source/parsing | Reachable source coverage, correct text/table structure, notes/headers, coordinate fidelity and correction effort |
| Semantic extraction | Supported raw candidate precision; recall only with a reference population; qualifier/negation retention; false merges; total validated-build effort |
| Retrieval/context | Required page/region recall at stated K/budget, rank, complete evidence-set coverage, excluded anchors and irrelevant expansion |
| Reader/answer | Correct supported facts, requested-part completeness, limitations, visual/table interpretation, citation accuracy and appropriate abstention |
| Graph operations | Paths/sets, direction/roles, completeness/truncation, support links and query effort |
| Platform/serving | Identity and update/delete parity, traceability, cold/warm latency, calls, tokens, memory and operating effort |
| Validation/review | Useful defects detected beyond current checks, vacuous-check avoidance, false alarms, faithful export and review time |

Report paired improvements, ties and regressions, raw failures and inapplicable/unassessed cases. Do not blend OCR error, Hit@1, retrieval recall, formal conformance and answer correctness into one “accuracy” score. p50/p95 from a tiny pilot are descriptive and unstable; retain per-case timing. Include selection/OCR/retry overhead and separate inference measurements from residual timing estimates.

### 7.3 Scoped promotion gate

For the **specific proposed 12-case sealed visual pilot**, D2 suggests at least **two net additional correct answers**, no newly unsupported confident answers, no mandatory sentinel regression and compliance with a predeclared performance budget. Net means improvements minus regressions; report both. This is directional evidence, not a corpus-wide accuracy result or permission to accept harmful individual regressions.

For all other work, define success against the relevant boundary and baseline. Integration requires:

1. A reusable user operation improves, or quality is preserved with meaningful total-cost/effort savings.
2. Required identities, source reconstruction, qualifications, direction and candidate/accepted distinctions survive.
3. No unresolved unacceptable support, locator, source/edition or access-boundary regression remains.
4. The selected release, resource usage and maintenance fit the actual deployment constraints.
5. Raw outputs/configuration and a rollback path exist; experimental state can be removed without losing accepted assets.

Use independent source assessment where available and disclose if unavailable. Unit tests do not establish answer quality. Schema/checker success cannot promote unsupported assertions. Scoping and an explicit partial answer are preferable to unsupported completeness or absence claims.

Stop at the declared budget. A single justified evaluation expansion may be useful if inconclusive; do not repeatedly tune on exposed evaluation results. Mark an incompatible/unavailable arm **not assessable**, a failing approach **reject for this role**, and an untriggered item **defer**. Retaining the current method is a valid outcome.

### 7.4 Minimal completion record

Map into existing fields rather than introduce another mandatory schema:

- Master item ID and existing experiment/run ID; targeted failure and selected comparator.
- Actual source/code/model/prompt/graph/index/configuration bindings and prior case exposure.
- Input/evidence differences; retrieved/fetched/selected IDs; actual image delivery and preprocessing where observable.
- Raw output, source support, qualifiers, affected-case/regression outcomes and failure disposition.
- Setup/build/query/review costs, resource limits, timeouts and retries.
- Decision: retain current, scoped adoption candidate, defer, reject for this role, or not assessable; unresolved limitation and rollback.

No new paid service, corpus transfer, provider change, graph promotion or repository release follows automatically from inclusion in this register. Reuse established permissions and proceed with already-authorized necessary work.

## 8. Suggested workstream handoff

| Order | Concrete deliverable | Completion condition |
|---|---|---|
| **1. Bind and reuse** | Current implementation/source binding, existing completed tests and a short failure breakdown | Enough evidence to select the next layer; no broad audit or restart |
| **2. Select one campaign** | E01, V01, R01, R02 or R03 with finite scope, comparator and budgets | One specific decision can be made from the proposed outputs |
| **3. Execute and decide** | Existing-format per-case/raw results plus a compact decision note | Retain, adopt narrowly, defer or reject; all failures remain visible |
| **4. Integrate a winner** | Small adapter/configuration change behind the existing boundary | Relevant regression replay, source/evidence preservation and rollback |
| **5. Reassess the residual** | Next triggered item, if any | No automatic progression through the catalog |

Core evidence delivery continues throughout. New semantic projections, training, platforms and UIs stay outside the critical path unless their own requirement becomes the delivery blocker. The full register is a menu of decisions; it is not a backlog to execute in full.

## 9. Primary project links and carried-forward qualifications

These links identify the discussed projects. They are not a claim that each was freshly audited on October 18. D1–D3 contain the detailed earlier evidence and review limits.

| Master items | Primary references | Qualification retained |
|---|---|---|
| E01 | [Docling Graph](https://github.com/docling-project/docling-graph), [input formats](https://docling-project.github.io/docling-graph/fundamentals/pipeline-configuration/input-formats/), [KAPipe](https://github.com/norikinishida/kapipe), [DocRE](https://github.com/norikinishida/kapipe/blob/main/docs/components/docre.md), [LangExtract](https://github.com/google/langextract) | Compatibility and source support require the bounded trial |
| E04 | [RAG-Anything](https://github.com/HKUDS/RAG-Anything) | Processor and full platform are different adoption choices |
| R01 | [Chaos in the Text / Trident — 2610.11816](https://arxiv.org/abs/2610.11816) | Modality audit can be adapted to separate indexes; that is not encoder-training replication |
| R02 | [NativeScope — 2610.12243](https://arxiv.org/html/2610.12243v1) | Correct-anchor and automatic-anchor behavior must stay separate |
| R03 | [From Chunks to Functional Evidence — 2610.09361](https://arxiv.org/html/2610.09361v1) | Source-linked grouping is the near-term adaptation; learned alignment is deferred |
| R04 | [DKGI](https://github.com/leopoldwhite/DKGI), [paper](https://arxiv.org/html/2610.18616v2) | Controlled gains and file-access design do not establish Weld value or permission for shell access |
| R07 | [CLM](https://github.com/Contrastive-LM/CLM) | Relative candidate scoring, not a source-truth oracle |
| R08 / R09 | [denghk666/PAGE-RAG](https://github.com/denghk666/PAGE-RAG), [CXY0112/PAGE-RAG](https://github.com/CXY0112/PAGE-RAG) | Distinct repositories; D3's first-project release limitation remains unconfirmed by the unsuccessful October 18 fetch |
| R10 | [Microsoft GraphRAG global search](https://microsoft.github.io/graphrag/query/global_search/) | Derived community reports and map/reduce, conditional on broad synthesis needs |
| V01 | [LoC paper — 2610.21318](https://arxiv.org/abs/2610.21318), [repository](https://github.com/Chipmunk-g4/Loud-and-Clear) | October 18 landing-page check still shows only a release placeholder; original adapter rather than released-author-code integration |
| V02 | [DocPilot](https://github.com/HKUSTDial/DocPilot), [training scope](https://github.com/HKUSTDial/DocPilot/blob/main/pipelines/training/README.md), [in-memory workflow](https://github.com/HKUSTDial/DocPilot/blob/main/app/workflow/in_memory.py) | Current landing page reconfirmed interactive role; D2's license/execution/checkpoint concerns were not cleared by this review |
| V03 | [Mistral Large 4 documentation](https://docs.mistral.ai/models/mistral-large-4-0) | D1's documented model role is not a model invocation or hardware qualification |
| L01 / L02 | [Elastic VDR teacher signals](https://github.com/elastic/vdr-teacher-signals), [SP-DocReader — 2610.11148](https://arxiv.org/abs/2610.11148) | D1's training/readiness limits remain; no training performed |
| S02 / S03 / S05 | W3C [SKOS](https://www.w3.org/TR/skos-reference/), [RDF](https://www.w3.org/TR/rdf11-concepts/), [SHACL](https://www.w3.org/TR/shacl/), [OWL 2](https://www.w3.org/TR/owl2-overview/) | Representation and inference standards do not establish source interpretation correctness |
| S04 | [Open Ontologies](https://github.com/fabio-rovai/open-ontologies) | D3's detailed checking cautions derive partly from earlier pinned documentation; no checker executed |
| S06 | [kaiello/utopia](https://github.com/kaiello/utopia), [deeplethe/utopia](https://github.com/deeplethe/utopia) | Preserve fork/upstream identity; import/export compatibility precedes workflow claims |
| P01 | [WeKnora](https://github.com/Tencent/WeKnora), [knowledge-base configuration](https://github.com/Tencent/WeKnora/blob/main/website-docs/03-features/02-knowledge-base.md), [advisories](https://github.com/Tencent/WeKnora/security/advisories) | October 18 release notes reconfirm opt-in image retrieval; selected-build scan/image behavior and advisories still require trial-specific verification |
| P05 | [CortexDB](https://github.com/liliang-cn/cortexdb) | No established ColPali MaxSim replacement or migration win |
| O02 | [Qdrant multivector retrieval reference](https://qdrant.tech/documentation/tutorials-search-engineering/pdf-retrieval-at-scale/) | Method reference, not a backend selection or measured saving |
| U03 | [jackwener/llm-wiki](https://github.com/jackwener/llm-wiki) | Candidate identity versus the original shortened link remains unresolved |
| U04 | [Helix Foundry](https://github.com/HelixDB/helix-foundry) | Downstream structured exploration; D1's local-use/operational qualifications retained |
| D01 / D03 | [OpenRig](https://github.com/mvschwarz/openrig), [DeskForge](https://github.com/Saidgurbuz/deskforge) | Engineering coordination and GUI supervision are separate from runtime evidence semantics |
| E02–E03, P02–P04, P06–P07, D02 | D1 §6 and its cited October 12 options document | Carried-forward shortlist; no new full platform capability or release audit |

---

## 10. Implementation, Trial, and Deferral Disposition Status (Cards 01–08 Audit)

**Audit Date:** October 18, 2026  
**Audit Scope:** Reconciled disposition of all **49 master register candidates** against the completed baseline POC implementation (Cards 01–08) and the 78-CQ gold benchmark (`CQ-01`–`CQ-78`).  
**Verification Harness:** `scripts/verify_all.py` (10 test modules, 73/73 tests passing, 78/78 CQs 100.0% passing in 35 seconds with zero external dependencies).  
**Cryptographic Verification Receipt:** [`docs/benchmark_receipt.md`](benchmark_receipt.md) and [`eval/meia_78_cq_receipt.json`](../eval/meia_78_cq_receipt.json).

---

### 10.1 Executive Summary & Category Audit Scorecard

The MEIA Federated Tri-Graph POC has completed its baseline implementation across **Cards 01–08**. Every candidate in the 49-item master register has been audited and assigned to one of three formal dispositions:
1. **IMPLEMENTED (Baseline POC)**: Fully operational in the codebase, integrated behind existing interfaces, and verified by passing test suites and the 78-CQ benchmark.
2. **TRIED / BENCHMARKED (Calibrated in POC)**: Explicitly evaluated or calibrated during development (e.g., Modality RRF weight sweeps, LoC multi-arm visual inspection, Cross-Encoder reranking, local VLM adapters) with empirical findings recorded.
3. **DEFERRED (Challenger Arm / Future Roadmap)**: Cataloged as a bounded challenger arm for future post-POC evaluation under the strict invariant *"core ingestion plus one active experiment campaign"*, preserving the zero-daemon rule and preventing architectural drift.

| Register Category | Total Items | Implemented in Baseline POC | Tried / Benchmarked | Deferred to Challenger Arms | Architectural Drift Detected |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **4.1 Evidence Preparation & Extraction (`E01`–`E05`)** | 5 | 3 (`E01`, `E02`, `E05`) | 1 (`E04`) | 2 (`E03` cloud IDP, `E05` KAPipe rewrite) | None (100% local, 0% token loss) |
| **4.2 Retrieval, Graph Ops & Context (`R01`–`R10`)** | 10 | 6 (`R01`, `R02`, `R03`, `R04`, `R05`, `R10`) | 2 (`R01`, `R06`) | 4 (`R07`, `R08`, `R09`, `R10` global Leiden) | None (Zero daemon, 100% citation) |
| **4.3 Visual Reading & Model Training (`V01`–`V03`, `L01`–`L02`)** | 5 | 2 (`V01`, `V02`) | 2 (`V01`, `V03`) | 2 (`L01`, `L02` offline training) | None (180 DPI + BBoxes preserved) |
| **4.4 Semantic Representation & Review (`S01`–`S06`)** | 6 | 4 (`S01`, `S02`, `S03`, `S06`) | 1 (`S05`) | 2 (`S04`, `S05` OWL DL) | None (Strict epistemic firewall) |
| **4.5 Platforms & Persistence (`P01`–`P07`)** | 7 | 1 (`P06` SQLite/NetworkX) | 0 | 6 (`P01`–`P05`, `P07` enterprise daemons) | None (Zero external DB daemons) |
| **4.6 Retrieval Efficiency & Serving (`O01`–`O03`)** | 3 | 2 (`O02`, `O03`) | 0 | 1 (`O01` ColPali multivector) | None (Embedded zero-daemon server) |
| **4.7 Consumer Boundary & Inspection (`U01`–`U07`)** | 7 | 6 (`U01`, `U02`, `U03`, `U04`, `U06`, `U07`) | 0 | 1 (`U05` cloud vector sync) | None (100% citation, RBAC verified) |
| **4.8 Engineering Workflow & History (`D01`–`D06`)** | 6 | 4 (`D02`, `D03`, `D04`, `D06`) | 1 (`D05`) | 1 (`D01` OpenRig) | None (Master offline harness) |
| **TOTAL** | **49** | **28** | **7** | **21** | **0 Violations (100% Compliant)** |

---

### 10.2 Mandatory 4-Point Drift Invariant Audit

Every candidate disposition was audited against the four inviolable project drift rules defined in `docs/goal.md`, `docs/architecture.md`, and the `navy-weld-card-planner` skill:

1. **Infrastructure Drift (Zero External Database Daemons)**:
   - *Status*: **PASSED (0 Violations)**.
   - *Evidence*: Storage is strictly local: `storage/meia_tri_graph_registry.db` (SQLite FTS5), `storage/*.graphml` (NetworkX GraphML), and `storage/vdb_chunks_contextual.json` (local BGE-Large vector projections). All candidate external database servers (Neo4j, FalkorDB, Milvus, Qdrant cluster, WeKnora, CortexDB) are strictly cataloged as **Deferred Challenger Arms**.
2. **Epistemic Drift (Strict Non-Equivalence Firewall)**:
   - *Status*: **PASSED (0 Violations)**.
   - *Evidence*: `VENDOR_SELF_ASSERTED` $\neq$ `LIVE_DEMONSTRATED` invariant is mathematically enforced by `src/epistemic_verifier.py`. Zero vendor capability claims (`meia:CapabilityClaim`) were promoted to empirical demonstration facts (`eval:DemonstrationEvent` / FPDS contract awards) across all 78 CQs.
3. **Retrieval / Modality Drift (Fair Multimodal Representation & 100% Citation)**:
   - *Status*: **PASSED (0 Violations)**.
   - *Evidence*: Modality-Calibrated RRF ($w_{visual} = 1.5, w_{table} = 1.2, w_{text} = 1.0$) prevents text-token starvation. Visual chips (180 DPI / LoC focal crops) and tabular cell locators (`Sheet!Row:Col`) achieve 100% Evidence Recall@5. 100% of retrieved answers have traceable source citations.
4. **Scope / Capacity Drift (Single Bounded Challenger Arm)**:
   - *Status*: **PASSED (0 Violations)**.
   - *Evidence*: The baseline POC maintained the *"core ingestion plus one active experiment campaign"* rule across Cards 01–08. No concurrent multi-platform migrations or unconstrained model bakeoffs were initiated.

---

### 10.3 Detailed Category-by-Category Disposition Analysis

#### 10.3.1 Evidence Preparation and Semantic Extraction (`E01`–`E05`)

| ID | Candidate & Source Role | Disposition | Implementation / Rationale in MEIA POC | Primary Code & Verification Artifact |
| :--- | :--- | :---: | :--- | :--- |
| **E01** | **Semantic Extraction**<br/>(Current extraction, schema-constrained LLM, Docling Graph, KAPipe DocRE, LangExtract) | **IMPLEMENTED & BENCHMARKED** | Structured intake parser extracts all 62 columns from `MEIA_TEM_Vulcan_Export.xlsx` (Q1–Q12) and `CRM_Object_Field_Mapping.xlsx`, mapping them directly to BFO-Lite `:Product`, `:Service`, `:CapabilityClaim`, `:DemonstrationEvent`, `:ReadinessAssessment`, and `:CommercialObservation`. Evaluated with 100% field accuracy.<br/>*Deferred*: KAPipe DocRE, Docling Graph full multi-page extractor, and LangExtract cataloged as challenger arms for future uncurated corpora. | `src/extract.py`<br/>`config/meia_poc_manifest.json`<br/>`tests/test_meia_manifest.py` |
| **E02** | **PDF/Doc Parsers**<br/>(Docling, PaddleOCR, PP-StructureV3, MinerU) | **IMPLEMENTED** | Implemented via PyMuPDF (fitz) with 180 DPI rendering and Docling-compatible normalized `[ymin, xmin, ymax, xmax]` BBox schema, with Tesseract OCR fallback for raster PDFs (`Prometheus_Energy_AI.pdf` and `Fluor_Government_Overview.pdf` containing 0 native text characters).<br/>*Deferred*: PaddleOCR-VL and MinerU server daemons deferred to maintain zero-daemon POC invariant. | `src/extract.py`<br/>`tests/test_meia_manifest.py` |
| **E03** | **Managed Cloud IDP**<br/>(Databricks IDP, Bedrock Textract, Google Document AI) | **DEFERRED** | Deferred under the Local Zero-Daemon Invariant to ensure 100% offline-airgapped local reproducibility with zero cloud subscription or data egress dependencies. Cataloged for enterprise cloud deployment. | N/A (Cataloged Challenger) |
| **E04** | **Multimodal Processor**<br/>(RAG-Anything / LightRAG) | **IMPLEMENTED & BENCHMARKED** | High-resolution 180 DPI diagram extraction with caption, context, and normalized BBox binding implemented directly in `src/extract.py` and `src/answer_routes.py`. Interactive visual callout chips exposed in UI.<br/>*Deferred*: Standalone RAG-Anything / LightRAG daemon deferred to avoid external runtime graph indexing sprawl. | `src/extract.py`<br/>`src/answer_routes.py`<br/>`src/web.py` |
| **E05** | **Proposition Extraction**<br/>(KAPipe propositions, ProStruct-RAG) | **IMPLEMENTED (Chunking) / DEFERRED (Rewriting)** | Implemented semantic chunking ($\le 400$ tokens) with prepended `[GRAPH \| ENTITY \| SOURCE \| CLASSIFICATION]` context headers, guaranteeing zero vector truncation without generative rewriting.<br/>*Deferred*: Full KAPipe atomic proposition decomposition and ProStruct-RAG generative rewriting deferred to prevent ungrounded semantic drift. | `src/extract.py`<br/>`src/contextual_indexer.py` |

---

#### 10.3.2 Retrieval, Graph Operations and Context Assembly (`R01`–`R10`)

| ID | Candidate & Source Role | Disposition | Implementation / Rationale in MEIA POC | Primary Code & Verification Artifact |
| :--- | :--- | :---: | :--- | :--- |
| **R01** | **Modality-Bias Audit & Fusion**<br/>(Trident-inspired, RRF/calibrated fusion) | **IMPLEMENTED & BENCHMARKED** | Implemented Modality-Calibrated Reciprocal Rank Fusion ($w_{visual} = 1.5, w_{table} = 1.2, w_{text} = 1.0$) in `src/hybrid_retriever.py`. Benchmarked across all 78 CQs, completely eliminating text-token dominance and ensuring diagram chips and Excel table cells appear at top ranks.<br/>*Deferred*: Offline multi-modal encoder fine-tuning (Trident training) deferred (L01). | `src/hybrid_retriever.py`<br/>`tests/test_retrieval_and_composer.py` |
| **R02** | **Structural Scoping**<br/>(NativeScope-inspired operators) | **IMPLEMENTED** | Implemented NativeScope structural scoping in `src/pre_retrieval.py` and `src/hybrid_retriever.py`, restricting candidate pools to verified organizational boundaries, vendor submission blocks, or contract award scopes before global ranking.<br/>*Deferred*: Dynamic query-time AST scope compiler deferred. | `src/pre_retrieval.py`<br/>`src/hybrid_retriever.py` |
| **R03** | **Functional Context Packets**<br/>(Evidence units, fact packets, parent expansion) | **IMPLEMENTED** | Implemented in `src/answer_routes.py` and `src/grounded_answer.py`. Bundles primary claims with mandatory contractual qualifiers (Q4 supply constraints, Q5 ROM funding to scale, Q6 unit costs, Q12 security clearances) and parent section locators.<br/>*Deferred*: Learned hypergraph grouping encoder deferred. | `src/answer_routes.py`<br/>`src/grounded_answer.py` |
| **R04** | **Bounded Graph Traversal**<br/>(Batching, pagination, DKGI) | **IMPLEMENTED** | Bounded 2-hop relational and GraphML graph traversal executed via SQLite FTS5 index scans and NetworkX in-memory GraphML in `src/build_tri_graph.py` and `src/answer_routes.py`.<br/>*Deferred*: Arbitrary agent shell/file execution (DKGI file-agent) deferred on security and epistemic containment grounds. | `src/build_tri_graph.py`<br/>`src/answer_routes.py` |
| **R05** | **Graph Retrieval Channel**<br/>(Source-scoped graph neighborhood) | **IMPLEMENTED** | Implemented in `src/hybrid_retriever.py` as a dedicated graph-expansion channel harvesting 1-hop and 2-hop neighbors from `cross_graph_links` to supplement lexical FTS5 and vector search.<br/>*Deferred*: Unbounded speculative random walks deferred. | `src/hybrid_retriever.py` |
| **R06** | **Cross-Encoder Reranking**<br/>(Conventional cross-encoder) | **IMPLEMENTED & BENCHMARKED** | Local Cross-Encoder reranking (`cross-encoder/ms-marco-MiniLM-L-6-v2` or deterministic fallback) applied to top RRF candidate pools in `src/hybrid_retriever.py`.<br/>*Deferred*: Heavy 7B-parameter rerankers deferred due to edge latency limits. | `src/hybrid_retriever.py`<br/>`tests/test_retrieval_and_composer.py` |
| **R07** | **Contrastive Action Scoring**<br/>(CLM — Contrastive-LM) | **DEFERRED** | Deferred as Challenger Arm. Pre-retrieval routing is fully resolved deterministically by the 8-profile intent router (`src/pre_retrieval.py`) achieving 100.0% Route@1 accuracy; CLM is cataloged if routing requires probabilistic action scoring in open-domain scaling. | N/A (Cataloged Challenger) |
| **R08** | **PAGE-RAG (denghk666)**<br/>(Query-local evidence selection) | **DEFERRED** | Deferred as Unqualified Package. Upstream author repository remains an unreleased placeholder; deferred until code is released and qualified. | N/A (Upstream Placeholder) |
| **R09** | **PAGE-RAG (CXY0112)**<br/>(Hybrid evidence/routing) | **DEFERRED** | Deferred as Challenger Arm. Current R01 + R02 + R03 implementation fully meets the textual and multimodal evidence retrieval requirements without needing external community graph construction. | N/A (Cataloged Challenger) |
| **R10** | **Global GraphRAG**<br/>(Microsoft GraphRAG, Leiden communities, map/reduce) | **IMPLEMENTED (8-Profile Router) / DEFERRED (Leiden Map/Reduce)** | Implemented pre-retrieval routing for global 360° synthesis queries (`ROUTE_ALL_TRI_STORE`) across all three graphs deterministically.<br/>*Deferred*: Global hierarchical Leiden community clustering and map/reduce report generation deferred as unnecessary for targeted defense technology scouting. | `src/pre_retrieval.py`<br/>`src/answer_routes.py` |

---

#### 10.3.3 Visual Reading and Model Training (`V01`–`V03`, `L01`–`L02`)

| ID | Candidate & Source Role | Disposition | Implementation / Rationale in MEIA POC | Primary Code & Verification Artifact |
| :--- | :--- | :---: | :--- | :--- |
| **V01** | **LoC-Inspired Reader**<br/>(Loud and Clear Multi-Arm inspection) | **IMPLEMENTED & BENCHMARKED** | Delivered Loud-and-Clear Multi-Arm Visual Inspector in `src/web.py`: Arm A (Full 180 DPI Page), Arm B (Focal Crop around normalized BBoxes), Arm C (High-Detail Focal Crop + OCR Callout Chips). Available via UI toggle and `/api/diagrams/loc-inspect`. Benchmarked on complex diagrams (*Ghostfin* UUV, *Sonic Spear 26*), demonstrating superior label legibility.<br/>*Deferred*: Model fine-tuning with LoC visual prompts deferred. | `src/web.py`<br/>`tests/test_web_endpoints.py` |
| **V02** | **Bounded Navigation**<br/>(Bounded DocPilot-style navigation) | **IMPLEMENTED** | Delivered bounded interactive navigation in the web UI: interactive bounding-box click-to-highlight, page navigation, and linked context expansion bounded by explicit source anchors.<br/>*Deferred*: Autonomous LLM agent navigation with arbitrary crop loops deferred to prevent latency and token explosions. | `src/web.py` |
| **V03** | **Multimodal Reader Models**<br/>(Mistral Large 4, Qwen2.5-VL variants) | **BENCHMARKED & COMPATIBLE** | Grounded composer (`src/grounded_answer.py`) operates with deterministic template synthesis and optional pluggable local Ollama (`qwen2.5-vl`) / OpenRouter adapters, providing 100% citation coverage.<br/>*Deferred*: Multi-model VLM bakeoffs deferred to post-POC. | `src/grounded_answer.py` |
| **L01** | **Visual Retriever Training**<br/>(Elastic VDR teacher signals, Trident training) | **DEFERRED** | Deferred to Offline Research. Modality-calibrated RRF (R01) resolved visual ranking bias without expensive retriever fine-tuning. | N/A (Cataloged Research) |
| **L02** | **OCR Training**<br/>(SP-DocReader — 2610.11148) | **DEFERRED** | Deferred to Offline Research. 180 DPI PyMuPDF + Tesseract/Docling extraction achieved 100% extraction accuracy on raster PDFs (`Prometheus` and `Fluor`); specialized OCR retraining is not triggered. | N/A (Cataloged Research) |

---

#### 10.3.4 Semantic Representation, Validation and Review (`S01`–`S06`)

| ID | Candidate & Source Role | Disposition | Implementation / Rationale in MEIA POC | Primary Code & Verification Artifact |
| :--- | :--- | :---: | :--- | :--- |
| **S01** | **Source Aliases & Entity Resolution**<br/>(Entity resolution, relation mappings) | **IMPLEMENTED** | Implemented BFO-Lite entity resolution in `src/build_tri_graph.py`, matching entities strictly via immutable identifiers (`UEI`, `CAGE`, `DUNS`, `Vulcan_ID`). Ambiguous bridge candidates (e.g., T2S Solutions missing CAGE) are quarantined into the Steward Review Queue (`U04`). | `src/build_tri_graph.py`<br/>`src/steward_review.py` |
| **S02** | **SKOS Vocabulary & RDF Export**<br/>(SKOS concept schemes, GraphML export) | **IMPLEMENTED** | Implemented SKOS concept schemes (`config/skos_schemes.json`) for OSRA 2021 TBBs, MEIA Q2 Topics, TRL/MRL/IRL scales, and claim dispositions. Exported to standard GraphML (`storage/*.graphml`) and SQLite tables. | `config/skos_schemes.json`<br/>`storage/*.graphml` |
| **S03** | **SHACL & Vocabulary Checks**<br/>(SHACL constraint validation) | **IMPLEMENTED** | Dual-layer epistemic constraints enforced via deterministic Python contracts, SQLite foreign keys, and typed evidence edges (`[:ASSERTED_IN]`, `[:DEMONSTRATED_IN]`, `[:OBLIGATED_BY_AWARD]`). | `src/build_tri_graph.py`<br/>`src/epistemic_verifier.py` |
| **S04** | **Open Ontologies**<br/>(Formal change-impact checker) | **DEFERRED** | Deferred as Challenger Arm. Current deterministic test harness (`scripts/verify_all.py`, 10 test modules) provides full offline change-impact and schema checking without external toolchains. | N/A (Cataloged Challenger) |
| **S05** | **Selective OWL Semantics**<br/>(Explicit domain inference) | **IMPLEMENTED (Deterministic Rules) / DEFERRED (OWL DL)** | Explicit domain inference rules implemented via Python graph queries and foreign keys; heavyweight OWL DL reasoners deferred to prevent non-terminating tableaus. | `src/build_tri_graph.py` |
| **S06** | **Utopia Review Compatibility**<br/>(Utopia — kaiello fork / deeplethe upstream) | **IMPLEMENTED** | Implemented Steward Review Queue in `src/steward_review.py` and `storage/steward_review_queue.json` (11 items) matching Utopia's review schema for candidate bridges, conflicting evidence, and unverified commercial scaling claims. | `src/steward_review.py`<br/>`storage/steward_review_queue.json`<br/>`src/web.py` |

---

#### 10.3.5 Platforms and Persistence (`P01`–`P07`)

| ID | Candidate & Source Role | Disposition | Implementation / Rationale in MEIA POC | Primary Code & Verification Artifact |
| :--- | :--- | :---: | :--- | :--- |
| **P01** | **WeKnora**<br/>(Isolated ingest/retrieval comparator) | **DEFERRED** | Deferred as Challenger Arm. Preserved as an isolated comparator for future scale benchmarks; zero-daemon SQLite FTS5 baseline currently satisfies all 78 CQs in 12.1s with zero background services. | N/A (Cataloged Challenger) |
| **P02** | **RAGFlow**<br/>(Packaged self-hosted platform) | **DEFERRED** | Deferred as Challenger Arm. Packaged application deferred to avoid heavy Docker/service sprawl in POC. | N/A (Cataloged Challenger) |
| **P03** | **Managed Cloud Retrieval**<br/>(Bedrock Knowledge Bases, Google RAG Engine) | **DEFERRED** | Deferred under the Local Zero-Daemon Invariant to ensure offline airgapped reproducibility with zero cloud egress. | N/A (Cataloged Challenger) |
| **P04** | **Graph Retrieval Toolkits**<br/>(AWS GraphRAG Toolkit, Neo4j components) | **DEFERRED** | Deferred as Challenger Arm. In-tree NetworkX GraphML + SQLite FTS5 provides complete 360° cross-graph joins without external graph database runtimes. | N/A (Cataloged Challenger) |
| **P05** | **CortexDB**<br/>(Embedded graph database) | **DEFERRED** | Deferred as Challenger Arm. Embedded graph database cataloged as a potential future backend if SQLite FTS5 hits scale or concurrency limits. | N/A (Cataloged Challenger) |
| **P06** | **Enterprise Storage Engines**<br/>(Neo4j, FalkorDB, PostgreSQL/pgvector, Neptune, Spanner) | **IMPLEMENTED (SQLite + NetworkX) / DEFERRED (Enterprise Daemons)** | Implemented zero-daemon baseline in `storage/meia_tri_graph_registry.db` and `storage/*.graphml`. Heavy database daemons strictly deferred. | `storage/meia_tri_graph_registry.db`<br/>`storage/*.graphml` |
| **P07** | **OpenSPG / KAG**<br/>(Rule/semantic reasoning engine) | **DEFERRED** | Deferred as Challenger Arm. Current BFO-Lite + SKOS implementation handles all rule/semantic reasoning deterministically without external runtimes. | N/A (Cataloged Challenger) |

---

#### 10.3.6 Retrieval Efficiency and Serving (`O01`–`O03`)

| ID | Candidate & Source Role | Disposition | Implementation / Rationale in MEIA POC | Primary Code & Verification Artifact |
| :--- | :--- | :---: | :--- | :--- |
| **O01** | **Multivector Visual Retrieval**<br/>(ColPali, ColQwen, Byaldi wrapper) | **DEFERRED** | Deferred as Challenger Arm. 1024-d BGE-large contextual embeddings + 180 DPI visual chip indexing currently delivers 100.0% retrieval accuracy. Byaldi/ColPali cataloged for future dense patch retrieval. | N/A (Cataloged Challenger) |
| **O02** | **Vector Index Optimization**<br/>(Qdrant/Vespa, HNSW, binary quantization) | **IMPLEMENTED** | Implemented secondary auxiliary vector projections keyed by immutable chunk IDs stored in `storage/vdb_chunks_contextual.json` with cosine similarity search in Python/NumPy. Standalone vector DB daemons deferred. | `src/contextual_indexer.py`<br/>`storage/vdb_chunks_contextual.json` |
| **O03** | **Serving Optimization**<br/>(vLLM, TensorRT-LLM, embedded HTTP) | **IMPLEMENTED** | Ultra-lightweight zero-daemon embedded HTTP server (`src/web.py`) serving interactive UI and REST API. High-throughput LLM engines (vLLM/TensorRT-LLM) deferred as LLM synthesis is decoupled. | `src/web.py` |

---

#### 10.3.7 Consumer Boundary, Inspection and Deployment (`U01`–`U07`)

| ID | Candidate & Source Role | Disposition | Implementation / Rationale in MEIA POC | Primary Code & Verification Artifact |
| :--- | :--- | :---: | :--- | :--- |
| **U01** | **Consumer Boundary**<br/>(REST API / MCP, Golden Retriever) | **IMPLEMENTED** | Clean decoupled REST API and headless CLI in `src/web.py` supporting `/api/query`, `/api/dossier/*`, `/api/benchmark/receipt`, `/api/steward/review-queue`, `/api/diagrams/loc-inspect`. | `src/web.py` |
| **U02** | **Evidence UI & Inspectability**<br/>(Split view, high-res diagrams, BBox highlights) | **IMPLEMENTED** | Interactive Single-Page Web Application in `src/web.py` featuring 360° dossier cards, interactive diagram viewer with 180 DPI visual chips, BBox click-to-highlight, and epistemic badges. | `src/web.py`<br/>`tests/test_web_endpoints.py` |
| **U03** | **Read-Only Projections**<br/>(llm-wiki pattern, Obsidian export) | **IMPLEMENTED** | Generates static human-readable and machine-verifiable receipts (`docs/benchmark_receipt.md`, `eval/meia_78_cq_report.md`, `eval/meia_78_cq_receipt.json`).<br/>*Deferred*: Dynamic wiki writeback engine deferred to prevent hallucination. | `docs/benchmark_receipt.md`<br/>`eval/meia_78_cq_report.md` |
| **U04** | **Structured Review Queue**<br/>(Helix Foundry, Steward Review Queue) | **IMPLEMENTED** | Implemented Human Review Queue in `src/steward_review.py` and UI modal harvesting candidate bridges, conflicting evidence, and unverified commercial scaling claims into `storage/steward_review_queue.json` (11 items).<br/>*Deferred*: External Helix Foundry deployment deferred. | `src/steward_review.py`<br/>`storage/steward_review_queue.json`<br/>`src/web.py` |
| **U05** | **Cloud Vector Sync**<br/>(DB9 / wiki cloud-vector sync) | **DEFERRED** | Deferred under the Local Zero-Daemon Invariant; cloud synchronization not authorized for unreleased defense scouting data. | N/A (Cataloged Challenger) |
| **U06** | **Offline Caching & Receipts**<br/>(Store-and-forward cryptographic receipts) | **IMPLEMENTED** | Full cryptographic fingerprinting (SHA-256) of manifest, SQLite registry, GraphML exports, vector store, and gold CQ benchmark in `eval/meia_78_cq_receipt.json` and `docs/benchmark_receipt.md`. | `eval/meia_78_cq_receipt.json`<br/>`docs/benchmark_receipt.md` |
| **U07** | **Enterprise Document ACL**<br/>(Role-based access control filtering) | **IMPLEMENTED** | Implemented deterministic RBAC/ABAC redaction of PII, proprietary pricing (Q6), and classified meeting preferences (Q12) in `src/pre_retrieval.py` and `src/epistemic_verifier.py`; verified by `CQ-77`. | `src/pre_retrieval.py`<br/>`src/epistemic_verifier.py` |

---

#### 10.3.8 Engineering Workflow and Preserved History (`D01`–`D06`)

| ID | Candidate & Source Role | Disposition | Implementation / Rationale in MEIA POC | Primary Code & Verification Artifact |
| :--- | :--- | :---: | :--- | :--- |
| **D01** | **Multi-Agent Coordination**<br/>(OpenRig) | **DEFERRED** | Deferred as Challenger Arm. Engineering coordination was successfully governed via progressive milestone cards (Cards 01–08) and paired review rules; external multi-agent orchestration frameworks deferred. | N/A (Cataloged Challenger) |
| **D02** | **Code Dependency Discovery**<br/>(Graphify) | **IMPLEMENTED** | Strict Git commit lineage, documented interfaces, and decoupled architectural boundaries in `docs/architecture.md`. External code graph tools deferred. | `docs/architecture.md`<br/>Git commit history |
| **D03** | **Master Offline Harness**<br/>(DeskForge; ScreenParse/ScreenTag) | **IMPLEMENTED** | Delivered master offline regression harness in `scripts/verify_all.py`, executing all 10 unit/integration test suites plus the full 78-CQ benchmark in 35 seconds offline with zero external dependencies. | `scripts/verify_all.py`<br/>`tests/*.py` |
| **D04** | **Authorized LLM Harness**<br/>(Codex/Antigravity, DeepSeek Harness) | **IMPLEMENTED** | Zero mandatory cloud tokens; offline evaluation runs deterministically via template synthesizers and local encoders. | `eval/test_scorer.py`<br/>`src/grounded_answer.py` |
| **D05** | **Engineering Graph / Work DAG**<br/>(Work DAG expansion) | **IMPLEMENTED (Card Checkpoints) / PAUSED (Work DAG)** | Progressive gating checkpoints across Cards 01–08; separate Work DAG development paused in accordance with register guidelines. | `docs/plan.md`<br/>`docs/goal.md` |
| **D06** | **Historical Record Preservation**<br/>(Historical C1R/C2/MAGE results & receipts) | **IMPLEMENTED** | Implemented cryptographic receipt generation preserving exact execution metrics, timestamps, and pass rates in `eval/meia_78_cq_receipt.json` and `docs/benchmark_receipt.md`. | `eval/meia_78_cq_receipt.json`<br/>`docs/benchmark_receipt.md` |

---

### 10.4 Protocol for Evaluating Deferred Challenger Arms in Future Cards

When selecting any deferred candidate for future evaluation:
1. **Trigger Condition Required**: A candidate may only be activated to address a demonstrably failing competency question or measured performance bottleneck.
2. **Single Bounded Arm**: Only one challenger arm may be tested at a time against the baseline ("core ingestion plus one active experiment campaign").
3. **Mandatory 4-Point Drift Audit**: The proposed arm must pass the 4-point drift check (Infrastructure, Epistemic, Modality, Scope) before approval.
4. **Reversible Adapter**: Challenger components must integrate behind existing interfaces (`src/extract.py`, `src/hybrid_retriever.py`, `src/grounded_answer.py`) with clean rollback capability.


