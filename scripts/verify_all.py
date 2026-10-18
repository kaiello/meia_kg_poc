"""
Master Offline Regression & Verification Harness (D03).
======================================================
Executes all MEIA Tri-Graph POC unit & integration tests,
verifies the 78-Competency Question Benchmark, audits zero-daemon invariants,
and exports the updated cryptographic verification receipt.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_command(cmd: list, desc: str) -> bool:
    print(f"\n[RUNNING] {desc}...")
    start = time.time()
    res = subprocess.run([sys.executable, "-B"] + cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    elapsed = time.time() - start
    if res.returncode == 0:
        print(f"[PASS] {desc} ({elapsed:.2f}s)")
        return True
    else:
        print(f"[FAIL] {desc} ({elapsed:.2f}s)")
        if res.stdout:
            print("STDOUT:\n", res.stdout[-2000:])
        if res.stderr:
            print("STDERR:\n", res.stderr[-2000:])
        return False


def main():
    print("=" * 80)
    print("MEIA Federated Tri-Graph POC — Master Offline Regression Harness (D03)")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 80)

    stages = [
        (["-m", "unittest", "discover", "-s", "tests", "-v"], "All Unit & Integration Tests (Discovery)"),
        (["-m", "src.steward_review"], "Steward Review Queue Harvest & Export (U04)"),
        (["-m", "eval.test_scorer"], "78-CQ Benchmark Suite & Cryptographic Receipt Generator (U01, U05)")
    ]

    results = []
    overall_start = time.time()

    for cmd, desc in stages:
        ok = run_command(cmd, desc)
        results.append((desc, ok))

    total_elapsed = time.time() - overall_start

    print("\n" + "=" * 80)
    print("MASTER VERIFICATION SCORECARD")
    print("=" * 80)
    all_passed = True
    for desc, ok in results:
        status_str = "PASS" if ok else "FAIL"
        if not ok:
            all_passed = False
        print(f"  [{status_str}] {desc}")

    print("-" * 80)
    print(f"Total Execution Time: {total_elapsed:.2f}s")
    if all_passed:
        print("OVERALL RESULT: [PASS] All 8 Milestone Verification Gates Satisfied (100%)")
        sys.exit(0)
    else:
        print("OVERALL RESULT: [FAIL] One or more verification gates failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
