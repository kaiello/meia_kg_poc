"""Configuration constants and path definitions for MEIA Knowledge Graph POC."""
from __future__ import annotations

import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "config"
DATA_DIR = REPO_ROOT / "data"
PARSED_DIR = REPO_ROOT / "parsed"
STORAGE_DIR = REPO_ROOT / "storage"
FIGURES_DIR = PARSED_DIR / "figures"
TABLES_DIR = PARSED_DIR / "tables"
SKILLS_DIR = REPO_ROOT / "skills"

# Manifest
MANIFEST_PATH = CONFIG_DIR / "meia_poc_manifest.json"

# Ingested sources
VULCAN_EXPORT_PATH = DATA_DIR / "MEIA_TEM_Vulcan_Export.xlsx"
CRM_MAPPING_PATH = DATA_DIR / "CRM_Object_Field_Mapping.xlsx"
CHARTER_PATH = DATA_DIR / "MEIA_Charter_2026.pdf"
COMPANY_DATA_DIR = DATA_DIR / "company_data"
FEDERAL_FEEDS_DIR = DATA_DIR / "federal_feeds"
USASPENDING_DATA_PATH = FEDERAL_FEEDS_DIR / "usaspending_vendor_history.json"

# Output parsed paths
VULCAN_PARSED_JSONL = PARSED_DIR / "vulcan_submissions.jsonl"
USASPENDING_PARSED_JSONL = PARSED_DIR / "usaspending_awards.jsonl"
TEXT_CHUNKS_JSONL = PARSED_DIR / "text_chunks.jsonl"
FIGURE_BBOXES_JSON = FIGURES_DIR / "figure_bboxes.json"

# Storage paths
TRI_GRAPH_DB_PATH = STORAGE_DIR / "meia_tri_graph_registry.db"
ORG_GRAPHML_PATH = STORAGE_DIR / "org_kg.graphml"
TECH_GRAPHML_PATH = STORAGE_DIR / "tech_kg.graphml"
CRM_GRAPHML_PATH = STORAGE_DIR / "crm_graph.graphml"
FEDERATED_GRAPHML_PATH = STORAGE_DIR / "federated_epistemic_graph.graphml"
VDB_CHUNKS_PATH = STORAGE_DIR / "vdb_chunks_contextual.json"
VDB_ENTITIES_PATH = STORAGE_DIR / "vdb_entities.json"

# Multimodal extraction parameters
RENDER_DPI = 180
MAX_CHUNK_TOKENS = 400
CHUNK_OVERLAP_TOKENS = 50
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-large-en-v1.5")
EMBEDDING_DIM = 1024

# Cross-Encoder Reranker & Visual Models (Cached in ~/.cache/huggingface/hub)
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base")
VISUAL_RETRIEVER_MODEL = os.getenv("VISUAL_RETRIEVER_MODEL", "vidore/colqwen2.5-v0.2")
DOCLING_MODEL = os.getenv("DOCLING_MODEL", "ibm/granite-docling:258m")

# Load environment (.env in repo root, home, or fallback to sibling prototypes)
load_dotenv(REPO_ROOT / ".env")
load_dotenv(Path.home() / ".env")
if not os.getenv("DEEPSEEK_API_KEY"):
    fallback_a30 = Path("C:/Users/kenai/aws-a30-prototype/.env")
    if fallback_a30.is_file():
        load_dotenv(fallback_a30)

# Local Ollama Open-Weight Inference Configuration (Non-DeepSeek Default)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_NATIVE_URL = os.getenv("OLLAMA_NATIVE_URL", "http://localhost:11434")
OLLAMA_DEFAULT_MODEL = os.getenv("OLLAMA_DEFAULT_MODEL", "qwen3-vl:8b-instruct")

OLLAMA_RECOMMENDED_MODELS = {
    "qwen3-vl:8b-instruct": {
        "label": "Qwen3-VL 8B Instruct (Multimodal + RAG)",
        "role": "Primary Multimodal & Grounded Synthesis",
        "vram_gb": 6.1,
        "multimodal": True,
    },
    "gemma4:e4b": {
        "label": "Google Gemma 4 E4B (Analytical Reasoning)",
        "role": "Cross-Graph Analytical Synthesis",
        "vram_gb": 9.6,
        "multimodal": True,
    },
    "hermes3:8b": {
        "label": "Nous Hermes 3 8B (Skill & Citation Follower)",
        "role": "Strict Skill Execution & Citation Formatting",
        "vram_gb": 4.7,
        "multimodal": False,
    },
    "qwen2.5vl:7b": {
        "label": "Qwen2.5-VL 7B (Visual Schematic Inspector)",
        "role": "LoC Arm-C Diagram & BBox Inspection",
        "vram_gb": 6.0,
        "multimodal": True,
    },
    "glm-ocr:latest": {
        "label": "GLM-OCR (Schematic & Document OCR)",
        "role": "Region Callout & Table OCR",
        "vram_gb": 2.2,
        "multimodal": True,
    },
}

# Inference Configuration: DeepSeek (Optional Cloud Fallback)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# Dual-Engine: Google Gemini (Optional Cloud Fallback)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Custom / OpenAI / Alternative Loopback
CUSTOM_API_KEY = os.getenv("CUSTOM_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
CUSTOM_BASE_URL = os.getenv("CUSTOM_BASE_URL", "https://api.openai.com/v1")
CUSTOM_MODEL = os.getenv("CUSTOM_MODEL", "gpt-4o-mini")

# Default Engine: Local Ollama Open-Weight Model
DEFAULT_ENGINE = os.getenv("DEFAULT_ENGINE", "ollama:qwen3-vl:8b-instruct")

# ColPali / Late-Interaction Adapter reference (from LANL card09 demo assets)
LANL_ADAPTER_DIR = Path("C:/Users/kenai/lanl-demo-assets-card09/models/adapter")

