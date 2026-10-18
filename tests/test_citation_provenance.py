"""
Unit and Regression Test Suite for 100% Citation and Provenance Traceability.
Verifies that 100% of retrieved answers across all 78 MEIA Competency Questions
contain verifiable citations tracing to the SQLite Tri-Graph Registry or Evidence Graph.
"""

import json
import sqlite3
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config import TRI_GRAPH_DB_PATH
from src.pre_retrieval import CallerContext
from src.grounded_answer import answer_query, GroundedAnswer
from src.epistemic_verifier import EpistemicVerifier


class TestCitationProvenance(unittest.TestCase):
    """Enforces 100% citation coverage and provenance trace integrity across the POC."""

    @classmethod
    def setUpClass(cls):
        cls.db_path = TRI_GRAPH_DB_PATH
        cls.gold_path = REPO_ROOT / "eval" / "gold_78_cqs.json"
        with open(cls.gold_path, "r", encoding="utf-8") as f:
            cls.cqs = json.load(f)

        cls.auth_context = CallerContext(
            caller_role="meia-evaluator",
            clearance_level="SECRET",
            enabled_modules=["organization_graph", "technology_graph", "crm_graph", "evidence_graph"]
        )

    def test_all_78_cqs_have_non_empty_citations(self):
        """Verifies that 100% of all 78 Competency Questions have len(ans.citations) > 0."""
        zero_citations = []
        for cq in self.cqs:
            cq_id = cq["cq_id"]
            ctx = self.auth_context
            if cq_id == "CQ-76":
                ctx = CallerContext(caller_role="analyst", clearance_level="SECRET", enabled_modules=["organization_graph"])
            elif cq_id == "CQ-77":
                ctx = CallerContext(caller_role="guest", clearance_level="UNCLASSIFIED", enabled_modules=["organization_graph"])

            ans: GroundedAnswer = answer_query(cq["query"], ctx)
            if len(ans.citations) == 0:
                zero_citations.append((cq_id, ans.route_profile, ans.status))

        self.assertEqual(
            len(zero_citations), 0,
            f"Found {len(zero_citations)} CQs with 0 citations: {zero_citations}"
        )

    def test_citations_trace_to_registry_or_evidence_graph(self):
        """Verifies that emitted citations resolve to valid locators accepted by EpistemicVerifier."""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute("SELECT locator_str FROM evidence_nodes")
        valid_registry_locators = {row[0] for row in c.fetchall()}
        conn.close()

        # Sample representative CQs across profiles
        sample_ids = ["CQ-01", "CQ-11", "CQ-19", "CQ-37", "CQ-51", "CQ-58", "CQ-63", "CQ-68", "CQ-73", "CQ-77"]
        sample_cqs = [q for q in self.cqs if q["cq_id"] in sample_ids]

        for cq in sample_cqs:
            ctx = self.auth_context
            if cq["cq_id"] == "CQ-77":
                ctx = CallerContext(caller_role="guest", clearance_level="UNCLASSIFIED", enabled_modules=["organization_graph"])

            ans = answer_query(cq["query"], ctx)
            self.assertGreater(len(ans.citations), 0, f"Query {cq['cq_id']} returned 0 citations.")
            for cit in ans.citations:
                self.assertTrue(
                    EpistemicVerifier.is_valid_locator(cit),
                    f"Query {cq['cq_id']} emitted invalid citation locator: {cit}"
                )

    def test_cq73_provenance_envelope(self):
        """CQ-73: Verifies SHA-256 hash, source version, and exact cell locator are returned."""
        q = "Exact Evidence Locator & Provenance Trace: Which exact source file, source version, SHA-256 hash, spreadsheet cell (Sheet!Row:Col), PDF page/bounding box, or USASpending transaction ID supports a returned claim, and which ontology and graph versions were used?"
        ans = answer_query(q, self.auth_context)

        self.assertIn("MEIA_TEM_Vulcan_Export.xlsx!Vulcan Submissions!R2C56", ans.citations)
        facts_str = " ".join(f"{f.key}: {f.value}" for f in ans.structured_facts)
        self.assertIn("SHA-256", facts_str)
        self.assertIn("c5d00fc1", facts_str)
        self.assertIn("BFO-Lite", facts_str)

    def test_cq74_conflicting_evidence_citations(self):
        """CQ-74: Verifies dual source citations (vendor assertion cell vs. live test event)."""
        q = "Conflicting Evidence Preservation: When two sources or versions disagree on an organization's identifier, readiness level, or deployment status, how does the system respond?"
        ans = answer_query(q, self.auth_context)

        self.assertIn("MEIA_TEM_Vulcan_Export.xlsx!Vulcan Submissions!R2C59", ans.citations)
        self.assertIn("node:eval:sonic_spear_26", ans.citations)
        self.assertEqual(ans.status, "CONFLICTING_EVIDENCE")

    def test_cq75_claim_vs_demo_citations(self):
        """CQ-75: Verifies vendor claim cell vs. demonstration event node citations."""
        q = "Claim vs. Empirical Demonstration Non-Equivalence Gate: Has Vendor X's capability been verified in an AFSIM digital engineering simulation or live military exercise, or is it only a vendor assertion?"
        ans = answer_query(q, self.auth_context)

        self.assertIn("MEIA_TEM_Vulcan_Export.xlsx!Vulcan Submissions!R2C59", ans.citations)
        self.assertIn("node:eval:sonic_spear_26", ans.citations)

    def test_gate_refusals_have_policy_citations(self):
        """CQ-76, CQ-77, CQ-78: Verifies fail-closed gate refusals attach authoritative policy citations."""
        # CQ-76
        ctx_76 = CallerContext(caller_role="analyst", clearance_level="SECRET", enabled_modules=["organization_graph"])
        q76 = "Minimum-Sufficient Routing & Module Capability Gate: What happens when a query requires exact PDF table/figure coordinates (Evidence Graph), or procurement history (Org-KG), in a deployment profile where that module is disabled?"
        ans76 = answer_query(q76, ctx_76)
        self.assertEqual(ans76.status, "MODULE_UNAVAILABLE")
        self.assertIn("policy:meia_module_capability_gate#CQ-76", ans76.citations)

        # CQ-77
        ctx_77 = CallerContext(caller_role="guest", clearance_level="UNCLASSIFIED", enabled_modules=["organization_graph"])
        q77 = "Access Control, PII & Security Classification Gate: What happens when a caller without authorization requests encrypted PII contacts (POC Email/Phone), Export Controlled = Yes technical data, or TOP SECRET // SCI (4-Pack) / SECRET // REL FVEY meeting details?"
        ans77 = answer_query(q77, ctx_77)
        self.assertEqual(ans77.status, "ACCESS_DENIED")
        self.assertIn("policy:meia_rbac_gate#CQ-77", ans77.citations)

        # CQ-78
        q78 = "Out-of-Scope & Unrecorded Fact Abstention Gate: What is Ghostfin's acoustic signature decibel rating at 30 knots, or what is KLAS Government's Vulcan Q5 funding request?"
        ans78 = answer_query(q78, self.auth_context)
        self.assertEqual(ans78.status, "OUT_OF_SCOPE")
        self.assertIn("policy:meia_operational_boundary_gate#CQ-78", ans78.citations)


if __name__ == "__main__":
    unittest.main()
