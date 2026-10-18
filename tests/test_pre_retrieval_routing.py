"""
Card 03 Pre-Retrieval 8-Profile Router & SKOS Expander Integration Test Suite
Validates minimum-sufficient graph routing, SKOS acronym expansions, entity resolution,
and fail-closed policy gates across the MEIA 78 Competency Questions Catalog.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.pre_retrieval import (
    PreRetrievalRouter,
    RoutingProfile,
    CallerContext,
    RoutingDecision,
    route_user_query
)


class TestPreRetrievalRouting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.router = PreRetrievalRouter()
        cls.auth_context = CallerContext(
            caller_role="meia-authorized-evaluator",
            clearance_level="SECRET",
            enabled_modules=["organization_graph", "technology_graph", "crm_graph", "evidence_graph"]
        )

    # -------------------------------------------------------------------------
    # Profile A: Organization Graph Standalone (CQs 01-18)
    # -------------------------------------------------------------------------
    def test_route_org_profile_a(self):
        queries = [
            "What is the legal business name, corporate website, and country of incorporation for Albacore?",
            "Which federal identifiers UEI, CAGE code, and DUNS number are recorded for Voltage Vessels?",
            "What is the complete physical headquarters address of Fluor Federal Services?",
            "Is Klas Government foreign-owned, foreign-controlled, or flagged for FOCI?",
            "What is Fluor's total all-time federal prime spending and annual obligation trend by fiscal year?"
        ]
        for q in queries:
            dec = self.router.route_query(q, self.auth_context)
            self.assertEqual(dec.route_profile, RoutingProfile.ROUTE_ORG, f"Failed on query: {q}")
            self.assertEqual(dec.status, "SUPPORTED")
            self.assertEqual(dec.selected_modules, ["organization_graph"], f"Failed module scoping for: {q}")

    # -------------------------------------------------------------------------
    # Profile B: Technology & Mission Graph Standalone (CQs 19-36)
    # -------------------------------------------------------------------------
    def test_route_tech_profile_b(self):
        queries = [
            "What is the canonical name, version series, and offering type of Ghostfin?",
            "What core technical differentiator distinguishes Ghostfin's engineering design?",
            "Which active MEIA Topic Area does the capability align to?",
            "What specific quantifiable operational capability contribution does Ghostfin deliver in Q3?",
            "What are the recorded TRL, MRL, and IRL values for VoltVessel?"
        ]
        for q in queries:
            dec = self.router.route_query(q, self.auth_context)
            self.assertEqual(dec.route_profile, RoutingProfile.ROUTE_TECH, f"Failed on query: {q}")
            self.assertEqual(dec.status, "SUPPORTED")
            self.assertEqual(dec.selected_modules, ["technology_graph"], f"Failed module scoping for: {q}")

    # -------------------------------------------------------------------------
    # Profile C: CRM Operational Graph Standalone (CQs 37-50)
    # -------------------------------------------------------------------------
    def test_route_crm_profile_c(self):
        queries = [
            "What submission identifier and submitted timestamp are recorded for Vulcan submission 26705?",
            "What is the current Twenty CRM pipeline stage and 48-hour callback timer state?",
            "Who is the primary vendor point of contact POC 1 for Albacore?",
            "What is the vendor's One-on-One Meeting Security Preference in Q12 for Ghostfin?",
            "What funding tier is requested by the vendor to scale production in Q5 Funding to Scale?",
            "What current unit cost and projected unit cost are recorded in Q6 Unit Cost?"
        ]
        for q in queries:
            dec = self.router.route_query(q, self.auth_context)
            self.assertEqual(dec.route_profile, RoutingProfile.ROUTE_CRM, f"Failed on query: {q}")
            self.assertEqual(dec.status, "SUPPORTED")
            self.assertEqual(dec.selected_modules, ["crm_graph"], f"Failed module scoping for: {q}")

    # -------------------------------------------------------------------------
    # Profile D1: 2-Way Federated Join — Org ⋈ Tech (CQs 51-57)
    # -------------------------------------------------------------------------
    def test_route_org_tech_profile_d1(self):
        queries = [
            "Which U.S. Small Business startups offer technologies aligned to Counter C5ISR-T with current TRL >= 6?",
            "How do an organization's historical federal NAICS and PSC codes align with the EDA OSRA Technology Building Blocks?",
            "Which organizations offering C5ISR tactical networking carry FOCI indicators?",
            "Which technologies originated in an SBIR transitioning to sole source operational contracts?"
        ]
        for q in queries:
            dec = self.router.route_query(q, self.auth_context)
            self.assertEqual(dec.route_profile, RoutingProfile.ROUTE_ORG_TECH, f"Failed on query: {q}")
            self.assertEqual(dec.status, "SUPPORTED")
            self.assertEqual(set(dec.selected_modules), {"organization_graph", "technology_graph"}, f"Failed modules for: {q}")

    # -------------------------------------------------------------------------
    # Profile D2: 2-Way Federated Join — CRM ⋈ Org (CQs 58-62)
    # -------------------------------------------------------------------------
    def test_route_crm_org_profile_d2(self):
        queries = [
            "For all submissions in the CRM, which submitting vendors have complete federal registration CAGE and UEI?",
            "How does a vendor's requested scaling funding in CRM compare against historical federal prime award volume?",
            "Which submissions requesting classified one-on-one meetings involve organizations with socioeconomic preferences or FOCI?",
            "Which government technical POCs named on a CRM submission belong to agencies that previously contracted with the vendor?"
        ]
        for q in queries:
            dec = self.router.route_query(q, self.auth_context)
            self.assertEqual(dec.route_profile, RoutingProfile.ROUTE_CRM_ORG, f"Failed on query: {q}")
            self.assertEqual(dec.status, "SUPPORTED")
            self.assertEqual(set(dec.selected_modules), {"crm_graph", "organization_graph"}, f"Failed modules for: {q}")

    # -------------------------------------------------------------------------
    # Profile D3: 2-Way Federated Join — CRM ⋈ Tech (CQs 63-67)
    # -------------------------------------------------------------------------
    def test_route_crm_tech_profile_d3(self):
        queries = [
            "Which capabilities in the CRM portfolio combine high TRL and MRL with Government Purpose Rights or CRADA?",
            "How do the unit cost and production rate projections relate to Manufacturing Readiness Level MRL and COTS architecture?",
            "Which capabilities that completed live operational field experimentation at SONIC SPEAR 26 are candidates for Joint Acceleration Reserve scale funding?",
            "Which submitted capabilities satisfy Contested Logistics and can be briefed at an UNCLASSIFIED level?"
        ]
        for q in queries:
            dec = self.router.route_query(q, self.auth_context)
            self.assertEqual(dec.route_profile, RoutingProfile.ROUTE_CRM_TECH, f"Failed on query: {q}")
            self.assertEqual(dec.status, "SUPPORTED")
            self.assertEqual(set(dec.selected_modules), {"crm_graph", "technology_graph"}, f"Failed modules for: {q}")

    # -------------------------------------------------------------------------
    # Profile D4: 3-Way Tri-Store Executive Dossiers (CQs 68-72)
    # -------------------------------------------------------------------------
    def test_route_all_tri_store_dossier_profile_d4(self):
        queries = [
            "Generate a complete MEIA Executive Business & Capability Dossier for Ghostfin: Long-Range, Hybrid Electric Medium UUV",
            "Generate a complete MEIA Executive Business & Capability Dossier for Eclipse X9 Distributed Composite Manufacturing for Austere Logistics",
            "Generate a complete MEIA Executive Business & Capability Dossier for Counter Sensing T2S Solutions",
            "Produce a complete business and capability assessment report for Prometheus Torch and Fluor Federal Services"
        ]
        for q in queries:
            dec = self.router.route_query(q, self.auth_context)
            self.assertEqual(dec.route_profile, RoutingProfile.ROUTE_ALL_TRI_STORE, f"Failed on query: {q}")
            self.assertEqual(dec.status, "SUPPORTED")
            expected_mods = {"organization_graph", "technology_graph", "crm_graph", "evidence_graph"}
            self.assertEqual(set(dec.selected_modules), expected_mods, f"Dossier must select all 4 modules for: {q}")

    # -------------------------------------------------------------------------
    # Profile D5: Guarded Policy & Fail-Closed Security Gates (CQs 73-78)
    # -------------------------------------------------------------------------
    def test_fail_closed_gates_profile_d5(self):
        # CQ-76: Disabled Module Gate (Fails closed when required module is omitted)
        restricted_context = CallerContext(
            caller_role="analyst",
            clearance_level="SECRET",
            enabled_modules=["organization_graph"]  # technology_graph disabled!
        )
        tech_query = "What is Ghostfin's TRL and operational range?"
        dec_disabled = self.router.route_query(tech_query, restricted_context)
        self.assertEqual(dec_disabled.status, "INSUFFICIENT_DEPLOYED_CAPABILITY")
        self.assertIn("disabled", dec_disabled.reasons[0].lower())

        # CQ-77: Unauthenticated PII Access Control Gate
        unauth_context = CallerContext(
            caller_role="guest",
            clearance_level="UNCLASSIFIED"
        )
        pii_query = "What is the primary vendor POC personal phone number for Dante Vaisbort?"
        dec_pii = self.router.route_query(pii_query, unauth_context)
        self.assertEqual(dec_pii.status, "ACCESS_DENIED")
        self.assertIn("pii", dec_pii.reasons[0].lower())

        # CQ-77: Classified Security Clearance Gate
        cleared_query = "What are the classified meeting details and TOP SECRET // SCI (4-Pack) requirements?"
        dec_clearance = self.router.route_query(cleared_query, unauth_context)
        self.assertEqual(dec_clearance.status, "ACCESS_DENIED")
        self.assertIn("clearance", dec_clearance.reasons[0].lower())

        # CQ-78: Out-of-Scope & Unrecorded Fact Gate
        out_of_scope_q = "What is Ghostfin's acoustic signature decibel rating at 30 knots?"
        dec_oos = self.router.route_query(out_of_scope_q, self.auth_context)
        self.assertEqual(dec_oos.route_profile, RoutingProfile.FAIL_CLOSED_GATE)
        self.assertEqual(dec_oos.status, "OUT_OF_SCOPE")
        self.assertIn("out-of-scope", dec_oos.reasons[0].lower())

    # -------------------------------------------------------------------------
    # Entity Resolution & SKOS Expansion
    # -------------------------------------------------------------------------
    def test_entity_resolution(self):
        query = "What are the contracts for CAGE 0QSF0 and UEI NZ9CUMF36PK1 in Vulcan submission 26705 for Ghostfin?"
        resolved = self.router.resolve_entities(query)
        ids = {r["id"] for r in resolved}
        self.assertIn("org:albacore", ids)
        self.assertIn("org:fluor_federal", ids)
        self.assertIn("crm:submission_26705", ids)
        self.assertIn("tech:ghostfin_uuv", ids)

    def test_skos_acronym_expansion(self):
        query = "What is the UUV range and C5ISR-T alignment at TRL 6 for AFSIM mission simulations under FOCI?"
        expansions, clean_q = self.router.expand_acronyms(query)
        exp_text = " ".join(expansions)
        self.assertIn("Unmanned Underwater Vehicle", exp_text)
        self.assertIn("TBB-29", exp_text)
        self.assertIn("CounterC5ISRT", exp_text)
        self.assertIn("Technology Readiness Level", exp_text)
        self.assertIn("Advanced Framework for Simulation", exp_text)
        self.assertIn("Foreign Ownership, Control, or Influence", exp_text)


if __name__ == "__main__":
    unittest.main()
