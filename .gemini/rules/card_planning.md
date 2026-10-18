---
description: Mandatory rule to trigger navy-weld-card-planner skill whenever /plan is requested for cards or milestones
always_on: true
---

# Card Planning & Drift Audit Rule

Whenever the user requests `/plan` for a card or milestone (e.g. `/plan card 08`, `plan card 8`, `plan next milestone`):

1. **Activate the Skill**: Invoke and strictly follow [`navy-weld-card-planner`](.agents/skills/navy-weld-card-planner/SKILL.md).
2. **Master Integration Register Cross-Reference**: Cross-reference all proposed features and candidate options against [`docs/NAVY_WELD_MASTER_INTEGRATION_AND_BAKEOFF_LIST_2026-10-18.md`](docs/NAVY_WELD_MASTER_INTEGRATION_AND_BAKEOFF_LIST_2026-10-18.md) (E01–E05, R01–R10, V01–V03, S01–S06, P01–P07, O01–O03, U01–U07, D01–D06).
3. **Mandatory 4-Point Drift Audit**: Explicitly evaluate and document compliance with the 4 core invariants:
   - **Infrastructure Invariant**: Zero external DB daemons (100% local SQLite + NetworkX + BGE-large vector files).
   - **Epistemic Invariant**: Strict non-equivalence firewall (`VENDOR_SELF_ASSERTED` $\neq$ `LIVE_DEMONSTRATED`). Zero claim promotions.
   - **Modality & Citation Invariant**: Balanced multimodal representations (180 DPI / LoC focal crops) and 100% cell/page citation coverage.
   - **Scope & Capacity Invariant**: Single bounded challenger arm per milestone ("core ingestion plus one active experiment campaign").
4. **Publish Implementation Plan Artifact**:
   - Write the plan to `<appDataDir>\brain\<conversation-id>\meia_<card_name>_plan.md` with `RequestFeedback: true` and `UserFacing: true`.
   - Never write production code or execute modifying changes until the user explicitly reviews and approves the plan artifact.
5. **Git Verification & Synchronization**:
   - Prior to execution: verify working tree clean, commit, pull, and verify sync.
   - Post-execution: run unit tests and 78-CQ benchmark, stage, commit, push, pull, and confirm local and remote are fully in sync.
