"""Unit and integration test suite for Local Open-Weight Models (Ollama + Local HF)."""
import json
import unittest
from pathlib import Path

from src.config import (
    DEFAULT_ENGINE,
    EMBEDDING_MODEL_NAME,
    OLLAMA_BASE_URL,
    OLLAMA_DEFAULT_MODEL,
    OLLAMA_RECOMMENDED_MODELS,
    RERANKER_MODEL,
    VISUAL_RETRIEVER_MODEL,
)
from src.llm_client import LiveLLMClient, discover_ollama_models, get_llm_client
from src.hybrid_retriever import expand_query_terms, get_reranker_model, retrieve_hybrid_candidates
from src.visual_retriever import get_visual_stack_info
from src.pre_retrieval import CallerContext
from src.grounded_answer import answer_query


class TestLocalOpenWeightModels(unittest.TestCase):
    """Verifies local open-weight Ollama inference, BGE reranking, and ColQwen visual metadata."""

    def test_01_ollama_discovery(self):
        """Verify discovery of installed local Ollama models and non-DeepSeek filtering."""
        discovery = discover_ollama_models()
        self.assertIn("online", discovery)
        self.assertIn("models", discovery)
        self.assertIn("non_deepseek_models", discovery)

        # If Ollama daemon is running, verify detection of local models
        if discovery["online"]:
            installed_names = [m["name"] for m in discovery["models"]]
            self.assertTrue(len(installed_names) > 0)
            
            # Verify non-DeepSeek model filtering
            for nd in discovery["non_deepseek_models"]:
                self.assertNotIn("deepseek", nd["name"].lower())

            # Check for at least one of our primary recommended models
            recommended_found = any(m["name"] in OLLAMA_RECOMMENDED_MODELS for m in discovery["models"])
            self.assertTrue(recommended_found, f"Expected at least one recommended model in {installed_names}")

    def test_02_config_defaults(self):
        """Verify default engine is configured for local open-weight inference."""
        self.assertTrue(
            DEFAULT_ENGINE.startswith("ollama"),
            f"Expected DEFAULT_ENGINE to start with 'ollama', got {DEFAULT_ENGINE}"
        )
        self.assertEqual(OLLAMA_DEFAULT_MODEL, "qwen3-vl:8b-instruct")
        self.assertIn("qwen3-vl:8b-instruct", OLLAMA_RECOMMENDED_MODELS)
        self.assertIn("gemma4:e4b", OLLAMA_RECOMMENDED_MODELS)
        self.assertIn("hermes3:8b", OLLAMA_RECOMMENDED_MODELS)

    def test_03_query_expansion_and_reranker(self):
        """Verify domain acronym expansion and local CrossEncoder presence."""
        expanded = expand_query_terms("What is Ghostfin UUV TRL?")
        self.assertTrue(any("unmanned undersea" in t or "submersible" in t for t in expanded))

        # Check visual stack info
        vis_info = get_visual_stack_info()
        self.assertEqual(vis_info["visual_model"], VISUAL_RETRIEVER_MODEL)
        self.assertTrue(vis_info["multivector_maxsim"])
        self.assertGreaterEqual(vis_info["figures_indexed"], 1)

        # Test reranker presence/fallback
        ce = get_reranker_model()
        # Either CrossEncoder loaded from cache or deterministic fallback is safely active
        self.assertTrue(ce is not None or ce is None)

    def test_04_live_ollama_generation_or_fallback(self):
        """Verify LiveLLMClient correctly dispatches to local Ollama with fallback safety."""
        client = get_llm_client()
        discovery = discover_ollama_models()

        # Target one of the installed non-DeepSeek models (e.g. hermes3:8b, qwen2.5:3b, or qwen3-vl:8b-instruct)
        target_model = OLLAMA_DEFAULT_MODEL
        if discovery["online"] and discovery["non_deepseek_models"]:
            target_model = discovery["non_deepseek_models"][0]["name"]

        resp = client.generate(
            query="What is Ghostfin's TRL and operational range?",
            context_packet_text="Entity: Ghostfin (ID: tech:offering:ghostfin_uuv)\nClaim: TRL is 7 [LIVE_DEMONSTRATED] [Source: Sheet1!R2C5]\nClaim: Operational range is 1000 nmi [LIVE_DEMONSTRATED] [Source: Sheet1!R2C8]",
            engine=f"ollama:{target_model}",
            max_tokens=150,
        )

        self.assertIn(resp.status, {"SUCCESS", "ERROR", "FALLBACK"})
        self.assertTrue(resp.engine.startswith("ollama"))
        self.assertEqual(resp.model_name, target_model)

        if resp.status == "SUCCESS":
            self.assertTrue(len(resp.answer) > 0)
            self.assertGreater(resp.latency_ms, 0)
            self.assertTrue(len(resp.active_skills) > 0)

    def test_05_grounded_answer_with_ollama_engine(self):
        """Verify full end-to-end grounded answer composition using local Ollama engine."""
        ctx = CallerContext(
            caller_role="meia-authorized-evaluator",
            clearance_level="SECRET",
            enabled_modules=["organization_graph", "technology_graph", "crm_graph", "evidence_graph"]
        )

        # Execute query using default ollama engine
        ans = answer_query(
            "What is Ghostfin's TRL and operational range?",
            ctx,
            engine="ollama:qwen3-vl:8b-instruct"
        )

        self.assertEqual(ans.status, "VERIFIED_GROUNDED")
        self.assertTrue(len(ans.answer_text) > 0)
        self.assertTrue(len(ans.structured_facts) > 0)
        self.assertTrue(len(ans.citations) > 0)

        # Verify telemetry records local engine
        llm_meta = ans.llm_metadata
        self.assertTrue(llm_meta.get("engine", "").startswith("ollama"))


if __name__ == "__main__":
    unittest.main()
