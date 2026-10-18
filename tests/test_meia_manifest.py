"""Unit tests verifying the integrity of config/meia_poc_manifest.json and standard_manifest.py."""
import unittest
from pathlib import Path
import sys

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.standard_manifest import StandardManifest, ManifestIntegrityError


class TestMeiaManifest(unittest.TestCase):

    def setUp(self):
        self.manifest = StandardManifest()

    def test_schema_version(self):
        self.assertEqual(self.manifest.schema_version, "1.0.0")
        self.assertEqual(self.manifest.manifest_revision, 1)

    def test_all_file_hashes_match(self):
        results = self.manifest.validate_hashes()
        self.assertTrue(len(results) >= 11, "Expected at least 11 verified files in manifest")
        for file_id, matched in results.items():
            self.assertTrue(matched, f"Hash validation failed for {file_id}")

    def test_vulcan_workbook_metadata(self):
        wb = self.manifest.get_workbook("doc:vulcan_export_2026")
        self.assertEqual(wb["standard_id"], "MEIA_TEM_Vulcan_Export")
        sheet = wb["sheets"][0]
        self.assertEqual(sheet["sheet_name"], "Vulcan Submissions")
        self.assertEqual(sheet["max_column"], 62)
        self.assertEqual(len(sheet["submissions"]), 3)

        # Check Albacore
        s1 = sheet["submissions"][0]
        self.assertEqual(s1["vendor_name"], "Albacore Inc.")
        self.assertEqual(s1["cage"], "0QSF0")
        self.assertEqual(s1["vulcan_id"], "26705")

    def test_raster_documents_flagged(self):
        doc_prom = self.manifest.get_document("doc:prometheus_energy_ai")
        self.assertTrue(doc_prom["raster_only"])
        self.assertEqual(doc_prom["render_dpi"], 180)

        doc_fluor_gov = self.manifest.get_document("doc:fluor_gov_overview")
        self.assertTrue(doc_fluor_gov["raster_only"])

        doc_klas = self.manifest.get_document("doc:klas_voyager_2")
        self.assertFalse(doc_klas["raster_only"])

    def test_usaspending_receipt_metadata(self):
        rec = self.manifest.get_api_receipt("api:usaspending_vendor_history_2026")
        self.assertTrue(len(rec["entities_covered"]) >= 6)


if __name__ == "__main__":
    unittest.main()
