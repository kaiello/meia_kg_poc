"""
Deterministic Tri-Graph Constructor & Shared Epistemic Spine Builder
Populates SQLite storage (tables + FTS5) and exports GraphML substrates for:
1. Organization Graph (Org-KG)
2. Technology & Capability Graph (Tech-KG)
3. CRM & Engagement Graph (CRM-Graph)
4. Federated Epistemic Graph (Tri-Graph + Evidence Spine)
"""

import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import networkx as nx

from src.config import (
    REPO_ROOT,
    STORAGE_DIR,
    TRI_GRAPH_DB_PATH,
    ORG_GRAPHML_PATH,
    TECH_GRAPHML_PATH,
    CRM_GRAPHML_PATH,
    FEDERATED_GRAPHML_PATH,
    VULCAN_PARSED_JSONL,
    USASPENDING_PARSED_JSONL,
    TEXT_CHUNKS_JSONL,
    FIGURE_BBOXES_JSON,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("build_tri_graph")


def init_database(db_path: Path) -> sqlite3.Connection:
    """Initializes the SQLite schema with domain tables, link registry, and FTS5 search."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        try:
            db_path.unlink()
        except Exception:
            pass

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    c = conn.cursor()

    # 1. Domain Nodes
    c.execute("""
    CREATE TABLE IF NOT EXISTS domain_nodes (
        id TEXT PRIMARY KEY,
        graph_domain TEXT NOT NULL,     -- 'ORG', 'TECH', 'CRM'
        bfo_category TEXT NOT NULL,     -- 'MaterialEntity', 'InformationContentEntity', 'Process', 'Disposition', 'Role'
        skos_concepts TEXT,             -- JSON array of SKOS terms
        label TEXT NOT NULL,
        properties_json TEXT NOT NULL
    );
    """)

    # 2. Domain Edges
    c.execute("""
    CREATE TABLE IF NOT EXISTS domain_edges (
        edge_id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        edge_type TEXT NOT NULL,
        graph_domain TEXT NOT NULL,
        properties_json TEXT,
        FOREIGN KEY(source_id) REFERENCES domain_nodes(id),
        FOREIGN KEY(target_id) REFERENCES domain_nodes(id)
    );
    """)

    # 3. Cross-Graph Links (Integration Spine)
    c.execute("""
    CREATE TABLE IF NOT EXISTS cross_graph_links (
        link_id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        source_graph TEXT NOT NULL,
        target_id TEXT NOT NULL,
        target_graph TEXT NOT NULL,
        link_predicate TEXT NOT NULL,   -- '[:DEVELOPS_OFFERING]', '[:SUBMITTED_BY_ORG]', '[:EVALUATES_OFFERING]', '[:VALIDATED_BY_CONTRACT]'
        match_method TEXT NOT NULL,     -- 'CAGE_EXACT', 'UEI_EXACT', 'VULCAN_ID_EXACT', 'OFFERING_NAME_EXACT'
        review_status TEXT NOT NULL,    -- 'CONFIRMED', 'PROVISIONAL_REVIEW'
        properties_json TEXT
    );
    """)

    # 4. Epistemic Claim Ledger
    c.execute("""
    CREATE TABLE IF NOT EXISTS claim_ledger (
        claim_id TEXT PRIMARY KEY,
        subject_id TEXT NOT NULL,
        predicate TEXT NOT NULL,
        object_value TEXT NOT NULL,
        epistemic_status TEXT NOT NULL, -- 'VENDOR_SELF_ASSERTED', 'AFSIM_SIMULATED', 'LIVE_DEMONSTRATED', 'FPDS_OBLIGATED'
        confidence REAL NOT NULL,
        handling_level TEXT NOT NULL,   -- 'PUBLIC', 'CUI', 'COMMERCIAL_PROPRIETARY', 'PII_ENCRYPTED'
        evidence_id TEXT,
        notes TEXT
    );
    """)

    # 5. Multimodal Evidence Nodes
    c.execute("""
    CREATE TABLE IF NOT EXISTS evidence_nodes (
        evidence_id TEXT PRIMARY KEY,
        doc_id TEXT NOT NULL,
        standard_id TEXT NOT NULL,
        locator_type TEXT NOT NULL,     -- 'SPREADSHEET_CELL', 'TEXT_CHUNK', 'VISUAL_ASSET', 'API_RECEIPT'
        locator_str TEXT NOT NULL,      -- 'Sheet!R2C51', 'chunk_id', 'img.png'
        bbox_json TEXT,
        sha256 TEXT
    );
    """)

    # 6. SQLite FTS5 Virtual Tables for Scoped Hybrid Retrieval
    c.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS fts_org USING fts5(
        node_id UNINDEXED,
        name,
        cage,
        uei,
        city,
        state,
        contracts_summary,
        all_text
    );
    """)

    c.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS fts_tech USING fts5(
        node_id UNINDEXED,
        offering_name,
        topic_area,
        problem_statement,
        capabilities,
        advantages,
        integration,
        all_text
    );
    """)

    c.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS fts_crm USING fts5(
        node_id UNINDEXED,
        submission_id,
        vendor_name,
        poc_info,
        supply_constraints,
        funding_to_scale,
        unit_cost,
        security_preference,
        all_text
    );
    """)

    conn.commit()
    logger.info("Initialized SQLite database schema at %s", db_path)
    return conn


def build_tri_graph() -> None:
    """Loads parsed assets and projects them into SQLite and GraphML files."""
    conn = init_database(TRI_GRAPH_DB_PATH)
    c = conn.cursor()

    # Track sets for fast lookup
    nodes: Dict[str, Dict[str, Any]] = {}
    edges: List[Dict[str, Any]] = []
    links: List[Dict[str, Any]] = []
    claims: List[Dict[str, Any]] = []
    evidences: Dict[str, Dict[str, Any]] = {}

    def add_node(nid: str, domain: str, bfo: str, label: str, skos: List[str] = None, props: Dict[str, Any] = None):
        if nid not in nodes:
            nodes[nid] = {
                "id": nid,
                "graph_domain": domain,
                "bfo_category": bfo,
                "skos_concepts": json.dumps(skos or []),
                "label": label,
                "properties_json": json.dumps(props or {})
            }

    def add_edge(eid: str, src: str, tgt: str, etype: str, domain: str, props: Dict[str, Any] = None):
        edges.append({
            "edge_id": eid,
            "source_id": src,
            "target_id": tgt,
            "edge_type": etype,
            "graph_domain": domain,
            "properties_json": json.dumps(props or {})
        })

    def add_link(lid: str, src: str, sgraph: str, tgt: str, tgraph: str, pred: str, method: str, status: str = "CONFIRMED", props: Dict[str, Any] = None):
        links.append({
            "link_id": lid,
            "source_id": src,
            "source_graph": sgraph,
            "target_id": tgt,
            "target_graph": tgraph,
            "link_predicate": pred,
            "match_method": method,
            "review_status": status,
            "properties_json": json.dumps(props or {})
        })

    def add_claim(cid: str, sub: str, pred: str, val: str, status: str, conf: float, handling: str, evid: str = None, notes: str = None):
        claims.append({
            "claim_id": cid,
            "subject_id": sub,
            "predicate": pred,
            "object_value": val,
            "epistemic_status": status,
            "confidence": conf,
            "handling_level": handling,
            "evidence_id": evid,
            "notes": notes
        })

    def add_evidence(eid: str, doc_id: str, std_id: str, ltype: str, loc: str, bbox: Any = None, sha: str = None):
        if eid not in evidences:
            evidences[eid] = {
                "evidence_id": eid,
                "doc_id": doc_id,
                "standard_id": std_id,
                "locator_type": ltype,
                "locator_str": loc,
                "bbox_json": json.dumps(bbox) if bbox else None,
                "sha256": sha
            }

    # =========================================================================
    # 1. Ingest Vulcan Submissions (Albacore, Voltage Vessels, T2S Solutions)
    # =========================================================================
    logger.info("Ingesting Vulcan submissions from %s", VULCAN_PARSED_JSONL)
    vulcan_records = []
    if VULCAN_PARSED_JSONL.exists():
        with open(VULCAN_PARSED_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                vulcan_records.append(json.loads(line))

    for rec in vulcan_records:
        vid = str(rec["vulcan_id"])
        org_name = rec["organization_name"]
        offering_name = rec["offering_name"]
        cage = rec.get("cage")
        city = rec.get("city")
        state = rec.get("state")
        country = rec.get("country")
        org_subcat = rec.get("org_subcategory")

        # Normalize canonical IDs
        if "Albacore" in org_name:
            org_id = "org:albacore"
            tech_id = "tech:ghostfin_uuv"
            display_tech_name = "Ghostfin: Long-Range, Hybrid Electric Medium UUV"
            skos_tech = ["osra:UnmannedUnderwaterVehicles", "meia:CounterC5ISRT", "meia:CollaborativeAutonomy"]
        elif "Voltage" in org_name:
            org_id = "org:voltage_vessels"
            tech_id = "tech:voltvessel_energy"
            display_tech_name = "VoltVessel Maritime High-Density Energy Module"
            skos_tech = ["osra:PowerAndEnergyStorage", "meia:ContestedLogistics"]
        else:
            org_id = "org:t2s_solutions"
            tech_id = "tech:tactical_microgrid"
            display_tech_name = "Tactical Micro-Grid Hybrid Energy & Storage System"
            skos_tech = ["osra:PowerAndEnergyStorage", "meia:ExpeditionaryEnergy"]

        sub_id = f"crm:submission_{vid}"

        # Populate Evidence for each cell
        for cell in rec.get("cells", []):
            loc = cell["locator"]
            val = cell.get("value", "")
            col_idx = cell["col_index"]
            cell_eid = f"evid:vulcan_{vid}_c{col_idx}"
            add_evidence(cell_eid, "doc:vulcan_export_2026", "MEIA_TEM_Vulcan_Export", "SPREADSHEET_CELL", loc)

        # ---------------------------------------------------------------------
        # ORG-KG Nodes & Edges
        # ---------------------------------------------------------------------
        add_node(
            org_id, "ORG", "MaterialEntity",
            skos=["org:SmallBusiness", "org:DefenseIndustrialBase"],
            props={
                "name": org_name,
                "cage": cage,
                "city": city,
                "state": state,
                "country": country,
                "subcategory": org_subcat,
                "website": rec.get("website", "")
            },
            label=org_name
        )

        # Socioeconomic classification node
        class_id = f"org_class:{org_id.split(':')[1]}_subcat"
        add_node(
            class_id, "ORG", "InformationContentEntity",
            skos=["org:SocioeconomicDesignation"],
            props={"subcategory": org_subcat},
            label=f"{org_name} Classification: {org_subcat}"
        )
        add_edge(f"edge:{org_id}_{class_id}", org_id, class_id, "[:CLASSIFIED_UNDER]", "ORG")

        # ---------------------------------------------------------------------
        # TECH-KG Nodes & Edges
        # ---------------------------------------------------------------------
        trl = rec.get("trl") or "3"
        mrl = rec.get("mrl") or "3"
        irl = rec.get("irl") or "3"
        add_node(
            tech_id, "TECH", "MaterialEntity",
            skos=skos_tech,
            props={
                "offering_name": display_tech_name,
                "raw_offering_name": offering_name,
                "description": rec.get("description", ""),
                "differentiator": rec.get("differentiator", ""),
                "type": rec.get("type", "Hardware"),
                "trl": trl,
                "mrl": mrl,
                "irl": irl
            },
            label=display_tech_name
        )

        # Readiness Assessment Node
        readiness_id = f"eval:{tech_id.split(':')[1]}_readiness"
        add_node(
            readiness_id, "TECH", "InformationContentEntity",
            skos=["meia:ReadinessAssessment"],
            props={"trl": trl, "mrl": mrl, "irl": irl, "assessor": "VENDOR_SELF_ASSESSED", "q9_raw": rec.get("q9_technical_maturity")},
            label=f"Readiness: TRL-{trl} MRL-{mrl} IRL-{irl}"
        )
        add_edge(f"edge:{tech_id}_{readiness_id}", tech_id, readiness_id, "[:HAS_READINESS_ASSESSMENT]", "TECH")
        add_claim(f"claim:{readiness_id}_trl", tech_id, "has_readiness_trl", str(trl), "VENDOR_SELF_ASSERTED", 0.90, "CUI", f"evid:vulcan_{vid}_c59")

        # Joint Operational Problem (Q1)
        jop_text = rec.get("q1_problem_understanding")
        if jop_text:
            jop_id = f"tech:jop_{tech_id.split(':')[1]}"
            add_node(
                jop_id, "TECH", "InformationContentEntity",
                skos=["meia:JointOperationalProblem"],
                props={"description": jop_text},
                label=f"Operational Problem: {display_tech_name[:35]}"
            )
            add_edge(f"edge:{tech_id}_{jop_id}", tech_id, jop_id, "[:ADDRESSES_JOP]", "TECH")
            add_claim(f"claim:{jop_id}", tech_id, "addresses_operational_problem", jop_text[:200], "VENDOR_SELF_ASSERTED", 0.95, "CUI", f"evid:vulcan_{vid}_c51")

        # Specific Capability Claims for Albacore Ghostfin
        if "Albacore" in org_name:
            claims_def = [
                ("claim:ghostfin_range", "range_nmi", "1000 nautical miles", "VENDOR_SELF_ASSERTED", 0.95, "CUI", f"evid:vulcan_{vid}_c53"),
                ("claim:ghostfin_endurance", "mission_endurance", "30 days", "VENDOR_SELF_ASSERTED", 0.95, "CUI", f"evid:vulcan_{vid}_c51"),
                ("claim:ghostfin_payload", "payload_capacity_lbs", "250 lbs modular payload", "VENDOR_SELF_ASSERTED", 0.95, "CUI", f"evid:vulcan_{vid}_c53"),
                ("claim:ghostfin_portability", "carry_configuration", "4-man carryable", "VENDOR_SELF_ASSERTED", 0.90, "CUI", f"evid:vulcan_{vid}_c53"),
                ("claim:ghostfin_propulsion", "powertrain_type", "hybrid-electric powertrain", "VENDOR_SELF_ASSERTED", 0.98, "CUI", f"evid:vulcan_{vid}_c58"),
            ]
            for cid, pred, val, stat, conf, hand, evid in claims_def:
                claim_node_id = f"tech:{cid.split(':')[1]}"
                add_node(claim_node_id, "TECH", "InformationContentEntity", skos=["meia:CapabilityClaim"], props={"predicate": pred, "value": val}, label=val)
                add_edge(f"edge:{tech_id}_{claim_node_id}", tech_id, claim_node_id, "[:CLAIMS_CAPABILITY]", "TECH")
                add_claim(cid, tech_id, pred, val, stat, conf, hand, evid)

            # Demonstration Events (Live Field Exercises vs Simulation)
            demos = [
                ("demo:sonic_spear_26", "SONIC SPEAR 26 Exercise", "LIVE_DEMONSTRATED", "Live demonstration at SONIC SPEAR 26 maritime exercise", f"evid:vulcan_{vid}_c60"),
                ("demo:silent_swarm_26", "Silent Swarm 2026", "LIVE_DEMONSTRATED", "Slated for participation at Silent Swarm multi-domain collaborative autonomy", f"evid:vulcan_{vid}_c60"),
                ("demo:repmus_26", "NATO REPMUS / Maritime Big Play", "LIVE_DEMONSTRATED", "Scheduled for NATO operational experimentation at REPMUS", f"evid:vulcan_{vid}_c60"),
                ("demo:nswc_pc_purchase", "NSWC Panama City T&E", "LIVE_DEMONSTRATED", "Purchased by Naval Surface Warfare Center Panama City for test and evaluation", f"evid:vulcan_{vid}_c60"),
                ("demo:afsim_ghostfin", "AFSIM Engagement Simulation Model", "AFSIM_SIMULATED", "Constructive simulation model available for mission analysis in AFSIM", f"evid:vulcan_{vid}_c60")
            ]
            for did, dname, dstat, ddesc, devid in demos:
                add_node(did, "TECH", "Process", skos=["meia:DemonstrationEvent"], props={"event_name": dname, "epistemic_status": dstat, "description": ddesc}, label=dname)
                add_edge(f"edge:{tech_id}_{did}", tech_id, did, "[:PARTICIPATED_IN_DEMO]", "TECH", props={"epistemic_status": dstat})
                add_claim(f"claim:{did}", tech_id, "participated_in_exercise", dname, dstat, 0.99 if dstat == "LIVE_DEMONSTRATED" else 0.85, "CUI", devid, ddesc)

        # ---------------------------------------------------------------------
        # CRM-GRAPH Nodes & Edges
        # ---------------------------------------------------------------------
        stage_name = "Triaged" if "Albacore" in org_name else ("SME Review" if "T2S" in org_name else "Submitted")
        add_node(
            sub_id, "CRM", "InformationContentEntity",
            skos=["twenty_crm:CapabilitySubmission"],
            props={
                "vulcan_id": vid,
                "submission_link": rec.get("vulcan_link", ""),
                "current_pipeline_stage": stage_name,
                "security_preference": rec.get("q12_security_preference", "SECRET // REL FVEY"),
                "sla_status": "WITHIN_48H_TRIAGE"
            },
            label=f"Vulcan Submission #{vid} ({org_name})"
        )

        stage_id = f"crm:stage_{stage_name.lower().replace(' ', '_')}"
        add_node(stage_id, "CRM", "InformationContentEntity", skos=["twenty_crm:PipelineStage"], props={"stage": stage_name}, label=f"Stage: {stage_name}")
        add_edge(f"edge:{sub_id}_{stage_id}", sub_id, stage_id, "[:IN_PIPELINE_STAGE]", "CRM")

        # Contact POC (Technical POC Cameron Matthews for Albacore)
        if "Albacore" in org_name:
            poc_id = "crm:poc_cameron_matthews"
            add_node(
                poc_id, "CRM", "Role",
                skos=["twenty_crm:Person"],
                props={
                    "name": "Cameron Matthews",
                    "role_type": "Technical 1 POC",
                    "email_encrypted": "cameron.a.matthews.civ@us.navy.mil",
                    "phone_encrypted": "18508675230"
                },
                label="Technical POC: Cameron Matthews (US Navy Civ)"
            )
            add_edge(f"edge:{sub_id}_{poc_id}", sub_id, poc_id, "[:DESIGNATES_CONTACT]", "CRM")
            add_claim(f"claim:{poc_id}_assignment", sub_id, "designated_technical_poc", "Cameron Matthews", "VENDOR_SELF_ASSERTED", 0.99, "PII_ENCRYPTED", f"evid:vulcan_{vid}_c39")

        # Commercial Observations (Q4, Q5, Q6)
        comm_obs = [
            ("q4_supply_constraints", rec.get("q4_supply_constraints"), "COMMERCIAL_PROPRIETARY", f"evid:vulcan_{vid}_c54"),
            ("q5_funding_to_scale", rec.get("q5_funding_to_scale"), "COMMERCIAL_PROPRIETARY", f"evid:vulcan_{vid}_c55"),
            ("q6_unit_cost", rec.get("q6_unit_cost"), "COMMERCIAL_PROPRIETARY", f"evid:vulcan_{vid}_c56"),
            ("q12_security_preference", rec.get("q12_security_preference"), "COMMERCIAL_PROPRIETARY", f"evid:vulcan_{vid}_c62"),
        ]
        for field_name, field_val, hand, evid in comm_obs:
            if field_val:
                obs_id = f"crm:obs_{vid}_{field_name}"
                add_node(
                    obs_id, "CRM", "InformationContentEntity",
                    skos=["twenty_crm:CommercialObservation"],
                    props={"observation_field": field_name, "value": field_val},
                    label=f"Commercial Obs ({field_name}): {field_val[:30]}"
                )
                add_edge(f"edge:{sub_id}_{obs_id}", sub_id, obs_id, "[:HAS_COMMERCIAL_OBSERVATION]", "CRM")
                add_claim(f"claim:{obs_id}", sub_id, field_name, field_val, "VENDOR_SELF_ASSERTED", 0.95, hand, evid)

        # ---------------------------------------------------------------------
        # Cross-Graph Links
        # ---------------------------------------------------------------------
        add_link(f"link:{org_id}_{tech_id}", org_id, "ORG", tech_id, "TECH", "[:DEVELOPS_OFFERING]", "CAGE_EXACT" if cage else "VULCAN_ROW")
        add_link(f"link:{sub_id}_{org_id}", sub_id, "CRM", org_id, "ORG", "[:SUBMITTED_BY_ORG]", "VULCAN_ID_EXACT")
        add_link(f"link:{sub_id}_{tech_id}", sub_id, "CRM", tech_id, "TECH", "[:EVALUATES_OFFERING]", "VULCAN_ID_EXACT")

    # =========================================================================
    # 2. Ingest USASpending Federal History & Awards
    # =========================================================================
    logger.info("Ingesting USASpending awards from %s", USASPENDING_PARSED_JSONL)
    usa_records = []
    if USASPENDING_PARSED_JSONL.exists():
        with open(USASPENDING_PARSED_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                usa_records.append(json.loads(line))

    for rec in usa_records:
        uei = rec.get("uei")
        vendor_name = rec.get("vendor_name")
        parent_uei = rec.get("parent_uei")
        parent_name = rec.get("parent_name")
        cage = rec.get("cage")
        tot_spending = rec.get("total_obligated_amount", 0.0)
        contract_count = rec.get("contract_count", 0)

        # Map to Canonical ORG node ID
        if uei == "NZ9CUMF36PK1":
            org_id = "org:fluor_federal"
            label = "Fluor Federal Services Inc."
        elif uei == "KQ28QJU21GY3":
            org_id = "org:klas_gov"
            label = "Klas Government Inc."
        elif uei == "J767K9B843S5":
            org_id = "org:prometheus_intelligence"
            label = "Prometheus Intelligence Technology LLC"
        elif uei == "PW8DT7RK5261":
            org_id = "org:prometheus_intelligence_inc"
            label = "Prometheus Intelligence, Inc."
        else:
            org_id = f"org:uei_{uei.lower()}"
            label = vendor_name

        add_node(
            org_id, "ORG", "MaterialEntity",
            skos=["org:FederalPrimeContractor", "org:DefenseIndustrialBase"],
            props={
                "name": label,
                "uei": uei,
                "cage": cage,
                "parent_uei": parent_uei,
                "parent_name": parent_name,
                "total_obligated_spending": tot_spending,
                "contract_count": contract_count
            },
            label=label
        )

        # Parent corporate lineage
        if parent_name or uei == "NZ9CUMF36PK1":
            parent_id = "org:fluor_corp" if uei == "NZ9CUMF36PK1" else f"org:parent_{parent_uei.lower()}"
            add_node(
                parent_id, "ORG", "MaterialEntity",
                skos=["org:ParentCorporation"],
                props={"name": parent_name or "Fluor Corporation", "uei": parent_uei},
                label=parent_name or "Fluor Corporation"
            )
            add_edge(f"edge:{org_id}_{parent_id}", org_id, parent_id, "[:SUBSIDIARY_OF]", "ORG")

        # Contract awards
        for c_idx, contract in enumerate(rec.get("contracts", [])):
            award_id = contract.get("award_id")
            if not award_id:
                continue
            amt = contract.get("amount") or 0.0
            agency = contract.get("agency") or ""
            desc = contract.get("description") or ""

            award_node_id = f"award:{award_id.replace('-', '_').replace(':', '_').lower()}"
            add_node(
                award_node_id, "ORG", "InformationContentEntity",
                skos=["org:ContractAward", "org:FPDSPrimeAward"],
                props={
                    "award_id": award_id,
                    "awarding_agency": agency,
                    "award_amount": amt,
                    "description": desc,
                    "start_date": contract.get("start_date"),
                    "end_date": contract.get("end_date")
                },
                label=f"Contract {award_id} (${float(amt):,.2f})"
            )
            add_edge(f"edge:{org_id}_{award_node_id}", org_id, award_node_id, "[:HOLDS_PRIME_AWARD]", "ORG")
            add_claim(f"claim:{award_node_id}_obligation", org_id, "holds_federal_obligation", f"${float(amt):,.2f} ({agency})", "FPDS_OBLIGATED", 1.0, "PUBLIC", "api:usaspending_vendor_history_2026")

            # Link Prometheus award to Tech-KG
            if award_id == "697DCK-24-C-00237":
                prom_tech_id = "tech:prometheus_energy_ai"
                add_node(
                    prom_tech_id, "TECH", "MaterialEntity",
                    skos=["osra:ArtificialIntelligence", "meia:OperationalEnergy"],
                    props={
                        "offering_name": "Prometheus Spatial Energy Optimization Engine",
                        "description": "Virtual spatial energy intelligence and dynamic power management for mission continuity",
                        "regulatory_application": "Federal Aviation Administration (FAA) Air Traffic Management Facility Energy Continuity"
                    },
                    label="Prometheus Spatial Energy Optimization Engine"
                )
                add_link(f"link:{org_id}_{prom_tech_id}", org_id, "ORG", prom_tech_id, "TECH", "[:DEVELOPS_OFFERING]", "UEI_EXACT")
                add_link(f"link:{prom_tech_id}_{award_node_id}", prom_tech_id, "TECH", award_node_id, "ORG", "[:VALIDATED_BY_CONTRACT]", "AWARD_ID_EXACT")

        # Klas Government Tech Offering
        if uei == "KQ28QJU21GY3":
            klas_tech_id = "tech:klas_voyager"
            add_node(
                klas_tech_id, "TECH", "MaterialEntity",
                skos=["osra:TacticalCommunications", "meia:C5ISRT"],
                props={
                    "offering_name": "Klas Voyager Modular Tactical Communications",
                    "description": "Rugged, low-SWaP modular compute and networking platform for tactical edge communications and C5ISR"
                },
                label="Klas Voyager Modular Tactical Communications"
            )
            add_link(f"link:{org_id}_{klas_tech_id}", org_id, "ORG", klas_tech_id, "TECH", "[:DEVELOPS_OFFERING]", "UEI_EXACT")

    # =========================================================================
    # 3. Ingest Semantic Text Chunks as Evidence Nodes
    # =========================================================================
    logger.info("Ingesting semantic text chunks from %s", TEXT_CHUNKS_JSONL)
    chunk_records = []
    if TEXT_CHUNKS_JSONL.exists():
        with open(TEXT_CHUNKS_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                chunk_records.append(json.loads(line))

    for ch in chunk_records:
        cid = ch["chunk_id"]
        doc_id = ch["doc_id"]
        std_id = ch["standard_id"]
        page_ord = ch["page_ordinal"]
        t_graph = ch["target_graph"]
        add_evidence(f"evid:{cid}", doc_id, std_id, "TEXT_CHUNK", f"{std_id} p.{page_ord}")

    # =========================================================================
    # 4. Ingest Rendered Visual Assets & BBox Chips
    # =========================================================================
    logger.info("Ingesting visual figures and bounding box chips from %s", FIGURE_BBOXES_JSON)
    if FIGURE_BBOXES_JSON.exists():
        with open(FIGURE_BBOXES_JSON, "r", encoding="utf-8") as f:
            bbox_data = json.load(f)
            for fname, fmeta in bbox_data.get("figures", {}).items():
                fig_eid = f"evid:fig_{fname.replace('.', '_')}"
                add_evidence(fig_eid, fmeta["doc_id"], fmeta["standard_id"], "VISUAL_ASSET", fmeta["image_relpath"])

    # =========================================================================
    # 5. Commit to SQLite Database
    # =========================================================================
    logger.info("Writing %d domain nodes, %d domain edges, %d cross-graph links, %d claims, %d evidence records",
                len(nodes), len(edges), len(links), len(claims), len(evidences))

    c.executemany("""
    INSERT OR REPLACE INTO domain_nodes (id, graph_domain, bfo_category, skos_concepts, label, properties_json)
    VALUES (:id, :graph_domain, :bfo_category, :skos_concepts, :label, :properties_json);
    """, list(nodes.values()))

    c.executemany("""
    INSERT OR REPLACE INTO domain_edges (edge_id, source_id, target_id, edge_type, graph_domain, properties_json)
    VALUES (:edge_id, :source_id, :target_id, :edge_type, :graph_domain, :properties_json);
    """, edges)

    c.executemany("""
    INSERT OR REPLACE INTO cross_graph_links (link_id, source_id, source_graph, target_id, target_graph, link_predicate, match_method, review_status, properties_json)
    VALUES (:link_id, :source_id, :source_graph, :target_id, :target_graph, :link_predicate, :match_method, :review_status, :properties_json);
    """, links)

    c.executemany("""
    INSERT OR REPLACE INTO claim_ledger (claim_id, subject_id, predicate, object_value, epistemic_status, confidence, handling_level, evidence_id, notes)
    VALUES (:claim_id, :subject_id, :predicate, :object_value, :epistemic_status, :confidence, :handling_level, :evidence_id, :notes);
    """, claims)

    c.executemany("""
    INSERT OR REPLACE INTO evidence_nodes (evidence_id, doc_id, standard_id, locator_type, locator_str, bbox_json, sha256)
    VALUES (:evidence_id, :doc_id, :standard_id, :locator_type, :locator_str, :bbox_json, :sha256);
    """, list(evidences.values()))

    # =========================================================================
    # 6. Populate FTS5 Full-Text Tables
    # =========================================================================
    logger.info("Populating SQLite FTS5 full-text indices")
    c.execute("DELETE FROM fts_org;")
    c.execute("DELETE FROM fts_tech;")
    c.execute("DELETE FROM fts_crm;")

    # Populate fts_org
    for n in nodes.values():
        if n["graph_domain"] == "ORG":
            props = json.loads(n["properties_json"])
            all_txt = f"{n['label']} {props.get('cage', '')} {props.get('uei', '')} {props.get('city', '')} {props.get('state', '')} {props.get('description', '')}"
            c.execute("""
            INSERT INTO fts_org (node_id, name, cage, uei, city, state, contracts_summary, all_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                n["id"],
                props.get("name", n["label"]),
                props.get("cage", ""),
                props.get("uei", ""),
                props.get("city", ""),
                props.get("state", ""),
                str(props.get("total_obligated_spending", "")),
                all_txt
            ))

    # Populate fts_tech
    for n in nodes.values():
        if n["graph_domain"] == "TECH":
            props = json.loads(n["properties_json"])
            all_txt = f"{n['label']} {props.get('offering_name', '')} {props.get('description', '')} {props.get('differentiator', '')} {n.get('skos_concepts', '')}"
            c.execute("""
            INSERT INTO fts_tech (node_id, offering_name, topic_area, problem_statement, capabilities, advantages, integration, all_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                n["id"],
                props.get("offering_name", n["label"]),
                props.get("type", ""),
                props.get("description", ""),
                props.get("differentiator", ""),
                props.get("q8_competitive_advantage", ""),
                props.get("trl", ""),
                all_txt
            ))

    # Populate fts_crm
    for n in nodes.values():
        if n["graph_domain"] == "CRM":
            props = json.loads(n["properties_json"])
            all_txt = f"{n['label']} {props.get('vulcan_id', '')} {props.get('security_preference', '')} {props.get('value', '')}"
            c.execute("""
            INSERT INTO fts_crm (node_id, submission_id, vendor_name, poc_info, supply_constraints, funding_to_scale, unit_cost, security_preference, all_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                n["id"],
                props.get("vulcan_id", ""),
                n["label"],
                props.get("name", ""),
                props.get("observation_field", ""),
                props.get("value", ""),
                "",
                props.get("security_preference", ""),
                all_txt
            ))

    conn.commit()

    # =========================================================================
    # 7. Export Standalone GraphML Substrates
    # =========================================================================
    logger.info("Exporting NetworkX GraphML substrates")
    export_graphml_substrates(nodes, edges, links, evidences)

    conn.close()
    logger.info("Tri-Graph SQLite and GraphML construction completed successfully!")


def export_graphml_substrates(nodes: Dict[str, Dict[str, Any]], edges: List[Dict[str, Any]], links: List[Dict[str, Any]], evidences: Dict[str, Dict[str, Any]]) -> None:
    """Exports standalone org_kg, tech_kg, crm_graph, and federated_epistemic_graph GraphML files."""
    g_org = nx.MultiDiGraph(name="MEIA Organization Graph")
    g_tech = nx.MultiDiGraph(name="MEIA Technology Graph")
    g_crm = nx.MultiDiGraph(name="MEIA CRM Graph")
    g_fed = nx.MultiDiGraph(name="MEIA Federated Epistemic Graph")

    # Add domain nodes
    for nid, nd in nodes.items():
        props = {
            "label": nd["label"],
            "graph_domain": nd["graph_domain"],
            "bfo_category": nd["bfo_category"],
            "skos_concepts": nd["skos_concepts"]
        }
        domain = nd["graph_domain"]
        if domain == "ORG":
            g_org.add_node(nid, **props)
        elif domain == "TECH":
            g_tech.add_node(nid, **props)
        elif domain == "CRM":
            g_crm.add_node(nid, **props)
        g_fed.add_node(nid, **props)

    # Add domain edges
    for ed in edges:
        src, tgt = ed["source_id"], ed["target_id"]
        domain = ed["graph_domain"]
        edge_attrs = {"edge_type": ed["edge_type"], "edge_id": ed["edge_id"]}
        if domain == "ORG" and src in g_org and tgt in g_org:
            g_org.add_edge(src, tgt, **edge_attrs)
        elif domain == "TECH" and src in g_tech and tgt in g_tech:
            g_tech.add_edge(src, tgt, **edge_attrs)
        elif domain == "CRM" and src in g_crm and tgt in g_crm:
            g_crm.add_edge(src, tgt, **edge_attrs)
        if src in g_fed and tgt in g_fed:
            g_fed.add_edge(src, tgt, **edge_attrs)

    # Add cross-graph links to federated graph
    for lk in links:
        src, tgt = lk["source_id"], lk["target_id"]
        if src in g_fed and tgt in g_fed:
            g_fed.add_edge(src, tgt, edge_type=lk["link_predicate"], link_id=lk["link_id"], match_method=lk["match_method"])

    # Add sample evidence nodes to federated graph (top 50)
    for eid, ev in list(evidences.items())[:50]:
        g_fed.add_node(eid, label=ev["locator_str"], graph_domain="EVIDENCE", locator_type=ev["locator_type"])

    nx.write_graphml(g_org, str(ORG_GRAPHML_PATH))
    nx.write_graphml(g_tech, str(TECH_GRAPHML_PATH))
    nx.write_graphml(g_crm, str(CRM_GRAPHML_PATH))
    nx.write_graphml(g_fed, str(FEDERATED_GRAPHML_PATH))

    logger.info("Saved Org-KG GraphML (%d nodes, %d edges) to %s", g_org.number_of_nodes(), g_org.number_of_edges(), ORG_GRAPHML_PATH)
    logger.info("Saved Tech-KG GraphML (%d nodes, %d edges) to %s", g_tech.number_of_nodes(), g_tech.number_of_edges(), TECH_GRAPHML_PATH)
    logger.info("Saved CRM-Graph GraphML (%d nodes, %d edges) to %s", g_crm.number_of_nodes(), g_crm.number_of_edges(), CRM_GRAPHML_PATH)
    logger.info("Saved Federated GraphML (%d nodes, %d edges) to %s", g_fed.number_of_nodes(), g_fed.number_of_edges(), FEDERATED_GRAPHML_PATH)


if __name__ == "__main__":
    build_tri_graph()
