"""
Stage 1: Pre-Retrieval Intent Classifier, 8-Profile Minimum-Sufficient Router,
SKOS Acronym Expander, and Guarded Policy Gates.
"""

import json
import logging
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pre_retrieval")


class RoutingProfile(str, Enum):
    ROUTE_ORG = "ROUTE_ORG"                       # Profile A: CQs 01-18 (Org-KG standalone)
    ROUTE_TECH = "ROUTE_TECH"                     # Profile B: CQs 19-36 (Tech-KG standalone)
    ROUTE_CRM = "ROUTE_CRM"                       # Profile C: CQs 37-50 (CRM-Graph standalone)
    ROUTE_ORG_TECH = "ROUTE_ORG_TECH"             # Profile D1: CQs 51-57 (Org ⋈ Tech)
    ROUTE_CRM_ORG = "ROUTE_CRM_ORG"               # Profile D2: CQs 58-62 (CRM ⋈ Org)
    ROUTE_CRM_TECH = "ROUTE_CRM_TECH"             # Profile D3: CQs 63-67 (CRM ⋈ Tech)
    ROUTE_ALL_TRI_STORE = "ROUTE_ALL_TRI_STORE"   # Profile D4: CQs 68-72 (360° Executive Dossier)
    FAIL_CLOSED_GATE = "FAIL_CLOSED_GATE"         # Profile D5: CQs 73-78 (Security & Scope Gates)


@dataclass
class CallerContext:
    caller_role: str = "meia-authorized-evaluator"
    clearance_level: str = "SECRET"               # UNCLASSIFIED, CUI, SECRET, TOP_SECRET
    enabled_modules: List[str] = field(default_factory=lambda: [
        "organization_graph",
        "technology_graph",
        "crm_graph",
        "evidence_graph"
    ])


@dataclass
class RoutingDecision:
    route_profile: RoutingProfile
    status: str                                  # SUPPORTED, ACCESS_DENIED, INSUFFICIENT_DEPLOYED_CAPABILITY, OUT_OF_SCOPE, NOT_RECORDED
    selected_modules: List[str]
    resolved_entities: List[Dict[str, Any]]
    expanded_terms: List[str]
    clean_query: str
    confidence: float
    reasons: List[str]


# -----------------------------------------------------------------------------
# SKOS Acronym & Concept Expansion Dictionary
# -----------------------------------------------------------------------------
DEFENSE_SKOS_EXPANSIONS: Dict[str, Tuple[str, str]] = {
    "uuv": ("Unmanned Underwater Vehicle", "osra:TBB-29 (Underwater Unmanned Vehicles)"),
    "c5isr": ("Command, Control, Communications, Computers, Cyber, Intelligence, Surveillance, Reconnaissance", "meia:CounterC5ISRT"),
    "c5isr-t": ("Command, Control, Communications, Computers, Cyber, Intelligence, Surveillance, Reconnaissance, and Targeting", "meia:CounterC5ISRT"),
    "c-uas": ("Counter Unmanned Aerial Systems", "osra:TBB-32 (Counter-UAS)"),
    "trl": ("Technology Readiness Level", "meia:ReadinessAssessment"),
    "mrl": ("Manufacturing Readiness Level", "meia:ReadinessAssessment"),
    "irl": ("Integration Readiness Level", "meia:ReadinessAssessment"),
    "afsim": ("Advanced Framework for Simulation, Integration, and Modeling", "eval:ConstructiveSimulation"),
    "foci": ("Foreign Ownership, Control, or Influence", "org:SecurityGovernance"),
    "rom": ("Rough Order of Magnitude", "twenty_crm:FundingNeed"),
    "itar": ("International Traffic in Arms Regulations", "twenty_crm:ExportControl"),
    "ear": ("Export Administration Regulations", "twenty_crm:ExportControl"),
    "jop": ("Joint Operational Problem", "meia:JointOperationalProblem"),
    "swap": ("Size, Weight, and Power", "tech:PhysicalCharacteristic"),
    "swap-c": ("Size, Weight, Power, and Cooling", "tech:PhysicalCharacteristic"),
    "gpr": ("Government Purpose Rights", "twenty_crm:ProductRights"),
    "crada": ("Cooperative Research and Development Agreement", "twenty_crm:ProductRights"),
    "idv": ("Indefinite Delivery Vehicle", "org:ContractVehicle"),
    "idiq": ("Indefinite Delivery Indefinite Quantity", "org:ContractVehicle"),
    "sdvosb": ("Service-Disabled Veteran-Owned Small Business", "org:SocioeconomicDesignation"),
    "csfc": ("Commercial Solutions for Classified", "tech:CryptographicStandard"),
    "cots": ("Commercial Off-The-Shelf", "tech:ComponentArchitecture"),
}

# -----------------------------------------------------------------------------
# Known Corpus Entity Dictionaries
# -----------------------------------------------------------------------------
KNOWN_ENTITIES = {
    # CAGE Codes
    "0qsf0": {"id": "org:albacore", "type": "Organization", "name": "Albacore Technologies"},
    "9w2w3": {"id": "org:voltage_vessels", "type": "Organization", "name": "Voltage Vessels, LLC"},
    "7z7b0": {"id": "org:t2s_solutions", "type": "Organization", "name": "T2S Solutions LLC"},
    "01037": {"id": "org:fluor_federal", "type": "Organization", "name": "Fluor Federal Services Inc."},
    "3z9w4": {"id": "org:klas_gov", "type": "Organization", "name": "Klas Government Inc."},
    "9m4c2": {"id": "org:prometheus_intelligence", "type": "Organization", "name": "Prometheus Intelligence Technology LLC"},
    # UEIs
    "nz9cumf36pk1": {"id": "org:fluor_federal", "type": "Organization", "name": "Fluor Federal Services Inc."},
    "kq28qju21gy3": {"id": "org:klas_gov", "type": "Organization", "name": "Klas Government Inc."},
    "j767k9b843s5": {"id": "org:prometheus_intelligence", "type": "Organization", "name": "Prometheus Intelligence Technology LLC"},
    "pw8dt7rk5261": {"id": "org:prometheus_intelligence_inc", "type": "Organization", "name": "Prometheus Intelligence, Inc."},
    "l3t9vhgp44d1": {"id": "org:albacore", "type": "Organization", "name": "Albacore (L3T9VHGP44D1)"},
    # Vulcan IDs
    "26705": {"id": "crm:submission_26705", "type": "CapabilitySubmission", "name": "Ghostfin Vulcan Submission (26705)"},
    "25615": {"id": "crm:submission_25615", "type": "CapabilitySubmission", "name": "Eclipse X9 Vulcan Submission (25615)"},
    "27268": {"id": "crm:submission_27268", "type": "CapabilitySubmission", "name": "Counter Sensing Vulcan Submission (27268)"},
    # Offerings & Technologies
    "ghostfin": {"id": "tech:ghostfin_uuv", "type": "Offering", "name": "Ghostfin: Long-Range, Hybrid Electric Medium UUV"},
    "voltvessel": {"id": "tech:voltvessel_energy", "type": "Offering", "name": "VoltVessel Maritime High-Density Energy Module"},
    "eclipse x9": {"id": "tech:voltvessel_energy", "type": "Offering", "name": "Eclipse X9 Distributed Composite Manufacturing"},
    "counter sensing": {"id": "tech:tactical_microgrid", "type": "Offering", "name": "Counter Sensing / Micro-Grid"},
    "tactical micro-grid": {"id": "tech:tactical_microgrid", "type": "Offering", "name": "Tactical Micro-Grid Hybrid Energy"},
    "voyager": {"id": "tech:klas_voyager", "type": "Offering", "name": "Klas Voyager Modular Tactical Communications"},
    "torch": {"id": "tech:prometheus_energy_ai", "type": "Offering", "name": "Prometheus Torch Tactical AI"},
    # Key Vendors
    "albacore": {"id": "org:albacore", "type": "Organization", "name": "Albacore Technologies"},
    "voltage vessels": {"id": "org:voltage_vessels", "type": "Organization", "name": "Voltage Vessels, LLC"},
    "t2s solutions": {"id": "org:t2s_solutions", "type": "Organization", "name": "T2S Solutions LLC"},
    "fluor": {"id": "org:fluor_federal", "type": "Organization", "name": "Fluor Federal Services Inc."},
    "klas": {"id": "org:klas_gov", "type": "Organization", "name": "Klas Government Inc."},
    "prometheus": {"id": "org:prometheus_intelligence", "type": "Organization", "name": "Prometheus Intelligence Technology LLC"},
}


class PreRetrievalRouter:
    """Pre-Retrieval Intent Classifier, Minimum-Sufficient Graph Router, and Policy Gate."""

    def __init__(self):
        pass

    def resolve_entities(self, query: str) -> List[Dict[str, Any]]:
        """Extracts known CAGEs, UEIs, Vulcan IDs, and vendor/product names from query."""
        q_lower = query.lower()
        matched = []
        seen_ids = set()

        # Check regex for CAGE-like or Vulcan IDs
        tokens = re.findall(r"\b[A-Za-z0-9_-]+\b", q_lower)
        for t in tokens:
            if t in KNOWN_ENTITIES:
                ent = KNOWN_ENTITIES[t]
                if ent["id"] not in seen_ids:
                    matched.append(ent)
                    seen_ids.add(ent["id"])

        # Check multi-word keys
        for key, ent in KNOWN_ENTITIES.items():
            if " " in key and key in q_lower:
                if ent["id"] not in seen_ids:
                    matched.append(ent)
                    seen_ids.add(ent["id"])

        return matched

    def expand_acronyms(self, query: str) -> Tuple[List[str], str]:
        """Identifies defense acronyms and returns expanded SKOS taxonomy concepts."""
        q_lower = query.lower()
        tokens = re.findall(r"\b[A-Za-z0-9-]+\b", q_lower)
        expansions = []

        for t in tokens:
            if t in DEFENSE_SKOS_EXPANSIONS:
                full_name, skos_code = DEFENSE_SKOS_EXPANSIONS[t]
                expansions.append(f"{t.upper()}: {full_name} ({skos_code})")

        return expansions, query

    def evaluate_policy_gates(self, query: str, context: CallerContext) -> Optional[RoutingDecision]:
        """Evaluates Fail-Closed Security, Clearance, and Out-of-Scope Gates (CQ-76, CQ-77, CQ-78)."""
        q_lower = query.lower()

        # 1. CQ-78: Out-of-Scope & Unrecorded Fact Gate
        out_of_scope_patterns = [
            "acoustic signature", "decibel rating", "decibels at 30 knots",
            "radar cross section in dbsm", "nuclear warhead yield",
            "stock price target 2030", "ceo personal net worth"
        ]
        for oos in out_of_scope_patterns:
            if oos in q_lower:
                return RoutingDecision(
                    route_profile=RoutingProfile.FAIL_CLOSED_GATE,
                    status="OUT_OF_SCOPE",
                    selected_modules=[],
                    resolved_entities=[],
                    expanded_terms=[],
                    clean_query=query,
                    confidence=1.0,
                    reasons=[f"Query targets out-of-scope or unrecorded empirical parameter: '{oos}' (CQ-78 Invariant)"]
                )

        # 2. CQ-77: Access Control, PII, and Security Clearance Gate
        is_pii_request = any(p in q_lower for p in ["poc phone", "poc personal phone", "phone number", "personal cell", "direct phone"])
        is_classified_request = any(c in q_lower for c in ["top secret", "sci (4-pack)", "secret // rel fvey", "classified meeting detail"])

        if is_pii_request and context.clearance_level == "UNCLASSIFIED":
            return RoutingDecision(
                route_profile=RoutingProfile.FAIL_CLOSED_GATE,
                status="ACCESS_DENIED",
                selected_modules=[],
                resolved_entities=self.resolve_entities(query),
                expanded_terms=[],
                clean_query=query,
                confidence=1.0,
                reasons=["Access denied: Requested field contains encrypted PII contact records requiring authorized CUI clearance (CQ-77 Invariant)"]
            )

        if is_classified_request and context.clearance_level not in ["SECRET", "TOP_SECRET"]:
            return RoutingDecision(
                route_profile=RoutingProfile.FAIL_CLOSED_GATE,
                status="ACCESS_DENIED",
                selected_modules=[],
                resolved_entities=self.resolve_entities(query),
                expanded_terms=[],
                clean_query=query,
                confidence=1.0,
                reasons=["Access denied: Caller clearance level insufficient for classified meeting security preferences (CQ-77 Invariant)"]
            )

        return None

    def route_query(self, query: str, context: Optional[CallerContext] = None) -> RoutingDecision:
        """Determines the minimum-sufficient routing profile and active modules for any NLQ."""
        if context is None:
            context = CallerContext()

        # 1. Check Policy & Fail-Closed Gates first
        gate_decision = self.evaluate_policy_gates(query, context)
        if gate_decision is not None:
            return gate_decision

        resolved_ents = self.resolve_entities(query)
        expanded_terms, clean_q = self.expand_acronyms(query)
        q_lower = query.lower()

        # 2. Check Profile D4: 3-Way Tri-Store Dossier (CQs 68-72)
        dossier_triggers = [
            "executive business and capability dossier",
            "business and capability dossier",
            "executive capability dossier",
            "executive due diligence dossier",
            "360-degree assessment",
            "complete business and capability assessment report",
            "360 business and capability report",
            "complete meia business and capability dossier"
        ]
        if any(dt in q_lower for dt in dossier_triggers) or ("dossier" in q_lower and ("report" in q_lower or "complete" in q_lower or "executive" in q_lower)):
            required = ["organization_graph", "technology_graph", "crm_graph", "evidence_graph"]
            # Check CQ-76 Module Deployment Gate
            missing = [m for m in required if m not in context.enabled_modules]
            if missing:
                return RoutingDecision(
                    route_profile=RoutingProfile.ROUTE_ALL_TRI_STORE,
                    status="INSUFFICIENT_DEPLOYED_CAPABILITY",
                    selected_modules=[m for m in required if m in context.enabled_modules],
                    resolved_entities=resolved_ents,
                    expanded_terms=expanded_terms,
                    clean_query=query,
                    confidence=1.0,
                    reasons=[f"Required modules {missing} are disabled in active deployment profile (CQ-76 Invariant)"]
                )

            return RoutingDecision(
                route_profile=RoutingProfile.ROUTE_ALL_TRI_STORE,
                status="SUPPORTED",
                selected_modules=required,
                resolved_entities=resolved_ents,
                expanded_terms=expanded_terms,
                clean_query=query,
                confidence=0.98,
                reasons=["Detected 360° Tri-Store Executive Dossier request (Profile D4, CQs 68-72)"]
            )

        # 3. Check Profile D5: Exact Evidence Locator / Provenance Trace (CQs 73-75)
        provenance_triggers = [
            "exact evidence locator", "provenance trace", "cell locator", "sha-256 hash", "conflicting evidence",
            "claim vs. empirical demonstration", "vendor assertion", "minimum-sufficient routing",
            "module capability gate", "where that module is disabled", "afsim digital engineering"
        ]
        if any(pt in q_lower for pt in provenance_triggers):
            return RoutingDecision(
                route_profile=RoutingProfile.FAIL_CLOSED_GATE,
                status="SUPPORTED",
                selected_modules=["evidence_graph"],
                resolved_entities=resolved_ents,
                expanded_terms=expanded_terms,
                clean_query=query,
                confidence=0.95,
                reasons=["Routing to Evidence Graph for exact cell/chunk locators and provenance trace (CQ-73 to CQ-75)"]
            )

        # 4. Check Pairwise Joins (D1, D2, D3)
        # D1: Org ⋈ Tech (CQs 51-57)
        org_tech_triggers = [
            ("small business" in q_lower or "startup" in q_lower or "foci" in q_lower or "naics" in q_lower or "psc" in q_lower) and
            ("trl" in q_lower or "c5isr" in q_lower or "topic" in q_lower or "counter c5isr-t" in q_lower or "capability" in q_lower or "osra" in q_lower),
            "sbir transitioning to sole source" in q_lower,
            ("sbir" in q_lower or "sttr" in q_lower) and ("sole source" in q_lower or "transition" in q_lower or "r&d" in q_lower or "phase" in q_lower),
            "subaward-to-prime ratio" in q_lower and "component" in q_lower,
            "contract awards" in q_lower and "capabilities" in q_lower,
            "demonstrated in" in q_lower and "awarded" in q_lower,
            ("which company" in q_lower or "which vendor" in q_lower or "develops" in q_lower or "cage" in q_lower) and ("ghostfin" in q_lower or "voltvessel" in q_lower or "microgrid" in q_lower or "uuv" in q_lower or "offering" in q_lower)
        ]
        if any(org_tech_triggers):
            required = ["organization_graph", "technology_graph"]
            missing = [m for m in required if m not in context.enabled_modules]
            if missing:
                return RoutingDecision(
                    route_profile=RoutingProfile.ROUTE_ORG_TECH,
                    status="INSUFFICIENT_DEPLOYED_CAPABILITY",
                    selected_modules=[m for m in required if m in context.enabled_modules],
                    resolved_entities=resolved_ents,
                    expanded_terms=expanded_terms,
                    clean_query=query,
                    confidence=0.92,
                    reasons=[f"Required module {missing} disabled for 2-way join Org⋈Tech (CQ-76 Invariant)"]
                )
            return RoutingDecision(
                route_profile=RoutingProfile.ROUTE_ORG_TECH,
                status="SUPPORTED",
                selected_modules=required,
                resolved_entities=resolved_ents,
                expanded_terms=expanded_terms,
                clean_query=query,
                confidence=0.93,
                reasons=["Query joins corporate/procurement profile (Org-KG) with technical capabilities (Tech-KG) (Profile D1, CQs 51-57)"]
            )

        # D2: CRM ⋈ Org (CQs 58-62)
        crm_org_triggers = [
            ("submission" in q_lower or "crm" in q_lower or "q5" in q_lower or "q12" in q_lower or "funding" in q_lower) and
            ("registration" in q_lower or "cage" in q_lower or "uei" in q_lower or "duns" in q_lower or "federal prime" in q_lower or "federal spend" in q_lower or "award volume" in q_lower or "link to the same resolved organization" in q_lower or "foci" in q_lower or "socioeconomic" in q_lower or "previously contracted" in q_lower),
            "funding to scale" in q_lower and ("prime" in q_lower or "spend" in q_lower or "award" in q_lower),
            "classified one-on-one meeting" in q_lower and ("socioeconomic" in q_lower or "foci" in q_lower),
            "government technical poc" in q_lower and "previously contracted" in q_lower
        ]
        if any(crm_org_triggers):
            required = ["crm_graph", "organization_graph"]
            missing = [m for m in required if m not in context.enabled_modules]
            if missing:
                return RoutingDecision(
                    route_profile=RoutingProfile.ROUTE_CRM_ORG,
                    status="INSUFFICIENT_DEPLOYED_CAPABILITY",
                    selected_modules=[m for m in required if m in context.enabled_modules],
                    resolved_entities=resolved_ents,
                    expanded_terms=expanded_terms,
                    clean_query=query,
                    confidence=0.91,
                    reasons=[f"Required module {missing} disabled for 2-way join CRM⋈Org (CQ-76 Invariant)"]
                )
            return RoutingDecision(
                route_profile=RoutingProfile.ROUTE_CRM_ORG,
                status="SUPPORTED",
                selected_modules=required,
                resolved_entities=resolved_ents,
                expanded_terms=expanded_terms,
                clean_query=query,
                confidence=0.92,
                reasons=["Query joins intake/pipeline status (CRM-Graph) with verified federal registration/spend (Org-KG) (Profile D2, CQs 58-62)"]
            )

        # D3: CRM ⋈ Tech (CQs 63-67)
        crm_tech_triggers = [
            ("trl" in q_lower or "mrl" in q_lower) and ("government purpose rights" in q_lower or "crada" in q_lower or "rights" in q_lower),
            ("unit cost" in q_lower or "q6" in q_lower) and ("mrl" in q_lower or "architecture" in q_lower or "cots" in q_lower),
            ("live operational field experimentation" in q_lower or "sonic spear" in q_lower or "experimentation" in q_lower) and ("joint acceleration reserve" in q_lower or "scale" in q_lower or "funding" in q_lower),
            "contested logistics" in q_lower and ("unclassified level" in q_lower or "q12" in q_lower or "security preference" in q_lower),
            "canonical capability offering" in q_lower and "across multiple crm submissions" in q_lower
        ]
        if any(crm_tech_triggers):
            required = ["crm_graph", "technology_graph"]
            missing = [m for m in required if m not in context.enabled_modules]
            if missing:
                return RoutingDecision(
                    route_profile=RoutingProfile.ROUTE_CRM_TECH,
                    status="INSUFFICIENT_DEPLOYED_CAPABILITY",
                    selected_modules=[m for m in required if m in context.enabled_modules],
                    resolved_entities=resolved_ents,
                    expanded_terms=expanded_terms,
                    clean_query=query,
                    confidence=0.91,
                    reasons=[f"Required module {missing} disabled for 2-way join CRM⋈Tech (CQ-76 Invariant)"]
                )
            return RoutingDecision(
                route_profile=RoutingProfile.ROUTE_CRM_TECH,
                status="SUPPORTED",
                selected_modules=required,
                resolved_entities=resolved_ents,
                expanded_terms=expanded_terms,
                clean_query=query,
                confidence=0.92,
                reasons=["Query joins commercial terms/cost/rights (CRM-Graph) with technical readiness and operational demonstrations (Tech-KG) (Profile D3, CQs 63-67)"]
            )

        # 5. Check Single-Domain Graphs (A, B, C)
        # Profile A: Organization Graph Standalone (CQs 01-18)
        org_keywords = [
            "legal business name", "cage code", "cage", "uei", "duns", "corporate parent",
            "headquarters address", "physical address", "incorporation", "foci", "foreign-owned",
            "socioeconomic", "small business certification", "naics", "psc", "federal prime spending",
            "contract awards", "prime awards", "subawards", "prime-to-subaward", "idv", "idiq", "sole-source percentage",
            "organization type", "business category", "subcategory", "federal agencies", "sub-agencies",
            "primary customers", "obligated dollars", "pricing structures", "firm fixed price", "time & materials", "cost-plus", "contract pricing"
        ]
        org_score = sum(1 for kw in org_keywords if kw in q_lower)

        # Profile B: Technology & Mission Graph Standalone (CQs 19-36)
        tech_keywords = [
            "technology capability", "offering type", "prototype", "q11", "system hierarchy",
            "technical description", "architectural composition", "technical differentiator",
            "competitive advantage", "q8", "bfo", "osra", "tbb", "topic area", "q2", "jop",
            "operational problem", "q1", "capability contribution", "q3", "swap", "swap-c",
            "trl", "mrl", "irl", "q9", "maturity", "performance measures", "q7", "open standards",
            "integration architecture", "q10", "mission engineering", "icf"
        ]
        tech_score = sum(1 for kw in tech_keywords if kw in q_lower)

        # Profile C: CRM Operational Graph Standalone (CQs 37-50)
        crm_keywords = [
            "submission identifier", "scoutcard", "submitted timestamp", "pipeline stage",
            "twenty crm", "48-hour", "callback timer", "point of contact", "poc 1", "poc 2",
            "poc", "phone", "email", "cell", "contact",
            "government sponsors", "sponsor 1", "technical 1", "user 1", "security preference",
            "q12", "funding to scale", "q5", "unit cost", "q6", "supply-chain constraints",
            "q4", "product rights", "crada", "government purpose rights", "export controlled",
            "itar", "human review queue", "intake program", "source system", "outreach event",
            "twenty portal", "intake record", "enter the portfolio", "transition partner", "risk ratings", "four-dimensional risk"
        ]
        crm_score = sum(1 for kw in crm_keywords if kw in q_lower)

        # Disambiguate highest score
        scores = [
            (org_score, RoutingProfile.ROUTE_ORG, ["organization_graph"], "Profile A: Standalone Organization Graph (CQs 01-18)"),
            (tech_score, RoutingProfile.ROUTE_TECH, ["technology_graph"], "Profile B: Standalone Technology Graph (CQs 19-36)"),
            (crm_score, RoutingProfile.ROUTE_CRM, ["crm_graph"], "Profile C: Standalone CRM Operational Graph (CQs 37-50)")
        ]
        scores.sort(key=lambda x: x[0], reverse=True)
        top_score, top_profile, top_mods, top_desc = scores[0]

        if top_score > 0:
            missing = [m for m in top_mods if m not in context.enabled_modules]
            if missing:
                return RoutingDecision(
                    route_profile=top_profile,
                    status="INSUFFICIENT_DEPLOYED_CAPABILITY",
                    selected_modules=[],
                    resolved_entities=resolved_ents,
                    expanded_terms=expanded_terms,
                    clean_query=query,
                    confidence=0.88,
                    reasons=[f"Required module {missing} is disabled in active deployment profile (CQ-76 Invariant)"]
                )
            return RoutingDecision(
                route_profile=top_profile,
                status="SUPPORTED",
                selected_modules=top_mods,
                resolved_entities=resolved_ents,
                expanded_terms=expanded_terms,
                clean_query=query,
                confidence=min(0.99, 0.70 + (top_score * 0.08)),
                reasons=[top_desc]
            )

        # Fallback default: If entity is known or ambiguous, default to minimum sufficient graph
        if resolved_ents:
            first_type = resolved_ents[0]["type"]
            if first_type == "Organization":
                return RoutingDecision(
                    route_profile=RoutingProfile.ROUTE_ORG,
                    status="SUPPORTED",
                    selected_modules=["organization_graph"],
                    resolved_entities=resolved_ents,
                    expanded_terms=expanded_terms,
                    clean_query=query,
                    confidence=0.75,
                    reasons=["Defaulted to ROUTE_ORG based on resolved Organization entity"]
                )
            elif first_type == "Offering":
                return RoutingDecision(
                    route_profile=RoutingProfile.ROUTE_TECH,
                    status="SUPPORTED",
                    selected_modules=["technology_graph"],
                    resolved_entities=resolved_ents,
                    expanded_terms=expanded_terms,
                    clean_query=query,
                    confidence=0.75,
                    reasons=["Defaulted to ROUTE_TECH based on resolved Offering entity"]
                )
            elif first_type == "CapabilitySubmission":
                return RoutingDecision(
                    route_profile=RoutingProfile.ROUTE_CRM,
                    status="SUPPORTED",
                    selected_modules=["crm_graph"],
                    resolved_entities=resolved_ents,
                    expanded_terms=expanded_terms,
                    clean_query=query,
                    confidence=0.75,
                    reasons=["Defaulted to ROUTE_CRM based on resolved Submission entity"]
                )

        # General Tri-Store fallback
        return RoutingDecision(
            route_profile=RoutingProfile.ROUTE_ALL_TRI_STORE,
            status="SUPPORTED",
            selected_modules=["organization_graph", "technology_graph", "crm_graph"],
            resolved_entities=[],
            expanded_terms=expanded_terms,
            clean_query=query,
            confidence=0.60,
            reasons=["Unconstrained query routed to general federated search across all 3 graphs"]
        )


_ROUTER = PreRetrievalRouter()


def route_user_query(query: str, context: Optional[CallerContext] = None) -> RoutingDecision:
    """Convenience functional interface for query routing."""
    return _ROUTER.route_query(query, context)


if __name__ == "__main__":
    sample_queries = [
        "What is Albacore's CAGE code and headquarters address?",
        "What is Ghostfin's TRL and operational range?",
        "What is the Twenty CRM pipeline stage and funding request for Vulcan submission 26705?",
        "Which U.S. Small Business startups offer technologies aligned to Counter C5ISR-T with TRL >= 6?",
        "Compare requested scaling funding in CRM against historical federal prime award volume",
        "Which capabilities combine high TRL and MRL with government purpose rights?",
        "Generate a complete MEIA Executive Business & Capability Dossier for Ghostfin: Long-Range, Hybrid Electric Medium UUV",
        "What is Ghostfin's acoustic signature decibel rating at 30 knots?",
        "What is Dante Vaisbort's personal cell phone number?"
    ]
    for sq in sample_queries:
        dec = route_user_query(sq)
        print(f"\nQuery: {sq}")
        print(f"  Route: {dec.route_profile.value} | Status: {dec.status} | Modules: {dec.selected_modules}")
        print(f"  Entities: {[e['name'] for e in dec.resolved_entities]} | Reasons: {dec.reasons[0]}")
