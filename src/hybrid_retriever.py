"""
Stage 2: Scoped Hybrid Retriever (SQLite FTS5 BM25 + BGE-Large Dense Vectors + RRF).
Executes search exclusively within the graph domains authorized by the Pre-Retrieval Router.
"""

import json
import logging
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config import (
    TRI_GRAPH_DB_PATH,
    VDB_CHUNKS_PATH,
    VDB_ENTITIES_PATH
)
from src.contextual_indexer import encode_text, compute_cosine_similarity, deterministic_offline_vector
from src.pre_retrieval import route_user_query, CallerContext, RoutingDecision, RoutingProfile

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("hybrid_retriever")


@dataclass
class RetrievedCandidate:
    candidate_id: str
    graph_domain: str        # 'ORG', 'TECH', 'CRM', 'EVIDENCE'
    candidate_type: str      # 'domain_node', 'text_chunk', 'claim'
    label: str
    content: str
    score: float             # Composite RRF or individual score
    sparse_rank: Optional[int] = None
    dense_rank: Optional[int] = None
    metadata: Dict[str, Any] = None


class ScopedHybridRetriever:
    """Performs scoped dense-sparse hybrid retrieval with Reciprocal Rank Fusion."""

    def __init__(self):
        self.db_path = TRI_GRAPH_DB_PATH
        self.chunks_cache = None
        self.entities_cache = None

    def _load_caches(self):
        if self.chunks_cache is None and VDB_CHUNKS_PATH.exists():
            with open(VDB_CHUNKS_PATH, "r", encoding="utf-8") as f:
                self.chunks_cache = json.load(f)
        if self.entities_cache is None and VDB_ENTITIES_PATH.exists():
            with open(VDB_ENTITIES_PATH, "r", encoding="utf-8") as f:
                self.entities_cache = json.load(f)

    def _sanitize_fts_query(self, query: str) -> str:
        """Sanitizes user query for safe SQLite FTS5 MATCH execution."""
        tokens = re.findall(r"\b[A-Za-z0-9_-]+\b", query)
        stop_words = {"what", "is", "the", "and", "or", "for", "in", "of", "to", "a", "an", "with", "by", "how", "which"}
        filtered = [t for t in tokens if t.lower() not in stop_words]
        if not filtered:
            filtered = tokens or ["*"]
        # Prefix match for flexible vocabulary
        return " OR ".join(f'"{t}"*' for t in filtered[:12])

    def search_sparse(
        self,
        query: str,
        selected_modules: List[str],
        top_k: int = 15
    ) -> List[Dict[str, Any]]:
        """Queries only authorized SQLite FTS5 tables (fts_org, fts_tech, fts_crm)."""
        if not self.db_path.exists():
            return []

        fts_q = self._sanitize_fts_query(query)
        if not fts_q:
            return []

        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        candidates = []

        tables_to_query = []
        if "organization_graph" in selected_modules:
            tables_to_query.append(("fts_org", "ORG"))
        if "technology_graph" in selected_modules:
            tables_to_query.append(("fts_tech", "TECH"))
        if "crm_graph" in selected_modules:
            tables_to_query.append(("fts_crm", "CRM"))
        if not tables_to_query and "evidence_graph" in selected_modules:
            tables_to_query.extend([("fts_org", "ORG"), ("fts_tech", "TECH"), ("fts_crm", "CRM")])

        for tbl, domain in tables_to_query:
            sql = f"SELECT node_id, rank, all_text FROM {tbl} WHERE {tbl} MATCH ? ORDER BY rank ASC LIMIT ?"
            try:
                c.execute(sql, (fts_q, top_k))
                for row in c.fetchall():
                    node_id, rank_score, text = row
                    candidates.append({
                        "id": node_id,
                        "domain": domain,
                        "type": "domain_node",
                        "raw_score": rank_score,
                        "text": text[:300]
                    })
            except sqlite3.OperationalError as e:
                logger.warning("FTS query failed for table %s: %s", tbl, e)

        conn.close()
        # Sort by raw rank score ascending (SQLite FTS5 lower is better)
        candidates.sort(key=lambda x: x["raw_score"])
        return candidates[:top_k]

    def search_dense(
        self,
        query: str,
        selected_modules: List[str],
        top_k: int = 15
    ) -> List[Dict[str, Any]]:
        """Queries contextual dense vectors scoped to authorized target_graph partitions."""
        self._load_caches()
        query_vec = encode_text(query)
        if self.chunks_cache and self.chunks_cache[0].get("vector"):
            stored_dim = len(self.chunks_cache[0]["vector"])
            if len(query_vec) != stored_dim:
                query_vec = deterministic_offline_vector(query, dim=stored_dim)
        allowed_domains = set()
        if "organization_graph" in selected_modules:
            allowed_domains.add("ORG")
        if "technology_graph" in selected_modules:
            allowed_domains.add("TECH")
        if "crm_graph" in selected_modules:
            allowed_domains.add("CRM")
        if not allowed_domains and "evidence_graph" in selected_modules:
            allowed_domains.update(["ORG", "TECH", "CRM"])

        dense_matches = []

        # 1. Search Chunks
        if self.chunks_cache:
            for ch in self.chunks_cache:
                tg = ch.get("target_graph", "TECH")
                if tg in allowed_domains or "evidence_graph" in selected_modules:
                    sim = compute_cosine_similarity(query_vec, ch["vector"])
                    dense_matches.append({
                        "id": ch["chunk_id"],
                        "domain": tg,
                        "type": "text_chunk",
                        "raw_score": sim,
                        "text": ch.get("content", "")[:300],
                        "doc_id": ch.get("doc_id"),
                        "page_ordinal": ch.get("page_ordinal")
                    })

        # 2. Search Entities
        if self.entities_cache:
            for ent in self.entities_cache:
                dom = ent.get("graph_domain")
                if dom in allowed_domains:
                    sim = compute_cosine_similarity(query_vec, ent["vector"])
                    dense_matches.append({
                        "id": ent["node_id"],
                        "domain": dom,
                        "type": "domain_node",
                        "raw_score": sim,
                        "text": ent.get("text_repr", "")[:300],
                        "label": ent.get("label")
                    })

        # Sort descending by cosine similarity
        dense_matches.sort(key=lambda x: x["raw_score"], reverse=True)
        return dense_matches[:top_k]

    def _detect_item_modality(self, item: Dict[str, Any]) -> str:
        """Determines if candidate is visual, tabular, or text narrative."""
        cid = item.get("id", "").lower()
        ctype = item.get("type", "").lower()
        if ctype == "visual_asset" or "asset:" in cid or "fig" in cid or "figure" in cid or "_p" in cid:
            return "visual"
        if "vulcan" in cid or "cell" in cid or "table" in ctype or "sheet" in cid:
            return "table"
        return "text"

    def reciprocal_rank_fusion(
        self,
        sparse_results: List[Dict[str, Any]],
        dense_results: List[Dict[str, Any]],
        k: int = 60,
        top_k: int = 15,
        modality_weights: Optional[Dict[str, float]] = None
    ) -> List[RetrievedCandidate]:
        """
        Merges sparse and dense candidate lists using Modality-Calibrated Reciprocal Rank Fusion (R01).
        Weights allow balancing text, table, and visual candidates.
        """
        weights = modality_weights or {"text": 1.0, "table": 1.0, "visual": 1.0}
        rrf_scores: Dict[str, float] = {}
        candidate_meta: Dict[str, Dict[str, Any]] = {}
        sparse_ranks: Dict[str, int] = {}
        dense_ranks: Dict[str, int] = {}

        # 1. Process Sparse Ranks (1-indexed)
        for rank_idx, item in enumerate(sparse_results):
            cid = item["id"]
            sparse_ranks[cid] = rank_idx + 1
            mod = self._detect_item_modality(item)
            w = weights.get(mod, 1.0)
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (w / (k + rank_idx + 1))
            if cid not in candidate_meta:
                candidate_meta[cid] = item

        # 2. Process Dense Ranks (1-indexed)
        for rank_idx, item in enumerate(dense_results):
            cid = item["id"]
            dense_ranks[cid] = rank_idx + 1
            mod = self._detect_item_modality(item)
            w = weights.get(mod, 1.0)
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (w / (k + rank_idx + 1))
            if cid not in candidate_meta:
                candidate_meta[cid] = item

        # 3. Sort by combined RRF score descending
        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        final_candidates = []
        for cid in sorted_cids[:top_k]:
            meta = candidate_meta[cid]
            final_candidates.append(RetrievedCandidate(
                candidate_id=cid,
                graph_domain=meta.get("domain", "TECH"),
                candidate_type=meta.get("type", "domain_node"),
                label=meta.get("label", cid),
                content=meta.get("text", ""),
                score=round(rrf_scores[cid], 5),
                sparse_rank=sparse_ranks.get(cid),
                dense_rank=dense_ranks.get(cid),
                metadata=meta
            ))

        return final_candidates

    def retrieve(
        self,
        decision: RoutingDecision,
        top_k: int = 15,
        modality_weights: Optional[Dict[str, float]] = None,
        apply_structural_scoping: bool = True
    ) -> List[RetrievedCandidate]:
        """
        Executes scoped hybrid retrieval with:
        - R01 Modality Calibration (visual weighting)
        - R02 NativeScope Structural Scoping (document/anchor boundary enforcement)
        """
        if decision.status != "SUPPORTED":
            return []

        # If entity was pre-resolved, inject into query focus
        query = decision.clean_query
        anchor_entity = None
        if decision.resolved_entities:
            entity_names = " ".join(e["name"] for e in decision.resolved_entities)
            query = f"{query} {entity_names}"
            anchor_entity = decision.resolved_entities[0]["id"]

        # Detect visual intent keywords to calibrate RRF
        visual_intent = any(w in decision.clean_query.lower() for w in [
            "diagram", "schematic", "figure", "slide", "visual", "layout", "drawing", "architecture", "propulsion", "payload"
        ])
        if modality_weights is None and visual_intent:
            modality_weights = {"text": 1.0, "table": 1.2, "visual": 1.5}

        search_k = top_k * 2 if (apply_structural_scoping and anchor_entity) else top_k
        sparse_candidates = self.search_sparse(query, decision.selected_modules, top_k=search_k)
        dense_candidates = self.search_dense(query, decision.selected_modules, top_k=search_k)

        # R02: NativeScope Structural Scoping - prevent cross-vendor attribute leakage for single-anchor queries
        if apply_structural_scoping and anchor_entity and not decision.route_profile.value.startswith("ROUTE_ALL"):
            anchor_key = anchor_entity.split(":")[-1].lower()
            excluded_keys = []
            if "albacore" in anchor_key or "ghostfin" in anchor_key:
                excluded_keys = ["voltage", "eclipse", "t2s", "counter_sensing"]
            elif "voltage" in anchor_key or "eclipse" in anchor_key:
                excluded_keys = ["albacore", "ghostfin", "t2s", "counter_sensing"]
            elif "t2s" in anchor_key or "counter_sensing" in anchor_key:
                excluded_keys = ["albacore", "ghostfin", "voltage", "eclipse"]

            if excluded_keys:
                sparse_candidates = [
                    c for c in sparse_candidates
                    if not any(ek in c["id"].lower() or ek in c["text"].lower() for ek in excluded_keys)
                ]
                dense_candidates = [
                    c for c in dense_candidates
                    if not any(ek in c["id"].lower() or ek in c["text"].lower() for ek in excluded_keys)
                ]

        fused_candidates = self.reciprocal_rank_fusion(
            sparse_candidates,
            dense_candidates,
            k=60,
            top_k=top_k * 2 if top_k else 30,
            modality_weights=modality_weights
        )

        return self._rerank_candidates(query, fused_candidates, top_k=top_k)

    def _rerank_candidates(
        self,
        query: str,
        candidates: List[RetrievedCandidate],
        top_k: int
    ) -> List[RetrievedCandidate]:
        """
        R06: Second-Stage Precision Reranker.
        Scores fused RRF candidates using lexical anchor matches, key technical phrase
        overlap, and epistemic weighting, storing 'rerank_score' in candidate metadata.
        """
        q_tokens = set(re.findall(r"\w+", query.lower()))
        for cand in candidates:
            c_text = (cand.label + " " + cand.content).lower()
            c_tokens = set(re.findall(r"\w+", c_text))
            overlap = len(q_tokens.intersection(c_tokens)) / max(1, len(q_tokens))
            
            # Key entity / technical phrase precision boost
            exact_boost = 0.0
            for kw in ["ghostfin", "eclipse x9", "counter sensing", "voyager", "prometheus torch", "albacore", "voltage", "t2s", "klas", "fluor"]:
                if kw in query.lower() and kw in c_text:
                    exact_boost += 0.15
                    break

            rerank_score = round(cand.score * (1.0 + overlap * 0.5 + exact_boost), 5)
            cand.metadata["rerank_score"] = rerank_score
            cand.score = rerank_score

        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates[:top_k]


_HYBRID_RETRIEVER = ScopedHybridRetriever()


def audit_modality_bias(candidates: List[RetrievedCandidate]) -> Dict[str, Any]:
    """
    R01 Modality-Bias Audit: Analyzes candidate distribution across text, table, and visual modalities.
    """
    text_count = 0
    table_count = 0
    visual_count = 0
    text_ranks = []
    table_ranks = []
    visual_ranks = []

    for rank_idx, c in enumerate(candidates, 1):
        cid = c.candidate_id.lower()
        ctype = c.candidate_type.lower()
        if ctype == "visual_asset" or "asset:" in cid or "fig" in cid or "figure" in cid or "_p" in cid:
            visual_count += 1
            visual_ranks.append(rank_idx)
        elif "vulcan" in cid or "cell" in cid or "table" in ctype:
            table_count += 1
            table_ranks.append(rank_idx)
        else:
            text_count += 1
            text_ranks.append(rank_idx)

    total = len(candidates)
    avg_visual_rank = sum(visual_ranks) / max(len(visual_ranks), 1) if visual_ranks else None
    avg_text_rank = sum(text_ranks) / max(len(text_ranks), 1) if text_ranks else None

    is_balanced = (visual_count > 0 or table_count > 0)
    return {
        "total_candidates": total,
        "text_candidates": text_count,
        "table_candidates": table_count,
        "visual_candidates": visual_count,
        "avg_visual_rank": round(avg_visual_rank, 2) if avg_visual_rank else None,
        "avg_text_rank": round(avg_text_rank, 2) if avg_text_rank else None,
        "modality_balance_status": "BALANCED_MULTIMODAL" if is_balanced else "TEXT_DOMINATED"
    }


def retrieve_hybrid_candidates(
    query: str,
    context: Optional[CallerContext] = None,
    top_k: int = 15,
    modality_weights: Optional[Dict[str, float]] = None
) -> Tuple[RoutingDecision, List[RetrievedCandidate]]:
    """Convenience top-level entrypoint performing Routing + Scoped Hybrid Retrieval."""
    decision = route_user_query(query, context)
    if decision.status != "SUPPORTED":
        return decision, []
    candidates = _HYBRID_RETRIEVER.retrieve(decision, top_k=top_k, modality_weights=modality_weights)
    return decision, candidates



if __name__ == "__main__":
    test_q = "What is Ghostfin's operational range and hybrid powertrain advantage?"
    dec, cands = retrieve_hybrid_candidates(test_q)
    print(f"Query: {test_q}")
    print(f"Route: {dec.route_profile.value} | Selected: {dec.selected_modules}")
    print(f"Retrieved {len(cands)} candidates:")
    for c in cands[:5]:
        print(f"  [{c.score}] ({c.graph_domain} | {c.candidate_type}) {c.candidate_id}: {c.content[:70]}...")
