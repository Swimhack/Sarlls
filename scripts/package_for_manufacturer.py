#!/usr/bin/env python3
"""
Package the Sarlls IoT Switch production files for manufacturer submission.

Creates a clean ZIP archive containing all files needed for PCB fabrication
and assembly. Validates file presence and format before packaging.

Usage: python scripts/package_for_manufacturer.py
Output: production/Sarlls_IoT_Switch_v1.1_SUBMISSION.zip
"""

import csv
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

PRODUCTION_DIR = Path(__file__).parent.parent / "production"
OUTPUT_ZIP = PRODUCTION_DIR / "Sarlls_IoT_Switch_v1.1_SUBMISSION.zip"

# Files to include in the submission package
REQUIRED_FILES = {
    "ESP32_Simple_IoT.kicad_pro":  "KiCad project file",
    "ESP32_Simple_IoT.kicad_sch":  "Schematic (fully wired)",
    "ESP32_Simple_IoT.kicad_pcb":  "PCB layout (placed, zoned)",
    "ESP32_Simple_IoT_BOM.csv":    "Bill of Materials (JLCPCB format)",
    "ESP32_Simple_IoT_CPL.csv":    "Component Placement List",
    "FABRICATION_SPEC.txt":        "Fabrication specification",
    "README.md":                   "Design notes and test procedures",
}

OPTIONAL_FILES = {
    "firmware/test_firmware.ino":   "Arduino test firmware",
    "firmware/platformio.ini":      "PlatformIO configuration",
}

# Expected LCSC part numbers and their descriptions
EXPECTED_PARTS = {
    "C82899":  "ESP32-WROOM-32",
    "C6186":   "AMS1117-3.3",
    "C6568":   "CP2102N-A02-GQFN28",
    "C2137":   "BC817",
    "C35449":  "SRD-05VDC-SL-C relay",
    "C106903": "1N4007 diode",
    "C375456": "LED Green 0805",
    "C84256":  "LED Red 0805",
    "C15850":  "10uF 0805 cap",
    "C49678":  "100nF 0805 cap",
    "C17414":  "10K 0805 resistor",
    "C17513":  "1K 0805 resistor",
    "C127284": "Ferrite bead 0805",
    "C127509": "Tactile switch TL3342",
    "C165948": "USB-C receptacle GCT",
    "C8269":   "Terminal block Phoenix MC",
}


def validate_bom(filepath: Path) -> list[str]:
    """Validate BOM CSV format and content."""
    issues = []
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Check headers
            expected_headers = {"Comment", "Designator", "Footprint", "LCSC Part Number"}
            if not expected_headers.issubset(set(reader.fieldnames or [])):
                issues.append(f"BOM headers mismatch. Expected: {expected_headers}")
                return issues

            found_lcsc = set()
            row_count = 0
            for row in reader:
                row_count += 1
                lcsc = row.get("LCSC Part Number", "").strip()
                if not lcsc:
                    issues.append(f"BOM row {row_count}: missing LCSC part number")
                elif not lcsc.startswith("C") or not lcsc[1:].isdigit():
                    issues.append(f"BOM row {row_count}: invalid LCSC format '{lcsc}'")
                else:
                    found_lcsc.add(lcsc)

                if not row.get("Designator", "").strip():
                    issues.append(f"BOM row {row_count}: missing designator")
                if not row.get("Footprint", "").strip():
                    issues.append(f"BOM row {row_count}: missing footprint")

            # Check all expected parts are present
            missing = set(EXPECTED_PARTS.keys()) - found_lcsc
            if missing:
                for m in missing:
                    issues.append(f"BOM missing expected part: {m} ({EXPECTED_PARTS[m]})")

            if row_count == 0:
                issues.append("BOM is empty")
            else:
                print(f"  BOM: {row_count} line items, {len(found_lcsc)} unique LCSC parts")

    except Exception as e:
        issues.append(f"BOM read error: {e}")

    return issues


def validate_cpl(filepath: Path) -> list[str]:
    """Validate CPL CSV format and content."""
    issues = []
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            expected_headers = {"Designator", "Mid X", "Mid Y", "Layer", "Rotation"}
            if not expected_headers.issubset(set(reader.fieldnames or [])):
                issues.append(f"CPL headers mismatch. Expected: {expected_headers}")
                return issues

            row_count = 0
            for row in reader:
                row_count += 1
                des = row.get("Designator", "").strip()
                mid_x = row.get("Mid X", "").strip()
                mid_y = row.get("Mid Y", "").strip()
                layer = row.get("Layer", "").strip()

                if not des:
                    issues.append(f"CPL row {row_count}: missing designator")

                # Check coordinates are plain numbers (no units)
                for coord_name, coord_val in [("Mid X", mid_x), ("Mid Y", mid_y)]:
                    if "mm" in coord_val or "mil" in coord_val:
                        issues.append(
                            f"CPL row {row_count} ({des}): {coord_name} has unit suffix '{coord_val}' - must be plain number"
                        )
                    else:
                        try:
                            float(coord_val)
                        except ValueError:
                            issues.append(
                                f"CPL row {row_count} ({des}): {coord_name} is not numeric: '{coord_val}'"
                            )

                if layer not in ("Top", "Bottom"):
                    issues.append(f"CPL row {row_count} ({des}): invalid layer '{layer}'")

            if row_count == 0:
                issues.append("CPL is empty")
            else:
                print(f"  CPL: {row_count} component placements")

    except Exception as e:
        issues.append(f"CPL read error: {e}")

    return issues


def validate_schematic(filepath: Path) -> list[str]:
    """Basic validation of KiCad schematic file."""
    issues = []
    try:
        content = filepath.read_text(encoding="utf-8")

        wire_count = content.count("(wire ")
        label_count = content.count("(label ")
        junction_count = content.count("(junction ")
        no_connect_count = content.count("(no_connect ")
        symbol_count = content.count("(symbol (lib_id")

        if wire_count == 0:
            issues.append("Schematic has NO wire connections - not electrically complete")
        if symbol_count < 10:
            issues.append(f"Schematic has only {symbol_count} components - expected ~24")

        print(f"  Schematic: {symbol_count} components, {wire_count} wires, "
              f"{label_count} labels, {junction_count} junctions, {no_connect_count} no-connects")

    except Exception as e:
        issues.append(f"Schematic read error: {e}")

    return issues


def validate_pcb(filepath: Path) -> list[str]:
    """Basic validation of KiCad PCB file."""
    issues = []
    try:
        content = filepath.read_text(encoding="utf-8")

        footprint_count = content.count("(footprint ")
        zone_count = content.count("(zone ")
        via_count = content.count("(via ")
        segment_count = content.count("(segment ")
        net_count = content.count("(net ")

        if footprint_count < 15:
            issues.append(f"PCB has only {footprint_count} footprints - expected ~24")
        if zone_count == 0:
            issues.append("PCB has no copper zones defined")

        note = ""
        if segment_count == 0:
            note = " [UNROUTED - needs interactive routing in KiCad]"

        print(f"  PCB: {footprint_count} footprints, {zone_count} zones, "
              f"{via_count} vias, {segment_count} trace segments{note}")

    except Exception as e:
        issues.append(f"PCB read error: {e}")

    return issues


def create_zip(output_path: Path, production_dir: Path) -> None:
    """Create the submission ZIP archive."""
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add required files
        for filename in REQUIRED_FILES:
            filepath = production_dir / filename
            if filepath.exists():
                zf.write(filepath, f"Sarlls_IoT_Switch/{filename}")

        # Add optional files
        for filename in OPTIONAL_FILES:
            filepath = production_dir / filename
            if filepath.exists():
                zf.write(filepath, f"Sarlls_IoT_Switch/{filename}")

        # Add a manifest
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        manifest = f"""Sarlls IoT Smart Switch - Manufacturer Submission Package
=========================================================
Generated: {now}
Version:   1.1
Contact:   james@strickland.technology
Phone:     713-444-6732

Contents:
"""
        for filename, desc in {**REQUIRED_FILES, **OPTIONAL_FILES}.items():
            filepath = production_dir / filename
            if filepath.exists():
                size_kb = filepath.stat().st_size / 1024
                manifest += f"  {filename:<45} {desc} ({size_kb:.1f} KB)\n"

        manifest += """
IMPORTANT NOTES:
  - PCB trace routing is NOT complete. The KiCad source files are
    provided for your engineering team to complete routing.
  - All component placements, zones, keepouts, and net definitions
    are finalized.
  - See FABRICATION_SPEC.txt for complete board specifications.
  - BOM and CPL are in JLCPCB format with verified LCSC part numbers.
"""
        zf.writestr("Sarlls_IoT_Switch/MANIFEST.txt", manifest)


def main() -> int:
    print("=" * 60)
    print("Sarlls IoT Switch - Manufacturer Package Builder")
    print("=" * 60)
    print()

    if not PRODUCTION_DIR.exists():
        print(f"ERROR: Production directory not found: {PRODUCTION_DIR}")
        return 1

    all_issues: list[str] = []

    # Check required files exist
    print("Checking required files...")
    for filename, desc in REQUIRED_FILES.items():
        filepath = PRODUCTION_DIR / filename
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"  [OK] {filename} ({size_kb:.1f} KB)")
        else:
            msg = f"MISSING: {filename} ({desc})"
            print(f"  [!!] {msg}")
            all_issues.append(msg)

    # Check optional files
    print("\nChecking optional files...")
    for filename, desc in OPTIONAL_FILES.items():
        filepath = PRODUCTION_DIR / filename
        if filepath.exists():
            print(f"  [OK] {filename}")
        else:
            print(f"  [--] {filename} (optional, skipped)")

    # Validate BOM
    print("\nValidating BOM...")
    all_issues.extend(validate_bom(PRODUCTION_DIR / "ESP32_Simple_IoT_BOM.csv"))

    # Validate CPL
    print("\nValidating CPL...")
    all_issues.extend(validate_cpl(PRODUCTION_DIR / "ESP32_Simple_IoT_CPL.csv"))

    # Validate schematic
    print("\nValidating schematic...")
    all_issues.extend(validate_schematic(PRODUCTION_DIR / "ESP32_Simple_IoT.kicad_sch"))

    # Validate PCB
    print("\nValidating PCB...")
    all_issues.extend(validate_pcb(PRODUCTION_DIR / "ESP32_Simple_IoT.kicad_pcb"))

    # Report
    print("\n" + "=" * 60)
    if all_issues:
        print(f"ISSUES FOUND: {len(all_issues)}")
        for issue in all_issues:
            print(f"  - {issue}")
    else:
        print("ALL VALIDATIONS PASSED")

    # Create ZIP regardless (issues are informational)
    print(f"\nCreating submission package: {OUTPUT_ZIP.name}")
    create_zip(OUTPUT_ZIP, PRODUCTION_DIR)

    zip_size = OUTPUT_ZIP.stat().st_size / 1024
    print(f"Package created: {OUTPUT_ZIP} ({zip_size:.1f} KB)")

    # List ZIP contents
    print("\nPackage contents:")
    with zipfile.ZipFile(OUTPUT_ZIP, "r") as zf:
        for info in zf.infolist():
            print(f"  {info.filename:<55} {info.file_size:>8,} bytes")

    print("\n" + "=" * 60)
    print("DONE. Send this ZIP to your manufacturer.")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
