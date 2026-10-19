---
name: trident-colpali-visual
description: Governs ColPali late-interaction visual MaxSim scoring, Trident modality-balanced fusion, and Loud and Clear (LoC) 3-arm reader input preparation.
route_profiles:
  - D2_TECHNICAL_READINESS
  - D4_CROSS_GRAPH_SYNTHESIS
visual_quota: 2
ocr_token_budget: 160
loc_reader_arm: ARM_C_HYBRID_OCR
---

# ColPali Visual Retrieval & Trident Modality Calibration Skill

## Purpose
Ensures that relevant technical schematics, deployment diagrams, and visual figures (e.g. Klas Voyager architecture, Fluor Pad B flight telemetry, Prometheus drone payload) are scored using late-interaction patch MaxSim, protected from text-chunk rank displacement via Trident modality calibration, and formatted for the LLM reader using Loud and Clear (LoC) `ARM_C_HYBRID_OCR`.

## Inputs
- `query_str`: User query string and embedded visual terms (`diagram`, `schematic`, `architecture`, `figure`, `flowchart`).
- `figure_candidates`: List of bounding box records from `parsed/figures/figure_bboxes.json` with vector embeddings and OCR chips.
- `text_candidates`: List of textual chunks from `storage/vdb_chunks_contextual.json`.

## Outputs
- `ranked_figures`: Top visual candidates scored by ColPali late-interaction MaxSim.
- `modality_audit`: Diagnostic telemetry tracking text vs figure score distribution and rank shifts.
- `fused_candidates`: Calibrated list of text and visual evidence respecting `visual_quota=2`.
- `loc_reader_payload`: 3-arm formatted reader bundle containing high-detail visual crops + region-filtered OCR tokens within `ocr_token_budget=160`.

## Guardrails
- **Modality Preservation**: On queries containing visual keywords (`diagram`, `architecture`, `schematic`, `figure`, `visual`, `layout`), text chunks must NEVER completely displace visual candidates. A minimum of 1 and up to 2 top visual candidates must be preserved.
- **LoC Token Budget**: OCR tokens in `ARM_C_HYBRID_OCR` must NOT exceed 160 tokens. Excessive OCR tokens degrade VLM attention and crowd out diagram visual context.
- **Visual Confidence**: Late-interaction MaxSim score must exceed 0.20 for inclusion; if no figures meet this threshold, omit figures and note absence in the modality audit.

## Workflow
1. **Late-Interaction MaxSim Scoring**:
   - Compute token-to-patch similarity between query tokens $q_i$ and visual region embeddings $f_j$.
   - Calculate $\text{MaxSim}(Q, F) = \frac{1}{|Q|} \sum_{i} \max_{j} \langle \hat{q}_i, \hat{f}_j \rangle$.
2. **Trident Modality-Bias Audit**:
   - Examine pre-fusion score distributions of top-5 text chunks and top-5 figure candidates.
   - If text scores artificially compress figure ranks despite strong visual query intent, apply calibrated rank fusion with reserved visual slots.
3. **Loud and Clear (LoC) Preparation**:
   - For top visual figures, assemble `ARM_C_HYBRID_OCR`:
     - Arm A: Full page context reference.
     - Arm B: High-detail focal crop around the bounding box.
     - Arm C: Budgeted region OCR tokens (filtering high-frequency labels and legend terms).
4. **Emit Reader Packet**: Provide the fused multi-modal evidence bundle to the LLM reader.

## Success Metrics
- Relevant architecture diagrams (Klas Voyager, Fluor Pad B, Prometheus payload) appear in the top-3 retrieved evidence for technical architecture questions.
- LoC reader payload strictly complies with the 160-token OCR budget.
