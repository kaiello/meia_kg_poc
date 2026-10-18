# Card 09 (`poc_audit1`): Post-POC Audit, Live Demo Hardening & Security/PII Scrubbing

* **Card ID**: `CARD-09-POC-AUDIT-1` (`docs/poc_audit1.md`)
* **Date**: 2026-10-18
* **Status**: `PLANNED — AWAITING EXECUTION APPROVAL`
* **Scope**: Remediation of all silent implementation shortcuts, live client demo brittle edge cases, web server security vulnerabilities, and unredacted PII/CUI artifacts uncovered during the comprehensive post-Card-08 codebase audit against [`docs/goal.md`](goal.md) and [`docs/architecture.md`](architecture.md).

---

## 1. Executive Summary & Audit Context

Following the completion of Cards `01` through `08`, automated verification ([`scripts/verify_all.py`](../scripts/verify_all.py)) passes `73/73` unit/integration tests and `78/78` Competency Questions (`100.0%` Route@1, Status, Locator Grounding, and Claim Firewall).

However, a line-by-line audit of `src/`, `eval/`, `config/`, `parsed/`, and `storage/` against [`docs/goal.md`](goal.md) and [`docs/architecture.md`](architecture.md) identified:
1. **5 Silent Implementation Gaps** masked by permissive assertions in [`eval/test_scorer.py`](../eval/test_scorer.py).
2. **5 High-Risk Brittle Spots** that will visibly fail or produce incorrect outputs during an interactive live client demonstration.
3. **Critical Unredacted PII/CUI Exposure & 3 Web Server Security Vulnerabilities** that must be remediated and scrubbed before external repository sharing.

---

## 2. Master Integration Register Cross-Reference

Per the [`navy-weld-card-planner`](../.agents/skills/navy-weld-card-planner/SKILL.md) protocol, every workstream in `poc_audit1` maps directly to [`docs/NAVY_WELD_MASTER_INTEGRATION_AND_BAKEOFF_LIST_2026-10-18.md`](NAVY_WELD_MASTER_INTEGRATION_AND_BAKEOFF_LIST_2026-10-18.md):

| Candidate ID | Name | Role in `poc_audit1` (`CARD-09`) | Target Files |
| :--- | :--- | :--- | :--- |
| **`U05`** | Multi-Source 360° Executive Dossier Cards | Replace hardcoded Albacore dictionary in `_build_executive_dossier` with dynamic entity-driven dossier synthesis across all 5 benchmark vendors (`Albacore`, `Voltage Vessels`, `T2S Solutions`, `Fluor Federal Services`, `Klas/Prometheus`). | `src/grounded_answer.py`, `eval/test_scorer.py` |
| **`R03`** | Functional Multi-Perspective Context Packet | Remove fabricated fallback values (`$12,000,000`, `$1,850,000`, `R4C55`) when an entity lacks `Q4`/`Q5`/`Q6` Vulcan rows; emit explicit `NOT_RECORDED` or omit unrecorded perspectives. | `src/context_packet.py`, `tests/test_card08_features.py` |
| **`R06`** | Cross-Encoder Reranking Stage | Implement deterministic second-stage Cross-Encoder / lexical-semantic precision reranker hook in `ScopedHybridRetriever.retrieve()` to align implementation with `goal.md` §3.4. | `src/hybrid_retriever.py` |
| **`E01` / `S02`** | StandardManifest & Twenty CRM Schema Disposition | Dynamically load column disposition rules from `data/CRM_Object_Field_Mapping.xlsx` (with deterministic fallback) and synchronize the `CQ-73` SHA-256 hash (`22602691...`) with `config/meia_poc_manifest.json`. | `src/extract.py`, `src/grounded_answer.py` |
| **`V01` / `V02`** | Loud-and-Clear (LoC) Arm B & Arm C Inspector | Fix `/parsed/figures/crops/...` 404 routing in `MeiaWebHandler.do_GET` and fix `figure_bboxes.json` schema traversal (`["figures"]` & `["chips"]`) in `LoCFigureInspector.get_ocr_callouts_for_asset`. | `src/web.py`, `src/figure_inspectors.py` |
| **`S03` / `U04`** | Epistemic Firewall, RBAC & Truthful Abstention | Harden `CQ-77` RBAC filtering (both pre-retrieval email/contact detection and post-retrieval bundle scrubbing for `UNCLASSIFIED` callers) and generalize `CQ-78` unrecorded specification abstention. | `src/pre_retrieval.py`, `src/answer_routes.py` |
| **`O01` / `D03`** | Zero-Daemon Local Serving & Security Hardening | Upgrade `HTTPServer` to `ThreadingHTTPServer`, enforce `.is_relative_to()` path traversal guards, escape DOM `.innerHTML` interpolations, cap POST `Content-Length`, and scrub/redact plaintext PII across `src/`, `parsed/`, and `storage/`. | `src/web.py`, `src/build_tri_graph.py`, `parsed/*` |

---

## 3. Mandatory 4-Point Drift Audit

| Drift Dimension | Invariant Rule | Assessment for `CARD-09` (`poc_audit1`) | Status |
| :--- | :--- | :--- | :--- |
| **1. Infrastructure Drift** | **Zero External Database Daemons** | All fixes execute 100% in-process using Python stdlib (`http.server.ThreadingHTTPServer`, `sqlite3`, `pathlib`, `html`), `networkx`, and local JSON/SQLite stores. Zero external servers or cloud dependencies introduced. | **PASS (0% Drift)** |
| **2. Epistemic Drift** | **Strict Non-Equivalence Firewall** | Strengthens epistemic integrity by removing synthetic fallback numbers from `ContextPacketBuilder` (`R03`) and replacing static Albacore dossier fields with entity-verified claims (`VENDOR_SELF_ASSERTED` vs. `LIVE_DEMONSTRATED`). | **PASS (0% Drift)** |
| **3. Retrieval / Modality Drift** | **Fair Multimodal Representation & 100% Citation** | Restores live browser rendering of LoC Arm B focal crops (`180 DPI`) and Arm C OCR callout extraction from `figure_bboxes.json`, while syncing `CQ-73` SHA-256 citation provenance with `meia_poc_manifest.json`. | **PASS (0% Drift)** |
| **4. Scope / Capacity Drift** | **Single Bounded Hardening Campaign** | Strictly bounded to hardening existing Cards `01`–`08` requirements, live demo edge cases, and security/PII hygiene without introducing new platform migrations. | **PASS (0% Drift)** |

---

## 4. Detailed Workstream Breakdown & Actionable Checklists

### Workstream A: Fix Silent Implementation Gaps (Task 1 Findings)

#### A1. Dynamic Multi-Vendor 360° Executive Dossier (`CQ-68`–`CQ-72`)
* **Defect**: [`GroundedAnswerComposer._build_executive_dossier`](../src/grounded_answer.py#L409-L484) returns hardcoded `Albacore` (`0QSF0`) and `Ghostfin` fields for every `ROUTE_ALL_TRI_STORE` query.
* **Remediation Checklist**:
  - [ ] **[MODIFY] [`src/grounded_answer.py`](../src/grounded_answer.py#L409-L484)**: Refactor `_build_executive_dossier(self, route_bundle)` to resolve the target organization and offering dynamically from `route_bundle.resolved_entities`, `route_bundle.sql_rows`, and `route_bundle.graph_traversal`:
    - [ ] Support `Albacore Inc.` / `Ghostfin` (`CQ-68`, CAGE `0QSF0`, `HR001122C0045` `$14.5M` DIU OT, ANTX-2024 Cohort).
    - [ ] Support `Voltage Vessels` / `rijido` (`CQ-69`, CAGE `9V8B2`, Vulcan ScoutCard commercial shipyard & unmanned surface vessel profile, `0` empirical demonstration records).
    - [ ] Support `T2S Solutions, LLC` / `Eclipse X9` (`CQ-70`, CAGE `7T2S9`, Aberdeen Proving Ground C5ISR sovereign tactical edge processor, ANTX-2024 Cohort).
    - [ ] Support `Fluor Federal Services` (`CQ-71`, CAGE `1FF88`, `N00024-21-C-4312` `$142.0M` SeaPort-NxG nuclear naval shipyard prime, `0` Vulcan capability claims).
    - [ ] Support `Klas Government` & `Prometheus Federal` (`CQ-72`, Voyager Tactical Cloud Module & JADC2 federated middleware, `W15P7T-23-D-0019` `$38.4M` & `FA8750-23-C-0112` `$19.2M`).
  - [ ] **[MODIFY] [`eval/test_scorer.py`](../eval/test_scorer.py#L181-L186)**: Strengthen the `CQ-68`–`CQ-72` scorer gate so it verifies that `ans.executive_dossier["1_organization_profile"]["legal_name"]` matches the queried organization (preventing any single-vendor hardcoded dossier from passing).

#### A2. Remove Fabricated Fallback Strings in `ContextPacketBuilder` (`R03`)
* **Defect**: [`ContextPacketBuilder.build_packet_for_entity`](../src/context_packet.py#L262-L305) injects synthetic strings (`"$12,000,000 for manufacturing scale-up"`, `"$1,850,000 per production unit"`, `"R4C55"`) when an entity has no `Q4`/`Q5`/`Q6`/`Q12` claims in `claim_ledger`.
* **Remediation Checklist**:
  - [ ] **[MODIFY] [`src/context_packet.py`](../src/context_packet.py#L262-L305)**: Query actual `domain_nodes`, `domain_edges`, and `claim_ledger` rows for the resolved entity; when a perspective (`Q4`, `Q5`, `Q6`, `Q12`) is absent in the database for a given vendor (e.g., `Fluor`, `Klas`, `Prometheus`), populate only verified contract/program claims or an explicit `NOT_RECORDED` indicator with `epistemic_status="ABSTAINED"` rather than fabricated dollar amounts.
  - [ ] **[MODIFY] [`tests/test_card08_features.py`](../tests/test_card08_features.py)**: Add assertion verifying that non-Vulcan prime contractors (`Fluor`) never receive fabricated Albacore `R4C55` locators or synthetic ROM/unit pricing.

#### A3. Align `CQ-73` SHA-256 Provenance Hash with Manifest (`E01`)
* **Defect**: [`GroundedAnswerComposer._synthesize_narrative`](../src/grounded_answer.py#L286) hardcodes `c5d00fc161f4c7811979ad2ae09a5ebfe8650df68a983196f7c8ec1ec0b7ee2e` instead of reading the actual SHA-256 (`226026917125c65dc8cda63266d8766e887b989387ef0e417263ce71bcaf28b0`) from [`config/meia_poc_manifest.json`](../config/meia_poc_manifest.json#L10).
* **Remediation Checklist**:
  - [ ] **[MODIFY] [`src/grounded_answer.py`](../src/grounded_answer.py#L280-L295)**: Dynamically lookup the SHA-256 hash of `MEIA_TEM_Vulcan_Export.xlsx` from `config/meia_poc_manifest.json` (or `StandardManifest`) so `CQ-73` always reports the exact cryptographic digest of the ingested file.

#### A4. Wire Second-Stage Precision Reranker in `ScopedHybridRetriever` (`R06`)
* **Defect**: [`ScopedHybridRetriever.retrieve`](../src/hybrid_retriever.py#L243-L304) stops after Modality-Calibrated RRF without executing a precision reranking pass (`R06`).
* **Remediation Checklist**:
  - [ ] **[MODIFY] [`src/hybrid_retriever.py`](../src/hybrid_retriever.py#L243-L304)**: Add `_rerank_candidates(query, candidates, top_k)` after RRF fusion that applies cross-encoder / exact entity-anchor & technical phrase overlap scoring (with optional `CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')` when loaded, and deterministic lexical-anchor precision boost when offline) and records `rerank_score` in chunk metadata.

#### A5. Ingest `CRM_Object_Field_Mapping.xlsx` Disposition Rules (`S02`)
* **Defect**: [`src/extract.py`](../src/extract.py#L31-L72) relies strictly on hardcoded column prefixes in `classify_vulcan_column` without reading `data/CRM_Object_Field_Mapping.xlsx`.
* **Remediation Checklist**:
  - [ ] **[MODIFY] [`src/extract.py`](../src/extract.py#L31-L72)**: Add `load_crm_field_mapping_overrides()` to parse `data/CRM_Object_Field_Mapping.xlsx` when present and merge its field dispositions with `classify_vulcan_column()`, writing a summary artifact `parsed/crm_field_mapping_audit.json`.

---

### Workstream B: Harden Top 5 Brittle Spots for Live Client Demo (Task 2 Findings)

#### B1. Fix Diagram Inspector `Arm B` (`404 Not Found`) & `Arm C` (OCR Callouts Schema Mismatch)
* **Defect 1**: Clicking `Arm B: Focal Crop Chip` in [`src/web.py`](../src/web.py#L454-L458) sets `diagImg.src = '/' + data.focal_crop_path` (`/parsed/figures/crops/...`), which returns `404 Not Found` because [`MeiaWebHandler.do_GET`](../src/web.py#L769) only serves `/api/figures/...`.
* **Defect 2**: [`LoCFigureInspector.get_ocr_callouts_for_asset`](../src/figure_inspectors.py#L142-L163) iterates `self.bbox_registry.items()` expecting `{doc_id: [items]}`, whereas [`parsed/figure_bboxes.json`](../parsed/figure_bboxes.json) has top-level keys `{"figures": {...}, "chips": [...]}`.
* **Remediation Checklist**:
  - [ ] **[MODIFY] [`src/web.py`](../src/web.py#L450-L465)**: Normalize `focal_crop_path` in `switchLoCArm('B')` so paths starting with `parsed/figures/` map cleanly to `/api/figures/...` (e.g., `/api/figures/crops/DOC-GHOSTFIN-TECH_p1_crop0.png`). Also add `/parsed/figures/` alias handling in `MeiaWebHandler.do_GET` as a belt-and-suspenders guard.
  - [ ] **[MODIFY] [`src/figure_inspectors.py`](../src/figure_inspectors.py#L40-L67) & [`#L142-L163`](../src/figure_inspectors.py#L142-L163)**: Update `_load_registries()` and `get_ocr_callouts_for_asset()` to traverse both `self.bbox_registry.get("figures", {})` and `self.bbox_registry.get("chips", [])` (as well as OCR text from `text_chunks.jsonl` where `chunk_type == "visual_ocr"`), returning real extracted diagram callouts for `Arm C`.
  - [ ] **[MODIFY] [`tests/test_card07_features.py`](../tests/test_card07_features.py)**: Add unit tests asserting that `Arm B` crop URLs resolve to existing files via `/api/figures/crops/...` and `Arm C` returns non-placeholder OCR callout strings.

#### B2. Generalize Out-of-Scope / Unrecorded Specification Abstention (`CQ-78`)
* **Defect**: [`PreRetrievalProcessor.evaluate_policy_gates`](../src/pre_retrieval.py#L168-L185) only triggers `OUT_OF_SCOPE` on 7 hardcoded strings. Free-form demo questions about unrecorded metrics (e.g., *"crush depth"*, *"wingspan"*, *"battery chemistry"*, *"sonar frequency"*, *"mtbf"*, *"cryptographic key length"*) route to `ROUTE_TECH` and return `VERIFIED_GROUNDED`.
* **Remediation Checklist**:
  - [ ] **[MODIFY] [`src/pre_retrieval.py`](../src/pre_retrieval.py#L168-L185)**: Expand unrecorded specification detection with a broader lexicon of unrecorded technical/financial parameters (`crush depth`, `operating depth`, `wingspan`, `flight ceiling`, `battery chemistry`, `propellant`, `warhead`, `acoustic`, `decibel`, `radar cross section`, `mtbf`, `mean time between failure`, `stock price`, `net worth`, `tax id`, `ein`) AND add a post-retrieval grounding verification in [`GroundedAnswerComposer.compose`](../src/grounded_answer.py#L130-L185) so if an ad-hoc query contains a specific interrogative parameter with zero lexical overlap in retrieved chunks/SQL rows, it downgrades to `NOT_RECORDED` (`TRUTHFUL_ABSTENTION`).

#### B3. Harden `UNCLASSIFIED` RBAC Enforcement Across Pre-Retrieval & Post-Retrieval (`CQ-77`)
* **Defect**: [`PreRetrievalProcessor.evaluate_policy_gates`](../src/pre_retrieval.py#L192-L217) only blocks phone-number phrases under `UNCLASSIFIED`, missing email/contact queries (`email`, `e-mail`, `contact info`, `cell`, `mobile`, `telephone`, `direct dial`, `ssn`, `clearance level`), and [`AnswerRouteBundler.assemble_bundle`](../src/answer_routes.py#L122-L212) does not strip `PII_ENCRYPTED` or `RESTRICTED_CLEARANCE` fields from SQLite rows when `user_clearance == "UNCLASSIFIED"`.
* **Remediation Checklist**:
  - [ ] **[MODIFY] [`src/pre_retrieval.py`](../src/pre_retrieval.py#L192-L217)**: Expand `is_pii_request` to catch `email`, `e-mail`, `contact info`, `contact details`, `phone`, `telephone`, `mobile`, `cell`, `direct dial`, `home address`, and `personal contact`.
  - [ ] **[MODIFY] [`src/answer_routes.py`](../src/answer_routes.py#L122-L212)**: Pass `user_clearance` into `assemble_bundle()` and redact/filter any `claim_ledger` or `domain_nodes` attributes marked `PII_ENCRYPTED` or requiring elevated clearance when `user_clearance == "UNCLASSIFIED"`.

#### B4. Upgrade Web Server Concurrency & Prevent Vector Dimension Mismatch
* **Defect**: [`src/web.py#L916`](../src/web.py#L916) uses single-threaded `HTTPServer`, and [`ContextualChunkIndexer.get_embedding`](../src/contextual_indexer.py#L40-L56) can mix 384-d offline hash vectors with 1024-d `sentence_transformers` vectors if runtime mode differs from index build mode.
* **Remediation Checklist**:
  - [ ] **[MODIFY] [`src/web.py`](../src/web.py#L13) & [`#L916`](../src/web.py#L916)**: Replace `HTTPServer` with `ThreadingHTTPServer` so concurrent `/api/query`, `/api/figures/...`, and `/api/benchmark/receipt` browser requests never block each other.
  - [ ] **[MODIFY] [`src/hybrid_retriever.py`](../src/hybrid_retriever.py#L180-L215)**: Check the dimensionality of stored vectors in `vdb_chunks_contextual.json` (`384` vs `1024`); if the stored index uses `384`-d deterministic vectors, automatically use `deterministic_offline_vector` for query encoding so cosine similarity never silently evaluates to `0.0`.

---

### Workstream C: Security Vulnerability Remediation & PII/CUI Scrubbing (Task 3 Findings)

#### C1. Scrub / Mask Plaintext PII & CUI Across Source Code, `parsed/`, and `storage/`
* **Defect**: Real names, `.mil` and corporate email addresses, phone numbers, and internal ScoutCard UUIDs are hardcoded in `src/build_tri_graph.py`, `src/pre_retrieval.py`, `src/web.py`, and stored in git-tracked `parsed/vulcan_submissions.jsonl` and `storage/*`.
* **Remediation Checklist**:
  - [ ] **[MODIFY] [`src/extract.py`](../src/extract.py#L130-L175)**: Add a deterministic PII redaction/tokenization sanitizer (`sanitize_pii_value`) during Vulcan extraction so `poc_email`, `poc_phone`, `gov_poc_email`, `gov_poc_phone`, and `user_email` in `parsed/vulcan_submissions.jsonl` store SHA-256 masked tokens (e.g., `REDACTED_EMAIL_<8-char-hash>@cui-redacted.local`, `REDACTED_PHONE_<8-char-hash>`) and redacted ScoutCard URLs (`https://vulcan-sof.local/redacted/scoutcard/<hash>`).
  - [ ] **[MODIFY] [`src/build_tri_graph.py`](../src/build_tri_graph.py#L412-L426)**: Replace hardcoded plaintext `"email_encrypted": "cameron.a.matthews.civ@us.navy.mil"` and `"phone_encrypted": "18508675230"` with SHA-256 HMAC/hash ciphertext (`sha256:8f4e...`) and synthetic/role-based display labels (`"Gov Sponsor POC (NSWCDD)"`, `"Vendor Primary POC"`), preserving `CQ-11`, `CQ-12`, `CQ-13`, and `CQ-77` behavior without exposing real personal phone numbers or emails in source code or SQLite/GraphML files.
  - [ ] **[Run Pipeline]**: Re-run `python -B src/extract.py` and `python -B src/build_tri_graph.py` to regenerate `parsed/vulcan_submissions.jsonl`, `storage/meia_tri_graph_registry.db`, `storage/crm_graph.graphml`, `storage/federated_epistemic_graph.graphml`, and `storage/vdb_entities.json` with zero plaintext email addresses or phone numbers.
  - [ ] **[Audit Scan]**: Run a repository-wide regex scan across all git-tracked files for `@albacore.inc`, `@voltagevessels.com`, `@us.navy.mil`, `18508675230`, `13104887606`, `19088216493`, `18082642776`, and `vulcan-sof.com/login` to verify `0` remaining occurrences.

#### C2. Fix Path Traversal Vulnerability in `MeiaWebHandler.do_GET`
* **Defect**: [`src/web.py#L769-L803`](../src/web.py#L769-L803) constructs `fig_path = FIGURES_DIR / filename` from unquoted URL paths without checking `.resolve().is_relative_to(FIGURES_DIR.resolve())`.
* **Remediation Checklist**:
  - [ ] **[MODIFY] [`src/web.py`](../src/web.py#L769-L803)**: Resolve `fig_path = (FIGURES_DIR / filename).resolve()` and verify `fig_path.is_relative_to(FIGURES_DIR.resolve())`; return `HTTP 403 Forbidden` immediately if the resolved path escapes `FIGURES_DIR` or contains traversal sequences.

#### C3. Fix DOM Cross-Site Scripting (XSS) & Unbounded POST Read in `src/web.py`
* **Defect**: [`src/web.py#L547-L593`](../src/web.py#L547-L593) and [`#L671-L679`](../src/web.py#L671-L679) inject unescaped strings into `.innerHTML`, and [`do_POST`](../src/web.py#L877-L878) reads `Content-Length` without a size cap.
* **Remediation Checklist**:
  - [ ] **[MODIFY] [`src/web.py`](../src/web.py#L430-L690)**: Add a JavaScript `escapeHtml(str)` utility function and wrap all dynamic fields (`q.content`, `q.locator`, `p.anchor_label`, `p.source_locator`, `it.proposed_value`, `it.entity_name`, `data.answer_text`) before `.innerHTML` assignment.
  - [ ] **[MODIFY] [`src/web.py`](../src/web.py#L875-L885)**: Enforce `MAX_POST_BYTES = 65536` (`64 KB`) in `do_POST`; return `HTTP 413 Payload Too Large` if `content_length > MAX_POST_BYTES`.

---

## 5. Verification & Acceptance Gate Checklist

- [ ] **Gate 1 — Multi-Vendor Dossier Verification**: Querying `CQ-68` (`Albacore`), `CQ-69` (`Voltage Vessels`), `CQ-70` (`T2S Solutions`), `CQ-71` (`Fluor Federal Services`), and `CQ-72` (`Klas / Prometheus`) each returns a distinct, vendor-accurate 5-part `executive_dossier` verified by `eval/test_scorer.py`.
- [ ] **Gate 2 — Diagram Inspector Arm B & Arm C Verification**: Requesting `/api/figures/crops/DOC-GHOSTFIN-TECH_p1_crop0.png` returns `HTTP 200` (`image/png`), and `LoCFigureInspector` returns non-placeholder OCR callouts from `figure_bboxes.json`.
- [ ] **Gate 3 — Ad-Hoc Policy Gate Verification**: Free-form `UNCLASSIFIED` email/contact queries trigger `RESTRICTED_CLEARANCE`, and free-form unrecorded specification queries (e.g., *"What is Ghostfin's maximum crush depth in meters?"*) trigger `OUT_OF_SCOPE` / `NOT_RECORDED`.
- [ ] **Gate 4 — Security & PII Zero-Leakage Scan**:
  - Path traversal request `/api/figures/..%2F..%2Fconfig%2Fmeia_poc_manifest.json` returns `HTTP 403`.
  - Repository-wide grep confirms `0` plaintext personal phone numbers or `.mil`/corporate emails in any git-tracked file.
- [ ] **Gate 5 — Full Regression Suite (`scripts/verify_all.py`)**:
  - `100%` pass rate across all existing + new `Card 09` unit tests.
  - `78/78` (`100.0%`) pass rate on the 78-CQ benchmark suite.
- [ ] **Gate 6 — Git Synchronization**:
  - Commit, push, pull, and verify local `main` and `origin/main` are 100% synchronized.
