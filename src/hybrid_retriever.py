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
from src.contextual_indexer import encode_text, compute_cosine_similarity
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

    def reciprocal_rank_fusion(
        self,
        sparse_results: List[Dict[str, Any]],
        dense_results: List[Dict[str, Any]],
        k: int = 60,
        top_k: int = 15
    ) -> List[RetrievedCandidate]:
        """Merges sparse and dense candidate lists using Reciprocal Rank Fusion."""
        rrf_scores: Dict[str, float] = {}
        candidate_meta: Dict[str, Dict[str, Any]] = {}
        sparse_ranks: Dict[str, int] = {}
        dense_ranks: Dict[str, int] = {}

        # 1. Process Sparse Ranks (1-indexed)
        for rank_idx, item in enumerate(sparse_results):
            cid = item["id"]
            sparse_ranks[cid] = rank_idx + 1
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank_idx + 1))
            if cid not in candidate_meta:
                candidate_meta[cid] = item

        # 2. Process Dense Ranks (1-indexed)
        for rank_idx, item in enumerate(dense_results):
            cid = item["id"]
            dense_ranks[cid] = rank_idx + 1
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank_idx + 1))
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
        top_k: int = 15
    ) -> List[RetrievedCandidate]:
        """Executes scoped hybrid retrieval based on a Pre-Retrieval RoutingDecision."""
        if decision.status != "SUPPORTED":
            return []

        # If entity was pre-resolved, inject into query focus
        query = decision.clean_query
        if decision.resolved_entities:
            entity_names = " ".join(e["name"] for e in decision.resolved_entities)
            query = f"{query} {entity_names}"

        sparse_candidates = self.search_sparse(query, decision.selected_modules, top_k=top_k)
        dense_candidates = self.search_dense(query, decision.selected_modules, top_k=top_k)

        return self.reciprocal_rank_fusion(sparse_candidates, dense_candidates, k=60, top_k=top_k)


_HYBRID_RETRIEVER = ScopedHybridRetriever()


def retrieve_hybrid_candidates(
    query: str,
    context: Optional[CallerContext] = None,
    top_k: int = 15
) -> Tuple[RoutingDecision, List[RetrievedCandidate]]:
    """Convenience top-level entrypoint performing Routing + Scoped Hybrid Retrieval."""
    decision = route_user_query(query, context)
    if decision.status != "SUPPORTED":
        return decision, []
    candidates = _HYBRID_RETRIEVER.retrieve(decision, top_k=top_k)
    return decision, candidates


if __name__ == "__main__":
    test_q = "What is Ghostfin's operational range and hybrid powertrain advantage?"
    dec, cands = retrieve_hybrid_candidates(test_q)
    print(f"Query: {test_q}")
    print(f"Route: {dec.route_profile.value} | Selected: {dec.selected_modules}")
    print(f"Retrieved {len(cands)} candidates:")
    for c in cands[:5]:
        print(f"  [{c.score}] ({c.graph_domain} | {c.candidate_type}) {c.candidate_id}: {c.content[:70]}...")
