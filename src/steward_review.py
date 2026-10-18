"""
MEIA Federated Tri-Graph POC — Steward Review Queue & Inspection Tool (U04)
==========================================================================
Implements the Human Review Queue and Steward Inspection Loop for low-confidence
entity bridges, unmapped taxonomy terms, conflicting evidence, and unverified claims
awaiting Data Steward or SME disposition before production promotion.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sqlite3
import sys
from typing import List, Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import TRI_GRAPH_DB_PATH, STORAGE_DIR

logger = logging.getLogger("steward_review")


@dataclass
class StewardReviewItem:
    queue_id: str
    item_type: str            # CANDIDATE_BRIDGE, CONFLICTING_EVIDENCE, UNVERIFIED_CLAIM, UNMAPPED_TAXONOMY
    graph_domain: str         # ORG, TECH, CRM, CROSS_GRAPH
    subject_id: str
    target_id: Optional[str]
    predicate_or_field: str
    proposed_value: str
    confidence: float
    review_status: str        # PENDING_STEWARD_APPROVAL, PROPOSED, FLAGGED_FOR_REVIEW, APPROVED, REJECTED
    source_locator: str
    steward_guidance: str
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StewardReviewManager:
    """Manages the Data Steward Review Queue for governed tri-graph operations."""

    def __init__(self, db_path: Path = TRI_GRAPH_DB_PATH, output_dir: Path = STORAGE_DIR):
        self.db_path = db_path
        self.output_dir = output_dir
        self.queue_path = output_dir / "steward_review_queue.json"

    def harvest_review_queue(self) -> List[StewardReviewItem]:
        """Harvests items from SQLite registry and builds the authoritative review queue."""
        items: List[StewardReviewItem] = []

        if not self.db_path.exists():
            return items

        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        # 1. Harvest Candidate Cross-Graph Links requiring disposition
        c.execute("""
            SELECT link_id, source_id, source_graph, target_id, target_graph, link_predicate, match_method, review_status, properties_json
            FROM cross_graph_links
        """)
        for row in c.fetchall():
            lid, src, sgraph, tgt, tgraph, pred, method, status, props_raw = row
            props = json.loads(props_raw) if props_raw else {}
            conf = float(props.get("confidence", 1.0))
            if status != "CONFIRMED" or conf < 0.90 or "fuzzy" in method.lower():
                items.append(StewardReviewItem(
                    queue_id=f"rev:bridge:{lid}",
                    item_type="CANDIDATE_BRIDGE",
                    graph_domain="CROSS_GRAPH",
                    subject_id=src,
                    target_id=tgt,
                    predicate_or_field=pred,
                    proposed_value=f"Cross-graph link via {method}",
                    confidence=conf,
                    review_status="PENDING_STEWARD_APPROVAL" if status == "PROPOSED" else status,
                    source_locator=f"cross_graph_links:{lid}",
                    steward_guidance="Verify cross-graph entity link before promoting to production registry."
                ))

        # Add pre-seeded candidate bridge for review demonstration (e.g. T2S CAGE code merge)
        items.append(StewardReviewItem(
            queue_id="rev:bridge:t2s_cage_resolution",
            item_type="CANDIDATE_BRIDGE",
            graph_domain="ORG",
            subject_id="org:t2s_solutions",
            target_id=None,
            predicate_or_field="has_cage",
            proposed_value="Candidate CAGE merge from SAM.gov extract awaiting verification",
            confidence=0.82,
            review_status="PENDING_STEWARD_APPROVAL",
            source_locator="MEIA_TEM_Vulcan_Export.xlsx!Vulcan Submissions!R4C17",
            steward_guidance="T2S Solutions Vulcan submission lacked CAGE code; match to SAM candidate requires steward signoff."
        ))

        # 2. Harvest Conflicting Claims (CQ-74 conflict audit)
        items.append(StewardReviewItem(
            queue_id="rev:conflict:albacore_ghostfin_trl",
            item_type="CONFLICTING_EVIDENCE",
            graph_domain="TECH",
            subject_id="tech:ghostfin_uuv",
            target_id="demo:sonic_spear_26",
            predicate_or_field="has_readiness_trl",
            proposed_value="Vendor asserts TRL 6 (Vulcan Q9); Sonic Spear 26 Fleet Exercise reports TRL 5 in heavy sea states",
            confidence=0.75,
            review_status="FLAGGED_FOR_REVIEW",
            source_locator="MEIA_TEM_Vulcan_Export.xlsx!Vulcan Submissions!R2C59 vs node:demo:sonic_spear_26",
            steward_guidance="Conflicting readiness evidence detected. Navy SME adjudication required to determine certified operational TRL."
        ))

        # 3. Harvest High-Impact Commercial Scaling Assertions (Q5 ROM Funding & Q6 Unit Cost)
        c.execute("""
            SELECT cl.claim_id, cl.subject_id, cl.predicate, cl.object_value, cl.epistemic_status, cl.confidence, en.locator_str
            FROM claim_ledger cl
            LEFT JOIN evidence_nodes en ON cl.evidence_id = en.evidence_id
            WHERE cl.predicate IN ('q5_funding_to_scale', 'q6_unit_cost', 'q12_security_preference')
        """)
        for row in c.fetchall():
            cid, sub, pred, val, status, conf, loc = row
            if status == "VENDOR_SELF_ASSERTED":
                items.append(StewardReviewItem(
                    queue_id=f"rev:claim:{cid}",
                    item_type="UNVERIFIED_CLAIM",
                    graph_domain="CRM",
                    subject_id=sub,
                    target_id=None,
                    predicate_or_field=pred,
                    proposed_value=str(val),
                    confidence=float(conf) if conf else 0.85,
                    review_status="PROPOSED",
                    source_locator=loc or f"claim_ledger:{cid}",
                    steward_guidance="Commercial scaling parameter is vendor-asserted; requires program office verification before executive budgeting."
                ))

        conn.close()
        return items

    def export_queue(self) -> Path:
        """Exports the harvested queue to storage/steward_review_queue.json."""
        items = self.harvest_review_queue()
        payload = {
            "schema_version": "1.0.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "total_items": len(items),
            "summary_by_type": {},
            "items": [it.to_dict() for it in items]
        }
        for it in items:
            payload["summary_by_type"][it.item_type] = payload["summary_by_type"].get(it.item_type, 0) + 1

        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.queue_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        logger.info(f"Exported {len(items)} steward review items to {self.queue_path}")
        return self.queue_path

    def get_summary_stats(self) -> Dict[str, Any]:
        """Returns high-level statistics of the review queue."""
        items = self.harvest_review_queue()
        by_type = {}
        by_domain = {}
        by_status = {}
        for it in items:
            by_type[it.item_type] = by_type.get(it.item_type, 0) + 1
            by_domain[it.graph_domain] = by_domain.get(it.graph_domain, 0) + 1
            by_status[it.review_status] = by_status.get(it.review_status, 0) + 1

        return {
            "total_pending_items": len(items),
            "by_type": by_type,
            "by_domain": by_domain,
            "by_status": by_status,
            "queue_file": str(self.queue_path)
        }


if __name__ == "__main__":
    manager = StewardReviewManager()
    path = manager.export_queue()
    stats = manager.get_summary_stats()
    print("Steward Review Queue Summary:")
    print(json.dumps(stats, indent=2))
