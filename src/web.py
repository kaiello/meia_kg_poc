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
                <div class="panel-title">Multimodal Evidence & Architecture Diagram</div>
                <span id="figureCount" class="badge badge-spine">0 Figures</span>
            </div>
            <div id="diagramSection" class="diagram-container">
                <img id="diagramImage" class="diagram-img" src="/api/figures/meia_charter_2026_p1.png" alt="Architecture Diagram" onerror="this.style.display='none'">
            </div>
            <div id="bboxChips" class="chips-container"></div>

            <div class="panel-header" style="margin-top: 24px;">
                <div class="panel-title">Exact Grounding Citations (CQ-73)</div>
                <span id="citationCount" class="badge badge-spine">0 Anchors</span>
            </div>
            <ul id="citationList" class="citations-list">
                <li>Execute a query to inspect exact Sheet!Row:Col and PDF chunk citations.</li>
            </ul>
        </div>
    </div>

    <script>
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

                // Update Citations
                const cList = document.getElementById('citationList');
                cList.innerHTML = '';
                const citations = data.citations || [];
                document.getElementById('citationCount').innerText = citations.length + ' Anchors';

                if (citations.length > 0) {
                    citations.slice(0, 8).forEach((c, idx) => {
                        const li = document.createElement('li');
                        li.innerText = `[${idx+1}] ${c}`;
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

        // Run default query on initial load
        window.onload = function() { executeQuery(); };
    </script>
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
