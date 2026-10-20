"""
Unit and Integration Test Suite for Tri-Graph Lineage and Topology Explorer:
- Graph Lineage assembly in AnswerRouteBundle & GroundedAnswer
- Explicit multi-graph provenance (Org-KG, Tech-KG, CRM-Graph, Cross-Graph Spine)
- Visual asset filtering (no static Charter Memo fallback)
- API endpoint GET /api/graph/overview
"""

import json
import threading
import time
import unittest
import urllib.request
from http.server import HTTPServer
from pathlib import Path

import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.answer_routes import assemble_answer_route
from src.grounded_answer import GroundedAnswerComposer
from src.pre_retrieval import CallerContext
from src.web import MeiaWebHandler


class TestTriGraphLineage(unittest.TestCase):
    """Verifies Tri-Graph Lineage extraction, serialization, and overview API."""

    @classmethod
    def setUpClass(cls):
        cls.test_port = 8098
        cls.server = HTTPServer(("127.0.0.1", cls.test_port), MeiaWebHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_answer_route_bundle_contains_graph_lineage(self):
        """Verifies assemble_answer_route packages structured graph_lineage."""
        bundle = assemble_answer_route(
            query="What is Ghostfin's TRL and battery endurance?",
            context=CallerContext(clearance_level="SECRET")
        )
        self.assertIsNotNone(bundle.graph_lineage)
        self.assertIn("summary", bundle.graph_lineage)
        self.assertIn("nodes", bundle.graph_lineage)
        self.assertIn("edges", bundle.graph_lineage)
        self.assertIn("claims", bundle.graph_lineage)

        summary = bundle.graph_lineage["summary"]
        self.assertGreater(summary.get("total_nodes", 0), 0)
        self.assertIn("TECH", summary.get("domain_breakdown", {}))

    def test_graph_lineage_node_and_edge_schema(self):
        """Verifies each node and edge in graph_lineage has required domain provenance."""
        bundle = assemble_answer_route(
            query="Which organization evaluates Project Albacore under DIU?",
            context=CallerContext(clearance_level="SECRET")
        )
        lineage = bundle.graph_lineage
        nodes = lineage["nodes"]
        self.assertGreater(len(nodes), 0)

        for node in nodes:
            self.assertIn("node_id", node)
            self.assertIn("domain", node)
            self.assertIn(node["domain"], ("ORG", "TECH", "CRM"))
            self.assertIn("label", node)
            self.assertIn("category", node)
            self.assertIn("properties", node)

        edges = lineage["edges"]
        for edge in edges:
            self.assertIn("source", edge)
            self.assertIn("target", edge)
            self.assertIn("predicate", edge)
            self.assertIn("graph_domain", edge)
            self.assertIn("edge_kind", edge)
            self.assertIn(edge["edge_kind"], ("INTRA_DOMAIN", "CROSS_GRAPH_SPINE"))

    def test_visual_asset_filtering_skips_charter_memo(self):
        """Verifies queries do NOT fall back to MEIA Charter memo page 1."""
        bundle = assemble_answer_route(
            query="What is Project Albacore's propulsion architecture?",
            context=CallerContext(clearance_level="SECRET")
        )
        for asset in bundle.visual_assets:
            self.assertNotIn("meia_charter_2026_p1", str(asset).lower())
            if asset.get("doc_id") == "doc:meia_charter_2026":
                self.assertNotEqual(asset.get("page_ordinal"), 1)

    def test_grounded_answer_to_dict_includes_graph_lineage(self):
        """Verifies GroundedAnswer serialization preserves graph_lineage."""
        bundle = assemble_answer_route(
            query="Compare Klas Telecom TRX and Fluor thermal dissipation.",
            context=CallerContext(clearance_level="SECRET")
        )
        composer = GroundedAnswerComposer()
        answer = composer.compose(bundle)
        ans_dict = answer.to_dict()

        self.assertIn("graph_lineage", ans_dict)
        self.assertIn("summary", ans_dict["graph_lineage"])
        self.assertIn("nodes", ans_dict["graph_lineage"])
        self.assertIn("edges", ans_dict["graph_lineage"])
        self.assertIn("claims", ans_dict["graph_lineage"])

    def test_api_graph_overview_endpoint(self):
        """Verifies GET /api/graph/overview serves full 78 nodes, 74 edges, and claims."""
        url = f"http://127.0.0.1:{self.test_port}/api/graph/overview"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))

            self.assertIn("summary", data)
            self.assertIn("nodes", data)
            self.assertIn("edges", data)
            self.assertIn("claims", data)

            # Check full dataset counts
            self.assertEqual(data["summary"]["total_nodes"], 78)
            self.assertEqual(data["summary"]["total_edges"], 74)
            self.assertEqual(data["summary"]["domain_breakdown"]["ORG"], 38)
            self.assertEqual(data["summary"]["domain_breakdown"]["TECH"], 21)
            self.assertEqual(data["summary"]["domain_breakdown"]["CRM"], 19)

            # Check that cross-graph edges are present
            cross_edges = [e for e in data["edges"] if e.get("edge_kind") == "CROSS_GRAPH_SPINE"]
            self.assertEqual(len(cross_edges), 12)

            # Check claims ledger
            self.assertEqual(len(data["claims"]), 53)


if __name__ == "__main__":
    unittest.main()
