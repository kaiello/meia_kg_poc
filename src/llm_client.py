"""Live LLM Inference Client for MEIA Knowledge Graph POC.

Supports DeepSeek (deepseek-chat), Google Gemini (gemini-2.0-flash), and Custom
OpenAI-compatible endpoints (Ollama, vLLM, OpenRouter) with strict endpoint
validation, active skill prompt injection, and epistemic verification gating.
"""
from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.config import (
    CUSTOM_API_KEY,
    CUSTOM_BASE_URL,
    CUSTOM_MODEL,
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    GEMINI_API_KEY,
    GEMINI_BASE_URL,
    GEMINI_MODEL,
)
from src.security_boundaries import validate_model_endpoint
from src.skill_loader import get_skill_registry

logger = logging.getLogger("meia_llm_client")


@dataclass
class LLMResponse:
    """Represents a generated response from a live LLM or deterministic fallback."""
    answer: str
    engine: str
    model_name: str
    latency_ms: float
    status: str = "SUCCESS"  # SUCCESS, FALLBACK, ERROR
    error_message: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    active_skills: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "engine": self.engine,
            "model_name": self.model_name,
            "latency_ms": round(self.latency_ms, 2),
            "status": self.status,
            "error_message": self.error_message,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "active_skills": self.active_skills,
        }


class LiveLLMClient:
    """Executes live queries against DeepSeek, Gemini, or Custom endpoints."""

    def __init__(self):
        self.skill_registry = get_skill_registry()

    def generate(
        self,
        query: str,
        context_packet_text: str,
        route_profile: str = "D4_CROSS_GRAPH_SYNTHESIS",
        engine: str = "deepseek",
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        loc_payload_text: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generates a grounded answer using the specified engine and skill rules."""
        engine_lower = (engine or "deepseek").lower()
        started = time.perf_counter()

        # Resolve credentials & endpoints
        if engine_lower == "deepseek":
            target_key = api_key or DEEPSEEK_API_KEY
            target_url = base_url or DEEPSEEK_BASE_URL
            target_model = model_name or DEEPSEEK_MODEL
        elif engine_lower == "gemini":
            target_key = api_key or GEMINI_API_KEY
            target_url = base_url or GEMINI_BASE_URL
            target_model = model_name or GEMINI_MODEL
        elif engine_lower in {"custom", "openai", "ollama"}:
            target_key = api_key or CUSTOM_API_KEY
            target_url = base_url or CUSTOM_BASE_URL
            target_model = model_name or CUSTOM_MODEL
        else:
            return LLMResponse(
                answer="",
                engine=engine_lower,
                model_name=model_name or "unknown",
                latency_ms=0.0,
                status="ERROR",
                error_message=f"Unsupported engine '{engine_lower}'. Use 'deepseek', 'gemini', or 'custom'.",
            )

        if not target_key and engine_lower != "custom":
            return LLMResponse(
                answer="",
                engine=engine_lower,
                model_name=target_model,
                latency_ms=0.0,
                status="FALLBACK",
                error_message=f"API key for {engine_lower} is not configured on server or in session.",
            )

        # Validate security boundaries on the endpoint URL
        try:
            approved_url = validate_model_endpoint(target_url, target_url)
        except Exception as sec_exc:
            return LLMResponse(
                answer="",
                engine=engine_lower,
                model_name=target_model,
                latency_ms=0.0,
                status="ERROR",
                error_message=f"Security boundary check failed for endpoint: {sec_exc}",
            )

        # Build prompt incorporating active SKILL.md rules
        active_skills = [s.name for s in self.skill_registry.get_skills_for_route(route_profile)]
        skill_extension = self.skill_registry.build_system_prompt_extension(route_profile)

        system_instruction = (
            "You are the MEIA Federated Tri-Graph Live Intelligence Reader.\n"
            "Your task is to synthesize rigorous, decision-ready answers using ONLY the supplied\n"
            "Tri-Graph Functional Evidence Units and Multimodal Evidence.\n\n"
            "MANDATORY EVIDENCE CONTRACTS:\n"
            "1. Answer ONLY what the supplied evidence supports. Do NOT invent companies, TRLs, or contract numbers.\n"
            "2. Epistemic Separation: Distinguish VENDOR_SELF_ASSERTED marketing from LIVE_DEMONSTRATED trial results\n"
            "   and FPDS_OBLIGATED contract awards. Never treat vendor claims as government-validated facts.\n"
            "3. Inline Citations: Every key metric or fact MUST cite the exact locator, e.g. [Source: <locator>].\n"
            f"{skill_extension}"
        )

        user_content_parts = [
            f"USER QUERY: {query}\n",
            f"[PRIMARY TRI-GRAPH FUNCTIONAL EVIDENCE UNITS]:\n{context_packet_text}\n"
        ]
        if loc_payload_text:
            user_content_parts.append(
                f"[LOUD AND CLEAR (LoC) MULTIMODAL READER ARM]:\n{loc_payload_text}\n"
            )
        user_content_parts.append(
            "\nProvide an authoritative, structured Executive Dossier answering the user's query."
        )

        full_user_content = "\n".join(user_content_parts)

        # Build OpenAI-compatible request payload
        api_endpoint = approved_url.rstrip("/") + "/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {target_key}",
        }

        payload = {
            "model": target_model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": full_user_content},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(api_endpoint, data=req_data, headers=headers, method="POST")
            
            with urllib.request.urlopen(req, timeout=60) as resp:
                status_code = resp.status
                body = resp.read().decode("utf-8")
                data = json.loads(body)

            latency = (time.perf_counter() - started) * 1000.0
            choices = data.get("choices", [])
            if not choices:
                return LLMResponse(
                    answer="",
                    engine=engine_lower,
                    model_name=target_model,
                    latency_ms=latency,
                    status="ERROR",
                    error_message="Model returned empty choices array.",
                    active_skills=active_skills,
                )

            answer_text = choices[0].get("message", {}).get("content", "").strip()
            usage = data.get("usage", {})
            prompt_toks = usage.get("prompt_tokens", 0)
            comp_toks = usage.get("completion_tokens", 0)

            return LLMResponse(
                answer=answer_text,
                engine=engine_lower,
                model_name=target_model,
                latency_ms=latency,
                status="SUCCESS",
                prompt_tokens=prompt_toks,
                completion_tokens=comp_toks,
                active_skills=active_skills,
            )

        except urllib.error.HTTPError as http_err:
            latency = (time.perf_counter() - started) * 1000.0
            err_body = http_err.read().decode("utf-8", errors="replace")
            logger.error("HTTP error from %s: %s - %s", api_endpoint, http_err.code, err_body)
            return LLMResponse(
                answer="",
                engine=engine_lower,
                model_name=target_model,
                latency_ms=latency,
                status="ERROR",
                error_message=f"HTTP {http_err.code}: {http_err.reason} - {err_body[:200]}",
                active_skills=active_skills,
            )
        except Exception as err:
            latency = (time.perf_counter() - started) * 1000.0
            logger.error("Inference exception from %s: %s", api_endpoint, err)
            return LLMResponse(
                answer="",
                engine=engine_lower,
                model_name=target_model,
                latency_ms=latency,
                status="ERROR",
                error_message=f"Connection/Inference error: {err}",
                active_skills=active_skills,
            )


# Global singleton
_GLOBAL_LLM_CLIENT: Optional[LiveLLMClient] = None


def get_llm_client() -> LiveLLMClient:
    global _GLOBAL_LLM_CLIENT
    if _GLOBAL_LLM_CLIENT is None:
        _GLOBAL_LLM_CLIENT = LiveLLMClient()
    return _GLOBAL_LLM_CLIENT
