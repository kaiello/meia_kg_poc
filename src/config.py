"""Configuration constants and path definitions for MEIA Knowledge Graph POC."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "config"
DATA_DIR = REPO_ROOT / "data"
PARSED_DIR = REPO_ROOT / "parsed"
STORAGE_DIR = REPO_ROOT / "storage"
FIGURES_DIR = PARSED_DIR / "figures"
TABLES_DIR = PARSED_DIR / "tables"

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

# Multimodal extraction parameters
RENDER_DPI = 180
MAX_CHUNK_TOKENS = 400
CHUNK_OVERLAP_TOKENS = 50
EMBEDDING_MODEL_NAME = "BAAI/bge-large-en-v1.5"
EMBEDDING_DIM = 1024
