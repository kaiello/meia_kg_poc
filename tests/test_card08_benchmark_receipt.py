"""
Card 08 Test Suite: Benchmark Receipts, Cryptographic Fingerprints,
Steward Review Queue, and Offline Regression Harness (U01, U04, U05, D03, D05).
=============================================================================
"""

import json
import logging
from pathlib import Path
import sqlite3
import unittest
from unittest.mock import MagicMock
from io import BytesIO

from src.config import (
    REPO_ROOT,
    MANIFEST_PATH,
    TRI_GRAPH_DB_PATH,
    VDB_CHUNKS_PATH,
    STORAGE_DIR
)
from eval.test_scorer import compute_file_sha256, run_benchmark
from src.steward_review import StewardReviewManager, StewardReviewItem
from src.web import MeiaWebHandler

logging.basicConfig(level=logging.WARNING)


class TestCard08BenchmarkReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gold_path = REPO_ROOT / "eval" / "gold_78_cqs.json"
        cls.receipt_json_path = REPO_ROOT / "eval" / "meia_78_cq_receipt.json"
        cls.docs_receipt_path = REPO_ROOT / "docs" / "benchmark_receipt.md"
        cls.steward_queue_path = STORAGE_DIR / "steward_review_queue.json"

    def test_cryptographic_fingerprints_valid(self):
        """U05: Computes and validates 64-char hex SHA-256 digests for all core artifacts."""
        manifest_sha = compute_file_sha256(MANIFEST_PATH)
        db_sha = compute_file_sha256(TRI_GRAPH_DB_PATH)
        vdb_sha = compute_file_sha256(VDB_CHUNKS_PATH)
        gold_sha = compute_file_sha256(self.gold_path)

        for name, sha in [
            ("Manifest", manifest_sha),
            ("Database", db_sha),
            ("Vector Store", vdb_sha),
            ("Gold CQs", gold_sha)
        ]:
            self.assertNotEqual(sha, "FILE_NOT_FOUND", f"{name} file must exist on disk.")
            self.assertEqual(len(sha), 64, f"{name} SHA-256 digest must be exactly 64 hex characters.")
            self.assertTrue(all(c in "0123456789abcdef" for c in sha.lower()))

    def test_benchmark_receipt_json_structure(self):
        """U01, U05: Verifies authoritative receipt contains all 78 CQs and achieves 100% across all metrics."""
        self.assertTrue(self.receipt_json_path.exists(), "meia_78_cq_receipt.json must exist.")
        with open(self.receipt_json_path, "r", encoding="utf-8") as f:
            receipt = json.load(f)

        self.assertEqual(receipt.get("schema_version"), "1.0.0")
        self.assertTrue(receipt.get("receipt_id", "").startswith("receipt:meia:78cq:"))
        self.assertIn("cryptographic_fingerprints", receipt)
        self.assertIn("execution_environment", receipt)

        # Verify 100% scorecard
        sc = receipt.get("scorecard", {})
        self.assertEqual(sc.get("total_cqs"), 78)
        self.assertEqual(sc.get("route_accuracy_pct"), 100.0)
        self.assertEqual(sc.get("status_accuracy_pct"), 100.0)
        self.assertEqual(sc.get("epistemic_audit_pass_rate_pct"), 100.0)
        self.assertEqual(sc.get("zero_promotions_rate_pct"), 100.0)
        self.assertEqual(sc.get("citation_coverage_pct"), 100.0)

        # Verify 78 results
        results = receipt.get("results", [])
        self.assertEqual(len(results), 78)

    def test_docs_benchmark_receipt_markdown(self):
        """U05: Verifies publication docs/benchmark_receipt.md exists and contains verification seal."""
        self.assertTrue(self.docs_receipt_path.exists(), "docs/benchmark_receipt.md must exist.")
        content = self.docs_receipt_path.read_text(encoding="utf-8")

        self.assertIn("Cryptographic Benchmark Verification Receipt", content)
        self.assertIn("Cryptographic Fingerprints & Provenance Hashes", content)
        self.assertIn("Complete 78 Competency Question Audit Matrix", content)
        self.assertIn("Verification Seal & Architectural Sign-Off", content)
        self.assertIn("Formal Verification Seal", content)

    def test_steward_review_queue_harvest_and_export(self):
        """U04: StewardReviewManager harvests candidate bridges, conflicts, and unverified claims."""
        mgr = StewardReviewManager()
        items = mgr.harvest_review_queue()
        self.assertGreaterEqual(len(items), 3, "Review queue must capture at least 3 governed items.")

        types = {it.item_type for it in items}
        self.assertIn("CANDIDATE_BRIDGE", types)
        self.assertIn("CONFLICTING_EVIDENCE", types)
        self.assertIn("UNVERIFIED_CLAIM", types)

        # Test export
        out_path = mgr.export_queue()
        self.assertTrue(out_path.exists())
        with open(out_path, "r", encoding="utf-8") as f:
            queue_data = json.load(f)
        self.assertIn("total_items", queue_data)
        self.assertEqual(queue_data["total_items"], len(items))

        # Test summary stats
        stats = mgr.get_summary_stats()
        self.assertEqual(stats["total_pending_items"], len(items))

    def test_web_receipt_and_review_endpoints(self):
        """Verifies GET /api/benchmark/receipt and GET /api/steward/review-queue return 200 OK."""
        # Test receipt endpoint simulation
        handler = MeiaWebHandler.__new__(MeiaWebHandler)
        handler.path = "/api/benchmark/receipt"
        handler.headers = {}
        handler.wfile = BytesIO()
        handler.rfile = BytesIO()
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()

        handler.do_GET()
        handler.send_response.assert_called_with(200)
        resp_data = json.loads(handler.wfile.getvalue().decode("utf-8"))
        self.assertIn("receipt_id", resp_data)
        self.assertIn("scorecard", resp_data)

        # Test review-queue endpoint simulation
        handler2 = MeiaWebHandler.__new__(MeiaWebHandler)
        handler2.path = "/api/steward/review-queue"
        handler2.headers = {}
        handler2.wfile = BytesIO()
        handler2.rfile = BytesIO()
        handler2.send_response = MagicMock()
        handler2.send_header = MagicMock()
        handler2.end_headers = MagicMock()

        handler2.do_GET()
        handler2.send_response.assert_called_with(200)
        queue_resp = json.loads(handler2.wfile.getvalue().decode("utf-8"))
        self.assertIn("summary", queue_resp)
        self.assertIn("items", queue_resp)

    def test_zero_daemon_and_governance_invariants(self):
        """Drift Check (D05): Zero external database sockets, local SQLite file, zero promotions."""
        # 1. Zero External DB Daemons: pure local SQLite
        self.assertTrue(TRI_GRAPH_DB_PATH.exists())
        self.assertTrue(TRI_GRAPH_DB_PATH.is_file())

        conn = sqlite3.connect(str(TRI_GRAPH_DB_PATH))
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM domain_nodes")
        node_count = c.fetchone()[0]
        self.assertGreater(node_count, 20)

        # 2. Epistemic Claim Firewall: Zero unverified vendor claims promoted to live demonstrated
        c.execute("""
            SELECT COUNT(*) FROM claim_ledger 
            WHERE epistemic_status = 'LIVE_DEMONSTRATED' 
            AND predicate NOT IN ('participated_in_exercise', 'demonstrated_in_simulation')
        """)
        invalid_promotions = c.fetchone()[0]
        self.assertEqual(invalid_promotions, 0, "Zero vendor claims promoted to LIVE_DEMONSTRATED without proof.")
        conn.close()


if __name__ == "__main__":
    unittest.main()
