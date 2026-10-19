"""MEIA Ontology & Semantic Graph Service (Phase 1 Semantic Enrichment).

Provides formal OWL 2 DL class hierarchies, W3C SKOS taxonomy indexing with
recursive broader/narrower transitive querying, object property inverse
resolution, and RDF Turtle (W3C Linked Data) graph serialization.
"""
from __future__ import annotations

import json
import logging
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import rdflib
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config import STORAGE_DIR, TRI_GRAPH_DB_PATH

logger = logging.getLogger("ontology_service")

# W3C and Domain Namespaces
BFO = Namespace("http://purl.obolibrary.org/obo/bfo.owl#")
IAO = Namespace("http://purl.obolibrary.org/obo/iao.owl#")
MEIA = Namespace("https://meia.mil/ontology#")
OSRA = Namespace("https://eda.europa.eu/osra#")
TWENTY_CRM = Namespace("https://twenty.com/crm#")
MEIA_DATA = Namespace("https://meia.mil/data/")

ONTOLOGY_FILE = REPO_ROOT / "ontology" / "meia_ontology.ttl"
TURTLE_EXPORT_PATH = STORAGE_DIR / "meia_federated_tri_graph.ttl"

# Canonical Inverse Property Mappings
INVERSE_PREDICATE_MAP: Dict[str, str] = {
    # Intra-domain predicates
    "[:CLASSIFIED_UNDER]": "[:CLASSIFIES_ENTITY]",
    "[:CLASSIFIES_ENTITY]": "[:CLASSIFIED_UNDER]",
    "[:HAS_READINESS_ASSESSMENT]": "[:ASSESSES_READINESS_OF]",
    "[:ASSESSES_READINESS_OF]": "[:HAS_READINESS_ASSESSMENT]",
    "[:ADDRESSES_JOP]": "[:ADDRESSED_BY_OFFERING]",
    "[:ADDRESSED_BY_OFFERING]": "[:ADDRESSES_JOP]",
    "[:CLAIMS_CAPABILITY]": "[:CLAIMED_BY_OFFERING]",
    "[:CLAIMED_BY_OFFERING]": "[:CLAIMS_CAPABILITY]",
    "[:PARTICIPATED_IN_DEMO]": "[:FEATURED_CAPABILITY]",
    "[:FEATURED_CAPABILITY]": "[:PARTICIPATED_IN_DEMO]",
    "[:IN_PIPELINE_STAGE]": "[:CONTAINS_SUBMISSION]",
    "[:CONTAINS_SUBMISSION]": "[:IN_PIPELINE_STAGE]",
    "[:DESIGNATES_CONTACT]": "[:CONTACT_FOR]",
    "[:CONTACT_FOR]": "[:DESIGNATES_CONTACT]",
    "[:HAS_COMMERCIAL_OBSERVATION]": "[:OBSERVATION_FOR]",
    "[:OBSERVATION_FOR]": "[:HAS_COMMERCIAL_OBSERVATION]",
    "[:SUBSIDIARY_OF]": "[:PARENT_OF]",
    "[:PARENT_OF]": "[:SUBSIDIARY_OF]",
    "[:HOLDS_PRIME_AWARD]": "[:AWARDED_TO_ORG]",
    "[:AWARDED_TO_ORG]": "[:HOLDS_PRIME_AWARD]",

    # Cross-graph spine links
    "[:DEVELOPS_OFFERING]": "[:DEVELOPED_BY]",
    "[:DEVELOPED_BY]": "[:DEVELOPS_OFFERING]",
    "[:SUBMITTED_BY_ORG]": "[:SUBMITTED_OFFERING]",
    "[:SUBMITTED_OFFERING]": "[:SUBMITTED_BY_ORG]",
    "[:EVALUATES_OFFERING]": "[:EVALUATED_BY]",
    "[:EVALUATED_BY]": "[:EVALUATES_OFFERING]",
    "[:VALIDATED_BY_CONTRACT]": "[:VALIDATES_CAPABILITY]",
    "[:VALIDATES_CAPABILITY]": "[:VALIDATED_BY_CONTRACT]",
}

# Standard SKOS Controlled Vocabularies
STANDARD_SKOS_TAXONOMY = [
    # OSRA (EDA Overarching Strategic Research Agenda)
    {
        "concept_uri": "osra:DefenseTechnologies",
        "pref_label": "EDA OSRA Defense Technologies",
        "alt_labels": ["OSRA", "Defense Tech Building Blocks"],
        "broader_uri": None,
        "scheme": "OSRA",
        "scope_note": "Top-level root for European Defence Agency Overarching Strategic Research Agenda technologies."
    },
    {
        "concept_uri": "osra:UnmannedUnderwaterVehicles",
        "pref_label": "Unmanned Underwater Vehicles",
        "alt_labels": ["UUV", "sUUV", "mUUV", "TBB-29"],
        "broader_uri": "osra:DefenseTechnologies",
        "scheme": "OSRA",
        "scope_note": "TBB-29 technology building block for autonomous undersea and submersible platforms."
    },
    {
        "concept_uri": "osra:CounterUAS",
        "pref_label": "Counter Unmanned Aerial Systems",
        "alt_labels": ["C-UAS", "CUAS", "TBB-32"],
        "broader_uri": "osra:DefenseTechnologies",
        "scheme": "OSRA",
        "scope_note": "TBB-32 kinetic and non-kinetic defeat capabilities against uncrewed aerial systems."
    },
    {
        "concept_uri": "osra:TacticalCommunications",
        "pref_label": "Tactical Communications & Networking",
        "alt_labels": ["C5ISR", "C5ISRT", "Tactical Edge Compute"],
        "broader_uri": "osra:DefenseTechnologies",
        "scheme": "OSRA",
        "scope_note": "Rugged, low-SWaP communications, compute, and radio networking for contested tactical edge."
    },
    {
        "concept_uri": "osra:PowerAndEnergyStorage",
        "pref_label": "Power and Energy Storage",
        "alt_labels": ["Hybrid Powertrain", "Micro-Grid", "Battery Energy Storage"],
        "broader_uri": "osra:DefenseTechnologies",
        "scheme": "OSRA",
        "scope_note": "High-density maritime and expeditionary energy modules, microgrids, and hybrid propulsion."
    },
    {
        "concept_uri": "osra:ArtificialIntelligence",
        "pref_label": "Artificial Intelligence & Edge Autonomy",
        "alt_labels": ["AI", "Edge Orchestration", "Spatial Optimization Engine"],
        "broader_uri": "osra:DefenseTechnologies",
        "scheme": "OSRA",
        "scope_note": "Intelligent edge computing, dynamic power routing, and mission scheduling algorithms."
    },

    # MEIA Mission Focus Areas
    {
        "concept_uri": "meia:JointMissionCapabilities",
        "pref_label": "MEIA Joint Warfighter Mission Capabilities",
        "alt_labels": ["MEIA Capabilities", "Joint Force Missions"],
        "broader_uri": None,
        "scheme": "MEIA",
        "scope_note": "Mission capabilities aligned with Joint Requirements and MEIA innovation topics."
    },
    {
        "concept_uri": "meia:CounterC5ISRT",
        "pref_label": "Counter-C5ISRT & Undersea Asymmetric Dominance",
        "alt_labels": ["Undersea Distance Gap", "C5ISRT Countermeasures"],
        "broader_uri": "meia:JointMissionCapabilities",
        "scheme": "MEIA",
        "scope_note": "Disrupting adversary sensing while maintaining persistent friendly undersea reconnaissance."
    },
    {
        "concept_uri": "meia:CollaborativeAutonomy",
        "pref_label": "Collaborative Autonomy & Multi-Domain Swarming",
        "alt_labels": ["Silent Swarm", "Swarm Coordination"],
        "broader_uri": "meia:JointMissionCapabilities",
        "scheme": "MEIA",
        "scope_note": "Coordinated multi-agent autonomous operations across maritime, air, and ground domains."
    },
    {
        "concept_uri": "meia:ContestedLogistics",
        "pref_label": "Contested Logistics & Forward Expeditionary Sustainment",
        "alt_labels": ["Austere Logistics", "Forward Additive Manufacturing"],
        "broader_uri": "meia:JointMissionCapabilities",
        "scheme": "MEIA",
        "scope_note": "Point-of-need fabrication, spare parts regeneration, and resilient supply lines."
    },
    {
        "concept_uri": "meia:ExpeditionaryEnergy",
        "pref_label": "Expeditionary Power & Tactical Microgrids",
        "alt_labels": ["Tactical Energy", "Field Grid"],
        "broader_uri": "meia:JointMissionCapabilities",
        "scheme": "MEIA",
        "scope_note": "Micro-grid deployment in austere forward bases and island-chain operating locations."
    },
    {
        "concept_uri": "meia:OperationalEnergy",
        "pref_label": "Operational Energy & Infrastructure Resilience",
        "alt_labels": ["Continuity Energy", "Mission Critical Power"],
        "broader_uri": "meia:JointMissionCapabilities",
        "scheme": "MEIA",
        "scope_note": "Multi-year lifecycle power systems for nuclear fleet logistics and federal facilities."
    },

    # Twenty CRM Intake & Governance
    {
        "concept_uri": "twenty_crm:IntakeWorkflow",
        "pref_label": "Twenty CRM Intake & Pipeline Governance",
        "alt_labels": ["CRM Pipeline", "Vendor Intake"],
        "broader_uri": None,
        "scheme": "TWENTY_CRM",
        "scope_note": "Workflow management for capability submissions, triage stages, and commercial vetting."
    },
    {
        "concept_uri": "twenty_crm:CapabilitySubmission",
        "pref_label": "Vendor Capability Submission",
        "alt_labels": ["Vulcan Submission", "Portal Intake Record"],
        "broader_uri": "twenty_crm:IntakeWorkflow",
        "scheme": "TWENTY_CRM",
        "scope_note": "Initial technology offering profile submitted by a commercial or academic vendor."
    },
    {
        "concept_uri": "twenty_crm:PipelineStage",
        "pref_label": "Pipeline Evaluation Stage",
        "alt_labels": ["Triage Stage", "SME Review", "SLA Stage"],
        "broader_uri": "twenty_crm:IntakeWorkflow",
        "scheme": "TWENTY_CRM",
        "scope_note": "Milestone stage in the 48-hour SLA review pipeline (Submitted, Triaged, SME Review)."
    },
    {
        "concept_uri": "twenty_crm:CommercialObservation",
        "pref_label": "Commercial & Production Scalability Observation",
        "alt_labels": ["ROM Funding", "Unit Cost", "Supply Chain Risk"],
        "broader_uri": "twenty_crm:IntakeWorkflow",
        "scheme": "TWENTY_CRM",
        "scope_note": "Commercial parameters governing unit economics and production scaling requirements."
    },

    # Federal Procurement & Organizational Classification
    {
        "concept_uri": "org:IndustrialClassifications",
        "pref_label": "Federal Industrial & Procurement Classifications",
        "alt_labels": ["DIB Taxonomy", "Vendor Types"],
        "broader_uri": None,
        "scheme": "ORG",
        "scope_note": "Federal taxonomy governing vendor corporate structure, certifications, and awards."
    },
    {
        "concept_uri": "org:DefenseIndustrialBase",
        "pref_label": "Defense Industrial Base Entity",
        "alt_labels": ["DIB Entity", "Defense Contractor"],
        "broader_uri": "org:IndustrialClassifications",
        "scheme": "ORG",
        "scope_note": "Entities developing, manufacturing, or supplying defense products and services."
    },
    {
        "concept_uri": "org:FederalPrimeContractor",
        "pref_label": "Federal Prime Contractor",
        "alt_labels": ["Prime Vendor", "FPDS Prime Awardee"],
        "broader_uri": "org:IndustrialClassifications",
        "scheme": "ORG",
        "scope_note": "Organizations holding direct prime contract obligations from federal departments."
    },
    {
        "concept_uri": "org:SmallBusiness",
        "pref_label": "Small Business Concern",
        "alt_labels": ["SBA Small Business", "Commercial Startup"],
        "broader_uri": "org:IndustrialClassifications",
        "scheme": "ORG",
        "scope_note": "Small business innovation entities qualifying under federal NAICS size thresholds."
    },
    {
        "concept_uri": "org:SocioeconomicDesignation",
        "pref_label": "Socioeconomic Business Designation",
        "alt_labels": ["SDVOSB", "WOSB", "HUBZone", "8(a)"],
        "broader_uri": "org:IndustrialClassifications",
        "scheme": "ORG",
        "scope_note": "Designations reflecting veteran, minority, or economically disadvantaged ownership."
    },
]


class OntologyService:
    """Manages formal OWL 2 ontology definitions, SKOS taxonomies, and RDF serialization."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or TRI_GRAPH_DB_PATH
        self.ontology_file = ONTOLOGY_FILE
        self._cached_graph: Optional[Graph] = None

    def initialize_skos_schema(self, conn: sqlite3.Connection) -> None:
        """Creates the skos_taxonomy table and populates standard defense concepts."""
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS skos_taxonomy (
            concept_uri TEXT PRIMARY KEY,
            pref_label TEXT NOT NULL,
            alt_labels_json TEXT,          -- JSON list of strings (acronyms, synonyms)
            broader_uri TEXT,              -- Self-referencing FK to skos_taxonomy(concept_uri)
            scheme TEXT NOT NULL,          -- 'OSRA', 'MEIA', 'TWENTY_CRM', 'ORG', 'DEFENSE'
            scope_note TEXT,
            FOREIGN KEY(broader_uri) REFERENCES skos_taxonomy(concept_uri)
        );
        """)

        # Insert or replace standard concepts
        for item in STANDARD_SKOS_TAXONOMY:
            c.execute("""
            INSERT OR REPLACE INTO skos_taxonomy (concept_uri, pref_label, alt_labels_json, broader_uri, scheme, scope_note)
            VALUES (?, ?, ?, ?, ?, ?);
            """, (
                item["concept_uri"],
                item["pref_label"],
                json.dumps(item.get("alt_labels", [])),
                item.get("broader_uri"),
                item["scheme"],
                item.get("scope_note", "")
            ))
        conn.commit()
        logger.info("Initialized and populated skos_taxonomy with %d concepts", len(STANDARD_SKOS_TAXONOMY))

    def get_inverse_predicate(self, predicate: str) -> Optional[str]:
        """Returns the declared inverse predicate for an edge or link."""
        return INVERSE_PREDICATE_MAP.get(predicate)

    def get_narrower_concepts(self, parent_uri: str) -> List[Dict[str, Any]]:
        """Transitively fetches all narrower descendant concepts using a recursive SQL CTE."""
        if not self.db_path.exists():
            return []
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        sql = """
        WITH RECURSIVE concept_tree AS (
            SELECT concept_uri, pref_label, alt_labels_json, broader_uri, scheme, scope_note, 1 as depth
            FROM skos_taxonomy
            WHERE broader_uri = ?
            UNION ALL
            SELECT s.concept_uri, s.pref_label, s.alt_labels_json, s.broader_uri, s.scheme, s.scope_note, ct.depth + 1
            FROM skos_taxonomy s
            JOIN concept_tree ct ON s.broader_uri = ct.concept_uri
        )
        SELECT concept_uri, pref_label, alt_labels_json, broader_uri, scheme, scope_note, depth
        FROM concept_tree
        ORDER BY depth, pref_label;
        """
        c.execute(sql, (parent_uri,))
        results = []
        for row in c.fetchall():
            curi, plab, alabs, buri, sch, snote, depth = row
            results.append({
                "concept_uri": curi,
                "pref_label": plab,
                "alt_labels": json.loads(alabs or "[]"),
                "broader_uri": buri,
                "scheme": sch,
                "scope_note": snote,
                "depth": depth
            })
        conn.close()
        return results

    def get_broader_concepts(self, child_uri: str) -> List[Dict[str, Any]]:
        """Transitively fetches all broader ancestor concepts up to the taxonomy root."""
        if not self.db_path.exists():
            return []
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        sql = """
        WITH RECURSIVE ancestor_tree AS (
            SELECT s.concept_uri, s.pref_label, s.alt_labels_json, s.broader_uri, s.scheme, s.scope_note, 1 as depth
            FROM skos_taxonomy s
            JOIN skos_taxonomy child ON child.broader_uri = s.concept_uri
            WHERE child.concept_uri = ?
            UNION ALL
            SELECT s.concept_uri, s.pref_label, s.alt_labels_json, s.broader_uri, s.scheme, s.scope_note, at.depth + 1
            FROM skos_taxonomy s
            JOIN ancestor_tree at ON at.broader_uri = s.concept_uri
        )
        SELECT concept_uri, pref_label, alt_labels_json, broader_uri, scheme, scope_note, depth
        FROM ancestor_tree
        ORDER BY depth;
        """
        c.execute(sql, (child_uri,))
        results = []
        for row in c.fetchall():
            curi, plab, alabs, buri, sch, snote, depth = row
            results.append({
                "concept_uri": curi,
                "pref_label": plab,
                "alt_labels": json.loads(alabs or "[]"),
                "broader_uri": buri,
                "scheme": sch,
                "scope_note": snote,
                "depth": depth
            })
        conn.close()
        return results

    def list_all_concepts(self) -> List[Dict[str, Any]]:
        """Returns all concepts indexed in the SKOS taxonomy."""
        if not self.db_path.exists():
            return STANDARD_SKOS_TAXONOMY
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute("SELECT concept_uri, pref_label, alt_labels_json, broader_uri, scheme, scope_note FROM skos_taxonomy ORDER BY scheme, concept_uri")
        results = []
        for row in c.fetchall():
            curi, plab, alabs, buri, sch, snote = row
            results.append({
                "concept_uri": curi,
                "pref_label": plab,
                "alt_labels": json.loads(alabs or "[]"),
                "broader_uri": buri,
                "scheme": sch,
                "scope_note": snote
            })
        conn.close()
        return results

    def validate_owl_ontology(self) -> Dict[str, Any]:
        """Loads and validates ontology/meia_ontology.ttl using rdflib."""
        if not self.ontology_file.is_file():
            return {"valid": False, "error": f"Ontology file missing at {self.ontology_file}"}

        g = Graph()
        try:
            g.parse(str(self.ontology_file), format="turtle")
            classes = list(g.subjects(RDF.type, OWL.Class))
            obj_props = list(g.subjects(RDF.type, OWL.ObjectProperty))
            inverses = list(g.subject_objects(OWL.inverseOf))

            return {
                "valid": True,
                "triples_count": len(g),
                "classes_count": len(classes),
                "object_properties_count": len(obj_props),
                "inverse_property_pairs": len(inverses) // 2,
                "classes": [str(c).split("#")[-1] for c in classes],
                "object_properties": [str(p).split("#")[-1] for p in obj_props],
            }
        except Exception as exc:
            return {"valid": False, "error": str(exc)}

    def export_federated_turtle_graph(self, output_path: Optional[Path] = None) -> Tuple[int, Path]:
        """Serializes the complete Tri-Graph SQLite registry into a W3C-compliant RDF Turtle file."""
        target_path = output_path or TURTLE_EXPORT_PATH
        target_path.parent.mkdir(parents=True, exist_ok=True)

        g = Graph()
        g.bind("bfo", BFO)
        g.bind("iao", IAO)
        g.bind("meia", MEIA)
        g.bind("osra", OSRA)
        g.bind("twenty_crm", TWENTY_CRM)
        g.bind("skos", SKOS)
        g.bind("meia_data", MEIA_DATA)

        # Include base ontology definitions if available
        if self.ontology_file.is_file():
            g.parse(str(self.ontology_file), format="turtle")

        if not self.db_path.is_file():
            g.serialize(destination=str(target_path), format="turtle")
            return len(g), target_path

        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        # 1. Export SKOS Taxonomy
        c.execute("SELECT concept_uri, pref_label, alt_labels_json, broader_uri, scheme FROM skos_taxonomy")
        for curi, plab, alabs, buri, sch in c.fetchall():
            concept_ref = MEIA_DATA[curi.replace(":", "_")]
            g.add((concept_ref, RDF.type, SKOS.Concept))
            g.add((concept_ref, SKOS.prefLabel, Literal(plab, lang="en")))
            for alt in json.loads(alabs or "[]"):
                g.add((concept_ref, SKOS.altLabel, Literal(alt, lang="en")))
            if buri:
                broader_ref = MEIA_DATA[buri.replace(":", "_")]
                g.add((concept_ref, SKOS.broader, broader_ref))
                g.add((broader_ref, SKOS.narrower, concept_ref))

        # 2. Export Domain Nodes
        c.execute("SELECT id, graph_domain, bfo_category, skos_concepts, label, properties_json FROM domain_nodes")
        node_bfo_map = {}
        for nid, domain, bfo_cat, skos_str, label, props_str in c.fetchall():
            subj = MEIA_DATA[nid.replace(":", "_")]
            node_bfo_map[nid] = bfo_cat

            # Assign BFO and MEIA classes
            g.add((subj, RDF.type, BFO[bfo_cat]))
            g.add((subj, RDFS.label, Literal(label)))
            g.add((subj, MEIA.graphDomain, Literal(domain)))

            # SKOS concept relations
            for concept in json.loads(skos_str or "[]"):
                concept_ref = MEIA_DATA[concept.replace(":", "_")]
                g.add((subj, SKOS.related, concept_ref))

            # Properties
            props = json.loads(props_str or "{}")
            for k, v in props.items():
                if isinstance(v, (str, int, float)) and v:
                    g.add((subj, MEIA[k], Literal(str(v))))

        # 3. Export Domain Edges & Inverses
        c.execute("SELECT edge_id, source_id, target_id, edge_type, properties_json FROM domain_edges")
        for eid, src, tgt, etype, props_str in c.fetchall():
            src_node = MEIA_DATA[src.replace(":", "_")]
            tgt_node = MEIA_DATA[tgt.replace(":", "_")]
            clean_pred = etype.strip("[]:").replace(":", "_")
            pred_uri = MEIA[clean_pred]

            g.add((src_node, pred_uri, tgt_node))

            # Add declared inverse edge
            inv_type = INVERSE_PREDICATE_MAP.get(etype)
            if inv_type:
                clean_inv = inv_type.strip("[]:").replace(":", "_")
                g.add((tgt_node, MEIA[clean_inv], src_node))

        # 4. Export Cross-Graph Links & Inverses
        c.execute("SELECT link_id, source_id, target_id, link_predicate, match_method, review_status FROM cross_graph_links")
        for lid, src, tgt, pred, method, status in c.fetchall():
            src_node = MEIA_DATA[src.replace(":", "_")]
            tgt_node = MEIA_DATA[tgt.replace(":", "_")]
            clean_pred = pred.strip("[]:").replace(":", "_")
            pred_uri = MEIA[clean_pred]

            g.add((src_node, pred_uri, tgt_node))

            inv_pred = INVERSE_PREDICATE_MAP.get(pred)
            if inv_pred:
                clean_inv = inv_pred.strip("[]:").replace(":", "_")
                g.add((tgt_node, MEIA[clean_inv], src_node))

        # 5. Export Epistemic Claims as Reified Statement Nodes
        c.execute("SELECT claim_id, subject_id, predicate, object_value, epistemic_status, confidence, handling_level, evidence_id FROM claim_ledger")
        for cid, sub, pred, val, status, conf, hand, evid in c.fetchall():
            claim_node = MEIA_DATA[cid.replace(":", "_")]
            subj_node = MEIA_DATA[sub.replace(":", "_")]

            g.add((claim_node, RDF.type, MEIA.EpistemicClaim))
            g.add((claim_node, RDF.type, IAO.InformationContentEntity))
            g.add((claim_node, MEIA.claimAbout, subj_node))
            g.add((subj_node, MEIA.hasEpistemicClaim, claim_node))
            g.add((claim_node, MEIA.claimPredicate, Literal(pred)))
            g.add((claim_node, MEIA.claimValue, Literal(val)))
            g.add((claim_node, MEIA.epistemicStatus, Literal(status)))
            g.add((claim_node, MEIA.epistemicConfidence, Literal(float(conf), datatype=XSD.float)))
            g.add((claim_node, MEIA.handlingLevel, Literal(hand)))

            if evid:
                evid_node = MEIA_DATA[evid.replace(":", "_")]
                g.add((claim_node, MEIA.supportedByEvidence, evid_node))
                g.add((evid_node, MEIA.supportsClaim, claim_node))

        # 6. Export Multimodal Evidence Nodes
        c.execute("SELECT evidence_id, doc_id, standard_id, locator_type, locator_str, sha256 FROM evidence_nodes")
        for evid, doc_id, std_id, ltype, loc_str, sha in c.fetchall():
            evid_node = MEIA_DATA[evid.replace(":", "_")]
            g.add((evid_node, RDF.type, MEIA.EvidenceNode))
            g.add((evid_node, RDF.type, IAO.InformationContentEntity))
            g.add((evid_node, MEIA.documentId, Literal(doc_id)))
            g.add((evid_node, MEIA.standardId, Literal(std_id)))
            g.add((evid_node, MEIA.locatorType, Literal(ltype)))
            g.add((evid_node, MEIA.locatorString, Literal(loc_str)))
            if sha:
                g.add((evid_node, MEIA.sha256Digest, Literal(sha)))

        conn.close()

        # Serialize to Turtle
        g.serialize(destination=str(target_path), format="turtle")
        logger.info("Successfully exported %d RDF triples to %s", len(g), target_path)
        return len(g), target_path


# Global singleton
_GLOBAL_ONTOLOGY_SERVICE: Optional[OntologyService] = None


def get_ontology_service() -> OntologyService:
    global _GLOBAL_ONTOLOGY_SERVICE
    if _GLOBAL_ONTOLOGY_SERVICE is None:
        _GLOBAL_ONTOLOGY_SERVICE = OntologyService()
    return _GLOBAL_ONTOLOGY_SERVICE
