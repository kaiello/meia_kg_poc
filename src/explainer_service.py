"""
MEIA Archify Explainer Service & Diagram IR Catalog.
Provides structured metadata, guided steps, active node/edge mappings,
and verified source file excerpts for the interactive Explainer Page.
"""

from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"
DIAGRAMS_DIR = STATIC_DIR / "diagrams"

# Complete Archify Explainer Panels Catalog
EXPLAINER_PANELS: List[Dict[str, Any]] = [
    {
        "id": "panel-1-architecture",
        "index": 1,
        "title": "Tri-Graph Federation & Epistemic Architecture",
        "shortTitle": "Federated Tri-Graph",
        "svgFile": "diagram1_architecture.svg",
        "domain": "trigraph",
        "conclusion": {
            "headline": "Formal Tri-Graph Isolation with Reified Epistemic Bridging",
            "summary": "The MEIA architecture segregates Org-KG, Tech-KG, and CRM-Graph into typed domain subgraphs tethered to an immutable Multimodal Evidence Spine, guaranteeing zero cross-domain state pollution while maintaining full federated traversability.",
            "metrics": [
                {"label": "Domain Graphs", "value": "3 (Org, Tech, CRM)"},
                {"label": "BFO Classes", "value": "21 Formal Classes"},
                {"label": "Inverse Object Pairs", "value": "13 Pairs (26 Total)"},
                {"label": "RDF Triples Exported", "value": "4,188 Triples"}
            ]
        },
        "steps": [
            {
                "step": 1,
                "title": "Declarative Ingestion & Document Fingerprinting",
                "badge": "INGEST",
                "narrative": "Every input source (Vulcan Excel, native PDFs, raster PDFs, federal API snapshots) is hashed with SHA-256 and mapped into exact physical coordinates before entering graph memory.",
                "activeNodes": ["node-manifest", "node-vulcan-excel", "node-pdf-corpus", "node-fed-apis", "node-extractor"],
                "activeEdges": ["edge-ingest-extract"],
                "sources": [
                    {
                        "id": "SRC 1",
                        "file": "config/meia_poc_manifest.json",
                        "startLine": 1,
                        "endLine": 35,
                        "label": "Declarative Corpus Manifest with SHA-256 digests"
                    }
                ]
            },
            {
                "step": 2,
                "title": "Federated Domain Graph Partitioning",
                "badge": "GRAPH STORES",
                "narrative": "Three distinct domain graphs are instantiated: Org-KG holds vendor CAGE/UEI registries and contract vehicles; Tech-KG stores offerings, SKOS taxonomy concepts, and TRL assessments; CRM-Graph tracks 48h SLA pipeline stages and commercial observations.",
                "activeNodes": ["node-org-entity", "node-org-award", "node-tech-offering", "node-tech-skos", "node-crm-submission", "node-crm-stage"],
                "activeEdges": ["edge-extract-org", "edge-extract-tech", "edge-extract-crm"],
                "sources": [
                    {
                        "id": "SRC 2",
                        "file": "ontology/meia_ontology.ttl",
                        "startLine": 25,
                        "endLine": 75,
                        "label": "BFO 2020 & SKOS OWL 2 DL class definitions"
                    }
                ]
            },
            {
                "step": 3,
                "title": "Typed Cross-Graph Link Bridges",
                "badge": "LINK BRIDGES",
                "narrative": "Cross-domain relations are maintained via explicit typed link bridges with bidirectional inverse mappings (e.g., [:DEVELOPS_OFFERING] <=> [:OFFERED_BY_ORGANIZATION], [:SUBMITTED_BY_ORG] <=> [:HAS_CAPABILITY_SUBMISSION]).",
                "activeNodes": ["node-org-entity", "node-tech-offering", "node-crm-submission"],
                "activeEdges": ["edge-bridge-org-tech", "edge-bridge-crm-tech", "edge-bridge-crm-org"],
                "sources": [
                    {
                        "id": "SRC 3",
                        "file": "src/ontology_service.py",
                        "startLine": 25,
                        "endLine": 65,
                        "label": "Inverse Predicate Registry (13 declared pairs)"
                    }
                ]
            },
            {
                "step": 4,
                "title": "Shared Multimodal Evidence Spine Grounding",
                "badge": "EVIDENCE",
                "narrative": "Every graph assertion is grounded to an immutable evidence locator: spreadsheet cell coordinates (Sheet!R:C), PDF bounding boxes (BBox), 180/300 DPI visual crops, or federal procurement receipts.",
                "activeNodes": ["node-ev-cells", "node-ev-chunks", "node-ev-figures", "node-ev-apis"],
                "activeEdges": ["edge-ev-org", "edge-ev-tech", "edge-ev-crm"],
                "sources": [
                    {
                        "id": "SRC 4",
                        "file": "src/build_tri_graph.py",
                        "startLine": 110,
                        "endLine": 165,
                        "label": "Epistemic spine anchoring and RDF triple synthesis"
                    }
                ]
            }
        ]
    },
    {
        "id": "panel-2-preretrieval",
        "index": 2,
        "title": "Pre-Retrieval Policy, NativeScope & Fail-Closed Gateways",
        "shortTitle": "Pre-Retrieval & Policy",
        "svgFile": "diagram2_preretrieval.svg",
        "domain": "policy",
        "conclusion": {
            "headline": "Zero-Hallucination Policy Gateways Before Vector Traversal",
            "summary": "To eliminate the risk of hallucination and security boundary violations, the pre-retrieval pipeline verifies security clearance, applies NativeScope multi-hop constraints, resolves SKOS hierarchies via SQL CTEs, and enforces fail-closed gates (CQ-76/77/78).",
            "metrics": [
                {"label": "Policy Gate Latency", "value": "< 1 ms"},
                {"label": "Fail-Closed Triggers", "value": "CQ-76, CQ-77, CQ-78"},
                {"label": "Hierarchy Resolution", "value": "Recursive SQL CTEs"},
                {"label": "Hallucination Rate", "value": "0.0% Verified"}
            ]
        },
        "steps": [
            {
                "step": 1,
                "title": "Ingress Validation & CallerContext Clearance",
                "badge": "SECURITY",
                "narrative": "Queries enter with a cryptographic CallerContext defining caller role and clearance level (UNCLASSIFIED, CUI, SECRET). Traversal engines strictly drop unauthorized compartments before parsing begins.",
                "activeNodes": ["node-raw-query", "node-caller-ctx", "node-intent-parser"],
                "activeEdges": ["edge-ingress-scope"],
                "sources": [
                    {
                        "id": "SRC 5",
                        "file": "src/pre_retrieval.py",
                        "startLine": 30,
                        "endLine": 75,
                        "label": "CallerContext clearance gating & minimum-sufficient routing"
                    }
                ]
            },
            {
                "step": 2,
                "title": "NativeScope Traversal & SKOS Recursive SQL CTEs",
                "badge": "CTE RESOLVER",
                "narrative": "NativeScope validates that multi-hop graph exploration does not breach authorization boundaries (max_hops = 3). Concurrently, a recursive SQL CTE executes transitive broader/narrower concept expansion across OSRA 2021 & MEIA topics.",
                "activeNodes": ["node-nativescope", "node-skos-cte", "node-min-router"],
                "activeEdges": ["edge-scope-skos", "edge-skos-router"],
                "sources": [
                    {
                        "id": "SRC 6",
                        "file": "src/ontology_service.py",
                        "startLine": 115,
                        "endLine": 175,
                        "label": "Recursive SQL CTEs for transitive SKOS taxonomy hierarchy"
                    }
                ]
            },
            {
                "step": 3,
                "title": "Fail-Closed Gateway Enforcement (CQ-76, CQ-77, CQ-78)",
                "badge": "FAIL-CLOSED",
                "narrative": "CQ-76 detects missing evidence and halts with zero tokens generated. CQ-77 rejects category conflation (Contract vs Grant). CQ-78 resolves historical entity lineage and mergers through CAGE tracking.",
                "activeNodes": ["node-gate-cq76", "node-gate-cq77", "node-gate-cq78"],
                "activeEdges": ["edge-router-gates", "edge-gate-abort"],
                "sources": [
                    {
                        "id": "SRC 7",
                        "file": "src/pre_retrieval.py",
                        "startLine": 140,
                        "endLine": 230,
                        "label": "CQ-76/77/78 Fail-closed policy rules and disjointness checkers"
                    }
                ]
            },
            {
                "step": 4,
                "title": "Execution Target Dispatch",
                "badge": "DISPATCH",
                "narrative": "Passing queries are routed to the optimal engine: deterministic graph proof (< 35ms), multimodal visual reader, or live LLM with domain skills.",
                "activeNodes": ["node-fastpath", "node-mmtarget", "node-llmtarget"],
                "activeEdges": ["edge-gate-fast", "edge-gate-mm", "edge-gate-llm"],
                "sources": [
                    {
                        "id": "SRC 8",
                        "file": "src/grounded_answer.py",
                        "startLine": 45,
                        "endLine": 95,
                        "label": "Query execution dispatch and pipeline routing"
                    }
                ]
            }
        ]
    },
    {
        "id": "panel-3-trident",
        "index": 3,
        "title": "Trident Multimodal Ingest & ColPali Late-Interaction",
        "shortTitle": "Trident Visual Search",
        "svgFile": "diagram3_trident.svg",
        "domain": "trident",
        "conclusion": {
            "headline": "Sub-Region Precision with ColPali ViT Patches and LoC 3-Arm Crops",
            "summary": "Trident ingests PDF documents into lossless 180 DPI rasters, generates 1024-patch multi-vector embeddings via ColPali, and extracts sub-region focal crops (LoC Arm A, B, C) to achieve zero OCR truncation loss and pin-point visual accuracy.",
            "metrics": [
                {"label": "Raster Resolution", "value": "180 DPI / 300 DPI"},
                {"label": "ViT Patch Tokens", "value": "1024 Patches / Page"},
                {"label": "Visual Arms", "value": "Arm A, Arm B, Arm C"},
                {"label": "Late-Interaction", "value": "MaxSim Multi-Vector"}
            ]
        },
        "steps": [
            {
                "step": 1,
                "title": "180 DPI Rasterization & Spatial Bounding",
                "badge": "RASTER",
                "narrative": "Native and raster-scanned PDFs are rendered into 180 DPI RGB24 pixel rasters. Docling and PyMuPDF segment document elements into normalized [ymin, xmin, ymax, xmax] bounding boxes, bypassing the 40-figure limitation.",
                "activeNodes": ["node-doc-input", "node-raster-engine", "node-layout-parser"],
                "activeEdges": ["edge-ingest-arm-a", "edge-ingest-arm-b", "edge-ingest-arm-c"],
                "sources": [
                    {
                        "id": "SRC 9",
                        "file": "src/extract.py",
                        "startLine": 80,
                        "endLine": 140,
                        "label": "PDF rasterization & spatial layout element bounding"
                    }
                ]
            },
            {
                "step": 2,
                "title": "Loud-and-Clear (LoC) 3-Arm Structural Cropping",
                "badge": "LOC ARMS",
                "narrative": "Three visual perspectives are generated: Arm A provides full-page macro topography; Arm B delivers 300 DPI high-zoom crops of complex schematics; Arm C provides hybrid focal crops fused with 160-token OCR chips.",
                "activeNodes": ["node-arm-a", "node-arm-b", "node-arm-c"],
                "activeEdges": ["edge-arm-vit"],
                "sources": [
                    {
                        "id": "SRC 10",
                        "file": "src/visual_retriever.py",
                        "startLine": 35,
                        "endLine": 95,
                        "label": "LoC 3-Arm visual reader cropping and configuration"
                    }
                ]
            },
            {
                "step": 3,
                "title": "ColPali ViT Multi-Vector Patch Alignment",
                "badge": "COLPALI",
                "narrative": "ColPali converts page images into 1024-patch multi-vector matrices without OCR. Text query tokens align directly against image patches using the late-interaction MaxSim dot-product scoring formula.",
                "activeNodes": ["node-vit-patches", "node-query-tokens", "node-maxsim"],
                "activeEdges": ["edge-vit-maxsim", "edge-query-maxsim", "edge-maxsim-fusion"],
                "sources": [
                    {
                        "id": "SRC 11",
                        "file": "src/visual_retriever.py",
                        "startLine": 105,
                        "endLine": 160,
                        "label": "ColPali multi-vector token-to-patch MaxSim scoring"
                    }
                ]
            },
            {
                "step": 4,
                "title": "Cross-Modal Hybrid Ranker & Safe Delivery",
                "badge": "DELIVERY",
                "narrative": "BM25 lexical search, BGE-large dense vectors, and ColPali visual scores are fused via reciprocal rank fusion into a single context packet. Images are streamed securely via GET /api/figures/crops/* with path traversal protection.",
                "activeNodes": ["node-ranker", "node-context-pack", "node-deliverable"],
                "activeEdges": ["edge-ranker-pack", "edge-pack-deliver"],
                "sources": [
                    {
                        "id": "SRC 12",
                        "file": "src/web.py",
                        "startLine": 1779,
                        "endLine": 1805,
                        "label": "Secure figure crop streaming with is_relative_to validation"
                    }
                ]
            }
        ]
    },
    {
        "id": "panel-4-firewall",
        "index": 4,
        "title": "Epistemic Authority Firewall & Reified Claim Ledger",
        "shortTitle": "Epistemic Firewall",
        "svgFile": "diagram4_firewall.svg",
        "domain": "firewall",
        "conclusion": {
            "headline": "Hierarchical Authority Triage with Reified Provenance Seals",
            "summary": "The Epistemic Authority Firewall classifies evidence into three sovereign tiers, enforces anti-conflation gates (CQ-74/75) to prevent marketing hype from overriding statutory awards, and lifts graph assertions into reified, cryptographically sealed claim statements.",
            "metrics": [
                {"label": "Authority Tiers", "value": "3 (Statutory, Program, Vendor)"},
                {"label": "Anti-Conflation Gates", "value": "CQ-74 & CQ-75 Active"},
                {"label": "Citation Audit Rate", "value": "100% of Assertions"},
                {"label": "Epistemic States", "value": "CONFIRMED, ASSERTED, CONTRADICTED"}
            ]
        },
        "steps": [
            {
                "step": 1,
                "title": "Three-Tier Normative Authority Hierarchy",
                "badge": "TIER HIERARCHY",
                "narrative": "Evidence is stratified into Tier 1 (statutory FAR/DFARS clauses & executed awards), Tier 2 (official program office evaluations & AFSIM logs), and Tier 3 (vendor self-asserted marketing & whitepapers).",
                "activeNodes": ["node-tier-1", "node-tier-2", "node-tier-3"],
                "activeEdges": ["edge-tier1-firewall", "edge-tier2-firewall", "edge-tier3-firewall"],
                "sources": [
                    {
                        "id": "SRC 13",
                        "file": "src/epistemic_verifier.py",
                        "startLine": 35,
                        "endLine": 85,
                        "label": "Normative authority tier classification & hierarchy rules"
                    }
                ]
            },
            {
                "step": 2,
                "title": "CQ-74 Authority Conflation Barrier",
                "badge": "CQ-74",
                "narrative": "Prevents vendor marketing claims from overriding or contradicting statutory contract terms. If a vendor claims production maturity but awards indicate Phase I SBIR, the sovereign award record prevails.",
                "activeNodes": ["node-cq74-barrier"],
                "activeEdges": ["edge-cq74-ledger"],
                "sources": [
                    {
                        "id": "SRC 14",
                        "file": "src/epistemic_verifier.py",
                        "startLine": 95,
                        "endLine": 155,
                        "label": "CQ-74 authority conflation barrier and contradiction handler"
                    }
                ]
            },
            {
                "step": 3,
                "title": "CQ-75 Cross-Domain Ledger Segregation",
                "badge": "CQ-75",
                "narrative": "Blocks conflating financial billing/indirect rate accounting with technical readiness or capability maturity assertions, guaranteeing clean audit boundaries for federal evaluators.",
                "activeNodes": ["node-cq75-barrier"],
                "activeEdges": ["edge-cq75-ledger"],
                "sources": [
                    {
                        "id": "SRC 15",
                        "file": "src/security_boundaries.py",
                        "startLine": 25,
                        "endLine": 65,
                        "label": "Cross-domain evidence segregation and disjoint predicate matrix"
                    }
                ]
            },
            {
                "step": 4,
                "title": "RDF Statement Reification & Audit Deliverables",
                "badge": "REIFIED LEDGER",
                "narrative": "Every graph triple is lifted into a meia:ReifiedStatement with confidence score, epistemic status, and exact evidence anchor, generating a 100% cited audit receipt.",
                "activeNodes": ["node-reified-stmt", "node-audit-trail", "node-citation-stamp", "node-audit-export"],
                "activeEdges": ["edge-ledger-receipts", "edge-ledger-audit"],
                "sources": [
                    {
                        "id": "SRC 16",
                        "file": "ontology/meia_ontology.ttl",
                        "startLine": 80,
                        "endLine": 135,
                        "label": "ReifiedStatement OWL 2 DL class & epistemic property axioms"
                    }
                ]
            }
        ]
    },
    {
        "id": "panel-5-dualengine",
        "index": 5,
        "title": "Dual-Engine Synthesis & Active Skill Orchestration",
        "shortTitle": "Dual-Engine & Skills",
        "svgFile": "diagram5_dual_engine.svg",
        "domain": "dualengine",
        "conclusion": {
            "headline": "Sub-35ms Deterministic Proofs with Live LLM Active Skill Ingress",
            "summary": "Evaluators can toggle between a fast deterministic graph proof engine (< 35ms, 100% reproducible, zero model latency) and a live LLM orchestrator (DeepSeek/Gemini) injected with specialized MEIA domain skills, unified under an epistemic citation gate.",
            "metrics": [
                {"label": "Deterministic Latency", "value": "< 35 ms"},
                {"label": "LLM Providers", "value": "DeepSeek API / Gemini"},
                {"label": "Active Skills", "value": "weld, retrieval, compliance"},
                {"label": "Evaluation Catalog", "value": "78/78 CQs (100% Passing)"}
            ]
        },
        "steps": [
            {
                "step": 1,
                "title": "Immutable Context Packet Assembly",
                "badge": "PACKET",
                "narrative": "Both engines receive an identical, hash-sealed ContextPacket containing top-k subgraphs, semantic text chunks, LoC visual crops, and active SKOS concept expansions.",
                "activeNodes": ["node-context-input", "node-engine-switch"],
                "activeEdges": ["edge-packet-eng-a", "edge-packet-eng-b"],
                "sources": [
                    {
                        "id": "SRC 17",
                        "file": "src/context_packet.py",
                        "startLine": 40,
                        "endLine": 110,
                        "label": "ContextPacket data model and serialization"
                    }
                ]
            },
            {
                "step": 2,
                "title": "Engine A: Pure Graph Proof Engine",
                "badge": "ENGINE A",
                "narrative": "Executes purely local SQLite FTS5 search, recursive SQL CTEs, and NetworkX GraphML path tracing. Delivers verifiable mathematical proofs in under 35 milliseconds with zero API costs.",
                "activeNodes": ["node-graph-engine-details"],
                "activeEdges": ["edge-eng-a-auditor"],
                "sources": [
                    {
                        "id": "SRC 18",
                        "file": "src/grounded_answer.py",
                        "startLine": 120,
                        "endLine": 190,
                        "label": "Deterministic graph proof resolution and trajectory generation"
                    }
                ]
            },
            {
                "step": 3,
                "title": "Engine B: Live LLM with Domain Skill Injection",
                "badge": "ENGINE B",
                "narrative": "Orchestrates DeepSeek API or Gemini with dynamic skill injection (meia-exact-weld for NAVSEA specs, meia-retrieval for hybrid search, meia-compliance for FAR/ITAR rules) into the streaming prompt.",
                "activeNodes": ["node-llm-orchestrator", "node-active-skills"],
                "activeEdges": ["edge-eng-b-auditor"],
                "sources": [
                    {
                        "id": "SRC 19",
                        "file": "src/skill_loader.py",
                        "startLine": 25,
                        "endLine": 95,
                        "label": "MEIA skill loader and runtime tool registry"
                    }
                ]
            },
            {
                "step": 4,
                "title": "Epistemic Auditor & Grounded Answer Delivery",
                "badge": "AUDITOR",
                "narrative": "Every sentence generated by the LLM is audited against reified claim statements in the ledger. Unverified claims are suppressed; passing responses receive a cryptographic citation seal.",
                "activeNodes": ["node-citation-gate", "node-trail-builder", "node-grounded-model"],
                "activeEdges": ["edge-auditor-output"],
                "sources": [
                    {
                        "id": "SRC 20",
                        "file": "src/grounded_answer.py",
                        "startLine": 240,
                        "endLine": 310,
                        "label": "Epistemic citation verification and GroundedAnswer serialization"
                    }
                ]
            }
        ]
    }
]


def get_all_panels() -> List[Dict[str, Any]]:
    """Returns the full catalog of Archify explainer panels."""
    return EXPLAINER_PANELS


def get_panel_by_id(panel_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a specific explainer panel by ID or index."""
    for p in EXPLAINER_PANELS:
        if p["id"] == panel_id or str(p["index"]) == panel_id:
            return p
    return None


def read_source_excerpt(rel_path: str, start_line: int, end_line: int) -> Dict[str, Any]:
    """
    Safely reads an excerpt from a repository source file.
    Validates that the path is within WORKSPACE_ROOT and bounds line numbers.
    """
    clean_path = rel_path.replace("\\", "/").lstrip("/")
    target = (WORKSPACE_ROOT / clean_path).resolve()
    
    if not target.is_relative_to(WORKSPACE_ROOT):
        return {
            "error": "Forbidden: Path traversal",
            "file": rel_path,
            "lines": []
        }
        
    if not target.exists() or not target.is_file():
        return {
            "error": "File not found",
            "file": rel_path,
            "lines": []
        }
        
    try:
        with open(target, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
            
        total_lines = len(all_lines)
        s = max(1, min(start_line, total_lines))
        e = max(s, min(end_line, total_lines))
        
        selected_lines = [
            {"lineNumber": idx, "content": all_lines[idx - 1].rstrip("\r\n")}
            for idx in range(s, e + 1)
        ]
        
        return {
            "file": clean_path,
            "startLine": s,
            "endLine": e,
            "totalLines": total_lines,
            "lines": selected_lines,
            "rawText": "".join(all_lines[s - 1:e])
        }
    except Exception as ex:
        return {
            "error": f"Read error: {str(ex)}",
            "file": rel_path,
            "lines": []
        }


def get_diagram_svg_content(svg_filename: str) -> Optional[str]:
    """Reads the raw SVG content for a given diagram file."""
    svg_path = (DIAGRAMS_DIR / svg_filename).resolve()
    if not svg_path.exists() or not svg_path.is_file():
        return None
    try:
        with open(svg_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None
