"""
Epistemic Verifier & Integrity Audit Engine (Stage 4).
Enforces:
- CQ-73: 100% locator grounding completeness (Sheet!Row:Col, doc chunks, awards).
- CQ-74: Contradiction surfacing & side-by-side conflict preservation.
- CQ-75: Claim promotion firewall (VENDOR_SELF_ASSERTED != LIVE_DEMONSTRATED != FPDS_OBLIGATED).
"""

import json
import logging
import re
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

logger = logging.getLogger("epistemic_verifier")


@dataclass
class EpistemicAuditResult:
    audit_passed: bool
    status: str                                  # VERIFIED_GROUNDED, CONFLICTING_EVIDENCE, UNVERIFIED_VENDOR_CLAIM, GATE_DENIAL
    locator_grounding_score: float               # Target: 1.0 (100%)
    total_facts_audited: int
    grounded_facts_count: int
    ungrounded_facts: List[Dict[str, Any]]
    conflicts_detected: List[Dict[str, Any]]
    promotions_detected: List[Dict[str, Any]]
    audit_notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EpistemicVerifier:
    """Audits composed answers against source epistemic evidence and policy gates."""

    # Regex patterns for valid evidence locators
    CELL_PATTERN = re.compile(r"^.*!.*!R\d+C\d+", re.IGNORECASE)
    ALT_CELL_PATTERN = re.compile(r"^.*!Row \d+:Col \d+", re.IGNORECASE)
    CHUNK_PATTERN = re.compile(r"^(doc:|chunk_|text_chunk:)", re.IGNORECASE)
    AWARD_PATTERN = re.compile(r"^(usaspending:|CONT_AWD_|award:|contract:)", re.IGNORECASE)
    FIGURE_PATTERN = re.compile(r"^(parsed/figures/|fig:|figure:)", re.IGNORECASE)

    @classmethod
    def is_valid_locator(cls, locator: Optional[str]) -> bool:
        """Checks if a locator string points to an exact verifiable evidence anchor."""
        if not locator or not isinstance(locator, str):
            return False
        loc = locator.strip()
        if not loc:
            return False
        if cls.CELL_PATTERN.match(loc) or cls.ALT_CELL_PATTERN.match(loc):
            return True
        if cls.CHUNK_PATTERN.match(loc):
            return True
        if cls.AWARD_PATTERN.match(loc):
            return True
        if cls.FIGURE_PATTERN.match(loc):
            return True
        # Also allow colon-delimited evidence node IDs: evid:..., node:..., graph:..., policy:...
        if loc.startswith("evid:") or loc.startswith("node:") or loc.startswith("graph:") or loc.startswith("policy:"):
            return True
        return False

    def audit(self, draft_answer: Any, bundle: Any) -> EpistemicAuditResult:
        """
        Executes epistemic verification checks on a draft grounded answer.
        draft_answer is GroundedAnswer, bundle is AnswerRouteBundle.
        """
        audit_notes: List[str] = []
        ungrounded: List[Dict[str, Any]] = []
        conflicts: List[Dict[str, Any]] = []
        promotions: List[Dict[str, Any]] = []

        # ---------------------------------------------------------------------
        # 1. Gate Check: If fail-closed gate triggered, pass audit as gate denial
        # ---------------------------------------------------------------------
        bundle_status = getattr(bundle, "status", "SUPPORTED")
        if bundle_status != "SUPPORTED":
            draft_status = getattr(draft_answer, "status", bundle_status)
            audit_notes.append(f"Fail-closed policy gate confirmed: {draft_status}")
            return EpistemicAuditResult(
                audit_passed=True,
                status=draft_status,
                locator_grounding_score=1.0,
                total_facts_audited=0,
                grounded_facts_count=0,
                ungrounded_facts=[],
                conflicts_detected=[],
                promotions_detected=[],
                audit_notes=audit_notes
            )

        structured_facts = getattr(draft_answer, "structured_facts", [])
        answer_text = getattr(draft_answer, "answer_text", "")
        epistemic_claims = getattr(bundle, "epistemic_claims", [])

        # ---------------------------------------------------------------------
        # 2. Check CQ-73: 100% Locator Grounding Completeness
        # ---------------------------------------------------------------------
        total_facts = len(structured_facts)
        grounded_count = 0

        for fact in structured_facts:
            key = getattr(fact, "key", str(fact.get("key") if isinstance(fact, dict) else ""))
            val = getattr(fact, "value", str(fact.get("value") if isinstance(fact, dict) else ""))
            loc = getattr(fact, "locator", str(fact.get("locator") if isinstance(fact, dict) else ""))
            stat = getattr(fact, "epistemic_status", str(fact.get("epistemic_status") if isinstance(fact, dict) else ""))

            if self.is_valid_locator(loc):
                grounded_count += 1
            else:
                ungrounded.append({
                    "key": key,
                    "value": val,
                    "epistemic_status": stat,
                    "missing_locator": loc
                })

        locator_score = (grounded_count / total_facts) if total_facts > 0 else 1.0

        if locator_score == 1.0:
            audit_notes.append(f"CQ-73 Passed: 100% locator grounding ({grounded_count}/{total_facts} facts).")
        else:
            audit_notes.append(f"CQ-73 Warning: {len(ungrounded)} ungrounded facts detected (score: {locator_score:.2f}).")

        # ---------------------------------------------------------------------
        # 3. Check CQ-74: Contradiction Surfacing & Side-by-Side Preservation
        # ---------------------------------------------------------------------
        # Multi-valued predicates that legitimately have multiple distinct entries
        multi_valued_predicates = {
            "holds_federal_obligation",
            "participated_in_exercise",
            "addresses_operational_problem",
            "integration_interface",
            "skos_concepts",
            "naics_codes",
            "psc_codes",
            "contract_vehicles",
            "awarding_agency"
        }

        # Detect contradictory claims for the SAME subject and single-valued predicate
        claims_by_sub_pred: Dict[tuple, List[Dict[str, Any]]] = {}
        for c in epistemic_claims:
            sub = c.get("subject_id", "")
            pred = c.get("predicate", "")
            if pred not in multi_valued_predicates:
                claims_by_sub_pred.setdefault((sub, pred), []).append(c)

        for (sub, pred), clist in claims_by_sub_pred.items():
            if len(clist) > 1:
                # Compare distinct values
                distinct_values = {c.get("value", "").strip().lower() for c in clist}
                if len(distinct_values) > 1:
                    conflict_record = {
                        "subject_id": sub,
                        "predicate": pred,
                        "variants": clist,
                        "detected_conflict": True
                    }
                    conflicts.append(conflict_record)
                    audit_notes.append(f"CQ-74 Conflict Surfaced: Discrepancy on '{pred}' for subject '{sub}' across {len(clist)} source records.")

        # Also inspect explicit conflict flags in claims or structured facts
        for c in epistemic_claims:
            notes = str(c.get("notes") or "")
            if "CONFLICT" in notes.upper() or "DISCREPANCY" in notes.upper():
                pred = c.get("predicate", "unknown_predicate")
                if not any(cf.get("predicate") == pred for cf in conflicts):
                    conflicts.append({
                        "subject_id": c.get("subject_id"),
                        "predicate": pred,
                        "notes": notes,
                        "detected_conflict": True
                    })
                    audit_notes.append(f"CQ-74 Conflict Surfaced: Explicit conflict note on '{pred}': {notes}")

        for fact in structured_facts:
            notes = getattr(fact, "notes", str(fact.get("notes") if isinstance(fact, dict) else ""))
            if "CONFLICT" in str(notes).upper() or "DISCREPANCY" in str(notes).upper():
                pred = getattr(fact, "key", "unknown")
                if not any(cf.get("predicate") == pred for cf in conflicts):
                    conflicts.append({
                        "predicate": pred,
                        "notes": notes,
                        "detected_conflict": True
                    })
                    audit_notes.append(f"CQ-74 Conflict Surfaced: Preserved explicit contradictory finding on '{pred}'.")

        # ---------------------------------------------------------------------
        # 4. Check CQ-75: Claim Promotion Firewall
        # ---------------------------------------------------------------------
        # Enforce that VENDOR_SELF_ASSERTED is never promoted to LIVE_DEMONSTRATED
        for fact in structured_facts:
            stat = getattr(fact, "epistemic_status", str(fact.get("epistemic_status") if isinstance(fact, dict) else ""))
            key = getattr(fact, "key", str(fact.get("key") if isinstance(fact, dict) else ""))
            val = getattr(fact, "value", str(fact.get("value") if isinstance(fact, dict) else ""))

            if stat == "VENDOR_SELF_ASSERTED":
                # Ensure the text or structured fact acknowledges vendor qualification
                # Look for forbidden promotion phrases in answer text referring to this claim
                val_sample = str(val)[:30].lower()
                if val_sample and val_sample in answer_text.lower():
                    # Check context around val_sample
                    idx = answer_text.lower().find(val_sample)
                    surrounding = answer_text[max(0, idx - 80):min(len(answer_text), idx + 80)].lower()
                    if ("verified by navy" in surrounding or "empirically proven" in surrounding or "government validated" in surrounding) and "not verified" not in surrounding:
                        promotions.append({
                            "key": key,
                            "value": val,
                            "violation": "Vendor claim promoted to verified empirical capability in text."
                        })
                        audit_notes.append(f"CQ-75 Violation: Unauthorized promotion of vendor claim '{key}' to empirical status.")

        # ---------------------------------------------------------------------
        # 5. Final Audit Status Determination
        # ---------------------------------------------------------------------
        audit_passed = (locator_score >= 0.99) and (len(promotions) == 0)

        if len(conflicts) > 0:
            final_status = "CONFLICTING_EVIDENCE"
        elif any(getattr(f, "epistemic_status", "") == "VENDOR_SELF_ASSERTED" for f in structured_facts) and not any(getattr(f, "epistemic_status", "") in ("LIVE_DEMONSTRATED", "FPDS_OBLIGATED") for f in structured_facts):
            final_status = "UNVERIFIED_VENDOR_CLAIM"
        else:
            final_status = "VERIFIED_GROUNDED"

        return EpistemicAuditResult(
            audit_passed=audit_passed,
            status=final_status,
            locator_grounding_score=locator_score,
            total_facts_audited=total_facts,
            grounded_facts_count=grounded_count,
            ungrounded_facts=ungrounded,
            conflicts_detected=conflicts,
            promotions_detected=promotions,
            audit_notes=audit_notes
        )
