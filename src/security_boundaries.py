"""Security boundaries and validation for local assets and model endpoints.

Enforces strict URL validation, prevents SSRF/credential leakage, and restricts
model endpoints to approved local or external APIs.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

# Approved host allowlist for external LLM inference
APPROVED_HOST_ALLOWLIST = frozenset({
    "localhost",
    "127.0.0.1",
    "::1",
    "api.deepseek.com",
    "generativelanguage.googleapis.com",
    "openrouter.ai",
    "api.openai.com",
    "api.groq.com",
})


def canonical_endpoint(value: str) -> str:
    """Validate an HTTP API root without changing meaningful path components."""
    if not isinstance(value, str) or not value or re.search(r"[\s\x00-\x1f\x7f\\%]", value):
        raise ValueError("Invalid model endpoint.")
    try:
        parts = urlsplit(value)
        host, port = parts.hostname, parts.port
    except ValueError:
        raise ValueError("Invalid model endpoint.") from None

    if (parts.scheme not in {"https", "http"} or not host or parts.username is not None
            or parts.password is not None or parts.query or parts.fragment or "?" in value or "#" in value
            or any(segment in {".", ".."} for segment in parts.path.split("/"))):
        raise ValueError("Invalid model endpoint.")

    if parts.scheme == "http" and host not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Model endpoints require HTTPS except for configured loopback services.")

    if not host.isascii():
        raise ValueError("Invalid model endpoint.")

    authority = "[" + host + "]" if ":" in host else host.lower()
    if port is not None and port != (443 if parts.scheme == "https" else 80):
        authority += ":" + str(port)
    return parts.scheme + "://" + authority + parts.path.rstrip("/")


def validate_model_endpoint(requested: str | None, configured: str, allow_remote_api: bool = True) -> str:
    """Verify that the model endpoint is canonical and belongs to an approved host."""
    target = requested if requested else configured
    approved = canonical_endpoint(target)
    parts = urlsplit(approved)
    host = (parts.hostname or "").lower()

    if host not in APPROVED_HOST_ALLOWLIST:
        # Check if it's a subdomain of an approved host (e.g., region-specific endpoints)
        if not any(host.endswith("." + allowed) for allowed in APPROVED_HOST_ALLOWLIST if not allowed.startswith(":")):
            raise ValueError(f"Host '{host}' is not in the approved model endpoint allowlist.")

    return approved


def canonical_origin(value: str) -> str:
    """Validate a web origin."""
    endpoint = canonical_endpoint(value)
    if urlsplit(endpoint).path:
        raise ValueError("An origin must contain only scheme, host and port.")
    return endpoint


def decode_asset_name(raw: str) -> str:
    """Decode to closure, then reject Windows aliases, ADS and path traversal syntax."""
    value = raw
    for _ in range(8):
        if re.search(r"%(?![0-9a-fA-F]{2})", value):
            raise ValueError("Invalid asset encoding.")
        decoded = unquote(value, errors="strict")
        if decoded == value:
            break
        value = decoded
    else:
        raise ValueError("Too many asset encodings.")
    if (not value or value in {".", ".."} or value.rstrip(" .") != value
            or any(ord(c) < 32 or c in '/\\:%<>"|?*' for c in value)):
        raise ValueError("Invalid asset name.")
    return value
