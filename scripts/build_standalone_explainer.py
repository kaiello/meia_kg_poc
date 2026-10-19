#!/usr/bin/env python3
"""
Archify Standalone Explainer Compiler for MEIA Federated Tri-Graph POC.
Bundles all HTML, CSS, JS, SVG diagrams, panel metadata, and source receipts
into a single, 100% portable, air-gapped HTML file with zero external dependencies.
"""

import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.explainer_service import (
    get_all_panels,
    get_diagram_svg_content,
    read_source_excerpt
)

STATIC_DIR = REPO_ROOT / "src" / "static"
OUTPUT_HTML_PATH = REPO_ROOT / "docs" / "meia_architecture_explainer.html"


def build_standalone_explainer() -> Path:
    print("=" * 70)
    print("Building Archify Standalone Offline Explainer for MEIA Tri-Graph POC")
    print("=" * 70)

    # 1. Read base HTML template
    base_html_path = STATIC_DIR / "explainer.html"
    with open(base_html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 2. Read and inline CSS
    css_explainer = (STATIC_DIR / "css" / "explainer.css").read_text(encoding="utf-8")
    css_diagram = (STATIC_DIR / "css" / "diagram_theme.css").read_text(encoding="utf-8")
    combined_css = f"""
<style>
/* --- INLINED EXPLAINER CSS --- */
{css_explainer}

/* --- INLINED DIAGRAM THEME CSS --- */
{css_diagram}
</style>
"""
    # Replace link tags with inline styles
    html = html.replace('<link rel="stylesheet" href="/static/css/explainer.css">', '')
    html = html.replace('<link rel="stylesheet" href="/static/css/diagram_theme.css">', combined_css)

    # 3. Read and inline JavaScript files
    js_controller = (STATIC_DIR / "js" / "diagram_controller.js").read_text(encoding="utf-8")
    js_drawer = (STATIC_DIR / "js" / "source_drawer.js").read_text(encoding="utf-8")
    js_app = (STATIC_DIR / "js" / "explainer_app.js").read_text(encoding="utf-8")

    # 4. Prepare data catalog & pre-cache source excerpts
    panels = get_all_panels()
    source_cache = {}

    print(f"Bundling {len(panels)} panels...")
    for p in panels:
        print(f"  - Panel {p['index']}: {p['title']}")
        for s in p.get("steps", []):
            for src in s.get("sources", []):
                src_id = src["id"]
                if src_id not in source_cache:
                    excerpt = read_source_excerpt(src["file"], src["startLine"], src["endLine"])
                    source_cache[src_id] = excerpt

    print(f"Pre-cached {len(source_cache)} verifiable source receipts.")

    # 5. Embed SVG templates into hidden container
    svg_templates_html = '<div id="archify-svg-catalog" style="display:none;" aria-hidden="true">\n'
    for p in panels:
        svg_file = p["svgFile"]
        svg_content = get_diagram_svg_content(svg_file)
        if svg_content:
            svg_templates_html += f'  <div id="inlined-{svg_file}">\n{svg_content}\n  </div>\n'
            print(f"  + Inlined SVG: {svg_file} ({len(svg_content):,} bytes)")
        else:
            print(f"  ! Warning: Missing SVG content for {svg_file}")
    svg_templates_html += '</div>\n'

    # Insert SVGs right before closing body
    html = html.replace("</body>", f"{svg_templates_html}\n</body>")

    # 6. Build combined inline script block
    panels_json = json.dumps(panels, indent=2)
    source_cache_json = json.dumps(source_cache, indent=2)

    combined_js = f"""
<script>
/* --- INLINED ARCHIFY PANELS DATA --- */
window.ARCHIFY_PANELS = {panels_json};

/* --- INLINED VERIFIED SOURCE RECEIPTS CACHE --- */
window.ARCHIFY_SOURCE_CACHE = {source_cache_json};

/* --- INLINED DIAGRAM CONTROLLER --- */
{js_controller}

/* --- INLINED SOURCE DRAWER --- */
{js_drawer}

/* --- INLINED EXPLAINER APP --- */
{js_app}
</script>
"""

    # Replace external script tags with combined inline script
    html = html.replace('<script src="/static/js/diagram_controller.js"></script>', '')
    html = html.replace('<script src="/static/js/source_drawer.js"></script>', '')
    html = html.replace('<script src="/static/js/explainer_app.js"></script>', combined_js)

    # 7. Write to docs/meia_architecture_explainer.html
    OUTPUT_HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print("=" * 70)
    print(f"SUCCESS: Compiled standalone deliverable ({OUTPUT_HTML_PATH.stat().st_size:,} bytes)")
    print(f"Output path: {OUTPUT_HTML_PATH}")
    print("=" * 70)
    return OUTPUT_HTML_PATH


if __name__ == "__main__":
    build_standalone_explainer()
