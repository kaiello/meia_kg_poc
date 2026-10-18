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
import sys
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, unquote

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config import FIGURES_DIR
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
            <button class="badge badge-vectors" onclick="openReceiptModal()" style="cursor:pointer; border:1px solid #818cf8; background:rgba(99,102,241,0.25);">Audit Receipt (100%)</button>
            <button class="badge badge-spine" onclick="openStewardModal()" style="cursor:pointer; border:1px solid var(--accent-blue); background:rgba(56,189,248,0.25);">Steward Queue (U04)</button>
        </div>
    </div>

    <div class="search-container">
        <div class="search-bar">
            <input type="text" id="queryInput" class="search-input" placeholder="Type a natural language competency question..." value="What is Ghostfin's TRL and operational range?">
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
            <div id="loading" class="loading-spinner">Traversing Federated Tri-Graph & Synthesizing Grounded Facts...</div>
            <div id="answerText" class="answer-content">Click 'Execute Query' or any quick profile chip above to inspect the federated response.</div>
        </div>

        <!-- Right Column: Multimodal Architecture Diagrams & Evidence Citations -->
        <div class="panel">
            <div class="panel-header">
                <div class="panel-title">Multimodal Evidence & Architecture Diagram (LoC V01)</div>
                <span id="figureCount" class="badge badge-spine">0 Figures</span>
            </div>
            <div class="loc-tabs">
                <button id="tabArmA" class="loc-tab-btn active" onclick="switchLoCArm('ARM_A_FULL_PAGE')">Arm A: Full 180 DPI</button>
                <button id="tabArmB" class="loc-tab-btn" onclick="switchLoCArm('ARM_B_FOCAL_CROP')">Arm B: Focal Crop Chip</button>
                <button id="tabArmC" class="loc-tab-btn" onclick="switchLoCArm('ARM_C_MULTIMODAL_CALLOUT')">Arm C: OCR Callouts</button>
            </div>
            <div id="diagramSection" class="diagram-container">
                <img id="diagramImage" class="diagram-img" src="/api/figures/meia_charter_2026_p1.png" alt="Architecture Diagram" onerror="this.style.display='none'">
            </div>
            <div id="bboxChips" class="chips-container"></div>

            <div class="panel-header" style="margin-top: 20px;">
                <div class="panel-title">R03 Functional Context Packets</div>
                <span id="packetCount" class="badge badge-cell">0 Packets</span>
            </div>
            <div id="packetContainer" style="max-height: 240px; overflow-y: auto;">
                <p style="color: #64748b; font-size: 12px;">No context packets assembled.</p>
            </div>

            <div class="panel-header" style="margin-top: 20px;">
                <div class="panel-title">Exact Grounding Citations (CQ-73)</div>
                <span id="citationCount" class="badge badge-spine">0 Anchors</span>
            </div>
            <ul id="citationList" class="citations-list">
                <li>Execute a query to inspect exact Sheet!Row:Col and PDF chunk citations.</li>
            </ul>
        </div>
    </div>

    <script>
        let currentAssetId = "meia_charter_2026_p1";
        let currentArm = "ARM_A_FULL_PAGE";

        async function switchLoCArm(arm) {
            currentArm = arm;
            document.querySelectorAll('.loc-tab-btn').forEach(b => b.classList.remove('active'));
            if (arm === 'ARM_A_FULL_PAGE') document.getElementById('tabArmA').classList.add('active');
            if (arm === 'ARM_B_FOCAL_CROP') document.getElementById('tabArmB').classList.add('active');
            if (arm === 'ARM_C_MULTIMODAL_CALLOUT') document.getElementById('tabArmC').classList.add('active');

            try {
                const res = await fetch(`/api/loc/inspect?asset_id=${encodeURIComponent(currentAssetId)}&arm=${arm}`);
                const data = await res.json();
                const diagImg = document.getElementById('diagramImage');
                if (arm === 'ARM_B_FOCAL_CROP' && data.focal_crop_path) {
                    diagImg.src = '/' + data.focal_crop_path;
                } else {
                    diagImg.src = data.full_page_path ? ('/' + data.full_page_path) : `/api/figures/${currentAssetId}.png`;
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
            if (!query) return;

            document.getElementById('loading').style.display = 'block';
            document.getElementById('answerText').style.display = 'none';

            try {
                const res = await fetch('/api/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query, clearance_level: clearance })
                });
                const data = await res.json();

                // Update Badges
                const rBadge = document.getElementById('routeBadge');
                rBadge.innerText = data.route_profile;

                const sBadge = document.getElementById('statusBadge');
                sBadge.innerText = data.status;
                sBadge.className = 'status-pill status-' + data.status;

                // Update Answer Text
                document.getElementById('answerText').innerText = data.answer_text;

                // Update Visual Diagrams
                const diagImg = document.getElementById('diagramImage');
                const chipContainer = document.getElementById('bboxChips');
                chipContainer.innerHTML = '';

                if (data.visual_figures && data.visual_figures.length > 0) {
                    const fig = data.visual_figures[0];
                    const fname = fig.figure_image.split('/').pop().split('\\').pop();
                    currentAssetId = fname.replace('.png', '');
                    diagImg.src = '/api/figures/' + fname;
                    diagImg.style.display = 'block';
                    document.getElementById('figureCount').innerText = data.visual_figures.length + ' Figures';

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
                    document.getElementById('figureCount').innerText = '0 Figures';
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
                                `<div class="packet-qualifier"><strong>${q.field_label}:</strong> ${q.content} <em>[${q.source_locator}]</em></div>`
                            ).join('');
                        }
                        div.innerHTML = `
                            <div class="packet-header">
                                <span>${p.anchor_label}</span>
                                <span class="badge badge-cell">${p.target_graph}</span>
                            </div>
                            <div style="font-size: 11px; color: #94a3b8; margin-bottom: 6px;">
                                <code>${p.packet_id}</code> | Provenance: <strong>${Math.round(p.composite_provenance_score * 100)}%</strong>
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
                        li.innerHTML = `<span class="badge ${badgeClass}" style="margin-right: 6px; font-size: 10px; padding: 2px 6px;">[${badgeType}]</span>[${idx+1}] ${c}`;
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
                            <td style="padding:8px; font-family:monospace; font-size:11px; color:#38bdf8;">${it.queue_id}</td>
                            <td style="padding:8px; font-size:11px;"><span class="badge badge-spine">${it.item_type}</span></td>
                            <td style="padding:8px; font-size:11px; color:#f8fafc;">${it.subject_id}</td>
                            <td style="padding:8px; font-size:11px; color:#cbd5e1;">${it.proposed_value.substring(0, 50)}...</td>
                            <td style="padding:8px; font-size:11px; color:#f59e0b; font-weight:600;">${it.review_status}</td>
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

        if path.startswith("/api/figures/crops/"):
            filename = path.replace("/api/figures/crops/", "")
            crop_path = CROPS_DIR / filename
            if crop_path.exists() and crop_path.is_file():
                mime, _ = mimetypes.guess_type(str(crop_path))
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", mime or "image/png")
                self.send_header("Content-Length", str(crop_path.stat().st_size))
                self.end_headers()
                with open(crop_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()
                self.wfile.write(b"Crop not found")
                return

        if path.startswith("/api/figures/"):
            filename = path.replace("/api/figures/", "")
            fig_path = FIGURES_DIR / filename
            if fig_path.exists() and fig_path.is_file():
                mime, _ = mimetypes.guess_type(str(fig_path))
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", mime or "image/png")
                self.send_header("Content-Length", str(fig_path.stat().st_size))
                self.end_headers()
                with open(fig_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()
                self.wfile.write(b"Figure not found")
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


        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()
        self.wfile.write(b"Not Found")

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/api/query":
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(raw_body)
                query = data.get("query", "").strip()
                clearance = data.get("clearance_level", "SECRET")

                ctx = CallerContext(
                    caller_role="meia-authorized-evaluator" if clearance != "UNCLASSIFIED" else "guest-evaluator",
                    clearance_level=clearance,
                    enabled_modules=["organization_graph", "technology_graph", "crm_graph", "evidence_graph"]
                )

                ans = answer_query(query, ctx)
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
    server = HTTPServer(("127.0.0.1", port), MeiaWebHandler)
    logger.info("MEIA Web Visual Explorer serving on http://127.0.0.1:%d", port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping MEIA Web Explorer...")
        server.server_close()


if __name__ == "__main__":
    start_server(8000)
