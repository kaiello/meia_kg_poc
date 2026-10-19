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
from pathlib import Path
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
    OLLAMA_BASE_URL,
    OLLAMA_NATIVE_URL,
    OLLAMA_DEFAULT_MODEL,
    OLLAMA_RECOMMENDED_MODELS,
)
from src.security_boundaries import validate_model_endpoint
from src.skill_loader import get_skill_registry

logger = logging.getLogger("meia_llm_client")


def discover_ollama_models(native_url: Optional[str] = None) -> Dict[str, Any]:
    """Queries live Ollama daemon to discover installed models with VRAM and role recommendations."""
    url = (native_url or OLLAMA_NATIVE_URL).rstrip("/") + "/api/tags"
    try:
        approved_url = validate_model_endpoint(url, url)
        req = urllib.request.Request(approved_url, headers={"User-Agent": "MEIA-TriGraph/1.0"}, method="GET")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status == 200:
                body = resp.read().decode("utf-8")
                data = json.loads(body)
                raw_models = data.get("models", [])
                installed = []
                for m in raw_models:
                    tag = m.get("name", "")
                    size_bytes = m.get("size", 0)
                    size_gb = round(size_bytes / (1024 ** 3), 2)
                    is_deepseek = "deepseek" in tag.lower()
                    rec = OLLAMA_RECOMMENDED_MODELS.get(tag, {})
                    installed.append({
                        "name": tag,
                        "model": m.get("model", tag),
                        "size_gb": size_gb,
                        "modified_at": m.get("modified_at", ""),
                        "is_deepseek": is_deepseek,
                        "role": rec.get("role", "General Open-Weight LLM"),
                        "recommended": bool(rec),
                        "multimodal": rec.get("multimodal", "vl" in tag.lower() or "vision" in tag.lower()),
                        "vram_gb": rec.get("vram_gb", size_gb),
                    })
                return {
                    "online": True,
                    "endpoint": url,
                    "total_models": len(installed),
                    "non_deepseek_models": [m for m in installed if not m["is_deepseek"]],
                    "models": installed,
                }
    except Exception as exc:
        logger.debug("Ollama daemon check error at %s: %s", url, exc)
    return {
        "online": False,
        "endpoint": url,
        "total_models": 0,
        "non_deepseek_models": [],
        "models": [],
        "error": "Ollama daemon unreachable at localhost:11434",
    }


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
    """Executes live queries against Ollama, DeepSeek, Gemini, or Custom endpoints."""

    def __init__(self):
        self.skill_registry = get_skill_registry()

    def generate(
        self,
        query: str,
        context_packet_text: str,
        route_profile: str = "D4_CROSS_GRAPH_SYNTHESIS",
        engine: str = "ollama:qwen3-vl:8b-instruct",
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        loc_payload_text: Optional[str] = None,
        loc_image_path: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generates a grounded answer using the specified engine and skill rules."""
        raw_engine = engine or OLLAMA_DEFAULT_MODEL
        engine_lower = raw_engine.lower()
        started = time.perf_counter()

        # Resolve credentials & endpoints
        if engine_lower.startswith("ollama"):
            # Supports "ollama" or "ollama:model_name"
            target_key = api_key or "ollama"
            target_url = base_url or OLLAMA_BASE_URL
            if ":" in raw_engine and not model_name:
                target_model = raw_engine.split(":", 1)[1]
            else:
                target_model = model_name or OLLAMA_DEFAULT_MODEL
        elif engine_lower == "deepseek":
            target_key = api_key or DEEPSEEK_API_KEY
            target_url = base_url or DEEPSEEK_BASE_URL
            target_model = model_name or DEEPSEEK_MODEL
        elif engine_lower == "gemini":
            target_key = api_key or GEMINI_API_KEY
            target_url = base_url or GEMINI_BASE_URL
            target_model = model_name or GEMINI_MODEL
        elif engine_lower in {"custom", "openai"}:
            target_key = api_key or CUSTOM_API_KEY or "custom-key"
            target_url = base_url or CUSTOM_BASE_URL
            target_model = model_name or CUSTOM_MODEL
        else:
            return LLMResponse(
                answer="",
                engine=engine_lower,
                model_name=model_name or "unknown",
                latency_ms=0.0,
                status="ERROR",
                error_message=f"Unsupported engine '{engine_lower}'. Use 'ollama', 'deepseek', 'gemini', or 'custom'.",
            )

        if not target_key and not engine_lower.startswith("ollama") and engine_lower != "custom":
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

        # Check for multimodal vision models and optional figure image
        is_vision_model = any(v in target_model.lower() for v in ["vl", "vision", "gemma4"])
        img_b64_str: Optional[str] = None
        if is_vision_model and loc_image_path:
            p = Path(loc_image_path)
            if p.is_file():
                try:
                    import base64
                    import io
                    from PIL import Image
                    img = Image.open(p).convert("RGB")
                    img.thumbnail((512, 512))
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=80)
                    img_b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
                except Exception as img_exc:
                    logger.debug("Failed to encode image %s for vision model: %s", loc_image_path, img_exc)

        if engine_lower.startswith("ollama"):
            # Use Ollama's native /api/chat endpoint so num_ctx=4096 and think=False are strictly respected
            # (Ollama's /v1/chat/completions ignores options.num_ctx and allocates 256K context on qwen3-vl)
            native_base = approved_url.rstrip("/")
            if native_base.endswith("/v1"):
                native_base = native_base[:-3]
            api_endpoint = native_base + "/api/chat"
            headers = {"Content-Type": "application/json"}
            user_msg: Dict[str, Any] = {"role": "user", "content": full_user_content}
            if img_b64_str:
                user_msg["images"] = [img_b64_str]
            payload = {
                "model": target_model,
                "messages": [
                    {"role": "system", "content": system_instruction},
                    user_msg,
                ],
                "stream": False,
                "think": False,
                "options": {
                    "num_ctx": 4096,
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }
        else:
            # Build OpenAI-compatible request payload
            api_endpoint = approved_url.rstrip("/") + "/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {target_key}",
            }
            user_message_content: Any = full_user_content
            if img_b64_str:
                user_message_content = [
                    {"type": "text", "text": full_user_content},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_b64_str}"}
                    }
                ]
            payload = {
                "model": target_model,
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_message_content},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(api_endpoint, data=req_data, headers=headers, method="POST")
            
            with urllib.request.urlopen(req, timeout=90) as resp:
                body = resp.read().decode("utf-8")
                data = json.loads(body)

            latency = (time.perf_counter() - started) * 1000.0
            if engine_lower.startswith("ollama") and "message" in data:
                answer_text = data.get("message", {}).get("content", "").strip()
                prompt_toks = int(data.get("prompt_eval_count", 0))
                comp_toks = int(data.get("eval_count", 0))
            else:
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
