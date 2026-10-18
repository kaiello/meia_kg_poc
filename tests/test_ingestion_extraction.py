"""
Card 01 Ingestion and Extraction Comprehensive Integration Tests
Validates the parsed outputs for Vulcan submissions, USASpending awards,
text chunk token boundaries, and multimodal figure/bbox assets.
"""

import json
import os
import unittest
from pathlib import Path

from src.config import (
    PARSED_DIR,
    VULCAN_PARSED_JSONL,
    USASPENDING_PARSED_JSONL,
    TEXT_CHUNKS_JSONL,
    FIGURES_DIR,
    FIGURE_BBOXES_JSON,
    MAX_CHUNK_TOKENS
)
from src.standard_manifest import StandardManifest, ManifestIntegrityError


class TestIngestionExtraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = StandardManifest()

    def test_manifest_validation(self):
        """Validate all files in manifest exist and hashes match perfectly."""
        results = self.manifest.validate_hashes()
        self.assertGreaterEqual(len(results), 11)
        for fid, matched in results.items():
            self.assertTrue(matched, f"Hash check failed for {fid}")

    def test_vulcan_submissions_jsonl(self):
        """Verify Vulcan extraction output format, record count, and cell anchors."""
        self.assertTrue(VULCAN_PARSED_JSONL.exists(), "vulcan_submissions.jsonl must exist")
        
        with open(VULCAN_PARSED_JSONL, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f]
            
        self.assertEqual(len(records), 3, "Expected exactly 3 Vulcan submissions")
        
        vendors = {r["organization_name"] for r in records}
        expected_vendors = {
            "Albacore",
            "Voltage Vessels, LLC",
            "T2S Solutions (T2S, LLC)"
        }
        self.assertEqual(vendors, expected_vendors)
        
        vulcan_ids = {str(r["vulcan_id"]) for r in records}
        self.assertEqual(vulcan_ids, {"26705", "25615", "27268"})

        for rec in records:
            self.assertIn("vulcan_id", rec)
            self.assertIn("organization_name", rec)
            self.assertIn("offering_name", rec)
            self.assertIn("cells", rec)
            self.assertEqual(len(rec["cells"]), 62, "Each submission must have exactly 62 cell anchors")
            
            # Check cell locator format: e.g. "MEIA_TEM_Vulcan_Export.xlsx!Vulcan Submissions!R2C51"
            for cell in rec["cells"]:
                self.assertIn("locator", cell)
                self.assertIn("value", cell)
                self.assertIn("target_graph", cell)
                self.assertIn("sensitivity", cell)
                loc = cell["locator"]
                self.assertTrue("!" in loc and "R" in loc and "C" in loc, f"Invalid cell locator: {loc}")
                
            # Verify specific MEIA competency questions are captured
            self.assertIn("q1_problem_understanding", rec)
            self.assertIn("q2_topic_alignment", rec)
            self.assertIn("q3_capability_contribution", rec)
            self.assertIn("q4_supply_constraints", rec)
            self.assertIn("q5_funding_to_scale", rec)
            self.assertIn("q6_unit_cost", rec)
            self.assertIn("q7_measuring_performance", rec)
            self.assertIn("q8_competitive_advantage", rec)
            self.assertIn("q9_technical_maturity", rec)
            self.assertIn("q10_integration", rec)
            self.assertIn("q11_capability_is", rec)
            self.assertIn("q12_security_preference", rec)
            
        # Verify Albacore specifics
        albacore = next(r for r in records if r["organization_name"] == "Albacore")
        self.assertEqual(albacore["cage"], "0QSF0")
        self.assertIn("Ghostfin", albacore["q1_problem_understanding"])
        self.assertIn("1,000 nautical miles", albacore["q1_problem_understanding"])
        self.assertEqual(albacore["q5_funding_to_scale"], "$5M-10M")
        self.assertEqual(albacore["q12_security_preference"], "SECRET // REL FVEY")

    def test_usaspending_awards_jsonl(self):
        """Verify federal procurement awards parsed for all vendors."""
        self.assertTrue(USASPENDING_PARSED_JSONL.exists(), "usaspending_awards.jsonl must exist")
        
        with open(USASPENDING_PARSED_JSONL, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f]
            
        self.assertEqual(len(records), 5, "Expected 5 vendor records from USASpending history")
        
        vendors = {r["vendor_name"] for r in records}
        self.assertIn("FLUOR FEDERAL SERVICES INC", vendors)
        self.assertIn("KLAS GOVERNMENT INC", vendors)
        self.assertIn("PROMETHEUS INTELLIGENCE, INC.", vendors)
        self.assertIn("Prometheus Intelligence Technology LLC", vendors)
        
        # Check Prometheus FAA sole-source award presence
        prometheus = next(r for r in records if r["vendor_name"] == "Prometheus Intelligence Technology LLC")
        self.assertEqual(prometheus["uei"], "J767K9B843S5")
        self.assertEqual(prometheus["cage"], "9M4C2")
        self.assertEqual(prometheus["total_obligated_amount"], 2398500.00)
        self.assertEqual(len(prometheus["contracts"]), 1)
        self.assertEqual(prometheus["contracts"][0]["award_id"], "697DCK-24-C-00237")
        self.assertIn("Federal Aviation Administration", prometheus["contracts"][0]["agency"])
        
        # Check Fluor Corporation total volume
        fluor = next(r for r in records if r["vendor_name"] == "FLUOR FEDERAL SERVICES INC")
        self.assertGreater(fluor["total_obligated_amount"], 900000000.0)
        self.assertGreater(fluor["contract_count"], 40)

    def test_text_chunks_bounds_and_structure(self):
        """Verify semantic chunks respect token limits, zero truncation, and required metadata."""
        self.assertTrue(TEXT_CHUNKS_JSONL.exists(), "text_chunks.jsonl must exist")
        
        with open(TEXT_CHUNKS_JSONL, "r", encoding="utf-8") as f:
            chunks = [json.loads(line) for line in f]
            
        self.assertGreater(len(chunks), 100, f"Expected >100 semantic chunks, got {len(chunks)}")
        
        for chunk in chunks:
            self.assertIn("chunk_id", chunk)
            self.assertIn("doc_id", chunk)
            self.assertIn("standard_id", chunk)
            self.assertIn("page_index", chunk)
            self.assertIn("page_ordinal", chunk)
            self.assertIn("target_graph", chunk)
            self.assertIn("content", chunk)
            self.assertIn("word_count", chunk)
            self.assertIn("image_anchor", chunk)
            
            # Non-empty content
            self.assertGreater(len(chunk["content"].strip()), 0, f"Chunk {chunk['chunk_id']} has empty content")
            
            # Strict token bound check: word count <= 300 words (safely <= 400 tokens)
            self.assertLessEqual(
                chunk["word_count"], 
                300, 
                f"Chunk {chunk['chunk_id']} exceeds word count bound: {chunk['word_count']} words"
            )
            
            # Header format check: [GRAPH: ... | ENTITY: ... | SOURCE: ...]
            content = chunk["content"]
            first_line = content.split("\n")[0]
            self.assertTrue(first_line.startswith("[GRAPH:") and " | ENTITY:" in first_line and " | SOURCE:" in first_line,
                            f"Invalid header line format: {first_line}")
            
            # Image anchor exists on disk
            img_file = FIGURES_DIR / chunk["image_anchor"]
            self.assertTrue(img_file.exists(), f"Image anchor {chunk['image_anchor']} not found on disk")

    def test_figures_and_bboxes(self):
        """Verify 180 DPI page rendering and bounding box extractions."""
        self.assertTrue(FIGURES_DIR.exists(), "figures directory must exist")
        self.assertTrue(FIGURE_BBOXES_JSON.exists(), "figure_bboxes.json must exist")
        
        with open(FIGURE_BBOXES_JSON, "r", encoding="utf-8") as f:
            bbox_data = json.load(f)
            
        self.assertIn("figures", bbox_data)
        self.assertIn("chips", bbox_data)
        
        figures = bbox_data["figures"]
        chips = bbox_data["chips"]
        
        # Verify all 69 pages rendered across the 8 declared PDFs
        self.assertEqual(len(figures), 69, f"Expected 69 rendered figures, got {len(figures)}")
        for fname, fmeta in figures.items():
            img_path = FIGURES_DIR / fname
            self.assertTrue(img_path.exists(), f"Rendered image {fname} missing from disk")
            self.assertEqual(fmeta["dpi"], 180)
            self.assertGreater(fmeta["pixel_width"], 500)
            self.assertGreater(fmeta["pixel_height"], 500)
            
        # Verify chips count and normalized bounding box values
        self.assertGreater(len(chips), 1500, f"Expected >1500 chips, got {len(chips)}")
        
        for chip in chips:
            self.assertIn("chip_id", chip)
            self.assertIn("label", chip)
            self.assertIn("figure_image", chip)
            self.assertIn("bbox", chip)
            self.assertIn("source", chip)
            
            ymin, xmin, ymax, xmax = chip["bbox"]
            self.assertGreaterEqual(ymin, 0.0)
            self.assertGreaterEqual(xmin, 0.0)
            self.assertLessEqual(ymax, 1.05)
            self.assertLessEqual(xmax, 1.05)
            self.assertLessEqual(ymin, ymax)
            self.assertLessEqual(xmin, xmax)
            
        # Verify OCR chips extracted from the 3 raster PDFs
        ocr_chips = [c for c in chips if c.get("source") == "ocr_tesseract"]
        self.assertGreater(len(ocr_chips), 500, f"Expected >500 OCR chips, got {len(ocr_chips)}")
        
        ocr_images = {c["figure_image"] for c in ocr_chips}
        expected_raster_images = {
            "Fluor_Gov_Overview_p1.png",
            "Fluor_Gov_Overview_p2.png",
            "Fluor_Nuclear_Security_p1.png",
            "Fluor_Nuclear_Security_p2.png",
            "Prometheus_Energy_AI_p1.png",
            "Prometheus_Energy_AI_p2.png"
        }
        self.assertEqual(ocr_images, expected_raster_images)


if __name__ == "__main__":
    unittest.main()
