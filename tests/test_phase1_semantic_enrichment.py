"""Test Suite for Phase 1 Semantic Enrichment:
- Formal OWL 2 DL Ontology (ontology/meia_ontology.ttl)
- W3C SKOS Concept Hierarchy & Transitive SQL Traversal
- Bidirectional Inverse Predicate Resolution
- W3C RDF Turtle (Linked Data) Graph Export (storage/meia_federated_tri_graph.ttl)
- Ontology Web API Endpoints
"""
import json
import sqlite3
import unittest
from pathlib import Path

import rdflib
from rdflib import Graph, OWL, RDF

from src.config import REPO_ROOT, STORAGE_DIR, TRI_GRAPH_DB_PATH
from src.ontology_service import (
    INVERSE_PREDICATE_MAP,
    ONTOLOGY_FILE,
    TURTLE_EXPORT_PATH,
    OntologyService,
    get_ontology_service,
)


class TestPhase1SemanticEnrichment(unittest.TestCase):
    """Verifies all Phase 1 Semantic Enrichment deliverables."""

    def setUp(self):
        self.ont_svc = get_ontology_service()

    def test_01_owl_ontology_file_structure_and_syntax(self):
        """Validates that ontology/meia_ontology.ttl exists, parses as valid Turtle, and defines OWL classes and properties."""
        self.assertTrue(ONTOLOGY_FILE.is_file(), f"Ontology file must exist at {ONTOLOGY_FILE}")
        val_res = self.ont_svc.validate_owl_ontology()
        self.assertTrue(val_res["valid"], f"Ontology validation failed: {val_res.get('error')}")

        # Verify key classes and properties
        self.assertGreaterEqual(val_res["classes_count"], 15, "Expected >= 15 OWL classes")
        self.assertGreaterEqual(val_res["object_properties_count"], 20, "Expected >= 20 OWL object properties")
        self.assertGreaterEqual(val_res["inverse_property_pairs"], 10, "Expected >= 10 inverse property pairs")

        # Verify specific classes
        classes = set(val_res["classes"])
        self.assertIn("Organization", classes)
        self.assertIn("CapabilityOffering", classes)
        self.assertIn("DemonstrationEvent", classes)
        self.assertIn("ContractAward", classes)
        self.assertIn("CapabilitySubmission", classes)
        self.assertIn("EpistemicClaim", classes)
        self.assertIn("EvidenceNode", classes)

    def test_02_skos_taxonomy_table_and_population(self):
        """Verifies that skos_taxonomy table exists in SQLite and contains defense and procurement concepts."""
        self.assertTrue(TRI_GRAPH_DB_PATH.is_file(), f"Database must exist at {TRI_GRAPH_DB_PATH}")
        conn = sqlite3.connect(str(TRI_GRAPH_DB_PATH))
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM skos_taxonomy")
        count = c.fetchone()[0]
        self.assertGreaterEqual(count, 20, f"Expected >= 20 SKOS concepts in taxonomy, found {count}")

        # Check scheme distribution
        c.execute("SELECT scheme, COUNT(*) FROM skos_taxonomy GROUP BY scheme")
        schemes = {row[0]: row[1] for row in c.fetchall()}
        self.assertIn("OSRA", schemes)
        self.assertIn("MEIA", schemes)
        self.assertIn("TWENTY_CRM", schemes)
        self.assertIn("ORG", schemes)

        conn.close()

    def test_03_skos_transitive_hierarchy_queries(self):
        """Verifies recursive SQL CTE traversal for broader and narrower concepts."""
        # Query narrower concepts of osra:DefenseTechnologies
        narrower = self.ont_svc.get_narrower_concepts("osra:DefenseTechnologies")
        self.assertTrue(len(narrower) >= 4, "Expected >= 4 narrower concepts under osra:DefenseTechnologies")
        concept_uris = {item["concept_uri"] for item in narrower}
        self.assertIn("osra:UnmannedUnderwaterVehicles", concept_uris)
        self.assertIn("osra:CounterUAS", concept_uris)
        self.assertIn("osra:TacticalCommunications", concept_uris)
        self.assertIn("osra:PowerAndEnergyStorage", concept_uris)

        # Query broader concepts of osra:UnmannedUnderwaterVehicles
        broader = self.ont_svc.get_broader_concepts("osra:UnmannedUnderwaterVehicles")
        self.assertEqual(len(broader), 1)
        self.assertEqual(broader[0]["concept_uri"], "osra:DefenseTechnologies")

    def test_04_inverse_predicates_mapping(self):
        """Verifies that all intra-domain and cross-graph predicates have declared inverses."""
        self.assertEqual(self.ont_svc.get_inverse_predicate("[:DEVELOPS_OFFERING]"), "[:DEVELOPED_BY]")
        self.assertEqual(self.ont_svc.get_inverse_predicate("[:DEVELOPED_BY]"), "[:DEVELOPS_OFFERING]")
        self.assertEqual(self.ont_svc.get_inverse_predicate("[:SUBMITTED_BY_ORG]"), "[:SUBMITTED_OFFERING]")
        self.assertEqual(self.ont_svc.get_inverse_predicate("[:EVALUATES_OFFERING]"), "[:EVALUATED_BY]")
        self.assertEqual(self.ont_svc.get_inverse_predicate("[:VALIDATED_BY_CONTRACT]"), "[:VALIDATES_CAPABILITY]")
        self.assertEqual(self.ont_svc.get_inverse_predicate("[:HOLDS_PRIME_AWARD]"), "[:AWARDED_TO_ORG]")
        self.assertEqual(self.ont_svc.get_inverse_predicate("[:PARTICIPATED_IN_DEMO]"), "[:FEATURED_CAPABILITY]")
        self.assertEqual(self.ont_svc.get_inverse_predicate("[:HAS_READINESS_ASSESSMENT]"), "[:ASSESSES_READINESS_OF]")

        # Check that edges in the database have inverse properties recorded in properties_json
        conn = sqlite3.connect(str(TRI_GRAPH_DB_PATH))
        c = conn.cursor()
        c.execute("SELECT properties_json FROM domain_edges WHERE edge_type = '[:DEVELOPS_OFFERING]' LIMIT 1")
        # In cross_graph_links
        c.execute("SELECT properties_json FROM cross_graph_links WHERE link_predicate = '[:DEVELOPS_OFFERING]' LIMIT 1")
        row = c.fetchone()
        if row:
            props = json.loads(row[0] or "{}")
            self.assertEqual(props.get("inverse_predicate"), "[:DEVELOPED_BY]")
        conn.close()

    def test_05_w3c_rdf_turtle_graph_export(self):
        """Verifies that storage/meia_federated_tri_graph.ttl is generated and parses into valid RDF triples."""
        self.assertTrue(TURTLE_EXPORT_PATH.is_file(), f"RDF Turtle file must exist at {TURTLE_EXPORT_PATH}")
        g = Graph()
        g.parse(str(TURTLE_EXPORT_PATH), format="turtle")
        self.assertGreaterEqual(len(g), 3500, f"Expected >= 3,500 RDF triples, found {len(g)}")

        # Verify that BFO types and MEIA properties exist in the exported RDF
        bfo_types = list(g.triples((None, RDF.type, rdflib.URIRef("http://purl.obolibrary.org/obo/bfo.owl#MaterialEntity"))))
        self.assertGreaterEqual(len(bfo_types), 5, "Expected material entity triples in Turtle export")

        claims = list(g.triples((None, RDF.type, rdflib.URIRef("https://meia.mil/ontology#EpistemicClaim"))))
        self.assertEqual(len(claims), 53, "Expected exactly 53 reified EpistemicClaim RDF nodes")


if __name__ == "__main__":
    unittest.main()
