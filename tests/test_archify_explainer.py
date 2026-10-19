"""
Automated Verification Suite for MEIA Archify Diagrams & Explainer Page.
Tests web routes, SVG XML validity, step-node reference integrity,
source citation anchors, and air-gapped standalone HTML deliverable.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pytest
from src.explainer_service import (
    get_all_panels,
    get_diagram_svg_content,
    read_source_excerpt,
    EXPLAINER_PANELS
)


def test_panels_catalog_integrity():
    """Verify that all 5 required Archify panels are defined with required attributes."""
    panels = get_all_panels()
    assert len(panels) == 5, f"Expected 5 panels, got {len(panels)}"

    expected_svgs = [
        "diagram1_architecture.svg",
        "diagram2_preretrieval.svg",
        "diagram3_trident.svg",
        "diagram4_firewall.svg",
        "diagram5_dual_engine.svg"
    ]

    for idx, panel in enumerate(panels, start=1):
        assert panel["index"] == idx
        assert "id" in panel
        assert "title" in panel
        assert "svgFile" in panel
        assert panel["svgFile"] == expected_svgs[idx - 1]
        assert "conclusion" in panel
        assert "headline" in panel["conclusion"]
        assert "summary" in panel["conclusion"]
        assert "metrics" in panel["conclusion"]
        assert len(panel["conclusion"]["metrics"]) >= 3
        assert "steps" in panel
        assert len(panel["steps"]) >= 4


def test_svg_xml_validity_and_viewbox():
    """Verify each of the 5 SVGs is well-formed XML and has a valid viewBox."""
    diagrams_dir = REPO_ROOT / "src" / "static" / "diagrams"

    for panel in EXPLAINER_PANELS:
        svg_filename = panel["svgFile"]
        svg_path = diagrams_dir / svg_filename
        assert svg_path.exists(), f"SVG missing: {svg_path}"

        content = get_diagram_svg_content(svg_filename)
        assert content is not None
        assert len(content) > 1000

        # XML parse check
        root = ET.fromstring(content)
        # Check tag ends with svg
        assert root.tag.endswith("svg")
        assert "viewBox" in root.attrib


def test_step_lighting_nodes_exist_in_svg():
    """
    Verify that every node ID declared in a guided step actually exists
    as an element (<g id="..." or data-node-id="...">) in the SVG diagram.
    """
    diagrams_dir = REPO_ROOT / "src" / "static" / "diagrams"

    for panel in EXPLAINER_PANELS:
        svg_path = diagrams_dir / panel["svgFile"]
        svg_text = svg_path.read_text(encoding="utf-8")
        root = ET.fromstring(svg_text)

        # Collect all element IDs and data-node-ids
        found_ids = set()
        for elem in root.iter():
            if "id" in elem.attrib:
                found_ids.add(elem.attrib["id"])
            if "data-node-id" in elem.attrib:
                found_ids.add(elem.attrib["data-node-id"])

        for step in panel.get("steps", []):
            for node_id in step.get("activeNodes", []):
                assert node_id in found_ids, (
                    f"In {panel['svgFile']} Step {step['step']} '{step['title']}': "
                    f"Active node ID '{node_id}' not found in SVG elements."
                )


def test_source_citations_resolve_to_real_files():
    """
    Verify that every [SRC n] receipt points to an existing file in the repository,
    and that line numbers are within the bounds of the file.
    """
    for panel in EXPLAINER_PANELS:
        for step in panel.get("steps", []):
            for src in step.get("sources", []):
                rel_file = src["file"]
                target_file = REPO_ROOT / rel_file.replace("/", "\\")
                assert target_file.exists(), (
                    f"Cited source file '{rel_file}' does not exist on disk."
                )
                assert target_file.is_file()

                start_l = src["startLine"]
                end_l = src["endLine"]
                assert start_l <= end_l

                # Read excerpt using the service
                excerpt = read_source_excerpt(rel_file, start_l, end_l)
                assert "error" not in excerpt, f"Error reading {rel_file}: {excerpt.get('error')}"
                assert len(excerpt["lines"]) > 0
                assert excerpt["file"] == rel_file


def test_source_excerpt_path_traversal_guard():
    """Verify that path traversal attempts are rejected."""
    bad_call = read_source_excerpt("../../../Windows/System32/drivers/etc/hosts", 1, 10)
    assert "error" in bad_call
    assert "Forbidden" in bad_call["error"] or "File not found" in bad_call["error"]


def test_standalone_compiled_deliverable():
    """Verify docs/meia_architecture_explainer.html exists and is air-gapped."""
    deliverable_path = REPO_ROOT / "docs" / "meia_architecture_explainer.html"
    assert deliverable_path.exists(), "Standalone HTML deliverable does not exist"
    content = deliverable_path.read_text(encoding="utf-8")

    assert len(content) > 100_000, "Deliverable is too small to be complete"
    assert "ARCHIFY_PANELS" in content
    assert "ARCHIFY_SOURCE_CACHE" in content
    assert "diagram1_architecture.svg" in content
    assert "diagram5_dual_engine.svg" in content

    # Air-gap invariant: No external script or stylesheet loads
    assert 'src="http' not in content.lower(), "External script detected in air-gapped deliverable"
    assert 'href="http' not in content.lower() or 'href="https://' not in content.lower().split("</head>")[0], (
        "External stylesheet detected in head"
    )
