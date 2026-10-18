"""
Test Suite for Card 05: Grounded Multimodal Answer Composer and Epistemic Verifier.
Verifies:
- CQ-73: 100% locator grounding completeness (Sheet!Row:Col, doc chunks, awards).
- CQ-74: Contradiction surfacing & side-by-side conflict preservation.
- CQ-75: Claim promotion firewall (VENDOR_SELF_ASSERTED != LIVE_DEMONSTRATED != FPDS_OBLIGATED).
- CQ-68 to CQ-72: Full 360° Executive Business & Capability Dossier synthesis across all 3 stores.
- CQ-76 to CQ-78: Deterministic fail-closed policy gates.
"""

import unittest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.pre_retrieval import CallerContext
from src.answer_routes import assemble_answer_route, AnswerRouteBundle
from src.grounded_answer import (
    GroundedAnswerComposer,
    GroundedAnswer,
    GroundedFact,
    answer_query
)
from src.epistemic_verifier import EpistemicVerifier


class TestClaimVsDemoVerifier(unittest.TestCase):
    """Card 05 Unit & Integration Tests: Composer and Epistemic Verifier."""

    @classmethod
    def setUpClass(cls):
        cls.auth_context = CallerContext(
            caller_role="meia-authorized-evaluator",
            clearance_level="SECRET",
            enabled_modules=["organization_graph", "technology_graph", "crm_graph", "evidence_graph"]
        )
        cls.composer = GroundedAnswerComposer()
        cls.verifier = EpistemicVerifier()

    def test_locator_completeness_cq73_org_route(self):
        """CQ-73: Verifies 100% locator grounding on standalone Organization route (CQ-01/02)."""
        query = "What is Albacore's CAGE code, location, and corporate subcategory?"
        answer = answer_query(query, self.auth_context)

        self.assertEqual(answer.route_profile, "ROUTE_ORG")
        self.assertIn(answer.status, ("VERIFIED_GROUNDED", "UNVERIFIED_VENDOR_CLAIM"))
        self.assertGreaterEqual(len(answer.structured_facts), 1)

        # Audit score must be 1.0 (100% grounded)
        audit = answer.epistemic_audit
        self.assertTrue(audit.get("audit_passed"))
        self.assertGreaterEqual(audit.get("locator_grounding_score", 0.0), 0.99)
        self.assertEqual(len(audit.get("ungrounded_facts", [])), 0)

        # Check for exact spreadsheet cell citations
        self.assertGreaterEqual(len(answer.citations), 1)
        self.assertTrue(any("Vulcan Submissions" in c or "!R" in c or "usaspending" in c for c in answer.citations))

    def test_locator_completeness_cq73_tech_route(self):
        """CQ-73: Verifies 100% locator grounding on standalone Technology route (CQ-19/29)."""
        query = "What is Ghostfin's operational range, mission endurance, and payload capacity?"
        answer = answer_query(query, self.auth_context)

        self.assertEqual(answer.route_profile, "ROUTE_TECH")
        self.assertIn(answer.status, ("VERIFIED_GROUNDED", "UNVERIFIED_VENDOR_CLAIM"))
        self.assertGreaterEqual(len(answer.structured_facts), 1)

        # Audit score must be 1.0 (100% grounded)
        audit = answer.epistemic_audit
        self.assertTrue(audit.get("audit_passed"))
        self.assertGreaterEqual(audit.get("locator_grounding_score", 0.0), 0.99)

        # Check visual diagrams attached
        self.assertGreaterEqual(len(answer.visual_figures), 1)
        first_asset = answer.visual_figures[0]
        self.assertIn("figure_image", first_asset)

    def test_locator_completeness_cq73_cross_graph_join(self):
        """CQ-73: Verifies 100% locator grounding on pairwise Org-Tech join (CQ-51)."""
        query = "Which company develops the Ghostfin UUV and what is their CAGE code?"
        answer = answer_query(query, self.auth_context)

        self.assertEqual(answer.route_profile, "ROUTE_ORG_TECH")
        self.assertIn(answer.status, ("VERIFIED_GROUNDED", "UNVERIFIED_VENDOR_CLAIM"))

        # Verify fact locators are all valid
        for fact in answer.structured_facts:
            self.assertTrue(
                EpistemicVerifier.is_valid_locator(fact.locator),
                f"Fact locator '{fact.locator}' must be a valid evidence anchor"
            )

    def test_conflict_surfacing_cq74(self):
        """CQ-74: Contradiction Surfacing detects conflicting findings and preserves both side-by-side."""
        # Create a synthetic draft with conflicting TRL findings
        synthetic_bundle = AnswerRouteBundle(
            query="What is the evaluated TRL of Ghostfin?",
            route_profile="ROUTE_TECH",
            status="SUPPORTED",
            primary_entities=[{"id": "tech:ghostfin_uuv", "graph_domain": "TECH", "properties": {}}],
            cross_graph_bridges=[],
            epistemic_claims=[
                {
                    "claim_id": "c1",
                    "subject_id": "tech:ghostfin_uuv",
                    "predicate": "has_readiness_trl",
                    "value": "6",
                    "epistemic_status": "VENDOR_SELF_ASSERTED",
                    "evidence_id": "evid:vulcan_26705_c59",
                    "notes": "Vendor self-assessed maturity in Vulcan submission"
                },
                {
                    "claim_id": "c2",
                    "subject_id": "tech:ghostfin_uuv",
                    "predicate": "has_readiness_trl",
                    "value": "4",
                    "epistemic_status": "GOVERNMENT_EVALUATED",
                    "evidence_id": "evid:vulcan_26705_c59",
                    "notes": "CONFLICT: Navy Technical Evaluation downgraded TRL to 4 due to power cell thermal throttling"
                }
            ],
            text_chunks=[],
            visual_assets=[],
            cell_citations=["MEIA_TEM_Vulcan_Export.xlsx!Vulcan Submissions!R2C59"],
            execution_trace={}
        )

        draft = self.composer.compose(synthetic_bundle)

        # Must flag status as CONFLICTING_EVIDENCE
        self.assertEqual(draft.status, "CONFLICTING_EVIDENCE")
        self.assertGreaterEqual(len(draft.epistemic_audit.get("conflicts_detected", [])), 1)

        # Warning banner must be present in the markdown text
        self.assertIn("Epistemic Conflict Detected (CQ-74)", draft.answer_text)

    def test_claim_promotion_firewall_cq75(self):
        """CQ-75: Enforces that VENDOR_SELF_ASSERTED claims cannot be promoted to empirical capability."""
        # 1. Valid compliant answer: vendor claims are qualified with (Vendor-asserted)
        query = "What is Ghostfin's operational range?"
        answer = answer_query(query, self.auth_context)

        # Audit must pass with 0 unauthorized promotions
        audit = answer.epistemic_audit
        self.assertEqual(len(audit.get("promotions_detected", [])), 0)
        self.assertTrue(audit.get("audit_passed"))

        # 2. Test unauthorized promotion violation detection
        violation_draft = GroundedAnswer(
            query="What is Ghostfin's operational range?",
            route_profile="ROUTE_TECH",
            status="VERIFIED_GROUNDED",
            answer_text="Ghostfin's 1000 nautical miles range has been empirically proven and verified by Navy operational testing.",
            structured_facts=[
                GroundedFact(
                    key="range_nmi",
                    value="1000 nautical miles",
                    subject_id="tech:ghostfin_uuv",
                    epistemic_status="VENDOR_SELF_ASSERTED",
                    locator="MEIA_TEM_Vulcan_Export.xlsx!Vulcan Submissions!R2C53",
                    source_doc="doc:vulcan_export_2026"
                )
            ],
            citations=["MEIA_TEM_Vulcan_Export.xlsx!Vulcan Submissions!R2C53"],
            visual_figures=[],
            executive_dossier=None
        )

        mock_bundle = AnswerRouteBundle(
            query="What is Ghostfin's operational range?",
            route_profile="ROUTE_TECH",
            status="SUPPORTED",
            primary_entities=[],
            cross_graph_bridges=[],
            epistemic_claims=[],
            text_chunks=[],
            visual_assets=[],
            cell_citations=["MEIA_TEM_Vulcan_Export.xlsx!Vulcan Submissions!R2C53"],
            execution_trace={}
        )

        audit_result = self.verifier.audit(violation_draft, mock_bundle)
        self.assertFalse(audit_result.audit_passed)
        self.assertGreaterEqual(len(audit_result.promotions_detected), 1)
        self.assertIn("promoted to verified empirical capability", audit_result.promotions_detected[0]["violation"])

    def test_executive_dossier_cq68_72(self):
        """CQ-68 to CQ-72: Full 360° Tri-Store Executive Dossier compiles all 5 domains and evidence anchors."""
        query = "Provide a full 360-degree executive business and capability dossier for Albacore Ghostfin UUV."
        answer = answer_query(query, self.auth_context)

        self.assertEqual(answer.route_profile, "ROUTE_ALL_TRI_STORE")
        self.assertIsNotNone(answer.executive_dossier)

        dossier = answer.executive_dossier
        # Section 1: Corporate Profile (Org-KG)
        self.assertEqual(dossier.corporate_summary.get("legal_name"), "Albacore")
        self.assertEqual(dossier.corporate_summary.get("cage_code"), "0QSF0")

        # Section 2: Technical Capabilities (Tech-KG)
        self.assertIn("Ghostfin", dossier.technology_summary.get("offering_name"))
        self.assertIn("TRL 6", dossier.technology_summary.get("readiness_maturity"))
        self.assertIn("1000 nautical miles", dossier.technology_summary.get("operational_range"))
        self.assertGreaterEqual(len(dossier.technology_summary.get("participated_exercises", [])), 2)

        # Section 3: CRM Intake (CRM-Graph)
        self.assertEqual(dossier.crm_intake_summary.get("vulcan_submission_id"), "26705")
        self.assertEqual(dossier.crm_intake_summary.get("twenty_crm_pipeline_stage"), "Triaged")
        self.assertIn("Cameron Matthews", dossier.crm_intake_summary.get("technical_sponsor"))
        self.assertEqual(dossier.crm_intake_summary.get("q5_funding_to_scale"), "$5M-10M")

        # Section 4: Procurement Past Performance (Spine)
        self.assertIn("0.00", dossier.procurement_history.get("total_obligated_amount"))

        # Section 5: Epistemic Integrity
        self.assertEqual(dossier.epistemic_audit_summary.get("epistemic_fidelity"), "STRICT_SEPARATION_ENFORCED")

        # Citations completeness
        self.assertGreaterEqual(len(answer.citations), 5)

    def test_fail_closed_gates_cq76_module_disabled(self):
        """CQ-76: Node Capability Dependency Gate cleanly refuses queries for disabled modules."""
        restricted_context = CallerContext(
            caller_role="analyst",
            clearance_level="SECRET",
            enabled_modules=["organization_graph"]  # technology_graph disabled!
        )
        tech_query = "What is Ghostfin's TRL and operational range?"
        answer = answer_query(tech_query, restricted_context)

        self.assertEqual(answer.status, "MODULE_UNAVAILABLE")
        self.assertEqual(len(answer.structured_facts), 0)
        self.assertIn("CQ-76", answer.answer_text)
        self.assertIn("Module Unavailable", answer.answer_text)

    def test_fail_closed_gates_cq77_clearance_denial(self):
        """CQ-77: Mandatory RBAC/ABAC Gate cleanly refuses queries exceeding caller clearance."""
        unclass_context = CallerContext(
            caller_role="guest-evaluator",
            clearance_level="UNCLASSIFIED",
            enabled_modules=["organization_graph"]
        )
        pii_query = "What is the primary vendor POC personal phone number for Dante Vaisbort?"
        answer = answer_query(pii_query, unclass_context)

        self.assertEqual(answer.status, "ACCESS_DENIED")
        self.assertEqual(len(answer.structured_facts), 0)
        self.assertIn("CQ-77", answer.answer_text)
        self.assertIn("Access Denied", answer.answer_text)

    def test_fail_closed_gates_cq78_out_of_scope(self):
        """CQ-78: MEIA Operational Boundary Gate cleanly refuses non-defense / out-of-scope queries."""
        out_of_scope_q = "What is Ghostfin's acoustic signature decibel rating at 30 knots?"
        answer = answer_query(out_of_scope_q, self.auth_context)

        self.assertEqual(answer.status, "OUT_OF_SCOPE")
        self.assertEqual(len(answer.structured_facts), 0)
        self.assertIn("CQ-78", answer.answer_text)
        self.assertIn("Out of Scope", answer.answer_text)


if __name__ == "__main__":
    unittest.main()
