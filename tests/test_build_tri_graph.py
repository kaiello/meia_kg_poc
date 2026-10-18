"""
Card 02 Tri-Graph & Contextual Vector Indexing Integration Test Suite
Validates SQLite Tri-Graph Registry, FTS5 Search Tables, Epistemic Claim Ledger,
NetworkX GraphML Substrates, and Contextual 1024-d Dense Vector Stores.
"""

import json
import math
import sqlite3
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import networkx as nx

from src.config import (
    TRI_GRAPH_DB_PATH,
    ORG_GRAPHML_PATH,
    TECH_GRAPHML_PATH,
    CRM_GRAPHML_PATH,
    FEDERATED_GRAPHML_PATH,
    VDB_CHUNKS_PATH,
    VDB_ENTITIES_PATH,
    EMBEDDING_DIM
)
from src.contextual_indexer import encode_text, search_dense, compute_cosine_similarity


class TestTriGraphConstruction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(str(TRI_GRAPH_DB_PATH))
        cls.c = cls.conn.cursor()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_sqlite_schema_and_counts(self):
        """Verifies database tables exist and exceed minimum entity and edge thresholds."""
        self.assertTrue(TRI_GRAPH_DB_PATH.exists(), "Tri-Graph SQLite database must exist")

        # Check domain_nodes count
        self.c.execute("SELECT COUNT(*) FROM domain_nodes")
        node_count = self.c.fetchone()[0]
        self.assertGreaterEqual(node_count, 30, f"Expected >= 30 domain nodes, got {node_count}")

        # Check domain_edges count
        self.c.execute("SELECT COUNT(*) FROM domain_edges")
        edge_count = self.c.fetchone()[0]
        self.assertGreaterEqual(edge_count, 40, f"Expected >= 40 domain edges, got {edge_count}")

        # Check cross_graph_links count
        self.c.execute("SELECT COUNT(*) FROM cross_graph_links")
        link_count = self.c.fetchone()[0]
        self.assertGreaterEqual(link_count, 6, f"Expected >= 6 cross-graph links, got {link_count}")

        # Check claim_ledger count
        self.c.execute("SELECT COUNT(*) FROM claim_ledger")
        claim_count = self.c.fetchone()[0]
        self.assertGreaterEqual(claim_count, 30, f"Expected >= 30 claims in ledger, got {claim_count}")

        # Check evidence_nodes count
        self.c.execute("SELECT COUNT(*) FROM evidence_nodes")
        evid_count = self.c.fetchone()[0]
        self.assertGreaterEqual(evid_count, 150, f"Expected >= 150 evidence nodes, got {evid_count}")

    def test_fts5_virtual_tables(self):
        """Verifies full-text search across ORG, TECH, and CRM virtual tables."""
        # 1. fts_org
        self.c.execute("SELECT node_id, name FROM fts_org WHERE fts_org MATCH ?", ("Albacore",))
        org_res = self.c.fetchall()
        self.assertTrue(any("albacore" in r[0] for r in org_res), "FTS_ORG must find Albacore")

        self.c.execute("SELECT node_id, name FROM fts_org WHERE fts_org MATCH ?", ("Fluor",))
        fluor_res = self.c.fetchall()
        self.assertTrue(any("fluor" in r[0] for r in fluor_res), "FTS_ORG must find Fluor")

        # 2. fts_tech
        self.c.execute("SELECT node_id, offering_name FROM fts_tech WHERE fts_tech MATCH ?", ("Ghostfin",))
        tech_res = self.c.fetchall()
        self.assertTrue(any("ghostfin" in r[0] for r in tech_res), "FTS_TECH must find Ghostfin UUV")

        # 3. fts_crm
        self.c.execute("SELECT node_id, submission_id FROM fts_crm WHERE fts_crm MATCH ?", ("26705",))
        crm_res = self.c.fetchall()
        self.assertTrue(len(crm_res) >= 1, "FTS_CRM must find Vulcan submission 26705")

    def test_epistemic_separation_in_claim_ledger(self):
        """Verifies strict separation of vendor self-assertions, live demonstrations, and FPDS awards."""
        # Check vendor claims are strictly VENDOR_SELF_ASSERTED
        self.c.execute("SELECT epistemic_status FROM claim_ledger WHERE predicate = 'range_nmi'")
        row = self.c.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "VENDOR_SELF_ASSERTED", "Vendor range claim must be VENDOR_SELF_ASSERTED")

        # Check exercise demonstrations are LIVE_DEMONSTRATED
        self.c.execute("SELECT epistemic_status FROM claim_ledger WHERE subject_id = 'tech:ghostfin_uuv' AND object_value LIKE '%SONIC SPEAR%'")
        row = self.c.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "LIVE_DEMONSTRATED", "Exercise SONIC SPEAR must be LIVE_DEMONSTRATED")

        # Check simulation is AFSIM_SIMULATED
        self.c.execute("SELECT epistemic_status FROM claim_ledger WHERE subject_id = 'tech:ghostfin_uuv' AND object_value LIKE '%AFSIM%'")
        row = self.c.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "AFSIM_SIMULATED", "AFSIM engagement model must be AFSIM_SIMULATED")

        # Check FPDS contracts are FPDS_OBLIGATED
        self.c.execute("SELECT epistemic_status FROM claim_ledger WHERE predicate = 'holds_federal_obligation'")
        fpds_rows = self.c.fetchall()
        self.assertGreaterEqual(len(fpds_rows), 1)
        for r in fpds_rows:
            self.assertEqual(r[0], "FPDS_OBLIGATED", "Contract awards must be FPDS_OBLIGATED")

    def test_cross_graph_links_traversal(self):
        """Verifies cross-graph link registry relationships connect ORG, TECH, and CRM."""
        self.c.execute("SELECT source_id, target_id, link_predicate FROM cross_graph_links")
        links = self.c.fetchall()

        link_map = {(src, tgt): pred for src, tgt, pred in links}

        # Albacore -> Ghostfin (Org -> Tech)
        self.assertEqual(link_map.get(("org:albacore", "tech:ghostfin_uuv")), "[:DEVELOPS_OFFERING]")

        # Submission 26705 -> Albacore (CRM -> Org)
        self.assertEqual(link_map.get(("crm:submission_26705", "org:albacore")), "[:SUBMITTED_BY_ORG]")

        # Submission 26705 -> Ghostfin (CRM -> Tech)
        self.assertEqual(link_map.get(("crm:submission_26705", "tech:ghostfin_uuv")), "[:EVALUATES_OFFERING]")

        # Prometheus Energy AI -> Contract Award (Tech -> Org)
        self.assertEqual(link_map.get(("tech:prometheus_energy_ai", "award:697dck_24_c_00237")), "[:VALIDATED_BY_CONTRACT]")

    def test_graphml_exports(self):
        """Verifies all four GraphML files exist and are valid NetworkX graphs."""
        self.assertTrue(ORG_GRAPHML_PATH.exists(), "org_kg.graphml must exist")
        self.assertTrue(TECH_GRAPHML_PATH.exists(), "tech_kg.graphml must exist")
        self.assertTrue(CRM_GRAPHML_PATH.exists(), "crm_graph.graphml must exist")
        self.assertTrue(FEDERATED_GRAPHML_PATH.exists(), "federated_epistemic_graph.graphml must exist")

        g_org = nx.read_graphml(str(ORG_GRAPHML_PATH))
        self.assertGreater(g_org.number_of_nodes(), 25)
        self.assertGreater(g_org.number_of_edges(), 20)

        g_tech = nx.read_graphml(str(TECH_GRAPHML_PATH))
        self.assertGreater(g_tech.number_of_nodes(), 15)
        self.assertGreater(g_tech.number_of_edges(), 10)

        g_crm = nx.read_graphml(str(CRM_GRAPHML_PATH))
        self.assertGreater(g_crm.number_of_nodes(), 15)
        self.assertGreater(g_crm.number_of_edges(), 10)

        g_fed = nx.read_graphml(str(FEDERATED_GRAPHML_PATH))
        self.assertGreater(g_fed.number_of_nodes(), 100)
        self.assertGreater(g_fed.number_of_edges(), 50)

    def test_contextual_vector_indices(self):
        """Verifies vector indices have correct counts, dimensions (1024), and dense retrieval behavior."""
        self.assertTrue(VDB_CHUNKS_PATH.exists(), "vdb_chunks_contextual.json must exist")
        self.assertTrue(VDB_ENTITIES_PATH.exists(), "vdb_entities.json must exist")

        with open(VDB_CHUNKS_PATH, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        self.assertEqual(len(chunks), 127, f"Expected exactly 127 chunk vectors, got {len(chunks)}")

        # Verify dimension and normalization
        for ch in chunks[:10]:
            self.assertIn("chunk_id", ch)
            self.assertIn("vector", ch)
            vec = ch["vector"]
            self.assertEqual(len(vec), EMBEDDING_DIM, f"Vector must have {EMBEDDING_DIM} dims")
            norm = math.sqrt(sum(x * x for x in vec))
            self.assertAlmostEqual(norm, 1.0, places=2, msg="Vector must be unit-normalized")

        with open(VDB_ENTITIES_PATH, "r", encoding="utf-8") as f:
            entities = json.load(f)

        self.assertGreaterEqual(len(entities), 70, f"Expected >= 70 entity vectors, got {len(entities)}")

        # Test dense semantic search query
        query = "undersea autonomous long endurance UUV"
        q_vec = encode_text(query)
        top_results = search_dense(q_vec, chunks, top_k=5)
        self.assertGreaterEqual(len(top_results), 1)
        self.assertGreater(top_results[0]["cosine_similarity"], 0.20)


if __name__ == "__main__":
    unittest.main()
