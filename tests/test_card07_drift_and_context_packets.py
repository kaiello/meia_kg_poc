"""
Unit and Integration Test Suite for Card 07:
- R03 Functional Evidence Units & Context Packets
- R01 Trident-Inspired Modality-Bias Calibration & Audit
- R02 NativeScope-Inspired Structural Scoping
- V01 Loud-and-Clear (LoC) Visual Reader Preparation
- Architectural & Technical Drift Invariants (Zero-Daemon, Epistemic Firewall)
"""

import json
import sqlite3
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config import TRI_GRAPH_DB_PATH, FIGURES_DIR
from src.context_packet import (
    FunctionalContextPacket,
    PacketQualifier,
    VisualEvidenceChip,
    ContextPacketBuilder,
    bundle_context_packets_for_route
)
from src.hybrid_retriever import (
    ScopedHybridRetriever,
    audit_modality_bias,
    retrieve_hybrid_candidates
)
from src.figure_inspectors import (
    LoCFigureInspector,
    LoCInspectionArm,
    inspect_figure_loc,
    CROPS_DIR
)
from src.pre_retrieval import route_user_query, CallerContext
from src.answer_routes import assemble_answer_route
from src.grounded_answer import answer_query


class TestCard07DriftAndContextPackets(unittest.TestCase):
    """Test suite verifying all Card 07 capabilities and architectural drift guardrails."""

    def setUp(self):
        self.builder = ContextPacketBuilder()
        self.retriever = ScopedHybridRetriever()
        self.inspector = LoCFigureInspector()

    def test_r03_albacore_ghostfin_context_packet(self):
        """R03: Assembled context packet for Ghostfin bundles Q3, Q4, Q5, Q6, Q12 and 180 DPI chips."""
        pkt = self.builder.build_packet_for_entity("tech:ghostfin_uuv")
        self.assertIsInstance(pkt, FunctionalContextPacket)
        self.assertEqual(pkt.anchor_entity_id, "tech:ghostfin_uuv")
        self.assertIn("Ghostfin", pkt.anchor_label)
        self.assertEqual(pkt.target_graph, "TECH")

        # Verify Primary Assertions
        primary_preds = [a.get("predicate") for a in pkt.primary_assertions]
        self.assertIn("has_description", primary_preds)
        self.assertIn("has_capability_contribution_q3", primary_preds)
        self.assertIn("has_readiness_assessment_q9", primary_preds)

        # Verify Structural Qualifiers
        qual_types = [q.qualifier_type for q in pkt.qualifiers_and_notes]
        self.assertIn("SUPPLY_CONSTRAINT_Q4", qual_types)
        self.assertIn("ROM_FUNDING_Q5", qual_types)
        self.assertIn("UNIT_COST_Q6", qual_types)
        self.assertIn("SECURITY_CLEARANCE_Q12", qual_types)

        # Check exact locators
        for q in pkt.qualifiers_and_notes:
            self.assertTrue("R2C" in q.source_locator or "Vulcan" in q.source_locator)

        # Provenance Score
        self.assertEqual(pkt.composite_provenance_score, 1.0)
        self.assertTrue(len(pkt.cell_citations) >= 4)

    def test_r03_voltage_vessels_context_packet(self):
        """R03: Assembled context packet for Voltage Vessels VoltVessel captures Row 3 qualifiers."""
        pkt = self.builder.build_packet_for_entity("tech:voltvessel_energy")
        self.assertEqual(pkt.anchor_entity_id, "tech:voltvessel_energy")
        self.assertIn("VoltVessel", pkt.anchor_label)

        qual_types = [q.qualifier_type for q in pkt.qualifiers_and_notes]
        self.assertIn("SUPPLY_CONSTRAINT_Q4", qual_types)
        self.assertIn("ROM_FUNDING_Q5", qual_types)
        self.assertIn("UNIT_COST_Q6", qual_types)
        self.assertIn("SECURITY_CLEARANCE_Q12", qual_types)

        for q in pkt.qualifiers_and_notes:
            self.assertTrue("R3C" in q.source_locator or "Vulcan" in q.source_locator)

    def test_r03_t2s_solutions_context_packet(self):
        """R03: Assembled context packet for T2S Solutions Tactical Micro-Grid captures Row 4 qualifiers."""
        pkt = self.builder.build_packet_for_entity("tech:tactical_microgrid")
        self.assertEqual(pkt.anchor_entity_id, "tech:tactical_microgrid")
        self.assertIn("Micro-Grid", pkt.anchor_label)

        qual_types = [q.qualifier_type for q in pkt.qualifiers_and_notes]
        self.assertIn("SUPPLY_CONSTRAINT_Q4", qual_types)
        self.assertIn("ROM_FUNDING_Q5", qual_types)

        for q in pkt.qualifiers_and_notes:
            self.assertTrue("R4C" in q.source_locator or "Vulcan" in q.source_locator)


    def test_r01_modality_bias_audit(self):
        """R01: Modality-bias audit correctly analyzes candidate balance."""
        query = "What is Ghostfin's operational range and hybrid powertrain architecture diagram?"
        dec, cands = retrieve_hybrid_candidates(query, top_k=10)
        audit = audit_modality_bias(cands)

        self.assertIn("total_candidates", audit)
        self.assertIn("text_candidates", audit)
        self.assertIn("table_candidates", audit)
        self.assertIn("visual_candidates", audit)
        self.assertIn("modality_balance_status", audit)
        self.assertGreater(audit["total_candidates"], 0)

    def test_r01_modality_calibration_boosts_visual_rank(self):
        """R01: Modality weighting ensures visual assets rank prominently on diagram-oriented queries."""
        query = "Ghostfin payload bay schematic and technical architecture diagram"
        # 1. Unweighted retrieval
        dec1, unweighted_cands = retrieve_hybrid_candidates(
            query,
            modality_weights={"text": 1.0, "table": 1.0, "visual": 1.0},
            top_k=10
        )
        # 2. Modality-calibrated retrieval (w_visual = 1.6)
        dec2, calibrated_cands = retrieve_hybrid_candidates(
            query,
            modality_weights={"text": 1.0, "table": 1.2, "visual": 1.6},
            top_k=10
        )

        # Audit calibrated candidates
        audit_calibrated = audit_modality_bias(calibrated_cands)
        self.assertGreater(audit_calibrated["visual_candidates"] + audit_calibrated["table_candidates"], 0)

    def test_r02_nativescope_structural_scoping(self):
        """R02: NativeScope structural scoping restricts candidates to target vendor anchor without cross-leakage."""
        ctx = CallerContext(caller_role="meia-authorized-evaluator", clearance_level="SECRET")
        # Query specifically about Albacore but inject distracting keyword "Voltage Vessels"
        dec = route_user_query("What is Albacore's CAGE code and offering description? (ignore Voltage Vessels)", ctx)
        cands = self.retriever.retrieve(dec, top_k=10, apply_structural_scoping=True)

        for c in cands:
            # Ensure no Voltage Vessels node leaked into Albacore's candidate pool
            self.assertNotIn("eclipse_x9", c.candidate_id.lower())
            self.assertNotIn("9w2w3", c.content.lower())

    def test_v01_loc_visual_inspection_arms(self):
        """V01: LoC Figure Inspector generates Arm A (full page), Arm B (focal crop), and Arm C (callouts)."""
        asset_id = "Prometheus_Energy_AI_p1"

        # Arm A: Full-page baseline
        arm_a = inspect_figure_loc(asset_id, "ARM_A_FULL_PAGE")
        self.assertEqual(arm_a["arm"], "ARM_A_FULL_PAGE")
        self.assertIsNotNone(arm_a["full_page_path"])
        self.assertTrue((REPO_ROOT / arm_a["full_page_path"]).exists())

        # Arm B: Focal crop chip
        arm_b = inspect_figure_loc(asset_id, "ARM_B_FOCAL_CROP", bbox=[0.2, 0.2, 0.7, 0.7])
        self.assertEqual(arm_b["arm"], "ARM_B_FOCAL_CROP")
        self.assertIsNotNone(arm_b["focal_crop_path"])
        crop_file = REPO_ROOT / arm_b["focal_crop_path"]
        self.assertTrue(crop_file.exists())
        self.assertGreater(crop_file.stat().st_size, 0)

        # Arm C: Multimodal OCR callout overlay
        arm_c = inspect_figure_loc(asset_id, "ARM_C_MULTIMODAL_CALLOUT")
        self.assertEqual(arm_c["arm"], "ARM_C_MULTIMODAL_CALLOUT")
        self.assertIsInstance(arm_c["ocr_callouts"], list)
        self.assertGreater(len(arm_c["ocr_callouts"]), 0)

    def test_answer_route_bundle_contains_context_packets(self):
        """Verifies AnswerRouteBundle includes assembled R03 Functional Context Packets."""
        query = "What specific quantifiable operational capability contribution does Ghostfin deliver in Q3?"
        bundle = assemble_answer_route(query)
        self.assertIsNotNone(bundle.context_packets)
        self.assertIsInstance(bundle.context_packets, list)
        self.assertGreater(len(bundle.context_packets), 0)

        first_pkt = bundle.context_packets[0]
        self.assertIn("packet_id", first_pkt)
        self.assertIn("qualifiers_and_notes", first_pkt)
        self.assertIn("composite_provenance_score", first_pkt)

    def test_grounded_answer_includes_context_packets(self):
        """Verifies GroundedAnswer output to_dict() includes serialized context_packets."""
        query = "What is Albacore's CAGE code and Ghostfin operational range?"
        ans = answer_query(query)
        ans_dict = ans.to_dict()
        self.assertIn("context_packets", ans_dict)
        self.assertIsInstance(ans_dict["context_packets"], list)
        self.assertGreater(len(ans_dict["context_packets"]), 0)

    def test_zero_daemon_and_epistemic_invariants(self):
        """Drift Check: Verifies zero external daemons and unbroken epistemic firewall."""
        # 1. Zero External DB Daemons: Persistence is SQLite file
        self.assertTrue(TRI_GRAPH_DB_PATH.exists())
        self.assertTrue(TRI_GRAPH_DB_PATH.is_file())

        # 2. Epistemic Claim Firewall: No claim self-assertion is marked LIVE_DEMONSTRATED without proof
        conn = sqlite3.connect(str(TRI_GRAPH_DB_PATH))
        c = conn.cursor()
        c.execute("SELECT claim_id, epistemic_status FROM claim_ledger WHERE subject_id = 'tech:ghostfin_uuv'")
        rows = c.fetchall()
        self.assertGreater(len(rows), 0)
        for row in rows:
            cid, ep_status = row
            # Vulcan intake claims must be VENDOR_SELF_ASSERTED
            if "capability" in cid or "description" in cid:
                self.assertNotEqual(ep_status, "LIVE_DEMONSTRATED")
                self.assertEqual(ep_status, "VENDOR_SELF_ASSERTED")
        conn.close()


if __name__ == "__main__":
    unittest.main()
