#!/usr/bin/env python3
"""Fail unless a KiCad JSON DRC report contains only approved J1 edge errors."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


J1_EDGE_NETS = {"GND", "USB_D+", "USB_D-", "VBUS", "CC1", "CC2"}


def is_approved_j1_edge_error(violation: dict) -> bool:
    if violation.get("type") != "copper_edge_clearance":
        return False

    for item in violation.get("items", []):
        description = item.get("description", "")
        if "Edge.Cuts" in description or "of J1" in description:
            continue

        pos = item.get("pos", {})
        net = next((name for name in J1_EDGE_NETS if f"[{name}]" in description), None)
        if (
            net
            and abs(float(pos.get("x", 999)) - 0.32) < 0.01
            and 25.5 <= float(pos.get("y", -999)) <= 34.5
        ):
            continue

        return False

    return True


def validate(report: dict) -> tuple[list[dict], list[dict]]:
    approved = []
    blocking = list(report.get("unconnected_items", []))

    for violation in report.get("violations", []):
        if violation.get("severity") != "error":
            continue
        if is_approved_j1_edge_error(violation):
            approved.append(violation)
        else:
            blocking.append(violation)

    return approved, blocking


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path, help="KiCad JSON DRC report")
    args = parser.parse_args()

    with args.report.open(encoding="utf-8") as report_file:
        report = json.load(report_file)

    approved, blocking = validate(report)
    warnings = [
        violation
        for violation in report.get("violations", [])
        if violation.get("severity") == "warning"
    ]

    print(
        f"DRC gate: {len(blocking)} blocking, "
        f"{len(approved)} approved J1 edge errors, {len(warnings)} warnings"
    )

    if blocking:
        counts = Counter(item.get("type", "unconnected_items") for item in blocking)
        for finding_type, count in sorted(counts.items()):
            print(f"  BLOCKING {finding_type}: {count}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
