"""
Card 04 Scoped Hybrid Retrieval & Multimodal Answer Route Bundler Integration Test Suite
Validates Scoped FTS5 BM25, Scoped BGE-Large Dense Cosine Retrieval, Reciprocal Rank Fusion,
Cross-Graph Bridge Traversal, Epistemic Claim Ledger Grounding, and Multimodal Bundling.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.pre_retrieval import CallerContext, RoutingProfile, route_user_query
from src.hybrid_retriever import ScopedHybridRetriever, retrieve_hybrid_candidates
from src.answer_routes import AnswerRouteBundler, assemble_answer_route


class TestHybridTriGraphRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retriever = ScopedHybridRetriever()
        cls.bundler = AnswerRouteBundler()
        cls.auth_context = CallerContext(
            caller_role="meia-authorized-evaluator",
            clearance_level="SECRET",
            enabled_modules=["organization_graph", "technology_graph", "crm_graph", "evidence_graph"]
        )

    # -------------------------------------------------------------------------
    # 1. Scoped Sparse & Dense Retrieval Tests
    # -------------------------------------------------------------------------
    def test_scoped_sparse_search(self):
        """Verifies that FTS search respects domain scoping boundaries."""
        # Query for Albacore restricted to organization_graph
        org_results = self.retriever.search_sparse("Albacore", ["organization_graph"], top_k=5)
        self.assertGreaterEqual(len(org_results), 1)
        for r in org_results:
            self.assertEqual(r["domain"], "ORG", "Must only return ORG candidates when scoped to organization_graph")

        # Query for Ghostfin restricted to technology_graph
        tech_results = self.retriever.search_sparse("Ghostfin", ["technology_graph"], top_k=5)
        self.assertGreaterEqual(len(tech_results), 1)
        for r in tech_results:
            self.assertEqual(r["domain"], "TECH", "Must only return TECH candidates when scoped to technology_graph")

        # Verify that an ORG query produces empty results when only crm_graph is enabled
        empty_check = self.retriever.search_sparse("Fluor", ["crm_graph"], top_k=5)
        self.assertTrue(all(r["domain"] == "CRM" for r in empty_check))

    def test_scoped_dense_search(self):
        """Verifies dense cosine retrieval returns bounded similarity scores and respects target_graph."""
        dense_results = self.retriever.search_dense("undersea hybrid electric autonomous UUV", ["technology_graph"], top_k=5)
        self.assertGreaterEqual(len(dense_results), 1)
        top = dense_results[0]
        self.assertIn("raw_score", top)
        self.assertGreaterEqual(top["raw_score"], 0.10)
        self.assertLessEqual(top["raw_score"], 1.0)
        for r in dense_results:
            self.assertEqual(r["domain"], "TECH", "Dense matches must belong to allowed TECH domain")

    def test_reciprocal_rank_fusion(self):
        """Verifies RRF computes valid 1/(60+r) scores and sorts descending."""
        sparse_mock = [{"id": "item_1", "domain": "TECH", "type": "domain_node", "text": "t1"}]
        dense_mock = [{"id": "item_2", "domain": "TECH", "type": "domain_node", "text": "t2"},
                      {"id": "item_1", "domain": "TECH", "type": "domain_node", "text": "t1"}]

        fused = self.retriever.reciprocal_rank_fusion(sparse_mock, dense_mock, k=60, top_k=5)
        self.assertGreaterEqual(len(fused), 2)
        # item_1 is in both (sparse rank 1, dense rank 2) -> highest score: 1/61 + 1/62
        self.assertEqual(fused[0].candidate_id, "item_1")
        expected_score = round((1.0 / 61) + (1.0 / 62), 5)
        self.assertEqual(fused[0].score, expected_score)
        self.assertEqual(fused[0].sparse_rank, 1)
        self.assertEqual(fused[0].dense_rank, 2)

    # -------------------------------------------------------------------------
    # 2. Multimodal Answer Route Bundling Across Profiles
    # -------------------------------------------------------------------------
    def test_answer_bundle_org_standalone(self):
        """CQ-01/02: Standalone Organization query returns corporate node, CAGE, and cell citations."""
        query = "What is Albacore's CAGE code and physical headquarters address?"
        bundle = assemble_answer_route(query, self.auth_context)

        self.assertEqual(bundle.status, "SUPPORTED")
        self.assertEqual(bundle.route_profile, "ROUTE_ORG")
        ent_ids = {e["id"] for e in bundle.primary_entities}
        self.assertIn("org:albacore", ent_ids)

        albacore = next(e for e in bundle.primary_entities if e["id"] == "org:albacore")
        self.assertEqual(albacore["properties"].get("cage"), "0QSF0")
        self.assertIn("New York", albacore["properties"].get("city", ""))

        # Check cell locators present
        self.assertGreaterEqual(len(bundle.cell_citations), 1)
        self.assertTrue(any("Vulcan Submissions" in c for c in bundle.cell_citations))

    def test_answer_bundle_tech_standalone(self):
        """CQ-19/29: Standalone Technology query returns offering node, TRL, Q3 metrics, and visual figures."""
        query = "What is Ghostfin's TRL and operational range?"
        bundle = assemble_answer_route(query, self.auth_context)

        self.assertEqual(bundle.status, "SUPPORTED")
        self.assertEqual(bundle.route_profile, "ROUTE_TECH")
        ent_ids = {e["id"] for e in bundle.primary_entities}
        self.assertIn("tech:ghostfin_uuv", ent_ids)

        # Check claims
        claims_map = {c["predicate"]: c["value"] for c in bundle.epistemic_claims}
        self.assertIn("has_readiness_trl", claims_map)
        self.assertEqual(claims_map.get("has_readiness_trl"), "6")
        self.assertIn("range_nmi", claims_map)
        self.assertEqual(claims_map.get("range_nmi"), "1000 nautical miles")

        # Check visual diagrams with BBox chips
        self.assertGreaterEqual(len(bundle.visual_assets), 1)
        first_asset = bundle.visual_assets[0]
        self.assertIn("figure_image", first_asset)
        self.assertIn("sample_chips", first_asset)

    def test_answer_bundle_crm_standalone(self):
        """CQ-37/42: Standalone CRM query returns submission node, stage, and Q5 funding."""
        query = "What is the Twenty CRM pipeline stage and funding request for Vulcan submission 26705?"
        bundle = assemble_answer_route(query, self.auth_context)

        self.assertEqual(bundle.status, "SUPPORTED")
        self.assertEqual(bundle.route_profile, "ROUTE_CRM")
        ent_ids = {e["id"] for e in bundle.primary_entities}
        self.assertIn("crm:submission_26705", ent_ids)

        sub = next(e for e in bundle.primary_entities if e["id"] == "crm:submission_26705")
        self.assertEqual(sub["properties"].get("current_pipeline_stage"), "Triaged")
        self.assertEqual(sub["properties"].get("security_preference"), "SECRET // REL FVEY")

    def test_answer_bundle_org_tech_join(self):
        """CQ-51: Pairwise Org ⋈ Tech join traverses [:DEVELOPS_OFFERING]."""
        query = "Which U.S. Small Business startups offer technologies aligned to Counter C5ISR-T with current TRL >= 6?"
        bundle = assemble_answer_route(query, self.auth_context)

        self.assertEqual(bundle.status, "SUPPORTED")
        self.assertEqual(bundle.route_profile, "ROUTE_ORG_TECH")
        predicates = {b["predicate"] for b in bundle.cross_graph_bridges}
        self.assertIn("[:DEVELOPS_OFFERING]", predicates)

        ent_ids = {e["id"] for e in bundle.primary_entities}
        self.assertIn("org:albacore", ent_ids)
        self.assertIn("tech:ghostfin_uuv", ent_ids)

    def test_answer_bundle_crm_org_join(self):
        """CQ-58: Pairwise CRM ⋈ Org join traverses [:SUBMITTED_BY_ORG]."""
        query = "For all submissions in the CRM, which submitting vendors have complete federal registration CAGE and UEI?"
        bundle = assemble_answer_route(query, self.auth_context)

        self.assertEqual(bundle.status, "SUPPORTED")
        self.assertEqual(bundle.route_profile, "ROUTE_CRM_ORG")
        predicates = {b["predicate"] for b in bundle.cross_graph_bridges}
        self.assertIn("[:SUBMITTED_BY_ORG]", predicates)

    def test_answer_bundle_crm_tech_join(self):
        """CQ-63: Pairwise CRM ⋈ Tech join traverses [:EVALUATES_OFFERING]."""
        query = "Which capabilities in the CRM portfolio combine high TRL and MRL with Government Purpose Rights or CRADA?"
        bundle = assemble_answer_route(query, self.auth_context)

        self.assertEqual(bundle.status, "SUPPORTED")
        self.assertEqual(bundle.route_profile, "ROUTE_CRM_TECH")
        predicates = {b["predicate"] for b in bundle.cross_graph_bridges}
        self.assertIn("[:EVALUATES_OFFERING]", predicates)

    def test_answer_bundle_360_dossier(self):
        """CQ-68: Full 360° Tri-Store Executive Dossier aggregates all 3 domains, cell locators, and visual figures."""
        query = "Generate a complete MEIA Executive Business & Capability Dossier for Ghostfin: Long-Range, Hybrid Electric Medium UUV"
        bundle = assemble_answer_route(query, self.auth_context)

        self.assertEqual(bundle.status, "SUPPORTED")
        self.assertEqual(bundle.route_profile, "ROUTE_ALL_TRI_STORE")

        # Verify all 3 domains represented in primary entities
        domains = {e["graph_domain"] for e in bundle.primary_entities}
        self.assertIn("ORG", domains)
        self.assertIn("TECH", domains)
        self.assertIn("CRM", domains)

        # Verify cross-graph bridges
        self.assertGreaterEqual(len(bundle.cross_graph_bridges), 2)

        # Verify cell citations > 50 (captures full Vulcan row)
        self.assertGreaterEqual(len(bundle.cell_citations), 50)

        # Verify claims and visual assets
        self.assertGreaterEqual(len(bundle.epistemic_claims), 10)
        self.assertGreaterEqual(len(bundle.visual_assets), 1)

    def test_answer_bundle_fail_closed(self):
        """CQ-76/77/78: Security and scope gates produce clean fail-closed bundles without graph execution."""
        # 1. Disabled Module Gate (CQ-76)
        restricted_context = CallerContext(
            caller_role="analyst",
            clearance_level="SECRET",
            enabled_modules=["organization_graph"]  # tech disabled!
        )
        tech_q = "What is Ghostfin's TRL and operational range?"
        bundle_disabled = assemble_answer_route(tech_q, restricted_context)
        self.assertEqual(bundle_disabled.status, "INSUFFICIENT_DEPLOYED_CAPABILITY")
        self.assertEqual(len(bundle_disabled.primary_entities), 0)

        # 2. Access Control Gate (CQ-77)
        unauth_context = CallerContext(caller_role="guest", clearance_level="UNCLASSIFIED")
        pii_q = "What is Dante Vaisbort's personal cell phone number?"
        bundle_pii = assemble_answer_route(pii_q, unauth_context)
        self.assertEqual(bundle_pii.status, "ACCESS_DENIED")
        self.assertEqual(len(bundle_pii.primary_entities), 0)

        # 3. Out-of-Scope Gate (CQ-78)
        oos_q = "What is Ghostfin's acoustic signature decibel rating at 30 knots?"
        bundle_oos = assemble_answer_route(oos_q, self.auth_context)
        self.assertEqual(bundle_oos.status, "OUT_OF_SCOPE")
        self.assertEqual(len(bundle_oos.primary_entities), 0)


if __name__ == "__main__":
    unittest.main()
