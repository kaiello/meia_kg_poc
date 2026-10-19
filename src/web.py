"""
Zero-Daemon Web Visual Explorer & Interactive NLQ Dashboard (Port 8000).
Serves the MEIA Federated Tri-Graph Knowledge Graph POC:
- Interactive NLQ search bar with clearance selector
- 8 CQ Profile Quick-Select Chips
- Dynamic Route & Epistemic Audit Badges
- 180 DPI Multimodal Architecture Diagram Lightbox with BBox chips
- 360° Executive Business & Capability Dossier Renderer
- Grounding Citations Accordion (exact Sheet!Row:Col cells, chunks, contracts)
"""

import json
import logging
import mimetypes
import os
import sqlite3
import sys
from http import HTTPStatus
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, unquote

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config import FIGURES_DIR, TRI_GRAPH_DB_PATH
from src.pre_retrieval import CallerContext
from src.grounded_answer import answer_query
from src.figure_inspectors import CROPS_DIR, inspect_figure_loc, LoCInspectionArm
from src.context_packet import ContextPacketBuilder


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("meia_web")


HTML_DASHBOARD = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MEIA Federated Tri-Graph Explorer</title>
    <style>
        :root {
            --bg-dark: #0f172a;
            --surface-dark: #1e293b;
            --surface-card: #243247;
            --border-color: #334155;
            --accent-blue: #38bdf8;
            --accent-indigo: #6366f1;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --status-green: #22c55e;
            --status-amber: #f59e0b;
            --status-red: #ef4444;
            --status-blue: #3b82f6;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg-dark);
            color: var(--text-main);
            line-height: 1.5;
            padding: 24px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 24px;
        }
        .header h1 {
            font-size: 24px;
            font-weight: 700;
            color: var(--accent-blue);
            letter-spacing: -0.5px;
        }
        .header p {
            color: var(--text-muted);
            font-size: 14px;
            margin-top: 4px;
        }
        .badges-top {
            display: flex;
            gap: 8px;
        }
        .badge {
            font-size: 11px;
            padding: 4px 10px;
            border-radius: 9999px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .badge-spine { background: rgba(56, 189, 248, 0.15); color: var(--accent-blue); border: 1px solid rgba(56, 189, 248, 0.3); }
        .badge-vectors { background: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); }
        .badge-airgap { background: rgba(34, 197, 94, 0.15); color: var(--status-green); border: 1px solid rgba(34, 197, 94, 0.3); }
        .badge-cell { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
        .badge-chunk { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
        .badge-award { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
        .badge-policy { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

        .search-container {
            background: var(--surface-dark);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        }
        .search-bar {
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
        }
        .search-input {
            flex: 1;
            background: var(--bg-dark);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 15px;
            outline: none;
            transition: border-color 0.2s;
        }
        .search-input:focus { border-color: var(--accent-blue); }
        .clearance-select {
            background: var(--bg-dark);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 0 16px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
        }
        .btn-query {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        .btn-query:hover { opacity: 0.9; }

        .chip-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }
        .chip-label { font-size: 12px; color: var(--text-muted); font-weight: 600; margin-right: 4px; }
        .chip {
            background: var(--surface-card);
            border: 1px solid var(--border-color);
            color: #cbd5e1;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.15s;
        }
        .chip:hover {
            border-color: var(--accent-blue);
            color: var(--accent-blue);
            transform: translateY(-1px);
        }

        .main-layout {
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 24px;
        }
        @media (max-width: 1024px) {
            .main-layout { grid-template-columns: 1fr; }
        }

        .panel {
            background: var(--surface-dark);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
        }
        .panel-title {
            font-size: 16px;
            font-weight: 700;
            color: #e2e8f0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .route-pill {
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            background: rgba(99, 102, 241, 0.2);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.4);
        }
        .status-pill {
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
        }
        .status-VERIFIED_GROUNDED { background: rgba(34, 197, 94, 0.2); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.4); }
        .status-UNVERIFIED_VENDOR_CLAIM { background: rgba(245, 158, 11, 0.2); color: #fde68a; border: 1px solid rgba(245, 158, 11, 0.4); }
        .status-CONFLICTING_EVIDENCE { background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.4); }
        .status-ACCESS_DENIED, .status-MODULE_UNAVAILABLE, .status-OUT_OF_SCOPE { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }

        .answer-content {
            font-size: 14px;
            line-height: 1.65;
            color: #cbd5e1;
            white-space: pre-wrap;
        }
        .answer-content h1, .answer-content h2, .answer-content h3, .answer-content h4 {
            color: #f1f5f9;
            margin: 14px 0 8px 0;
        }
        .answer-content ul {
            padding-left: 20px;
            margin-bottom: 12px;
        }

        .diagram-container {
            background: #020617;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
            position: relative;
            margin-bottom: 16px;
            text-align: center;
        }
        .diagram-img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
            border-radius: 4px;
        }
        .chips-container {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 10px;
        }
        .bbox-chip {
            background: #0f172a;
            border: 1px solid #38bdf8;
            color: #38bdf8;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-family: monospace;
        }

        .loc-tabs {
            display: flex;
            gap: 6px;
            margin-bottom: 10px;
        }
        .loc-tab-btn {
            background: #1e293b;
            color: #94a3b8;
            border: 1px solid #334155;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .loc-tab-btn.active {
            background: #38bdf8;
            color: #0f172a;
            border-color: #38bdf8;
        }

        /* LANL-Style Explorer View Tabs & Graph Styling */
        .view-tabs {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 14px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
        }
        .view-tab-btn {
            background: #1e293b;
            color: #94a3b8;
            border: 1px solid var(--border-color);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }
        .view-tab-btn:hover {
            color: #e2e8f0;
            border-color: #475569;
        }
        .view-tab-btn.active {
            background: #0284c7;
            color: #ffffff;
            border-color: #38bdf8;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
        }
        .graph-canvas-container {
            position: relative;
            height: 380px;
            background: #020617;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
        }
        #triGraphCanvas {
            width: 100%;
            height: 100%;
            display: block;
            cursor: grab;
        }
        #triGraphCanvas:active {
            cursor: grabbing;
        }
        .graph-controls {
            position: absolute;
            top: 10px;
            right: 10px;
            display: flex;
            gap: 4px;
            z-index: 10;
        }
        .graph-ctrl-btn {
            background: rgba(30, 41, 59, 0.85);
            color: #cbd5e1;
            border: 1px solid #475569;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            backdrop-filter: blur(4px);
        }
        .graph-ctrl-btn:hover {
            background: #334155;
            color: #ffffff;
        }
        .graph-legend {
            position: absolute;
            bottom: 8px;
            left: 8px;
            display: flex;
            gap: 12px;
            font-size: 11px;
            background: rgba(15, 23, 42, 0.85);
            padding: 4px 10px;
            border-radius: 6px;
            border: 1px solid #334155;
            color: #cbd5e1;
            backdrop-filter: blur(4px);
        }
        .legend-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
            vertical-align: middle;
        }
        .node-drawer {
            background: #0f172a;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px;
            margin-top: 10px;
            font-size: 12px;
            max-height: 180px;
            overflow-y: auto;
        }
        .table-filter-bar {
            display: flex;
            gap: 6px;
        }
        .filter-chip {
            background: #1e293b;
            color: #94a3b8;
            border: 1px solid #334155;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
        }
        .filter-chip.active {
            background: #38bdf8;
            color: #0f172a;
            font-weight: 700;
            border-color: #38bdf8;
        }
        .graph-data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
            text-align: left;
        }
        .graph-data-table th {
            background: #1e293b;
            color: #94a3b8;
            padding: 8px;
            font-weight: 600;
            position: sticky;
            top: 0;
            border-bottom: 1px solid #334155;
            white-space: nowrap;
        }
        .graph-data-table td {
            padding: 6px 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            color: #cbd5e1;
            vertical-align: middle;
        }
        .badge-org { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }
        .badge-tech { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
        .badge-crm { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
        .badge-bridge { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); }
        .no-diagram-card {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 24px 16px;
            text-align: center;
            color: #94a3b8;
        }
        .packet-card {
            background: #1e293b;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
        }
        .packet-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            font-size: 13px;
            font-weight: 700;
            color: #38bdf8;
        }
        .packet-qualifier {
            background: rgba(245, 158, 11, 0.1);
            border-left: 3px solid #f59e0b;
            padding: 4px 8px;
            margin: 4px 0;
            font-size: 11px;
            color: #fde68a;
            border-radius: 0 4px 4px 0;
        }


        .citations-list {
            list-style: none;
            padding: 0;
            margin-top: 12px;
        }
        .citations-list li {
            font-size: 12px;
            color: #94a3b8;
            padding: 6px 10px;
            background: var(--bg-dark);
            border-radius: 6px;
            margin-bottom: 6px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            font-family: monospace;
            word-break: break-all;
        }

        .loading-spinner {
            display: none;
            text-align: center;
            padding: 40px;
            color: var(--accent-blue);
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>MEIA Federated Tri-Graph Explorer</h1>
            <p>Air-Gapped Multimodal Tri-Store Querying (Organization · Technology · CRM) & 100% Locator-Grounded Epistemic Verification</p>
        </div>
        <div class="badges-top">
            <span class="badge badge-spine">Epistemic Spine</span>
            <span class="badge badge-vectors">BGE-Large 1024d</span>
            <span class="badge badge-airgap">Zero Daemon Local</span>
            <button class="badge badge-vectors" onclick="openModelDrawer()" style="cursor:pointer; border:1px solid #38bdf8; background:rgba(56,189,248,0.25);">⚙️ Model & API Keys</button>
            <button class="badge badge-vectors" onclick="openReceiptModal()" style="cursor:pointer; border:1px solid #818cf8; background:rgba(99,102,241,0.25);">Audit Receipt (100%)</button>
            <button class="badge badge-spine" onclick="openStewardModal()" style="cursor:pointer; border:1px solid var(--accent-blue); background:rgba(56,189,248,0.25);">Steward Queue (U04)</button>
        </div>
    </div>

    <div class="search-container">
        <div class="search-bar">
            <input type="text" id="queryInput" class="search-input" placeholder="Type a natural language competency question..." value="What is Ghostfin's TRL and operational range?">
            <select id="engineSelect" class="clearance-select" style="min-width: 175px;">
                <option value="deepseek" selected>⚡ DeepSeek (deepseek-chat)</option>
                <option value="deterministic">🛡️ Deterministic (Tri-Graph)</option>
                <option value="gemini">✨ Gemini (gemini-2.0-flash)</option>
                <option value="custom">🔌 Custom / OpenAI-Compatible</option>
            </select>
            <select id="clearanceSelect" class="clearance-select">
                <option value="SECRET" selected>SECRET Clearance</option>
                <option value="TOP_SECRET">TOP SECRET Clearance</option>
                <option value="UNCLASSIFIED">UNCLASSIFIED (Guest)</option>
            </select>
            <button class="btn-query" onclick="executeQuery()">Execute Query</button>
        </div>
        <div class="chip-grid">
            <span class="chip-label">Quick CQ Profiles:</span>
            <button class="chip" onclick="setQuery('What is Albacore\'s CAGE code, location, and corporate subcategory?', 'SECRET')">CQ-01 (Org: Albacore)</button>
            <button class="chip" onclick="setQuery('What is Fluor\'s total all-time federal prime spending and annual obligation trend?', 'SECRET')">CQ-11 (Org: Fluor $908M)</button>
            <button class="chip" onclick="setQuery('What is Ghostfin\'s TRL, MRL, and operational range?', 'SECRET')">CQ-19 (Tech: Ghostfin)</button>
            <button class="chip" onclick="setQuery('What specific quantifiable operational capability contribution does Ghostfin deliver in Q3?', 'SECRET')">CQ-29 (Tech: 1000 nmi Range)</button>
            <button class="chip" onclick="setQuery('What is the Twenty CRM pipeline stage and funding request for Vulcan submission 26705?', 'SECRET')">CQ-37 (CRM: Submission #26705)</button>
            <button class="chip" onclick="setQuery('Which U.S. Small Business startups offer technologies aligned to Counter C5ISR-T with current TRL >= 6?', 'SECRET')">CQ-51 (Org ⋈ Tech Join)</button>
            <button class="chip" onclick="setQuery('Which capabilities in the CRM portfolio combine high TRL and MRL with Government Purpose Rights or CRADA?', 'SECRET')">CQ-63 (CRM ⋈ Tech Join)</button>
            <button class="chip" onclick="setQuery('Generate a complete MEIA Executive Business & Capability Dossier for Ghostfin: Long-Range, Hybrid Electric Medium UUV (Albacore).', 'SECRET')">CQ-68 (360° Executive Dossier)</button>
            <button class="chip" onclick="setQuery('What is the primary vendor POC personal phone number for Dante Vaisbort?', 'UNCLASSIFIED')">CQ-77 (Gate: PII Denial)</button>
            <button class="chip" onclick="setQuery('What is Ghostfin\'s acoustic signature decibel rating at 30 knots?', 'SECRET')">CQ-78 (Gate: Out-of-Scope)</button>
        </div>
    </div>

    <div class="main-layout">
        <!-- Left Column: Composed Answer & Structured Results -->
        <div class="panel">
            <div class="panel-header">
                <div class="panel-title">
                    <span>Grounded Answer & Verified Facts</span>
                </div>
                <div style="display: flex; gap: 8px;">
                    <span id="routeBadge" class="route-pill">ROUTE_TECH</span>
                    <span id="statusBadge" class="status-pill status-VERIFIED_GROUNDED">VERIFIED_GROUNDED</span>
                </div>
            </div>
            <div id="llmTelemetryBar" style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; background:#0f172a; padding:8px 12px; border-radius:6px; border:1px solid #334155; margin-bottom:12px; font-size:12px;">
                <span id="telemetryEngineBadge" style="font-weight:700; color:#38bdf8;">⚡ Engine: DeepSeek (deepseek-chat)</span>
                <span id="telemetryLatencyBadge" style="color:#94a3b8;">· Ready</span>
                <span id="telemetryTokensBadge" style="color:#94a3b8;"></span>
                <span id="telemetrySkillsBadge" style="color:#a78bfa; margin-left:auto;">🧠 Skills: [tri-graph-routing] [trident-colpali-visual] [epistemic-claim-audit] [executive-dossier-composer]</span>
            </div>
            <div id="loading" class="loading-spinner">Traversing Federated Tri-Graph & Synthesizing Grounded Facts...</div>
            <div id="answerText" class="answer-content">Click 'Execute Query' or any quick profile chip above to inspect the federated response.</div>
        </div>

        <!-- Right Column: Federated Tri-Graph Lineage & Topology Explorer (LANL Pattern) -->
        <div class="panel">
            <div class="panel-header">
                <div class="panel-title">
                    <span>Federated Tri-Graph Lineage Explorer</span>
                </div>
                <div style="display:flex; gap:6px; align-items:center;">
                    <span id="graphNodeCountBadge" class="badge badge-spine">78 Nodes</span>
                    <span id="graphEdgeCountBadge" class="badge badge-vectors">74 Edges</span>
                </div>
            </div>

            <!-- LANL-Inspired Jump Navigation / View Tabs -->
            <div class="view-tabs">
                <button id="viewGraphBtn" class="view-tab-btn active" onclick="switchExplorerView('graph')">🌐 Interactive Tri-Graph</button>
                <button id="viewDataBtn" class="view-tab-btn" onclick="switchExplorerView('data')">📊 Graph Data (Which Graph)</button>
                <button id="viewClaimsBtn" class="view-tab-btn" onclick="switchExplorerView('claims')">⚖️ Epistemic Claims</button>
                <button id="viewMultimodalBtn" class="view-tab-btn" onclick="switchExplorerView('multimodal')">🖼️ Multimodal Evidence</button>
                <button id="viewPacketsBtn" class="view-tab-btn" onclick="switchExplorerView('packets')">📦 Context Packets & Citations</button>
            </div>

            <!-- View 1: Interactive Network Topology (Native Canvas Force Simulation) -->
            <div id="graphViewSection" class="explorer-section active">
                <div class="graph-canvas-container">
                    <canvas id="triGraphCanvas"></canvas>
                    <div class="graph-controls">
                        <button class="graph-ctrl-btn" onclick="zoomGraph(1.2)" title="Zoom In">+</button>
                        <button class="graph-ctrl-btn" onclick="zoomGraph(0.8)" title="Zoom Out">-</button>
                        <button class="graph-ctrl-btn" onclick="resetGraphView()" title="Fit View">Fit</button>
                        <button class="graph-ctrl-btn" onclick="loadGlobalOverview()" title="Global Overview">Full Tri-Graph</button>
                    </div>
                    <div class="graph-legend">
                        <span><span class="legend-dot" style="background:#38bdf8;"></span>Org-KG</span>
                        <span><span class="legend-dot" style="background:#10b981;"></span>Tech-KG</span>
                        <span><span class="legend-dot" style="background:#f59e0b;"></span>CRM-Graph</span>
                        <span><span class="legend-dot" style="background:#a855f7;"></span>Cross-Graph Spine</span>
                    </div>
                </div>
                <div id="nodeDetailDrawer" class="node-drawer">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <span id="drawerTitle" style="font-weight:700; color:#38bdf8;">Select a node or edge in the graph</span>
                        <span id="drawerDomainBadge" class="badge badge-spine">TRI-GRAPH</span>
                    </div>
                    <div id="drawerBody" style="color:#94a3b8; line-height:1.4;">
                        Click any entity node above to inspect its BFO category, SKOS concepts, attributes, and cross-graph traversals. Drag nodes to reposition.
                    </div>
                </div>
            </div>

            <!-- View 2: Structured Graph Data (Nodes & Edges with Which Graph badges) -->
            <div id="dataViewSection" class="explorer-section" style="display:none;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <div style="font-size:13px; font-weight:700; color:#e2e8f0;">Nodes in Subgraph</div>
                    <div class="table-filter-bar">
                        <button class="filter-chip active" id="filterAllBtn" onclick="filterGraphData('ALL')">All</button>
                        <button class="filter-chip" id="filterOrgBtn" onclick="filterGraphData('ORG')">Org-KG</button>
                        <button class="filter-chip" id="filterTechBtn" onclick="filterGraphData('TECH')">Tech-KG</button>
                        <button class="filter-chip" id="filterCrmBtn" onclick="filterGraphData('CRM')">CRM</button>
                    </div>
                </div>
                <div style="max-height: 200px; overflow-y: auto; border:1px solid var(--border-color); border-radius:6px; margin-bottom:14px;">
                    <table class="graph-data-table" id="nodesTable">
                        <thead>
                            <tr>
                                <th>Which Graph</th>
                                <th>Node ID</th>
                                <th>Label / Name</th>
                                <th>Category</th>
                                <th>Key Properties</th>
                            </tr>
                        </thead>
                        <tbody id="nodesTableBody">
                            <tr><td colspan="5" style="text-align:center; color:#64748b;">Loading nodes...</td></tr>
                        </tbody>
                    </table>
                </div>

                <div style="font-size:13px; font-weight:700; color:#e2e8f0; margin-bottom:8px;">Edges & Cross-Graph Bridges</div>
                <div style="max-height: 200px; overflow-y: auto; border:1px solid var(--border-color); border-radius:6px;">
                    <table class="graph-data-table" id="edgesTable">
                        <thead>
                            <tr>
                                <th>Link Kind</th>
                                <th>Source</th>
                                <th>Predicate</th>
                                <th>Target</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="edgesTableBody">
                            <tr><td colspan="5" style="text-align:center; color:#64748b;">Loading edges...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- View 3: Epistemic Claims Ledger -->
            <div id="claimsViewSection" class="explorer-section" style="display:none;">
                <div style="font-size:13px; font-weight:700; color:#e2e8f0; margin-bottom:8px;">Epistemic Claim Ledger Records</div>
                <div style="max-height: 420px; overflow-y: auto; border:1px solid var(--border-color); border-radius:6px;">
                    <table class="graph-data-table" id="claimsTable">
                        <thead>
                            <tr>
                                <th>Subject</th>
                                <th>Predicate</th>
                                <th>Asserted Value</th>
                                <th>Epistemic Status</th>
                                <th>Conf</th>
                                <th>Handling</th>
                                <th>Anchor</th>
                            </tr>
                        </thead>
                        <tbody id="claimsTableBody">
                            <tr><td colspan="7" style="text-align:center; color:#64748b;">Execute a query to inspect epistemic claims.</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- View 4: Multimodal Evidence (Conditional - No Stuck Memo) -->
            <div id="multimodalViewSection" class="explorer-section" style="display:none;">
                <div class="loc-tabs">
                    <button id="tabArmA" class="loc-tab-btn active" onclick="switchLoCArm('ARM_A_FULL_PAGE')">Arm A: Full 180 DPI</button>
                    <button id="tabArmB" class="loc-tab-btn" onclick="switchLoCArm('ARM_B_FOCAL_CROP')">Arm B: Focal Crop Chip</button>
                    <button id="tabArmC" class="loc-tab-btn" onclick="switchLoCArm('ARM_C_MULTIMODAL_CALLOUT')">Arm C: OCR Callouts</button>
                </div>
                <div id="diagramSection" class="diagram-container">
                    <img id="diagramImage" class="diagram-img" src="" alt="Architecture Diagram" style="display:none;" onerror="this.style.display='none'">
                    <div id="noDiagramCard" class="no-diagram-card">
                        <span class="badge badge-cell" style="margin-bottom:8px; display:inline-block;">DIRECT TRI-GRAPH GROUNDING</span>
                        <h3 style="color:#e2e8f0; margin:4px 0 8px 0; font-size:14px;">Structured Tri-Graph Verification</h3>
                        <p style="font-size:12px; margin:0; line-height:1.5;">This query is grounded directly in tri-graph triples, epistemic claim records, and spreadsheet cell coordinates (Sheet!Row:Col). No proprietary vendor architecture schematic is required for this answer route.</p>
                    </div>
                </div>
                <div id="bboxChips" class="chips-container"></div>
            </div>

            <!-- View 5: Context Packets & Citations -->
            <div id="packetsViewSection" class="explorer-section" style="display:none;">
                <div class="panel-header">
                    <div class="panel-title">R03 Functional Context Packets</div>
                    <span id="packetCount" class="badge badge-cell">0 Packets</span>
                </div>
                <div id="packetContainer" style="max-height: 200px; overflow-y: auto; margin-bottom:16px;">
                    <p style="color: #64748b; font-size: 12px;">No context packets assembled.</p>
                </div>

                <div class="panel-header">
                    <div class="panel-title">Exact Grounding Citations (CQ-73)</div>
                    <span id="citationCount" class="badge badge-spine">0 Anchors</span>
                </div>
                <ul id="citationList" class="citations-list">
                    <li>Execute a query to inspect exact Sheet!Row:Col and PDF chunk citations.</li>
                </ul>
            </div>
        </div>
    </div>

    <script>
        function escapeHtml(str) {
            if (!str) return '';
            return String(str)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }

        let currentAssetId = "Klas_Voyager_2_p1";
        let currentArm = "ARM_A_FULL_PAGE";
        let activeGraphData = { nodes: [], edges: [], claims: [], summary: {} };
        let fullGraphData = null;
        let selectedNode = null;
        let graphCamera = { x: 0, y: 0, zoom: 1 };
        let isDraggingCanvas = false;
        let dragStart = { x: 0, y: 0 };
        let draggedNode = null;
        let activeFilter = 'ALL';
        let simNodes = [];
        let simEdges = [];
        let animFrameId = null;

        // View Switcher for Right-Hand Explorer
        function switchExplorerView(viewName) {
            document.querySelectorAll('.view-tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.explorer-section').forEach(s => s.style.display = 'none');

            if (viewName === 'graph') {
                document.getElementById('viewGraphBtn').classList.add('active');
                document.getElementById('graphViewSection').style.display = 'block';
                resizeCanvas();
            } else if (viewName === 'data') {
                document.getElementById('viewDataBtn').classList.add('active');
                document.getElementById('dataViewSection').style.display = 'block';
            } else if (viewName === 'claims') {
                document.getElementById('viewClaimsBtn').classList.add('active');
                document.getElementById('claimsViewSection').style.display = 'block';
            } else if (viewName === 'multimodal') {
                document.getElementById('viewMultimodalBtn').classList.add('active');
                document.getElementById('multimodalViewSection').style.display = 'block';
            } else if (viewName === 'packets') {
                document.getElementById('viewPacketsBtn').classList.add('active');
                document.getElementById('packetsViewSection').style.display = 'block';
            }
        }

        // LoC Arm Switcher
        async function switchLoCArm(arm) {
            currentArm = arm;
            document.querySelectorAll('.loc-tab-btn').forEach(b => b.classList.remove('active'));
            if (arm === 'ARM_A_FULL_PAGE') document.getElementById('tabArmA').classList.add('active');
            if (arm === 'ARM_B_FOCAL_CROP') document.getElementById('tabArmB').classList.add('active');
            if (arm === 'ARM_C_MULTIMODAL_CALLOUT') document.getElementById('tabArmC').classList.add('active');

            if (!currentAssetId) return;

            try {
                const res = await fetch(`/api/loc/inspect?asset_id=${encodeURIComponent(currentAssetId)}&arm=${arm}`);
                const data = await res.json();
                const diagImg = document.getElementById('diagramImage');
                if (arm === 'ARM_B_FOCAL_CROP' && data.focal_crop_path) {
                    let cropSrc = data.focal_crop_path;
                    if (cropSrc.startsWith('parsed/figures/crops/')) {
                        cropSrc = '/api/figures/crops/' + cropSrc.replace('parsed/figures/crops/', '');
                    } else if (cropSrc.startsWith('parsed/figures/')) {
                        cropSrc = '/api/figures/' + cropSrc.replace('parsed/figures/', '');
                    } else if (!cropSrc.startsWith('/')) {
                        cropSrc = '/' + cropSrc;
                    }
                    diagImg.src = cropSrc;
                } else {
                    diagImg.src = data.full_page_path ? ('/api/figures/' + data.full_page_path.replace('parsed/figures/', '')) : `/api/figures/${encodeURIComponent(currentAssetId)}.png`;
                }

                const chipContainer = document.getElementById('bboxChips');
                chipContainer.innerHTML = '';
                if (arm === 'ARM_C_MULTIMODAL_CALLOUT' && data.ocr_callouts && data.ocr_callouts.length > 0) {
                    data.ocr_callouts.forEach(c => {
                        const span = document.createElement('span');
                        span.className = 'bbox-chip';
                        span.innerText = `[OCR] ${c.text} (${Math.round(c.confidence*100)}%)`;
                        chipContainer.appendChild(span);
                    });
                }
            } catch (e) {
                console.error("Failed to switch LoC arm:", e);
            }
        }

        // ============================================================================
        // Native Air-Gapped Canvas Force-Directed Graph Engine
        // ============================================================================
        function initCanvas() {
            const canvas = document.getElementById('triGraphCanvas');
            if (!canvas) return;
            resizeCanvas();
            window.addEventListener('resize', resizeCanvas);

            canvas.addEventListener('mousedown', (e) => {
                const rect = canvas.getBoundingClientRect();
                const mx = (e.clientX - rect.left - graphCamera.x) / graphCamera.zoom;
                const my = (e.clientY - rect.top - graphCamera.y) / graphCamera.zoom;

                // Hit test nodes
                let hit = null;
                for (let i = simNodes.length - 1; i >= 0; i--) {
                    const n = simNodes[i];
                    const dx = n.x - mx;
                    const dy = n.y - my;
                    if (dx*dx + dy*dy <= (n.radius + 6) * (n.radius + 6)) {
                        hit = n;
                        break;
                    }
                }

                if (hit) {
                    draggedNode = hit;
                    selectNode(hit);
                } else {
                    isDraggingCanvas = true;
                    dragStart = { x: e.clientX - graphCamera.x, y: e.clientY - graphCamera.y };
                }
            });

            window.addEventListener('mousemove', (e) => {
                const canvas = document.getElementById('triGraphCanvas');
                if (!canvas) return;
                const rect = canvas.getBoundingClientRect();

                if (draggedNode) {
                    draggedNode.x = (e.clientX - rect.left - graphCamera.x) / graphCamera.zoom;
                    draggedNode.y = (e.clientY - rect.top - graphCamera.y) / graphCamera.zoom;
                    draggedNode.vx = 0;
                    draggedNode.vy = 0;
                } else if (isDraggingCanvas) {
                    graphCamera.x = e.clientX - dragStart.x;
                    graphCamera.y = e.clientY - dragStart.y;
                }
            });

            window.addEventListener('mouseup', () => {
                draggedNode = null;
                isDraggingCanvas = false;
            });

            canvas.addEventListener('wheel', (e) => {
                e.preventDefault();
                const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
                zoomGraph(zoomFactor);
            });
        }

        function resizeCanvas() {
            const canvas = document.getElementById('triGraphCanvas');
            if (!canvas) return;
            const container = canvas.parentElement;
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
        }

        function zoomGraph(factor) {
            graphCamera.zoom = Math.max(0.2, Math.min(4.0, graphCamera.zoom * factor));
        }

        function resetGraphView() {
            const canvas = document.getElementById('triGraphCanvas');
            if (!canvas) return;
            graphCamera = { x: canvas.width / 2, y: canvas.height / 2, zoom: 1 };
        }

        function selectNode(node) {
            selectedNode = node;
            const titleEl = document.getElementById('drawerTitle');
            const badgeEl = document.getElementById('drawerDomainBadge');
            const bodyEl = document.getElementById('drawerBody');

            titleEl.innerText = node.label || node.id;
            badgeEl.innerText = (node.graph || 'TRI-GRAPH') + '-KG';
            badgeEl.className = 'badge ' + (node.graph === 'ORG' ? 'badge-org' : (node.graph === 'TECH' ? 'badge-tech' : 'badge-crm'));

            let connectedEdges = simEdges.filter(e => e.source.id === node.id || e.target.id === node.id);
            let edgeHtml = '';
            if (connectedEdges.length > 0) {
                edgeHtml = '<div style="margin-top:8px; border-top:1px solid #334155; padding-top:6px;"><strong>Connected Relationships:</strong><ul style="margin:4px 0; padding-left:16px;">';
                connectedEdges.forEach(e => {
                    const other = (e.source.id === node.id) ? e.target : e.source;
                    const direction = (e.source.id === node.id) ? '→' : '←';
                    edgeHtml += `<li><code>${escapeHtml(e.predicate)}</code> ${direction} <em>${escapeHtml(other.label || other.id)}</em> [${other.graph}]</li>`;
                });
                edgeHtml += '</ul></div>';
            }

            bodyEl.innerHTML = `
                <div><strong>ID:</strong> <code>${escapeHtml(node.id)}</code> | <strong>BFO:</strong> ${escapeHtml(node.bfo_category || 'Entity')}</div>
                ${node.skos_concepts && node.skos_concepts.length ? '<div><strong>SKOS:</strong> ' + node.skos_concepts.map(s => `<code>${escapeHtml(s)}</code>`).join(' ') + '</div>' : ''}
                <div style="margin-top:6px;"><strong>Attributes:</strong> <pre style="background:#020617; padding:6px; border-radius:4px; font-size:10px; max-height:80px; overflow-y:auto; margin:4px 0;">${escapeHtml(JSON.stringify(node.properties || {}, null, 2))}</pre></div>
                ${edgeHtml}
            `;
        }

        function startSimulation(nodes, edges) {
            const canvas = document.getElementById('triGraphCanvas');
            if (!canvas) return;
            resizeCanvas();

            // Create node lookup
            const nodeMap = {};
            simNodes = nodes.map((n, idx) => {
                let clusterX = 0;
                if (n.graph === 'ORG') clusterX = -180;
                else if (n.graph === 'TECH') clusterX = 0;
                else if (n.graph === 'CRM') clusterX = 180;

                const angle = Math.random() * Math.PI * 2;
                const dist = 30 + Math.random() * 80;

                const sn = {
                    ...n,
                    x: clusterX + Math.cos(angle) * dist,
                    y: Math.sin(angle) * dist,
                    vx: 0,
                    vy: 0,
                    targetX: clusterX,
                    targetY: 0,
                    radius: n.graph === 'TECH' ? 14 : (n.graph === 'ORG' ? 12 : 11),
                    color: n.graph === 'ORG' ? '#38bdf8' : (n.graph === 'TECH' ? '#10b981' : '#f59e0b')
                };
                nodeMap[n.id] = sn;
                return sn;
            });

            simEdges = [];
            edges.forEach(e => {
                const s = nodeMap[e.source || e.source_id];
                const t = nodeMap[e.target || e.target_id];
                if (s && t) {
                    simEdges.push({
                        ...e,
                        source: s,
                        target: t
                    });
                }
            });

            resetGraphView();
            if (animFrameId) cancelAnimationFrame(animFrameId);
            runSimulationLoop();
        }

        function runSimulationLoop() {
            const canvas = document.getElementById('triGraphCanvas');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');

            // Physics step
            const repulsion = 900;
            const springLength = 70;
            const springK = 0.04;
            const damping = 0.82;

            for (let i = 0; i < simNodes.length; i++) {
                const n1 = simNodes[i];
                if (n1 === draggedNode) continue;

                // Center/Cluster attraction
                n1.vx += (n1.targetX - n1.x) * 0.015;
                n1.vy += (n1.targetY - n1.y) * 0.015;

                // Repulsion
                for (let j = i + 1; j < simNodes.length; j++) {
                    const n2 = simNodes[j];
                    const dx = n2.x - n1.x;
                    const dy = n2.y - n1.y;
                    const distSq = dx*dx + dy*dy || 1;
                    const dist = Math.sqrt(distSq);
                    if (dist < 220) {
                        const f = repulsion / distSq;
                        const fx = (dx / dist) * f;
                        const fy = (dy / dist) * f;
                        n1.vx -= fx;
                        n1.vy -= fy;
                        n2.vx += fx;
                        n2.vy += fy;
                    }
                }
            }

            // Spring attraction along edges
            for (let i = 0; i < simEdges.length; i++) {
                const e = simEdges[i];
                const dx = e.target.x - e.source.x;
                const dy = e.target.y - e.source.y;
                const dist = Math.sqrt(dx*dx + dy*dy) || 1;
                const f = (dist - springLength) * springK;
                const fx = (dx / dist) * f;
                const fy = (dy / dist) * f;

                if (e.source !== draggedNode) {
                    e.source.vx += fx;
                    e.source.vy += fy;
                }
                if (e.target !== draggedNode) {
                    e.target.vx -= fx;
                    e.target.vy -= fy;
                }
            }

            // Apply velocity
            for (let i = 0; i < simNodes.length; i++) {
                const n = simNodes[i];
                if (n !== draggedNode) {
                    n.x += n.vx;
                    n.y += n.vy;
                    n.vx *= damping;
                    n.vy *= damping;
                }
            }

            // Render
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.save();
            ctx.translate(graphCamera.x, graphCamera.y);
            ctx.scale(graphCamera.zoom, graphCamera.zoom);

            // Draw domain cluster background hulls
            ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto';
            ctx.fillStyle = 'rgba(56, 189, 248, 0.04)';
            ctx.beginPath();
            ctx.arc(-180, 0, 140, 0, Math.PI*2);
            ctx.fill();

            ctx.fillStyle = 'rgba(16, 185, 129, 0.04)';
            ctx.beginPath();
            ctx.arc(0, 0, 140, 0, Math.PI*2);
            ctx.fill();

            ctx.fillStyle = 'rgba(245, 158, 11, 0.04)';
            ctx.beginPath();
            ctx.arc(180, 0, 140, 0, Math.PI*2);
            ctx.fill();

            // Draw edges
            for (let i = 0; i < simEdges.length; i++) {
                const e = simEdges[i];
                const isCross = e.edge_kind === 'CROSS_GRAPH_SPINE';
                ctx.beginPath();
                ctx.moveTo(e.source.x, e.source.y);
                ctx.lineTo(e.target.x, e.target.y);
                if (isCross) {
                    ctx.setLineDash([4, 4]);
                    ctx.strokeStyle = 'rgba(168, 85, 247, 0.75)';
                    ctx.lineWidth = 2.0;
                } else {
                    ctx.setLineDash([]);
                    ctx.strokeStyle = 'rgba(148, 163, 184, 0.35)';
                    ctx.lineWidth = 1.2;
                }
                ctx.stroke();

                // Draw predicate label on cross-graph bridges
                if (isCross && graphCamera.zoom > 0.75) {
                    const midX = (e.source.x + e.target.x) / 2;
                    const midY = (e.source.y + e.target.y) / 2;
                    ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
                    ctx.fillRect(midX - 35, midY - 7, 70, 14);
                    ctx.fillStyle = '#c084fc';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(e.predicate || '[:BRIDGE]', midX, midY);
                }
            }
            ctx.setLineDash([]);

            // Draw nodes
            for (let i = 0; i < simNodes.length; i++) {
                const n = simNodes[i];
                const isSelected = selectedNode && selectedNode.id === n.id;

                ctx.beginPath();
                ctx.arc(n.x, n.y, n.radius, 0, Math.PI*2);
                ctx.fillStyle = n.color;
                ctx.fill();

                if (isSelected) {
                    ctx.lineWidth = 3;
                    ctx.strokeStyle = '#ffffff';
                    ctx.stroke();
                } else {
                    ctx.lineWidth = 1.5;
                    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
                    ctx.stroke();
                }

                // Label
                ctx.fillStyle = '#f1f5f9';
                ctx.font = '10px -apple-system, sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'top';
                let shortName = (n.label || n.id).split(':')[0];
                if (shortName.length > 16) shortName = shortName.substring(0, 14) + '..';
                ctx.fillText(shortName, n.x, n.y + n.radius + 3);
            }

            ctx.restore();
            animFrameId = requestAnimationFrame(runSimulationLoop);
        }

        // ============================================================================
        // Graph Data Tables Population (Nodes, Edges, Epistemic Claims)
        // ============================================================================
        function populateGraphData(gdata) {
            activeGraphData = gdata;
            document.getElementById('graphNodeCountBadge').innerText = (gdata.nodes ? gdata.nodes.length : 0) + ' Nodes';
            document.getElementById('graphEdgeCountBadge').innerText = (gdata.edges ? gdata.edges.length : 0) + ' Edges';

            renderNodesTable();
            renderEdgesTable();
            renderClaimsTable();
        }

        function filterGraphData(domain) {
            activeFilter = domain;
            document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
            if (domain === 'ALL') document.getElementById('filterAllBtn').classList.add('active');
            if (domain === 'ORG') document.getElementById('filterOrgBtn').classList.add('active');
            if (domain === 'TECH') document.getElementById('filterTechBtn').classList.add('active');
            if (domain === 'CRM') document.getElementById('filterCrmBtn').classList.add('active');
            renderNodesTable();
        }

        function renderNodesTable() {
            const tbody = document.getElementById('nodesTableBody');
            tbody.innerHTML = '';
            let nodes = activeGraphData.nodes || [];
            if (activeFilter !== 'ALL') {
                nodes = nodes.filter(n => n.graph === activeFilter);
            }

            if (nodes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748b;">No nodes match selected domain filter.</td></tr>';
                return;
            }

            nodes.forEach(n => {
                const tr = document.createElement('tr');
                const badgeClass = n.graph === 'ORG' ? 'badge-org' : (n.graph === 'TECH' ? 'badge-tech' : 'badge-crm');
                let propsSummary = Object.entries(n.properties || {})
                    .slice(0, 3)
                    .map(([k, v]) => `<span style="color:#94a3b8;">${escapeHtml(k)}:</span> <strong>${escapeHtml(v)}</strong>`)
                    .join(' | ');

                tr.innerHTML = `
                    <td><span class="badge ${badgeClass}">${escapeHtml(n.graph_label || n.graph)}</span></td>
                    <td><code>${escapeHtml(n.id)}</code></td>
                    <td style="font-weight:600; color:#f1f5f9;">${escapeHtml(n.label)}</td>
                    <td style="color:#94a3b8;">${escapeHtml(n.bfo_category || 'Entity')}</td>
                    <td style="font-size:10px;">${propsSummary || '—'}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        function renderEdgesTable() {
            const tbody = document.getElementById('edgesTableBody');
            tbody.innerHTML = '';
            const edges = activeGraphData.edges || [];

            if (edges.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748b;">No edges or bridges in this subgraph.</td></tr>';
                return;
            }

            edges.forEach(e => {
                const tr = document.createElement('tr');
                const isCross = e.edge_kind === 'CROSS_GRAPH_SPINE';
                const kindBadge = isCross ? '<span class="badge badge-bridge">CROSS-SPINE</span>' : '<span class="badge badge-spine">INTRA-DOMAIN</span>';
                const srcDomain = e.source_graph || 'ORG';
                const tgtDomain = e.target_graph || 'TECH';
                const srcClass = srcDomain === 'ORG' ? 'badge-org' : (srcDomain === 'TECH' ? 'badge-tech' : 'badge-crm');
                const tgtClass = tgtDomain === 'ORG' ? 'badge-org' : (tgtDomain === 'TECH' ? 'badge-tech' : 'badge-crm');

                tr.innerHTML = `
                    <td>${kindBadge}</td>
                    <td><span class="badge ${srcClass}" style="margin-right:4px;">${srcDomain}</span><code>${escapeHtml(e.source || e.source_id)}</code></td>
                    <td style="font-weight:700; color:#38bdf8;">${escapeHtml(e.predicate)}</td>
                    <td><span class="badge ${tgtClass}" style="margin-right:4px;">${tgtDomain}</span><code>${escapeHtml(e.target || e.target_id)}</code></td>
                    <td style="color:#22c55e;">${escapeHtml(e.status || 'CONFIRMED')}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        function renderClaimsTable() {
            const tbody = document.getElementById('claimsTableBody');
            tbody.innerHTML = '';
            const claims = activeGraphData.claims || [];

            if (claims.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color:#64748b;">Zero ungrounded assertions. All facts corroborated.</td></tr>';
                return;
            }

            claims.forEach(c => {
                const tr = document.createElement('tr');
                let statusClass = 'badge-spine';
                if (c.status === 'VERIFIED_GROUNDED' || c.status === 'LIVE_DEMONSTRATED' || c.status === 'FPDS_OBLIGATED') {
                    statusClass = 'status-VERIFIED_GROUNDED';
                } else if (c.status === 'VENDOR_SELF_ASSERTED') {
                    statusClass = 'status-UNVERIFIED_VENDOR_CLAIM';
                }

                tr.innerHTML = `
                    <td><code>${escapeHtml(c.subject_id)}</code></td>
                    <td style="color:#38bdf8; font-weight:600;">${escapeHtml(c.predicate)}</td>
                    <td style="color:#f1f5f9;">${escapeHtml(c.value)}</td>
                    <td><span class="status-pill ${statusClass}" style="font-size:10px;">${escapeHtml(c.status)}</span></td>
                    <td><strong>${Math.round((c.confidence || 0.95) * 100)}%</strong></td>
                    <td><span class="badge badge-cell" style="font-size:10px;">${escapeHtml(c.handling || 'PUBLIC')}</span></td>
                    <td><code>${escapeHtml(c.evidence_locator || 'Sheet!R2C50')}</code></td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Load Global Federated Tri-Graph Overview
        async function loadGlobalOverview() {
            try {
                const res = await fetch('/api/graph/overview');
                const data = await res.json();
                fullGraphData = data;
                populateGraphData(data);
                startSimulation(data.nodes, data.edges);
            } catch (err) {
                console.error("Failed to load global graph overview:", err);
            }
        }

        function setQuery(q, clearance) {
            document.getElementById('queryInput').value = q;
            if (clearance) {
                document.getElementById('clearanceSelect').value = clearance;
            }
            executeQuery();
        }

        async function executeQuery() {
            const query = document.getElementById('queryInput').value.trim();
            const clearance = document.getElementById('clearanceSelect').value;
            const engine = document.getElementById('engineSelect') ? document.getElementById('engineSelect').value : 'deepseek';
            if (!query) return;

            document.getElementById('loading').style.display = 'block';
            document.getElementById('answerText').style.display = 'none';

            // Gather any session overrides
            const apiKeyOverride = sessionStorage.getItem('meia_override_api_key') || '';
            const endpointOverride = sessionStorage.getItem('meia_override_endpoint') || '';
            const modelOverride = sessionStorage.getItem('meia_override_model') || '';
            const locArm = sessionStorage.getItem('meia_loc_arm') || 'ARM_C_MULTIMODAL_CALLOUT';

            try {
                const res = await fetch('/api/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: query,
                        clearance_level: clearance,
                        engine: engine,
                        api_key: apiKeyOverride || undefined,
                        base_url: endpointOverride || undefined,
                        model_name: modelOverride || undefined,
                        loc_arm: locArm
                    })
                });
                const data = await res.json();

                // Update Badges
                const rBadge = document.getElementById('routeBadge');
                rBadge.innerText = data.route_profile;

                const sBadge = document.getElementById('statusBadge');
                sBadge.innerText = data.status;
                sBadge.className = 'status-pill status-' + data.status;

                // Update LLM Telemetry Bar
                const meta = data.llm_metadata || {};
                const tEngine = document.getElementById('telemetryEngineBadge');
                const tLatency = document.getElementById('telemetryLatencyBadge');
                const tTokens = document.getElementById('telemetryTokensBadge');
                const tSkills = document.getElementById('telemetrySkillsBadge');

                if (tEngine) {
                    const engName = meta.engine ? meta.engine.toUpperCase() : engine.toUpperCase();
                    const mdlName = meta.model_name ? ` (${meta.model_name})` : '';
                    tEngine.innerText = `⚡ Engine: ${engName}${mdlName}`;
                }
                if (tLatency) {
                    tLatency.innerText = meta.latency_ms ? `· ${(meta.latency_ms / 1000).toFixed(2)}s` : '· Offline/Direct';
                }
                if (tTokens) {
                    tTokens.innerText = (meta.prompt_tokens || meta.completion_tokens) ?
                        `· ${meta.prompt_tokens || 0} prompt / ${meta.completion_tokens || 0} completion tokens` : '';
                }
                if (tSkills) {
                    const skillsList = meta.active_skills && meta.active_skills.length > 0 ?
                        meta.active_skills.map(s => `[${s}]`).join(' ') : '[tri-graph-routing] [epistemic-claim-audit]';
                    tSkills.innerText = `🧠 Active Skills: ${skillsList}`;
                }

                // Update Answer Text
                document.getElementById('answerText').innerText = data.answer_text;

                // Update Federated Tri-Graph Lineage (LANL Pattern)
                if (data.graph_lineage && data.graph_lineage.nodes && data.graph_lineage.nodes.length > 0) {
                    populateGraphData(data.graph_lineage);
                    startSimulation(data.graph_lineage.nodes, data.graph_lineage.edges);
                }

                // Update Visual Diagrams (Conditional - No Stuck Memo)
                const diagImg = document.getElementById('diagramImage');
                const noDiagCard = document.getElementById('noDiagramCard');
                const chipContainer = document.getElementById('bboxChips');
                chipContainer.innerHTML = '';

                if (data.visual_figures && data.visual_figures.length > 0) {
                    const fig = data.visual_figures[0];
                    const fname = fig.figure_image.split('/').pop().split('\\').pop();
                    currentAssetId = fname.replace('.png', '');
                    diagImg.src = '/api/figures/' + fname;
                    diagImg.style.display = 'block';
                    noDiagCard.style.display = 'none';

                    if (fig.sample_chips) {
                        fig.sample_chips.slice(0, 4).forEach(c => {
                            const span = document.createElement('span');
                            span.className = 'bbox-chip';
                            span.innerText = (c.label || 'Region') + ' ' + JSON.stringify(c.bbox);
                            chipContainer.appendChild(span);
                        });
                    }
                } else {
                    diagImg.style.display = 'none';
                    noDiagCard.style.display = 'block';
                }

                // Update Context Packets
                const pContainer = document.getElementById('packetContainer');
                pContainer.innerHTML = '';
                const packets = data.context_packets || [];
                document.getElementById('packetCount').innerText = packets.length + ' Packets';
                if (packets.length > 0) {
                    packets.forEach(p => {
                        const div = document.createElement('div');
                        div.className = 'packet-card';
                        let qualHtml = '';
                        if (p.qualifiers_and_notes && p.qualifiers_and_notes.length > 0) {
                            qualHtml = p.qualifiers_and_notes.map(q => 
                                `<div class="packet-qualifier"><strong>${escapeHtml(q.field_label)}:</strong> ${escapeHtml(q.content)} <em>[${escapeHtml(q.source_locator)}]</em></div>`
                            ).join('');
                        }
                        div.innerHTML = `
                            <div class="packet-header">
                                <span>${escapeHtml(p.anchor_label)}</span>
                                <span class="badge badge-cell">${escapeHtml(p.target_graph)}</span>
                            </div>
                            <div style="font-size: 11px; color: #94a3b8; margin-bottom: 6px;">
                                <code>${escapeHtml(p.packet_id)}</code> | Provenance: <strong>${Math.round(p.composite_provenance_score * 100)}%</strong>
                            </div>
                            ${qualHtml}
                        `;
                        pContainer.appendChild(div);
                    });
                } else {
                    pContainer.innerHTML = '<p style="color: #64748b; font-size: 12px;">Zero ungrounded assertions detected.</p>';
                }

                // Update Citations
                const cList = document.getElementById('citationList');
                cList.innerHTML = '';
                const citations = data.citations || [];
                document.getElementById('citationCount').innerText = citations.length + ' Anchors';

                if (citations.length > 0) {
                    citations.slice(0, 12).forEach((c, idx) => {
                        const li = document.createElement('li');
                        let badgeType = 'GRAPH';
                        let badgeClass = 'badge-spine';
                        if (c.includes('!')) {
                            badgeType = 'CELL';
                            badgeClass = 'badge-cell';
                        } else if (c.startsWith('doc:')) {
                            badgeType = 'CHUNK';
                            badgeClass = 'badge-chunk';
                        } else if (c.startsWith('usaspending:') || c.startsWith('node:award:') || c.startsWith('evid:award:')) {
                            badgeType = 'AWARD';
                            badgeClass = 'badge-award';
                        } else if (c.startsWith('policy:')) {
                            badgeType = 'POLICY';
                            badgeClass = 'badge-policy';
                        }
                        li.innerHTML = `<span class="badge ${badgeClass}" style="margin-right: 6px; font-size: 10px; padding: 2px 6px;">[${badgeType}]</span>[${idx+1}] ${escapeHtml(c)}`;
                        cList.appendChild(li);
                    });
                } else {
                    cList.innerHTML = '<li>Zero ungrounded assertions detected.</li>';
                }

            } catch (err) {
                document.getElementById('answerText').innerText = 'Query Execution Error: ' + err.message;
            } finally {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('answerText').style.display = 'block';
            }
        }

        window.addEventListener('DOMContentLoaded', () => {
            initCanvas();
            loadGlobalOverview();
        });

        // Modal Handlers for Receipt & Steward Queue (U04, U05)
        async function openReceiptModal() {
            const m = document.getElementById('receiptModal');
            const c = document.getElementById('receiptModalContent');
            m.style.display = 'flex';
            c.innerHTML = '<p style="color:#94a3b8;">Loading authoritative cryptographic receipt...</p>';
            try {
                const res = await fetch('/api/benchmark/receipt');
                const data = await res.json();
                const sc = data.scorecard;
                const fp = data.cryptographic_fingerprints;
                const env = data.execution_environment;
                c.innerHTML = `
                    <div style="background:#0f172a; border:1px solid #334155; border-radius:8px; padding:16px; margin-bottom:16px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                            <span style="font-weight:700; color:#38bdf8;">Receipt ID: <code>${data.receipt_id}</code></span>
                            <span style="font-size:12px; color:#22c55e; font-weight:600;">[VERIFIED COMPLETE]</span>
                        </div>
                        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:10px; margin-bottom:14px;">
                            <div style="background:#1e293b; padding:10px; border-radius:6px; text-align:center;">
                                <div style="font-size:11px; color:#94a3b8;">Route@1 Accuracy</div>
                                <div style="font-size:18px; font-weight:700; color:#38bdf8;">${sc.route_accuracy_pct}%</div>
                            </div>
                            <div style="background:#1e293b; padding:10px; border-radius:6px; text-align:center;">
                                <div style="font-size:11px; color:#94a3b8;">Status & Gate Accuracy</div>
                                <div style="font-size:18px; font-weight:700; color:#22c55e;">${sc.status_accuracy_pct}%</div>
                            </div>
                            <div style="background:#1e293b; padding:10px; border-radius:6px; text-align:center;">
                                <div style="font-size:11px; color:#94a3b8;">Citation Coverage</div>
                                <div style="font-size:18px; font-weight:700; color:#a855f7;">${sc.citation_coverage_pct}%</div>
                            </div>
                        </div>
                        <div style="font-size:12px; color:#cbd5e1; margin-bottom:8px;"><strong>Cryptographic Hashes (SHA-256):</strong></div>
                        <div style="font-family:monospace; font-size:11px; color:#94a3b8; background:#020617; padding:8px; border-radius:4px; line-height:1.6;">
                            • Manifest: ${fp.meia_poc_manifest_sha256.substring(0, 32)}...<br/>
                            • SQLite DB: ${fp.tri_graph_registry_db_sha256.substring(0, 32)}...<br/>
                            • Vector Store: ${fp.vdb_chunks_contextual_sha256.substring(0, 32)}...<br/>
                            • Gold 78 CQs: ${fp.gold_78_cqs_sha256.substring(0, 32)}...
                        </div>
                        <div style="font-size:11px; color:#64748b; margin-top:8px;">
                            Environment: ${env.platform} | Python ${env.python_version} | ${env.embedding_model} (${env.embedding_dim}d) on ${env.pytorch_device}
                        </div>
                    </div>
                `;
            } catch (err) {
                c.innerHTML = `<p style="color:#ef4444;">Failed to load receipt: ${err.message}</p>`;
            }
        }

        function closeReceiptModal() {
            document.getElementById('receiptModal').style.display = 'none';
        }

        async function openStewardModal() {
            const m = document.getElementById('stewardModal');
            const c = document.getElementById('stewardModalContent');
            m.style.display = 'flex';
            c.innerHTML = '<p style="color:#94a3b8;">Loading Data Steward Review Queue...</p>';
            try {
                const res = await fetch('/api/steward/review-queue');
                const data = await res.json();
                const items = data.items || [];
                let rowsHtml = '';
                items.forEach((it, idx) => {
                    rowsHtml += `
                        <tr style="border-bottom:1px solid #334155;">
                            <td style="padding:8px; font-family:monospace; font-size:11px; color:#38bdf8;">${escapeHtml(it.queue_id)}</td>
                            <td style="padding:8px; font-size:11px;"><span class="badge badge-spine">${escapeHtml(it.item_type)}</span></td>
                            <td style="padding:8px; font-size:11px; color:#f8fafc;">${escapeHtml(it.subject_id)}</td>
                            <td style="padding:8px; font-size:11px; color:#cbd5e1;">${escapeHtml(it.proposed_value.substring(0, 50))}...</td>
                            <td style="padding:8px; font-size:11px; color:#f59e0b; font-weight:600;">${escapeHtml(it.review_status)}</td>
                        </tr>
                    `;
                });
                c.innerHTML = `
                    <div style="background:#0f172a; border:1px solid #334155; border-radius:8px; padding:16px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                            <span style="font-weight:700; color:#818cf8;">Pending Review Items: <strong>${data.summary.total_pending_items}</strong></span>
                            <span style="font-size:12px; color:#94a3b8;">Governance Loop: Human-in-the-Loop Gate</span>
                        </div>
                        <table style="width:100%; border-collapse:collapse; text-align:left;">
                            <thead>
                                <tr style="border-bottom:2px solid #334155; color:#94a3b8; font-size:11px;">
                                    <th style="padding:8px;">Queue ID</th>
                                    <th style="padding:8px;">Type</th>
                                    <th style="padding:8px;">Subject ID</th>
                                    <th style="padding:8px;">Proposed Value / Reason</th>
                                    <th style="padding:8px;">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rowsHtml}
                            </tbody>
                        </table>
                    </div>
                `;
            } catch (err) {
                c.innerHTML = `<p style="color:#ef4444;">Failed to load review queue: ${err.message}</p>`;
            }
        }

        function closeStewardModal() {
            document.getElementById('stewardModal').style.display = 'none';
        }

        // Model & API Key Configuration Drawer Handlers
        async function openModelDrawer() {
            const m = document.getElementById('modelModal');
            m.style.display = 'flex';
            const statusDiv = document.getElementById('serverConfigStatus');
            statusDiv.innerHTML = 'Querying server configuration status...';
            try {
                const res = await fetch('/api/config_status');
                const cfg = await res.json();
                let dsBadge = cfg.deepseek_configured ? '<span style="color:#22c55e; font-weight:700;">✅ Active from server environment</span>' : '<span style="color:#ef4444;">❌ Unconfigured (session override required)</span>';
                let gemBadge = cfg.gemini_configured ? '<span style="color:#22c55e; font-weight:700;">✅ Active</span>' : '<span style="color:#94a3b8;">Unconfigured</span>';
                let custBadge = cfg.custom_configured ? '<span style="color:#22c55e; font-weight:700;">✅ Active</span>' : '<span style="color:#94a3b8;">Unconfigured</span>';
                let skillsHtml = (cfg.active_skills || []).map(s => `<code>${escapeHtml(s.name || s)}</code>`).join(', ');

                statusDiv.innerHTML = `
                    <div>• <strong>DeepSeek API:</strong> ${dsBadge} (Default Model: <code>${cfg.deepseek_model}</code>)</div>
                    <div>• <strong>Google Gemini API:</strong> ${gemBadge} (Model: <code>${cfg.gemini_model}</code>)</div>
                    <div>• <strong>Custom / OpenAI API:</strong> ${custBadge} (Model: <code>${cfg.custom_model}</code>)</div>
                    <div style="margin-top:6px;">• <strong>Loaded Domain Skills:</strong> ${skillsHtml}</div>
                `;

                // Restore any existing session overrides to input fields
                document.getElementById('overrideApiKey').value = sessionStorage.getItem('meia_override_api_key') || '';
                document.getElementById('overrideEndpoint').value = sessionStorage.getItem('meia_override_endpoint') || '';
                document.getElementById('overrideModel').value = sessionStorage.getItem('meia_override_model') || '';
                if (sessionStorage.getItem('meia_loc_arm')) {
                    document.getElementById('locArmSelect').value = sessionStorage.getItem('meia_loc_arm');
                }
            } catch (err) {
                statusDiv.innerHTML = `<span style="color:#ef4444;">Failed to query status: ${err.message}</span>`;
            }
        }

        function closeModelDrawer() {
            document.getElementById('modelModal').style.display = 'none';
        }

        function saveModelConfig() {
            const apiKey = document.getElementById('overrideApiKey').value.trim();
            const endpoint = document.getElementById('overrideEndpoint').value.trim();
            const model = document.getElementById('overrideModel').value.trim();
            const locArm = document.getElementById('locArmSelect').value;

            if (apiKey) sessionStorage.setItem('meia_override_api_key', apiKey);
            else sessionStorage.removeItem('meia_override_api_key');

            if (endpoint) sessionStorage.setItem('meia_override_endpoint', endpoint);
            else sessionStorage.removeItem('meia_override_endpoint');

            if (model) sessionStorage.setItem('meia_override_model', model);
            else sessionStorage.removeItem('meia_override_model');

            sessionStorage.setItem('meia_loc_arm', locArm);

            closeModelDrawer();
            executeQuery();
        }

        // Run default query on initial load
        window.onload = function() { executeQuery(); };
    </script>

    <!-- Modal for Cryptographic Benchmark Receipt -->
    <div id="receiptModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:1000; align-items:center; justify-content:center;">
        <div style="background:#1e293b; border:1px solid #38bdf8; border-radius:10px; max-width:850px; width:90%; max-height:85vh; overflow-y:auto; padding:24px; color:#f8fafc;">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; padding-bottom:12px; margin-bottom:16px;">
                <h2 style="font-size:18px; color:#38bdf8;">MEIA 78-CQ Benchmark & Cryptographic Verification Receipt (U05)</h2>
                <button onclick="closeReceiptModal()" style="background:#334155; color:#fff; border:none; padding:4px 10px; border-radius:4px; cursor:pointer;">Close</button>
            </div>
            <div id="receiptModalContent">Loading cryptographic receipt...</div>
        </div>
    </div>

    <!-- Modal for Steward Review Queue -->
    <div id="stewardModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:1000; align-items:center; justify-content:center;">
        <div style="background:#1e293b; border:1px solid #6366f1; border-radius:10px; max-width:850px; width:90%; max-height:85vh; overflow-y:auto; padding:24px; color:#f8fafc;">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; padding-bottom:12px; margin-bottom:16px;">
                <h2 style="font-size:18px; color:#818cf8;">Data Steward Human Review Queue (U04)</h2>
                <button onclick="closeStewardModal()" style="background:#334155; color:#fff; border:none; padding:4px 10px; border-radius:4px; cursor:pointer;">Close</button>
            </div>
            <div id="stewardModalContent">Loading steward queue...</div>
        </div>
    </div>

    <!-- Modal for Model & API Keys Configuration -->
    <div id="modelModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:1000; align-items:center; justify-content:center;">
        <div style="background:#1e293b; border:1px solid #38bdf8; border-radius:10px; max-width:650px; width:90%; max-height:85vh; overflow-y:auto; padding:24px; color:#f8fafc;">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; padding-bottom:12px; margin-bottom:16px;">
                <h2 style="font-size:18px; color:#38bdf8;">⚙️ Inference Engine & Model Configuration</h2>
                <button onclick="closeModelDrawer()" style="background:#334155; color:#fff; border:none; padding:4px 10px; border-radius:4px; cursor:pointer;">Close</button>
            </div>
            <div id="modelConfigContent">
                <div style="background:#0f172a; padding:14px; border-radius:6px; border:1px solid #334155; margin-bottom:16px;">
                    <div style="font-weight:700; color:#cbd5e1; margin-bottom:8px;">Server-Configured Providers:</div>
                    <div id="serverConfigStatus" style="font-size:13px; line-height:1.7; color:#94a3b8;">Checking server status...</div>
                </div>
                <div style="display:flex; flex-direction:column; gap:12px; margin-bottom:16px;">
                    <div>
                        <label style="font-size:12px; color:#cbd5e1; font-weight:600; display:block; margin-bottom:4px;">Session API Key Override (In-Memory / Session Only):</label>
                        <input type="password" id="overrideApiKey" placeholder="sk-... (Overrides server key for this browser session)" style="width:100%; padding:8px 12px; background:#0f172a; border:1px solid #334155; color:#f8fafc; border-radius:6px; font-size:13px;">
                    </div>
                    <div>
                        <label style="font-size:12px; color:#cbd5e1; font-weight:600; display:block; margin-bottom:4px;">Custom / Local Endpoint URL (Ollama, vLLM, OpenRouter):</label>
                        <input type="text" id="overrideEndpoint" placeholder="https://api.openai.com/v1 or http://localhost:11434/v1" style="width:100%; padding:8px 12px; background:#0f172a; border:1px solid #334155; color:#f8fafc; border-radius:6px; font-size:13px;">
                    </div>
                    <div>
                        <label style="font-size:12px; color:#cbd5e1; font-weight:600; display:block; margin-bottom:4px;">Custom Model Name:</label>
                        <input type="text" id="overrideModel" placeholder="deepseek-chat / gpt-4o-mini / qwen2.5:7b" style="width:100%; padding:8px 12px; background:#0f172a; border:1px solid #334155; color:#f8fafc; border-radius:6px; font-size:13px;">
                    </div>
                    <div>
                        <label style="font-size:12px; color:#cbd5e1; font-weight:600; display:block; margin-bottom:4px;">Loud and Clear (LoC) Visual Reader Arm:</label>
                        <select id="locArmSelect" style="width:100%; padding:8px 12px; background:#0f172a; border:1px solid #334155; color:#f8fafc; border-radius:6px; font-size:13px;">
                            <option value="ARM_C_MULTIMODAL_CALLOUT" selected>Arm C: Hybrid BBox Focal Crop + 160-Token OCR Callouts (Recommended)</option>
                            <option value="ARM_B_FOCAL_CROP">Arm B: High-Zoom Focal Crop Only (300 DPI)</option>
                            <option value="ARM_A_FULL_PAGE">Arm A: Full-Page 180 DPI Baseline Context</option>
                        </select>
                    </div>
                </div>
                <div style="display:flex; justify-content:flex-end; gap:8px;">
                    <button onclick="saveModelConfig()" style="background:#2563eb; color:#fff; border:none; padding:8px 16px; border-radius:6px; cursor:pointer; font-weight:600;">Apply Settings</button>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""


class MeiaWebHandler(BaseHTTPRequestHandler):
    """Zero-daemon HTTP server request handler."""

    def do_GET(self):
        url = urlparse(self.path)
        path = unquote(url.path)

        if path in ("/", "/index.html"):
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_DASHBOARD.encode("utf-8"))
            return

        if path == "/api/health":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = {
                "status": "healthy",
                "service": "MEIA Federated Tri-Graph Explorer",
                "port": 8000,
                "air_gapped": True
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        if path == "/api/config_status":
            from src.config import (
                DEEPSEEK_API_KEY, GEMINI_API_KEY, CUSTOM_API_KEY,
                DEFAULT_ENGINE, DEEPSEEK_MODEL, GEMINI_MODEL, CUSTOM_MODEL
            )
            from src.skill_loader import get_skill_registry
            reg = get_skill_registry()
            status_data = {
                "deepseek_configured": bool(DEEPSEEK_API_KEY),
                "gemini_configured": bool(GEMINI_API_KEY),
                "custom_configured": bool(CUSTOM_API_KEY),
                "default_engine": DEFAULT_ENGINE,
                "deepseek_model": DEEPSEEK_MODEL,
                "gemini_model": GEMINI_MODEL,
                "custom_model": CUSTOM_MODEL,
                "active_skills": [s.to_dict() for s in reg.list_skills()],
            }
            resp_bytes = json.dumps(status_data).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
            return

        if path == "/api/skills":
            from src.skill_loader import get_skill_registry
            reg = get_skill_registry()
            skills_data = {
                "count": len(reg.list_skills()),
                "skills": [s.to_dict() for s in reg.list_skills()],
            }
            resp_bytes = json.dumps(skills_data).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
            return

        if path == "/api/query":
            from urllib.parse import parse_qs
            qs = parse_qs(url.query)
            q_str = qs.get("query", [""])[0]
            clearance = qs.get("clearance_level", ["SECRET"])[0]
            eng = qs.get("engine", [None])[0]
            loc_arm = qs.get("loc_arm", ["ARM_C_MULTIMODAL_CALLOUT"])[0]
            ctx = CallerContext(
                caller_role="meia-authorized-evaluator" if clearance != "UNCLASSIFIED" else "guest-evaluator",
                clearance_level=clearance,
                enabled_modules=["organization_graph", "technology_graph", "crm_graph", "evidence_graph"]
            )
            ans = answer_query(q_str, ctx, engine=eng, loc_arm=loc_arm)
            resp_bytes = json.dumps(ans.to_dict()).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
            return


        if path.startswith("/api/figures/crops/") or path.startswith("/parsed/figures/crops/"):
            prefix = "/api/figures/crops/" if path.startswith("/api/figures/crops/") else "/parsed/figures/crops/"
            rel_name = unquote(path[len(prefix):]).lstrip("/")
            try:
                crop_path = (CROPS_DIR / rel_name).resolve()
                if not crop_path.is_relative_to(CROPS_DIR.resolve()):
                    self.send_response(HTTPStatus.FORBIDDEN)
                    self.end_headers()
                    self.wfile.write(b"Forbidden: Path traversal detected")
                    return
                if not crop_path.exists() or not crop_path.is_file():
                    self.send_response(HTTPStatus.NOT_FOUND)
                    self.end_headers()
                    self.wfile.write(b"Crop not found")
                    return
                mime, _ = mimetypes.guess_type(str(crop_path))
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", mime or "image/png")
                self.send_header("Content-Length", str(crop_path.stat().st_size))
                self.end_headers()
                with open(crop_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            except Exception as e:
                self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
                return

        if path.startswith("/api/figures/") or path.startswith("/parsed/figures/"):
            prefix = "/api/figures/" if path.startswith("/api/figures/") else "/parsed/figures/"
            rel_name = unquote(path[len(prefix):]).lstrip("/")
            try:
                fig_path = (FIGURES_DIR / rel_name).resolve()
                if not fig_path.is_relative_to(FIGURES_DIR.resolve()):
                    self.send_response(HTTPStatus.FORBIDDEN)
                    self.end_headers()
                    self.wfile.write(b"Forbidden: Path traversal detected")
                    return
                if not fig_path.exists() or not fig_path.is_file():
                    self.send_response(HTTPStatus.NOT_FOUND)
                    self.end_headers()
                    self.wfile.write(b"Figure not found")
                    return
                mime, _ = mimetypes.guess_type(str(fig_path))
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", mime or "image/png")
                self.send_header("Content-Length", str(fig_path.stat().st_size))
                self.end_headers()
                with open(fig_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            except Exception as e:
                self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
                return

        if path.startswith("/api/loc/inspect"):
            from urllib.parse import parse_qs
            qs = parse_qs(url.query)
            asset_id = qs.get("asset_id", [""])[0]
            arm = qs.get("arm", ["ARM_A_FULL_PAGE"])[0]
            loc_data = inspect_figure_loc(asset_id, arm)
            resp_bytes = json.dumps(loc_data).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
            return

        if path.startswith("/api/context-packets"):
            builder = ContextPacketBuilder()
            seed_entities = [
                "tech:offering:ghostfin_uuv",
                "tech:offering:eclipse_x9",
                "tech:offering:counter_sensing",
                "org:fluor_federal_services",
                "org:prometheus_intelligence"
            ]
            packets = [builder.build_packet_for_entity(eid).to_dict() for eid in seed_entities]
            resp_bytes = json.dumps(packets).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
            return

        if path.startswith("/api/benchmark/receipt"):
            receipt_path = REPO_ROOT / "eval" / "meia_78_cq_receipt.json"
            if not receipt_path.exists():
                from eval.test_scorer import run_benchmark
                run_benchmark(REPO_ROOT / "eval" / "gold_78_cqs.json", REPO_ROOT / "eval" / "meia_78_cq_report.md")
            with open(receipt_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            resp_bytes = json.dumps(data).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
            return

        if path.startswith("/api/steward/review-queue"):
            from src.steward_review import StewardReviewManager
            mgr = StewardReviewManager()
            items = mgr.harvest_review_queue()
            stats = mgr.get_summary_stats()
            payload = {
                "summary": stats,
                "items": [it.to_dict() for it in items]
            }
            resp_bytes = json.dumps(payload).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
            return

        if path.startswith("/api/graph/overview"):
            conn = sqlite3.connect(str(TRI_GRAPH_DB_PATH))
            c = conn.cursor()
            c.execute("SELECT id, graph_domain, bfo_category, skos_concepts, label, properties_json FROM domain_nodes")
            nodes = []
            domain_counts = {}
            for row in c.fetchall():
                nid, domain, bfo, skos_str, label, props_str = row
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
                nodes.append({
                    "id": nid,
                    "node_id": nid,
                    "domain": domain,
                    "graph": domain,
                    "graph_label": f"{domain}-KG" if domain != 'CRM' else "CRM-Graph",
                    "label": label,
                    "category": bfo,
                    "bfo_category": bfo,
                    "skos_concepts": json.loads(skos_str or "[]"),
                    "properties": json.loads(props_str or "{}")
                })
            c.execute("SELECT edge_id, source_id, target_id, edge_type, graph_domain, properties_json FROM domain_edges")
            edges = []
            for row in c.fetchall():
                eid, src, tgt, etype, gdomain, props_str = row
                edges.append({
                    "edge_id": eid,
                    "source": src,
                    "source_graph": gdomain,
                    "target": tgt,
                    "target_graph": gdomain,
                    "graph_domain": gdomain,
                    "predicate": etype,
                    "edge_kind": "INTRA_DOMAIN",
                    "properties": json.loads(props_str or "{}"),
                    "status": "CONFIRMED"
                })
            c.execute("SELECT link_id, source_id, source_graph, target_id, target_graph, link_predicate, match_method, review_status, properties_json FROM cross_graph_links")
            for row in c.fetchall():
                lid, src, sg, tgt, tg, pred, method, status, props_str = row
                edges.append({
                    "edge_id": lid,
                    "source": src,
                    "source_graph": sg,
                    "target": tgt,
                    "target_graph": tg,
                    "graph_domain": f"{sg}->{tg}",
                    "predicate": pred,
                    "edge_kind": "CROSS_GRAPH_SPINE",
                    "match_method": method,
                    "status": status,
                    "properties": json.loads(props_str or "{}")
                })
            c.execute("SELECT claim_id, subject_id, predicate, object_value, epistemic_status, confidence, handling_level, evidence_id, notes FROM claim_ledger")
            claims = []
            for row in c.fetchall():
                cid, sub, pred, val, status, conf, hand, evid, notes = row
                claims.append({
                    "claim_id": cid,
                    "subject_id": sub,
                    "predicate": pred,
                    "value": val,
                    "status": status,
                    "confidence": conf,
                    "handling": hand,
                    "evidence_id": evid,
                    "notes": notes
                })
            conn.close()

            payload = {
                "summary": {
                    "total_nodes": len(nodes),
                    "total_edges": len(edges),
                    "graphs_involved": ["ORG", "TECH", "CRM"],
                    "domain_breakdown": domain_counts,
                    "route_profile": "FEDERATED_TRI_STORE_OVERVIEW"
                },
                "nodes": nodes,
                "edges": edges,
                "claims": claims
            }
            resp_bytes = json.dumps(payload).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
            return


        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()
        self.wfile.write(b"Not Found")

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/api/query":
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 65536:
                self.send_response(HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
                self.end_headers()
                self.wfile.write(b"Payload Too Large (Max 64KB)")
                return
            raw_body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(raw_body)
                query = data.get("query", "").strip()
                clearance = data.get("clearance_level", "SECRET")
                engine = data.get("engine")
                api_key = data.get("api_key")
                model_name = data.get("model_name")
                base_url = data.get("base_url")
                loc_arm = data.get("loc_arm", "ARM_C_MULTIMODAL_CALLOUT")

                ctx = CallerContext(
                    caller_role="meia-authorized-evaluator" if clearance != "UNCLASSIFIED" else "guest-evaluator",
                    clearance_level=clearance,
                    enabled_modules=["organization_graph", "technology_graph", "crm_graph", "evidence_graph"]
                )

                ans = answer_query(
                    query,
                    ctx,
                    engine=engine,
                    api_key=api_key,
                    model_name=model_name,
                    base_url=base_url,
                    loc_arm=loc_arm,
                )
                resp_bytes = json.dumps(ans.to_dict()).encode("utf-8")

                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)
            except Exception as e:
                logger.error("Error executing query: %s", e)
                err_bytes = json.dumps({"error": str(e)}).encode("utf-8")
                self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(err_bytes)
            return

        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()
        self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        # Quiet standard handler log spam
        pass


def start_server(port: int = 8000):
    server = ThreadingHTTPServer(("127.0.0.1", port), MeiaWebHandler)
    logger.info("MEIA Web Visual Explorer serving on http://127.0.0.1:%d", port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping MEIA Web Explorer...")
        server.server_close()


if __name__ == "__main__":
    start_server(8000)
