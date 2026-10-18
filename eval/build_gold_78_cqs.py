"""
Extracts and builds the golden 78 Competency Questions benchmark dataset
from docs/MEIA_Federated_78_Competency_Questions.md into eval/gold_78_cqs.json.
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CQ_DOC_PATH = REPO_ROOT / "docs" / "MEIA_Federated_78_Competency_Questions.md"
OUTPUT_JSON = REPO_ROOT / "eval" / "gold_78_cqs.json"

PROFILE_MAPPING = {
    range(1, 19): ("ROUTE_ORG", "SUPPORTED"),
    range(19, 37): ("ROUTE_TECH", "SUPPORTED"),
    range(37, 51): ("ROUTE_CRM", "SUPPORTED"),
    range(51, 58): ("ROUTE_ORG_TECH", "SUPPORTED"),
    range(58, 63): ("ROUTE_CRM_ORG", "SUPPORTED"),
    range(63, 68): ("ROUTE_CRM_TECH", "SUPPORTED"),
    range(68, 73): ("ROUTE_ALL_TRI_STORE", "SUPPORTED"),
    range(73, 76): ("FAIL_CLOSED_GATE", "SUPPORTED"),
    range(76, 77): ("FAIL_CLOSED_GATE", "INSUFFICIENT_DEPLOYED_CAPABILITY"),
    range(77, 78): ("FAIL_CLOSED_GATE", "ACCESS_DENIED"),
    range(78, 79): ("FAIL_CLOSED_GATE", "OUT_OF_SCOPE"),
}


def get_profile_and_status(num: int):
    for r, (prof, stat) in PROFILE_MAPPING.items():
        if num in r:
            return prof, stat
    return "ROUTE_ALL_TRI_STORE", "SUPPORTED"


def build_gold_dataset():
    if not CQ_DOC_PATH.exists():
        raise FileNotFoundError(f"Missing {CQ_DOC_PATH}")

    with open(CQ_DOC_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    # Match rows like: | **CQ-01** | Question text... | ... |
    pattern = re.compile(r"\|\s*\*\*CQ-(\d+)\*\*\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|")
    matches = pattern.findall(text)

    records = []
    seen = set()

    for m in matches:
        num = int(m[0])
        cq_id = f"CQ-{num:02d}"
        if cq_id in seen:
            continue
        seen.add(cq_id)

        query = m[1].strip()
        # Clean markdown bold/italics
        query = re.sub(r"\*\*([^*]+)\*\*", r"\1", query)
        query = re.sub(r"`([^`]+)`", r"\1", query)
        # Strip leading titles like "Exact Evidence Locator & Provenance Trace: " if bolded
        if ":" in query and num in range(73, 79):
            # Keep question part or full text
            pass

        readiness = m[2].strip()
        concepts = m[3].strip()
        details = m[4].strip()

        profile, status = get_profile_and_status(num)

        # Entity targets and locator expectations based on question domain
        target_entities = []
        expected_locators = []
        if "albacore" in query.lower() or "ghostfin" in query.lower() or num in (1, 2, 3, 19, 21, 22, 23, 28, 29, 31, 32, 37, 39, 41, 42, 43, 51, 68):
            target_entities.append("org:albacore")
            target_entities.append("tech:ghostfin_uuv")
            expected_locators.append("MEIA_TEM_Vulcan_Export.xlsx!Vulcan Submissions!R2C4")
        if "voltage" in query.lower() or "voltvessel" in query.lower() or "eclipse" in query.lower() or num in (69,):
            target_entities.append("org:voltage_vessels")
            target_entities.append("tech:voltvessel_energy")
            expected_locators.append("MEIA_TEM_Vulcan_Export.xlsx!Vulcan Submissions!R3C4")
        if "t2s" in query.lower() or "microgrid" in query.lower() or "counter sensing" in query.lower() or num in (70,):
            target_entities.append("org:t2s_solutions")
            target_entities.append("tech:tactical_microgrid")
            expected_locators.append("MEIA_TEM_Vulcan_Export.xlsx!Vulcan Submissions!R4C4")
        if "fluor" in query.lower() or num in (11, 12, 13, 15, 17, 18):
            target_entities.append("org:fluor_federal")
            expected_locators.append("usaspending:CONT_AWD_DEDT0007774")
        if "klas" in query.lower() or num in (6, 14, 16, 21, 30, 35, 54, 56, 71):
            target_entities.append("org:klas_gov")
            expected_locators.append("usaspending:CONT_AWD_M0026411P0469")
        if "prometheus" in query.lower() or num in (7, 55, 72):
            target_entities.append("org:prometheus_intelligence")
            expected_locators.append("usaspending:CONT_AWD_697DCK_24_C_00237")

        rec = {
            "cq_id": cq_id,
            "query": query,
            "expected_profile": profile,
            "expected_status": status,
            "readiness": readiness,
            "target_entities": list(set(target_entities)),
            "expected_locators": expected_locators,
            "notes": details[:200]
        }
        records.append(rec)

    records.sort(key=lambda x: int(x["cq_id"].split("-")[1]))

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print(f"Successfully compiled {len(records)} CQs to {OUTPUT_JSON}")
    return records


if __name__ == "__main__":
    build_gold_dataset()
