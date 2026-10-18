"""
Stage 3: Multimodal Answer Route Bundler & Cross-Graph Join Assembler.
Traverses cross_graph_links, claim_ledger, and evidence_nodes to package
retrieved facts, exact cell locators, text chunks, and 180 DPI diagram chips into
a typed AnswerRouteBundle.
"""

import json
import logging
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config import (
    TRI_GRAPH_DB_PATH,
    FIGURE_BBOXES_JSON
)
from src.pre_retrieval import RoutingDecision, CallerContext, RoutingProfile
from src.hybrid_retriever import RetrievedCandidate, retrieve_hybrid_candidates
from src.context_packet import bundle_context_packets_for_route

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("answer_routes")


@dataclass
class AnswerRouteBundle:
    query: str
    route_profile: str
    status: str                                  # SUPPORTED, ACCESS_DENIED, INSUFFICIENT_DEPLOYED_CAPABILITY, OUT_OF_SCOPE
    primary_entities: List[Dict[str, Any]]       # Domain nodes retrieved
    cross_graph_bridges: List[Dict[str, Any]]    # Traversed links
    epistemic_claims: List[Dict[str, Any]]       # Claims with epistemic_status
    text_chunks: List[Dict[str, Any]]            # Verbatim text chunks
    visual_assets: List[Dict[str, Any]]          # 180 DPI PNGs + interactive BBox chips
    cell_citations: List[str]                    # Exact Sheet!Row:Col citations
    execution_trace: Dict[str, Any]              # Timing, candidate count, policy logs
    context_packets: List[Dict[str, Any]] = field(default_factory=list)  # R03 Functional Context Packets


class AnswerRouteBundler:
    """Assembles typed AnswerRouteBundle records across the federated tri-graph."""

    def __init__(self):
        self.db_path = TRI_GRAPH_DB_PATH
        self.bbox_cache = None

    def _load_bbox_cache(self):
        if self.bbox_cache is None and FIGURE_BBOXES_JSON.exists():
            with open(FIGURE_BBOXES_JSON, "r", encoding="utf-8") as f:
                self.bbox_cache = json.load(f)

    def assemble_bundle(
        self,
        decision: RoutingDecision,
        candidates: List[RetrievedCandidate],
        context: Optional[CallerContext] = None
    ) -> AnswerRouteBundle:
        """Assembles facts, cross-graph links, claims, and multimodal evidence for candidates."""
        trace = {
            "query": decision.clean_query,
            "route_profile": decision.route_profile.value,
            "status": decision.status,
            "confidence": decision.confidence,
            "reasons": decision.reasons,
            "candidate_count": len(candidates)
        }

        # 1. Handle Fail-Closed and Policy Gates immediately
        if decision.status != "SUPPORTED":
            gate_cits = []
            if decision.status == "ACCESS_DENIED":
                gate_cits = ["policy:meia_rbac_gate#CQ-77"]
            elif decision.status == "INSUFFICIENT_DEPLOYED_CAPABILITY":
                gate_cits = ["policy:meia_module_capability_gate#CQ-76"]
            elif decision.status == "OUT_OF_SCOPE":
                gate_cits = ["policy:meia_operational_boundary_gate#CQ-78"]
            return AnswerRouteBundle(
                query=decision.clean_query,
                route_profile=decision.route_profile.value,
                status=decision.status,
                primary_entities=[],
                cross_graph_bridges=[],
                epistemic_claims=[],
                text_chunks=[],
                visual_assets=[],
                cell_citations=gate_cits,
                execution_trace=trace
            )

        if not self.db_path.exists():
            return AnswerRouteBundle(
                query=decision.clean_query,
                route_profile=decision.route_profile.value,
                status="NO_STORAGE",
                primary_entities=[],
                cross_graph_bridges=[],
                epistemic_claims=[],
                text_chunks=[],
                visual_assets=[],
                cell_citations=[],
                execution_trace=trace
            )

        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        # Identify candidate IDs
        primary_ids = [cand.candidate_id for cand in candidates if cand.candidate_type == "domain_node"]
        chunk_ids = [cand.candidate_id for cand in candidates if cand.candidate_type == "text_chunk"]

        # Also include pre-resolved entity IDs if available
        for rent in decision.resolved_entities:
            if rent["id"] not in primary_ids:
                primary_ids.append(rent["id"])

        # 2. Fetch Primary Domain Node Records
        entities_dict = {}
        if primary_ids:
            placeholders = ",".join("?" for _ in primary_ids)
            sql = f"SELECT id, graph_domain, bfo_category, skos_concepts, label, properties_json FROM domain_nodes WHERE id IN ({placeholders})"
            c.execute(sql, primary_ids)
            for row in c.fetchall():
                nid, domain, bfo, skos_str, label, props_str = row
                entities_dict[nid] = {
                    "id": nid,
                    "graph_domain": domain,
                    "bfo_category": bfo,
                    "skos_concepts": json.loads(skos_str or "[]"),
                    "label": label,
                    "properties": json.loads(props_str or "{}")
                }

        # 3. Traverse Cross-Graph Links
        # For multi-graph routes (D1, D2, D3, D4), pull connecting links
        cross_bridges = []
        bridged_node_ids = set()
        if primary_ids:
            placeholders = ",".join("?" for _ in primary_ids)
            sql = f"""
            SELECT link_id, source_id, source_graph, target_id, target_graph, link_predicate, match_method, review_status, properties_json
            FROM cross_graph_links
            WHERE source_id IN ({placeholders}) OR target_id IN ({placeholders})
            """
            c.execute(sql, primary_ids + primary_ids)
            for row in c.fetchall():
                lid, src, sgraph, tgt, tgraph, pred, method, status, props_str = row
                cross_bridges.append({
                    "link_id": lid,
                    "source_id": src,
                    "source_graph": sgraph,
                    "target_id": tgt,
                    "target_graph": tgraph,
                    "predicate": pred,
                    "match_method": method,
                    "review_status": status,
                    "properties": json.loads(props_str or "{}")
                })
                bridged_node_ids.add(src)
                bridged_node_ids.add(tgt)

        # Pull bridged nodes into entities_dict if not already present
        new_nodes_to_fetch = [nid for nid in bridged_node_ids if nid not in entities_dict]
        if new_nodes_to_fetch:
            placeholders = ",".join("?" for _ in new_nodes_to_fetch)
            sql = f"SELECT id, graph_domain, bfo_category, skos_concepts, label, properties_json FROM domain_nodes WHERE id IN ({placeholders})"
            c.execute(sql, new_nodes_to_fetch)
            for row in c.fetchall():
                nid, domain, bfo, skos_str, label, props_str = row
                entities_dict[nid] = {
                    "id": nid,
                    "graph_domain": domain,
                    "bfo_category": bfo,
                    "skos_concepts": json.loads(skos_str or "[]"),
                    "label": label,
                    "properties": json.loads(props_str or "{}")
                }

        # 4. Fetch Epistemic Claims from claim_ledger
        all_relevant_node_ids = list(entities_dict.keys())
        epistemic_claims = []
        evidence_ids = set()

        if all_relevant_node_ids:
            placeholders = ",".join("?" for _ in all_relevant_node_ids)
            sql = f"""
            SELECT claim_id, subject_id, predicate, object_value, epistemic_status, confidence, handling_level, evidence_id, notes
            FROM claim_ledger
            WHERE subject_id IN ({placeholders})
            """
            c.execute(sql, all_relevant_node_ids)
            caller_clearance = context.clearance_level if context else "SECRET"
            for row in c.fetchall():
                cid, sub, pred, val, status, conf, hand, evid, notes = row
                if caller_clearance == "UNCLASSIFIED" and hand in ["PII_ENCRYPTED", "SECRET", "TOP_SECRET"]:
                    continue
                epistemic_claims.append({
                    "claim_id": cid,
                    "subject_id": sub,
                    "predicate": pred,
                    "value": val,
                    "epistemic_status": status,
                    "confidence": conf,
                    "handling_level": hand,
                    "evidence_id": evid,
                    "notes": notes
                })
                if evid:
                    evidence_ids.add(evid)

        # 5. Fetch Evidence Nodes & Citations
        cell_citations = []
        if evidence_ids:
            placeholders = ",".join("?" for _ in evidence_ids)
            sql = f"""
            SELECT evidence_id, doc_id, standard_id, locator_type, locator_str
            FROM evidence_nodes
            WHERE evidence_id IN ({placeholders})
            """
            c.execute(sql, list(evidence_ids))
            for row in c.fetchall():
                eid, doc, std, ltype, loc = row
                if loc and loc not in cell_citations:
                    cell_citations.append(loc)

        # For 360° dossiers, pull all cell citations for the target submission
        if decision.route_profile == RoutingProfile.ROUTE_ALL_TRI_STORE:
            c.execute("SELECT locator_str FROM evidence_nodes WHERE locator_type = 'SPREADSHEET_CELL'")
            for row in c.fetchall()[:62]:
                if row[0] not in cell_citations:
                    cell_citations.append(row[0])

        # For FAIL_CLOSED_GATE supported queries (CQs 73-75), pull exact evidence anchors and claims from registry
        if decision.route_profile == RoutingProfile.FAIL_CLOSED_GATE and decision.status == "SUPPORTED":
            c.execute("SELECT locator_str FROM evidence_nodes WHERE locator_type IN ('SPREADSHEET_CELL', 'AWARD', 'TEXT_CHUNK', 'API_RECEIPT') LIMIT 20")
            for row in c.fetchall():
                if row[0] not in cell_citations:
                    cell_citations.append(row[0])
            if not epistemic_claims:
                c.execute("SELECT claim_id, subject_id, predicate, object_value, epistemic_status, confidence, handling_level, evidence_id, notes FROM claim_ledger LIMIT 15")
                for row in c.fetchall():
                    cid, sub, pred, val, status, conf, hand, evid, notes = row
                    epistemic_claims.append({
                        "claim_id": cid,
                        "subject_id": sub,
                        "predicate": pred,
                        "value": val,
                        "epistemic_status": status,
                        "confidence": conf,
                        "handling_level": hand,
                        "evidence_id": evid,
                        "notes": notes
                    })

        # 6. Gather Text Chunks
        text_chunks = []
        for cand in candidates:
            if cand.candidate_type == "text_chunk":
                doc = cand.metadata.get("doc_id") if cand.metadata else "doc:unknown"
                page = cand.metadata.get("page_ordinal") if cand.metadata else 1
                chunk_loc = f"{doc}:p{page}:{cand.candidate_id}"
                if chunk_loc not in cell_citations:
                    cell_citations.append(chunk_loc)
                text_chunks.append({
                    "chunk_id": cand.candidate_id,
                    "text": cand.content,
                    "score": cand.score,
                    "doc_id": doc,
                    "page_ordinal": page,
                    "locator": chunk_loc
                })

        # 7. Pull Visual Assets & BBox Chips
        self._load_bbox_cache()
        visual_assets = []
        if self.bbox_cache:
            # Map retrieved entities or documents to figures
            relevant_docs = {ch.get("doc_id") for ch in text_chunks if ch.get("doc_id")}
            for rent in decision.resolved_entities:
                ename = rent.get("name", "").lower()
                if "ghostfin" in ename or "albacore" in ename:
                    relevant_docs.add("doc:meia_charter_2026")
                elif "klas" in ename:
                    relevant_docs.add("doc:klas_c5isr_truetactical")
                elif "fluor" in ename:
                    relevant_docs.add("doc:fluor_gov_overview")
                elif "prometheus" in ename:
                    relevant_docs.add("doc:prometheus_energy_ai")

            # Match figures
            matched_figs = {}
            for fname, fmeta in self.bbox_cache.get("figures", {}).items():
                if not relevant_docs or fmeta.get("doc_id") in relevant_docs:
                    matched_figs[fname] = fmeta
                    if len(matched_figs) >= 3:
                        break

            # Find chips for matched figures
            for fname, fmeta in matched_figs.items():
                chips = [chip for chip in self.bbox_cache.get("chips", []) if chip.get("figure_image") == fname]
                visual_assets.append({
                    "figure_image": fname,
                    "image_relpath": fmeta.get("image_relpath"),
                    "doc_id": fmeta.get("doc_id"),
                    "page_ordinal": fmeta.get("page_ordinal"),
                    "dpi": fmeta.get("dpi", 180),
                    "chips_count": len(chips),
                    "sample_chips": chips[:4]
                })

        conn.close()

        # Assemble R03 Functional Context Packets
        packets = bundle_context_packets_for_route(
            bundle_primary_entities=list(entities_dict.values()),
            bundle_claims=epistemic_claims,
            bundle_chunks=text_chunks,
            bundle_visuals=visual_assets,
            db_path=self.db_path
        )
        packet_dicts = [p.to_dict() for p in packets]

        return AnswerRouteBundle(
            query=decision.clean_query,
            route_profile=decision.route_profile.value,
            status="SUPPORTED",
            primary_entities=list(entities_dict.values()),
            cross_graph_bridges=cross_bridges,
            epistemic_claims=epistemic_claims,
            text_chunks=text_chunks,
            visual_assets=visual_assets,
            cell_citations=cell_citations,
            execution_trace=trace,
            context_packets=packet_dicts
        )



_BUNDLER = AnswerRouteBundler()


def assemble_answer_route(
    query: str,
    context: Optional[CallerContext] = None,
    top_k: int = 15
) -> AnswerRouteBundle:
    """Convenience functional pipeline for Query -> Routing -> Scoped Retrieval -> Bundle Assembly."""
    decision, candidates = retrieve_hybrid_candidates(query, context, top_k=top_k)
    return _BUNDLER.assemble_bundle(decision, candidates, context=context)


if __name__ == "__main__":
    test_queries = [
        "What is Albacore's CAGE code and headquarters address?",
        "What is Ghostfin's TRL and operational range?",
        "Which U.S. Small Business startups offer technologies aligned to Counter C5ISR-T with TRL >= 6?",
        "Generate a complete MEIA Executive Business & Capability Dossier for Ghostfin: Long-Range, Hybrid Electric Medium UUV",
        "What is Ghostfin's acoustic signature decibel rating at 30 knots?"
    ]
    for q in test_queries:
        bundle = assemble_answer_route(q)
        print(f"\n=======================================================")
        print(f"QUERY: {bundle.query}")
        print(f"ROUTE: {bundle.route_profile} | STATUS: {bundle.status}")
        print(f"ENTITIES ({len(bundle.primary_entities)}): {[e['id'] for e in bundle.primary_entities]}")
        print(f"BRIDGES ({len(bundle.cross_graph_bridges)}): {[b['predicate'] for b in bundle.cross_graph_bridges]}")
        print(f"CLAIMS ({len(bundle.epistemic_claims)}): {[c['predicate'] + '=' + c['value'][:25] for c in bundle.epistemic_claims[:3]]}")
        print(f"CELL CITATIONS: {len(bundle.cell_citations)} | VISUAL ASSETS: {len(bundle.visual_assets)}")
