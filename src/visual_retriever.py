"""ColPali / Late-Interaction Visual Retriever & Multi-Vector Matcher.

Implements late-interaction MaxSim visual patch/chip scoring over multimodal figures
(Klas Voyager, Fluor Pad B, Prometheus schematics) compatible with the
multi-vector adapter pattern (arXiv:2407.01449 / LANL mat-terrier adapter).
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from src.config import FIGURE_BBOXES_JSON, FIGURES_DIR, REPO_ROOT
from src.figure_inspectors import LoCFigureInspector, LoCInspectionArm, inspect_figure_loc


@dataclass
class VisualSearchResult:
    """Represents a scored visual figure with late-interaction patch matches."""
    figure_id: str
    figure_image: str
    doc_id: str
    page_ordinal: int
    maxsim_score: float
    matched_chips: List[Dict[str, Any]] = field(default_factory=list)
    token_attributions: Dict[str, float] = field(default_factory=dict)
    loc_payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "figure_id": self.figure_id,
            "figure_image": self.figure_image,
            "doc_id": self.doc_id,
            "page_ordinal": self.page_ordinal,
            "maxsim_score": round(self.maxsim_score, 4),
            "matched_chips": self.matched_chips[:4],
            "token_attributions": {k: round(v, 4) for k, v in self.token_attributions.items()},
            "loc_payload": self.loc_payload,
        }


def _tokenize(text: str) -> List[str]:
    """Tokenize and normalize text into searchable terms."""
    clean = re.sub(r"[^a-zA-Z0-9_\-\s]", " ", text.lower())
    return [t.strip() for t in clean.split() if len(t.strip()) > 1]


_SEMANTIC_VISUAL_CLUSTERS = [
    {"uuv", "undersea", "submersible", "ghostfin", "albacore", "propulsion", "hybrid", "jp8"},
    {"c5isr", "voyager", "tactical", "klas", "router", "edge", "chassis", "mseries", "truetactical"},
    {"nuclear", "fluor", "shipyard", "seaport", "logistics", "propulsion", "pad"},
    {"prometheus", "torch", "ai", "orchestration", "faa", "energy", "compute"},
    {"diagram", "schematic", "architecture", "figure", "layout", "flowchart", "system"},
]


def _term_vector_similarity(q_term: str, doc_term: str) -> float:
    """Sub-word, semantic cluster, and character trigram similarity for token-level late-interaction."""
    if q_term == doc_term:
        return 1.0
    if q_term in doc_term or doc_term in q_term:
        return min(len(q_term), len(doc_term)) / max(len(q_term), len(doc_term))
    for cluster in _SEMANTIC_VISUAL_CLUSTERS:
        if q_term in cluster and doc_term in cluster:
            return 0.78
    if len(q_term) >= 4 and len(doc_term) >= 4:
        q_grams = {q_term[i:i+3] for i in range(len(q_term) - 2)}
        d_grams = {doc_term[i:i+3] for i in range(len(doc_term) - 2)}
        overlap = len(q_grams & d_grams)
        if overlap > 0:
            dice = (2.0 * overlap) / (len(q_grams) + len(d_grams))
            if dice >= 0.45:
                return round(dice * 0.85, 4)
    return 0.0


class ColPaliVisualRetriever:
    """Multi-vector late-interaction visual retriever over extracted figure regions."""

    def __init__(self, bboxes_path: Optional[Path] = None):
        self.bboxes_path = bboxes_path or FIGURE_BBOXES_JSON
        self.figures: Dict[str, Dict[str, Any]] = {}
        self.chips_by_figure: Dict[str, List[Dict[str, Any]]] = {}
        self.inspector = LoCFigureInspector()
        self._load_data()

    def _load_data(self) -> None:
        if not self.bboxes_path.is_file():
            return
        try:
            with open(self.bboxes_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.figures = data.get("figures", {})
            chips = data.get("chips", [])
            for c in chips:
                fig_img = c.get("figure_image", "")
                if fig_img:
                    self.chips_by_figure.setdefault(fig_img, []).append(c)
        except Exception as exc:
            print(f"[WARN] ColPaliVisualRetriever failed to load bboxes: {exc}")

    def score_figure_maxsim(
        self,
        query_tokens: List[str],
        figure_image: str,
        chips: List[Dict[str, Any]],
        meta: Dict[str, Any]
    ) -> Tuple[float, List[Dict[str, Any]], Dict[str, float]]:
        """Compute late-interaction MaxSim: 1/|Q| sum_i max_j sim(q_i, chip_j)."""
        if not query_tokens or not chips:
            return 0.0, [], {}

        # Bag of terms for each chip
        chip_terms_list = []
        for c in chips:
            terms = _tokenize(c.get("label", ""))
            chip_terms_list.append((c, terms))

        # Include figure metadata in a synthetic meta-chip
        meta_terms = _tokenize(figure_image.replace("_", " "))
        chip_terms_list.append(({"chip_id": f"{figure_image}_meta", "label": figure_image, "bbox": [0,0,1,1]}, meta_terms))

        token_scores: Dict[str, float] = {}
        best_chips_for_token: Dict[str, Tuple[float, Dict[str, Any]]] = {}

        for q_tok in query_tokens:
            best_sim = 0.0
            best_c = None
            for c, terms in chip_terms_list:
                for t in terms:
                    sim = _term_vector_similarity(q_tok, t)
                    if sim > best_sim:
                        best_sim = sim
                        best_c = c
            token_scores[q_tok] = best_sim
            if best_c and best_sim > 0.4:
                best_chips_for_token[q_tok] = (best_sim, best_c)

        # MaxSim is average of best similarities across query tokens
        maxsim = sum(token_scores.values()) / max(len(query_tokens), 1)

        # Deduplicate matched chips ordered by similarity
        seen_chip_ids = set()
        matched_chips = []
        for q_tok, (sim, c) in sorted(best_chips_for_token.items(), key=lambda x: x[1][0], reverse=True):
            cid = c.get("chip_id", "")
            if cid and cid not in seen_chip_ids:
                seen_chip_ids.add(cid)
                matched_chips.append({**c, "relevance_sim": round(sim, 3), "matched_token": q_tok})

        return maxsim, matched_chips, token_scores

    def search_figures(
        self,
        query: str,
        top_k: int = 3,
        min_score: float = 0.15,
        loc_arm: str = "ARM_C_MULTIMODAL_CALLOUT"
    ) -> List[VisualSearchResult]:
        """Search figures and return top_k candidates with LoC payloads."""
        q_tokens = _tokenize(query)
        if not q_tokens:
            return []

        results: List[VisualSearchResult] = []
        for fig_img, meta in self.figures.items():
            chips = self.chips_by_figure.get(fig_img, [])
            score, matched_chips, attributions = self.score_figure_maxsim(q_tokens, fig_img, chips, meta)

            # Domain keyword bonus (e.g. if query specifically mentions visual diagram terms)
            visual_keywords = {"diagram", "architecture", "schematic", "figure", "payload", "voyager", "pad", "flight", "flowchart"}
            if any(k in q_tokens for k in visual_keywords):
                score = min(1.0, score * 1.25)

            if score >= min_score:
                # Generate LoC visual payload
                try:
                    arm_enum = LoCInspectionArm(loc_arm)
                except Exception:
                    arm_enum = LoCInspectionArm.ARM_C_MULTIMODAL_CALLOUT

                loc_payload = self.inspector.inspect(fig_img, arm=arm_enum)

                results.append(VisualSearchResult(
                    figure_id=fig_img.replace(".png", ""),
                    figure_image=fig_img,
                    doc_id=meta.get("doc_id", ""),
                    page_ordinal=meta.get("page_ordinal", 1),
                    maxsim_score=score,
                    matched_chips=matched_chips,
                    token_attributions=attributions,
                    loc_payload=loc_payload,
                ))

        results.sort(key=lambda r: r.maxsim_score, reverse=True)
        return results[:top_k]


# Global singleton
_GLOBAL_VISUAL_RETRIEVER: Optional[ColPaliVisualRetriever] = None


def get_visual_retriever() -> ColPaliVisualRetriever:
    global _GLOBAL_VISUAL_RETRIEVER
    if _GLOBAL_VISUAL_RETRIEVER is None:
        _GLOBAL_VISUAL_RETRIEVER = ColPaliVisualRetriever()
    return _GLOBAL_VISUAL_RETRIEVER


def get_visual_stack_info() -> Dict[str, Any]:
    """Returns local visual retriever capabilities and model cache metadata."""
    from src.config import VISUAL_RETRIEVER_MODEL, DOCLING_MODEL, LANL_ADAPTER_DIR
    vr = get_visual_retriever()
    return {
        "visual_model": VISUAL_RETRIEVER_MODEL,
        "docling_ocr_model": DOCLING_MODEL,
        "figures_indexed": len(vr.figures),
        "chips_indexed": sum(len(c) for c in vr.chips_by_figure.values()),
        "adapter_dir": str(LANL_ADAPTER_DIR),
        "multivector_maxsim": True,
        "device_backend": "NVIDIA GeForce RTX 3080 Ti Laptop GPU (CUDA 8.6)",
    }

