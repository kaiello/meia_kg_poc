"""
Contextual Vector Indexer for MEIA Tri-Graph POC
Builds 1024-dimensional dense vector stores for:
1. Semantic Text Chunks (storage/vdb_chunks_contextual.json)
2. Primary Domain Entities (storage/vdb_entities.json)

Supports BAAI/bge-large-en-v1.5 and deterministic offline projection fallback
for air-gapped test reproducibility.
"""

import hashlib
import json
import logging
import math
import sqlite3
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config import (
    STORAGE_DIR,
    TRI_GRAPH_DB_PATH,
    TEXT_CHUNKS_JSONL,
    VDB_CHUNKS_PATH,
    VDB_ENTITIES_PATH,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIM
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("contextual_indexer")

_ST_MODEL = None


def get_embedding_model():
    """Lazily loads SentenceTransformer if installed, otherwise returns None."""
    global _ST_MODEL
    if _ST_MODEL is False:
        return None
    if _ST_MODEL is not None:
        return _ST_MODEL
    try:
        from sentence_transformers import SentenceTransformer
        # Check if local cache or offline run
        logger.info("Loading embedding model %s (dim=%d)", EMBEDDING_MODEL_NAME, EMBEDDING_DIM)
        try:
            _ST_MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME, local_files_only=True)
        except Exception:
            _ST_MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME)
        return _ST_MODEL
    except Exception as e:
        logger.warning("SentenceTransformer load error (%s). Using deterministic offline fallback projector.", e)
        _ST_MODEL = False
        return None


def deterministic_offline_vector(text: str, dim: int = EMBEDDING_DIM) -> List[float]:
    """Generates a deterministic, unit-normalized dense vector using salted MD5/SHA256 feature hashing.
    Guarantees consistent 1024-dimensional vectors for air-gapped offline testing."""
    vec = [0.0] * dim
    words = text.lower().split()
    if not words:
        words = ["empty"]

    for idx, w in enumerate(words):
        h = int(hashlib.md5(f"w_{w}_{idx}".encode("utf-8")).hexdigest()[:8], 16)
        pos = h % dim
        sign = 1.0 if (h % 2 == 0) else -1.0
        vec[pos] += sign

    # Add character n-gram features
    for i in range(len(text) - 3):
        ngram = text[i:i+4]
        h = int(hashlib.sha256(ngram.encode("utf-8")).hexdigest()[:8], 16)
        pos = h % dim
        sign = 1.0 if (h % 2 == 0) else -1.0
        vec[pos] += 0.5 * sign

    # Unit normalize
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 1e-12:
        vec = [round(x / norm, 6) for x in vec]
    else:
        vec[0] = 1.0
    return vec


def encode_text(text: str) -> List[float]:
    """Encodes a single text string into a 1024-dimensional vector."""
    model = get_embedding_model()
    if model is not None:
        try:
            arr = model.encode(text, normalize_embeddings=True)
            return [round(float(x), 6) for x in arr]
        except Exception as e:
            logger.warning("Inference failed (%s), using offline fallback", e)
    return deterministic_offline_vector(text, EMBEDDING_DIM)


def compute_cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Computes cosine similarity between two unit vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    return max(-1.0, min(1.0, dot))


def search_dense(
    query_vector: List[float],
    index_records: List[Dict[str, Any]],
    top_k: int = 10,
    graph_domain: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Performs cosine similarity search over in-memory dense vector records."""
    scored = []
    for item in index_records:
        if graph_domain and item.get("target_graph") and item.get("target_graph") != graph_domain:
            continue
        if graph_domain and item.get("graph_domain") and item.get("graph_domain") != graph_domain:
            continue
        score = compute_cosine_similarity(query_vector, item["vector"])
        scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, item in scored[:top_k]:
        res = dict(item)
        res["cosine_similarity"] = round(score, 4)
        results.append(res)
    return results


def build_contextual_vector_indices() -> Tuple[int, int]:
    """Builds and persists both vdb_chunks_contextual.json and vdb_entities.json."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Index Semantic Text Chunks
    logger.info("Indexing semantic text chunks from %s", TEXT_CHUNKS_JSONL)
    chunk_records = []
    if TEXT_CHUNKS_JSONL.exists():
        with open(TEXT_CHUNKS_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                chunk_records.append(json.loads(line))

    vdb_chunks = []
    for ch in chunk_records:
        content = ch.get("content", "")
        vec = encode_text(content)
        vdb_chunks.append({
            "chunk_id": ch["chunk_id"],
            "doc_id": ch.get("doc_id"),
            "standard_id": ch.get("standard_id"),
            "target_graph": ch.get("target_graph", "TECH"),
            "page_ordinal": ch.get("page_ordinal"),
            "content": content,
            "vector": vec
        })

    with open(VDB_CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(vdb_chunks, f, indent=2)
    logger.info("Saved %d contextual chunk vectors to %s", len(vdb_chunks), VDB_CHUNKS_PATH)

    # 2. Index Primary Domain Entities from SQLite
    logger.info("Indexing domain entities from %s", TRI_GRAPH_DB_PATH)
    vdb_entities = []
    if TRI_GRAPH_DB_PATH.exists():
        conn = sqlite3.connect(str(TRI_GRAPH_DB_PATH))
        c = conn.cursor()
        c.execute("SELECT id, graph_domain, bfo_category, label, properties_json FROM domain_nodes")
        rows = c.fetchall()
        conn.close()

        for nid, domain, bfo, label, props_str in rows:
            props = json.loads(props_str)
            text_repr = f"[{domain} ENTITY: {label}] " + " ".join(f"{k}: {v}" for k, v in props.items() if isinstance(v, (str, int, float)) and v)
            vec = encode_text(text_repr)
            vdb_entities.append({
                "node_id": nid,
                "graph_domain": domain,
                "bfo_category": bfo,
                "label": label,
                "text_repr": text_repr,
                "vector": vec
            })

    with open(VDB_ENTITIES_PATH, "w", encoding="utf-8") as f:
        json.dump(vdb_entities, f, indent=2)
    logger.info("Saved %d entity vectors to %s", len(vdb_entities), VDB_ENTITIES_PATH)

    return len(vdb_chunks), len(vdb_entities)


if __name__ == "__main__":
    c_count, e_count = build_contextual_vector_indices()
    print(f"Successfully built {c_count} chunk vectors and {e_count} entity vectors!")
