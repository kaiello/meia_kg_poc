"""Unit and integration test suite for Card 09: Live LLM, ColPali Visuals & Domain Skills."""
import json
import unittest
from pathlib import Path

from src.config import DEEPSEEK_API_KEY, REPO_ROOT, SKILLS_DIR
from src.security_boundaries import canonical_endpoint, validate_model_endpoint
from src.skill_loader import SkillRegistry, get_skill_registry
from src.visual_retriever import ColPaliVisualRetriever, get_visual_retriever
from src.figure_inspectors import inspect_figure_loc, LoCInspectionArm
from src.hybrid_retriever import retrieve_hybrid_candidates, audit_modality_bias
from src.context_packet import ContextPacketBuilder, format_packets_as_evidence_text
from src.grounded_answer import answer_query


class TestCard09LiveLLMAndSkills(unittest.TestCase):
    """Card 09 Verification Suite: Model Security, Skills, ColPali, and Live Synthesis."""

    def test_01_security_boundaries(self):
        """Verify endpoint sanitization, allowlist enforcement, and SSRF prevention."""
        # Valid endpoints
        self.assertEqual(canonical_endpoint("https://api.deepseek.com"), "https://api.deepseek.com")
        self.assertEqual(canonical_endpoint("https://api.deepseek.com/v1"), "https://api.deepseek.com/v1")
        self.assertEqual(canonical_endpoint("http://localhost:11434"), "http://localhost:11434")
        self.assertEqual(canonical_endpoint("http://127.0.0.1:8000"), "http://127.0.0.1:8000")

        # Allowlist validation
        valid_ep = validate_model_endpoint("https://api.deepseek.com", "https://api.deepseek.com")
        self.assertEqual(valid_ep, "https://api.deepseek.com")

        # Invalid schemes or non-loopback HTTP
        with self.assertRaises(ValueError):
            canonical_endpoint("http://insecure-remote-site.com")
        with self.assertRaises(ValueError):
            canonical_endpoint("ftp://api.deepseek.com")
        with self.assertRaises(ValueError):
            canonical_endpoint("https://api.deepseek.com/../malicious")
        with self.assertRaises(ValueError):
            validate_model_endpoint("https://unapproved-evil-api.com", "https://unapproved-evil-api.com")

    def test_02_domain_skills_registry(self):
        """Verify all 4 SKILL.md files are loaded, parsed, and mapped to routes."""
        reg = get_skill_registry()
        skills = {s.name: s for s in reg.list_skills()}

        # Verify presence of the 4 card skills
        self.assertIn("tri-graph-routing", skills)
        self.assertIn("trident-colpali-visual", skills)
        self.assertIn("epistemic-claim-audit", skills)
        self.assertIn("executive-dossier-composer", skills)

        # Verify parsed sections in tri-graph-routing
        routing_skill = skills["tri-graph-routing"]
        self.assertIn("purpose", routing_skill.sections)
        self.assertIn("guardrails", routing_skill.sections)
        self.assertTrue(len(routing_skill.guardrails) >= 2)
        self.assertTrue(len(routing_skill.workflow_steps) >= 3)

        # Verify prompt extension generation
        prompt_ext = reg.build_system_prompt_extension("D4_CROSS_GRAPH_SYNTHESIS")
        self.assertIn("ACTIVE DOMAIN SKILL RULES", prompt_ext)
        self.assertIn("EPISTEMIC-CLAIM-AUDIT", prompt_ext)
        self.assertIn("EXECUTIVE-DOSSIER-COMPOSER", prompt_ext)

        # Verify parameters extraction
        d2_params = reg.get_retrieval_parameters("D2_TECHNICAL_READINESS")
        self.assertGreaterEqual(d2_params.get("visual_quota", 0), 1)
        self.assertEqual(d2_params.get("ocr_token_budget"), 160)

    def test_03_colpali_visual_retriever(self):
        """Verify ColPali late-interaction MaxSim scoring over figure regions."""
        vr = get_visual_retriever()
        results = vr.search_figures("Klas Telecom Voyager architecture diagram", top_k=3)
        self.assertTrue(len(results) > 0)

        top_fig = results[0]
        self.assertTrue("klas" in top_fig.figure_image.lower() or "voyager" in top_fig.figure_image.lower())
        self.assertGreater(top_fig.maxsim_score, 0.40)
        self.assertTrue(len(top_fig.matched_chips) > 0)

        # Verify token attributions
        self.assertIn("voyager", top_fig.token_attributions)
        self.assertGreater(top_fig.token_attributions["voyager"], 0.5)

    def test_04_trident_modality_calibration(self):
        """Verify Trident calibrated fusion preserves visual diagrams on architecture queries."""
        query = "Klas Telecom Voyager architecture diagram"
        dec, cands = retrieve_hybrid_candidates(query, top_k=10)
        self.assertTrue(len(cands) > 0)

        # Check that visual assets are present in retrieved candidates
        vis_cands = [c for c in cands if c.candidate_type == "visual_asset" or "asset:" in c.candidate_id]
        self.assertTrue(len(vis_cands) >= 1, "Trident fusion must preserve at least 1 visual candidate on architecture query")

        audit = audit_modality_bias(cands)
        self.assertEqual(audit["modality_balance_status"], "BALANCED_MULTIMODAL")
        self.assertGreaterEqual(audit["visual_candidates"], 1)

    def test_05_nativescope_anchor_scoping(self):
        """Verify NativeScope scopes candidates when structural anchor exists, with global fallback."""
        # Scoped query with Vulcan submission ID
        query_anchor = "What are the Q5 and Q6 values for vulcan-26705?"
        dec, cands_scoped = retrieve_hybrid_candidates(query_anchor, top_k=10)
        self.assertTrue(len(cands_scoped) > 0)

        # Unanchored query triggers global retrieval
        query_general = "What are general UUV applications?"
        dec2, cands_gen = retrieve_hybrid_candidates(query_general, top_k=10)
        self.assertTrue(len(cands_gen) > 0)

    def test_06_loc_reader_arm_and_packets(self):
        """Verify LoC ARM_C_MULTIMODAL_CALLOUT payload and Functional Evidence Units."""
        loc_res = inspect_figure_loc("MEIA_Charter_2026_p2", arm_name="ARM_C_MULTIMODAL_CALLOUT")
        self.assertEqual(loc_res["arm"], "ARM_C_MULTIMODAL_CALLOUT")
        self.assertIsNotNone(loc_res["full_page_path"])

        # Test Functional Context Packet formatting
        builder = ContextPacketBuilder()
        pkt = builder.build_packet_for_entity("tech:offering:ghostfin_uuv")
        evidence_text = format_packets_as_evidence_text([pkt])
        self.assertIn("FUNCTIONAL EVIDENCE UNIT", evidence_text)
        self.assertIn("Primary Tri-Graph Assertions", evidence_text)
        self.assertIn("EPISTEMIC:", evidence_text)
        self.assertIn("Source:", evidence_text)

    def test_07_deterministic_grounded_answer(self):
        """Verify deterministic engine synthesizes locator-grounded facts with zero errors."""
        ans = answer_query("What is Ghostfin's TRL and operational range?", engine="deterministic")
        self.assertEqual(ans.status, "VERIFIED_GROUNDED")
        self.assertTrue(len(ans.structured_facts) > 0)
        self.assertTrue(len(ans.citations) > 0)
        self.assertEqual(ans.llm_metadata.get("engine"), "deterministic")

    def test_08_live_llm_deepseek_synthesis(self):
        """Verify live DeepSeek LLM execution and epistemic gating when API key is present."""
        if not DEEPSEEK_API_KEY:
            self.skipTest("DEEPSEEK_API_KEY not configured; skipping live LLM call.")

        query = "What is Ghostfin's operational range and hybrid powertrain advantage?"
        ans = answer_query(query, engine="deepseek")
        self.assertIn(ans.status, {"VERIFIED_GROUNDED", "CONFLICTING_EVIDENCE"})
        self.assertEqual(ans.llm_metadata.get("status"), "SUCCESS")
        self.assertEqual(ans.llm_metadata.get("engine"), "deepseek")
        self.assertGreater(ans.llm_metadata.get("latency_ms", 0), 0)
        self.assertGreater(ans.llm_metadata.get("prompt_tokens", 0), 100)

        # Verify epistemic audit was run on the live LLM synthesis
        self.assertIn("status", ans.epistemic_audit)
        self.assertTrue(ans.epistemic_audit.get("audit_passed"))
        self.assertIn("locator_grounding_score", ans.epistemic_audit)



if __name__ == "__main__":
    unittest.main()
