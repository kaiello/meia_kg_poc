"""
Unit and Integration Test Suite for Card 06:
- Web Visual Explorer Endpoints (GET /, GET /api/health, POST /api/query, GET /api/figures)
- Golden 78-CQ Benchmark Smoke Test & Integrity Validation
"""

import json
import threading
import time
import unittest
import urllib.request
import urllib.error
from http.server import HTTPServer
from pathlib import Path

import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.web import MeiaWebHandler
from eval.test_scorer import run_benchmark


class TestWebAndBenchmark(unittest.TestCase):
    """Verifies Card 06 web dashboard server and benchmark scoring pipeline."""

    @classmethod
    def setUpClass(cls):
        cls.test_port = 8099
        cls.server = HTTPServer(("127.0.0.1", cls.test_port), MeiaWebHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_web_index_page(self):
        """Verifies GET / serves the interactive HTML5 explorer dashboard."""
        url = f"http://127.0.0.1:{self.test_port}/"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            html = response.read().decode("utf-8")
            self.assertIn("MEIA Federated Tri-Graph Explorer", html)
            self.assertIn("ROUTE_TECH", html)
            self.assertIn("1024d", html.lower())
            self.assertIn("multimodal", html.lower())

    def test_web_health_endpoint(self):
        """Verifies GET /api/health returns valid JSON service status."""
        url = f"http://127.0.0.1:{self.test_port}/api/health"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "healthy")
            self.assertTrue(data.get("air_gapped"))

    def test_web_query_endpoint(self):
        """Verifies POST /api/query executes grounded retrieval and returns typed answer."""
        url = f"http://127.0.0.1:{self.test_port}/api/query"
        payload = json.dumps({
            "query": "What is Ghostfin's TRL and operational range?",
            "clearance_level": "SECRET"
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            ans = json.loads(response.read().decode("utf-8"))
            self.assertEqual(ans.get("route_profile"), "ROUTE_TECH")
            self.assertIn(ans.get("status"), ("VERIFIED_GROUNDED", "UNVERIFIED_VENDOR_CLAIM"))
            self.assertGreaterEqual(len(ans.get("citations", [])), 1)

    def test_web_figure_serving(self):
        """Verifies GET /api/figures serves rendered 180 DPI PNG images."""
        url = f"http://127.0.0.1:{self.test_port}/api/figures/meia_charter_2026_p1.png"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get("Content-Type"), "image/png")
            content = response.read()
            self.assertGreater(len(content), 1000)

    def test_gold_dataset_integrity(self):
        """Verifies eval/gold_78_cqs.json contains exactly 78 structured competency questions."""
        gold_path = REPO_ROOT / "eval" / "gold_78_cqs.json"
        self.assertTrue(gold_path.exists())
        with open(gold_path, "r", encoding="utf-8") as f:
            cqs = json.load(f)

        self.assertEqual(len(cqs), 78)
        cq_ids = [c["cq_id"] for c in cqs]
        self.assertEqual(cq_ids[0], "CQ-01")
        self.assertEqual(cq_ids[-1], "CQ-78")

        # Verify profile distribution
        profiles = {c["expected_profile"] for c in cqs}
        self.assertEqual(len(profiles), 8)
        self.assertIn("ROUTE_ORG", profiles)
        self.assertIn("ROUTE_TECH", profiles)
        self.assertIn("ROUTE_CRM", profiles)
        self.assertIn("ROUTE_ORG_TECH", profiles)
        self.assertIn("ROUTE_CRM_ORG", profiles)
        self.assertIn("ROUTE_CRM_TECH", profiles)
        self.assertIn("ROUTE_ALL_TRI_STORE", profiles)
        self.assertIn("FAIL_CLOSED_GATE", profiles)

    def test_path_traversal_returns_403(self):
        """Verifies GET /api/figures with path traversal returns HTTP 403 Forbidden."""
        url = f"http://127.0.0.1:{self.test_port}/api/figures/..%2F..%2Fstorage%2Fmeia_tri_graph_registry.db"
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(url)
        self.assertEqual(ctx.exception.code, 403)

    def test_arm_b_crop_url_resolves_image(self):
        """Verifies GET /api/figures/crops/<filename> serves generated focal crops."""
        from src.figure_inspectors import inspect_figure_loc
        arm_b = inspect_figure_loc("Prometheus_Energy_AI_p1", "ARM_B_FOCAL_CROP", bbox=[0.2, 0.2, 0.7, 0.7])
        crop_path = arm_b.get("focal_crop_path")
        self.assertIsNotNone(crop_path)
        crop_filename = Path(crop_path).name
        url = f"http://127.0.0.1:{self.test_port}/api/figures/crops/{crop_filename}"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get("Content-Type"), "image/png")
            content = response.read()
            self.assertGreater(len(content), 100)

    def test_post_body_oversized_returns_413(self):
        """Verifies POST /api/query with oversized payload (>64KB) returns HTTP 413."""
        url = f"http://127.0.0.1:{self.test_port}/api/query"
        oversized_payload = json.dumps({
            "query": "A" * 70000,
            "clearance_level": "SECRET"
        }).encode("utf-8")
        req = urllib.request.Request(url, data=oversized_payload, headers={"Content-Type": "application/json"})
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 413)


if __name__ == "__main__":
    unittest.main()
