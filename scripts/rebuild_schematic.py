#!/usr/bin/env python3
"""
Rebuild the ESP32 Simple IoT Switch schematic in KiCad 9 format.

This script:
1. Reads the existing schematic (KiCad 7 format)
2. Extracts lib_symbols, placed symbols, text blocks
3. Transforms everything to KiCad 9 format (version 20250114)
4. Generates complete wire connections for every net
5. Outputs a valid KiCad 9 schematic file

KiCad 9 format requirements vs KiCad 7:
  - (version 20250114) + (generator "eeschema") + (generator_version "9.0")
  - (exclude_from_sim no) on lib_symbols and placed symbols
  - (instances ...) inside each placed symbol (not symbol_instances at root)
  - (embedded_fonts no) at end of file
"""

import re
import math
import uuid
from pathlib import Path


# Global UUID counter for deterministic generation
_uuid_counter = 0

def next_uuid():
    """Generate a valid UUID-4 format string."""
    global _uuid_counter
    _uuid_counter += 1
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"sarlls-iot-wire-{_uuid_counter}"))

SCHEMATIC = Path(__file__).parent.parent / "production" / "ESP32_Simple_IoT.kicad_sch"

# ============================================================
# PIN POSITION DATA
# ============================================================
# Pre-computed from lib_symbol definitions. Each entry:
#   lib_id: {pin_number: (rel_x, rel_y)}
# These are the connectable endpoints relative to symbol center.

LIB_PINS = {
    'Connector:USB_C_Receptacle_USB2.0': {
        'A4': (0, 20.32),       # VBUS
        'A6': (12.7, 7.62),     # D+
        'A7': (12.7, 5.08),     # D-
        'A1': (0, -20.32),      # GND
        'S1': (-12.7, 0),       # SHIELD
    },
    'Device:Ferrite_Bead': {
        '1': (0, 3.81),
        '2': (0, -3.81),
    },
    'Device:C': {
        '1': (0, 3.81),
        '2': (0, -3.81),
    },
    'Regulator_Linear:AMS1117-3.3': {
        '1': (0, -7.62),        # GND
        '2': (7.62, 0),         # VO
        '3': (-7.62, 0),        # VI
    },
    'MCU_Module:ESP32-WROOM-32': {
        '1': (0, -19.05),       # GND
        '2': (0, 19.05),        # 3V3
        '3': (-15.24, 12.7),    # EN
        '25': (15.24, -12.7),   # IO0
        '26': (15.24, 2.54),    # IO4
        '29': (15.24, 0),       # IO5
        '34': (15.24, 7.62),    # RXD0
        '35': (15.24, 10.16),   # TXD0
        '38': (0, -19.05),      # GND
        '39': (0, -19.05),      # GND
    },
    'Interface_USB:CP2102N-A02-GQFN28': {
        '3': (0, -22.86),       # GND
        '4': (-12.7, 15.24),    # D+
        '5': (-12.7, 12.7),     # D-
        '6': (0, 22.86),        # VDD
        '8': (-12.7, -10.16),   # VBUS
        '25': (12.7, 12.7),     # RXD
        '26': (12.7, 15.24),    # TXD
        '27': (12.7, 7.62),     # DTR
        '28': (12.7, 5.08),     # RTS
    },
    'Device:R': {
        '1': (0, 3.81),
        '2': (0, -3.81),
    },
    'Device:LED': {
        '1': (-3.81, 0),        # K (cathode)
        '2': (3.81, 0),         # A (anode)
    },
    'Switch:SW_Push': {
        '1': (-5.08, 0),
        '2': (5.08, 0),
    },
    'Transistor_BJT:BC817': {
        '1': (2.54, -5.08),     # E (emitter)
        '2': (-5.08, 0),        # B (base)
        '3': (2.54, 5.08),      # C (collector)
    },
    'Diode:1N4007': {
        '1': (-3.81, 0),        # K (cathode)
        '2': (3.81, 0),         # A (anode)
    },
    'Relay:SANYOU_SRD_Form_C': {
        '1': (0, -6.35),        # Coil-
        '2': (0, 6.35),         # Coil+
        '3': (-6.35, -1.27),    # NC
        '4': (-6.35, 1.27),     # NO
        '5': (6.35, 0),         # COM
    },
    'Connector_Generic:Conn_01x02': {
        '1': (-5.08, 0),        # Pin_1
        '2': (-5.08, -2.54),    # Pin_2
    },
    # Power symbols have pin at (0,0)
    'power:GND': {'1': (0, 0)},
    'power:+5V': {'1': (0, 0)},
    'power:+3V3': {'1': (0, 0)},
}

# Component placements: (ref, lib_id, x, y, rot)
PLACEMENTS = [
    ('J1',  'Connector:USB_C_Receptacle_USB2.0', 38.1, 63.5, 0),
    ('FB1', 'Device:Ferrite_Bead', 63.5, 43.18, 90),
    ('C1',  'Device:C', 76.2, 50.8, 0),
    ('U2',  'Regulator_Linear:AMS1117-3.3', 91.44, 43.18, 0),
    ('C2',  'Device:C', 106.68, 50.8, 0),
    ('C3',  'Device:C', 116.84, 50.8, 0),
    ('U1',  'MCU_Module:ESP32-WROOM-32', 165.1, 101.6, 0),
    ('R1',  'Device:R', 139.7, 83.82, 0),
    ('C4',  'Device:C', 139.7, 96.52, 0),
    ('R2',  'Device:R', 193.04, 107.95, 0),
    ('SW1', 'Switch:SW_Push', 193.04, 121.92, 90),
    ('SW2', 'Switch:SW_Push', 127.0, 96.52, 90),
    ('C5',  'Device:C', 154.94, 78.74, 0),
    ('U3',  'Interface_USB:CP2102N-A02-GQFN28', 63.5, 101.6, 0),
    ('R3',  'Device:R', 220.98, 99.06, 0),
    ('Q1',  'Transistor_BJT:BC817', 233.68, 99.06, 0),
    ('K1',  'Relay:SANYOU_SRD_Form_C', 251.46, 83.82, 0),
    ('D1',  'Diode:1N4007', 236.22, 78.74, 270),
    ('J2',  'Connector_Generic:Conn_01x02', 274.32, 83.82, 0),
    ('D2',  'Device:LED', 127.0, 48.26, 0),
    ('R4',  'Device:R', 139.7, 48.26, 90),
    ('D3',  'Device:LED', 203.2, 99.06, 180),
    ('R5',  'Device:R', 191.77, 99.06, 90),
]


def rotate_point(x, y, angle_deg):
    """Rotate point by angle_deg counterclockwise (standard KiCad convention)."""
    if angle_deg == 0:
        return x, y
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    rx = x * cos_a - y * sin_a
    ry = x * sin_a + y * cos_a
    return round(rx, 4), round(ry, 4)


def pin_pos(ref, pin_num):
    """Get absolute schematic position of a pin."""
    for r, lib_id, sx, sy, srot in PLACEMENTS:
        if r == ref:
            pins = LIB_PINS.get(lib_id, {})
            if pin_num not in pins:
                raise ValueError(f"{ref} pin {pin_num} not in lib_pins for {lib_id}")
            px, py = pins[pin_num]
            rpx, rpy = rotate_point(px, py, srot)
            # Y-negate: lib_symbols use Y-up, schematic uses Y-down
            ax = round(sx + rpx, 2)
            ay = round(sy - rpy, 2)
            return ax, ay
    raise ValueError(f"Component {ref} not found in placements")


def pwr_pin_pos(pwr_ref, value, x, y):
    """Get power symbol pin position. Pin is at symbol origin."""
    return round(x, 2), round(y, 2)


# ============================================================
# NETLIST
# ============================================================

def build_netlist():
    """Build the complete netlist with computed positions."""
    nets = {}

    # === POWER PATH: USB-C -> Ferrite -> +5V ===
    nets['VBUS_TO_FB'] = [
        pin_pos('J1', 'A4'),     # USB-C VBUS
        pin_pos('FB1', '1'),     # Ferrite input
    ]

    nets['+5V_RAIL'] = [
        pin_pos('FB1', '2'),     # Ferrite output
        pin_pos('C1', '1'),      # Bulk cap
        pin_pos('U2', '3'),      # AMS1117 VI
    ]

    nets['+5V_RELAY'] = [
        pin_pos('K1', '2'),      # Relay coil+
        pin_pos('D1', '1'),      # Flyback cathode
    ]

    # === 3.3V RAIL ===
    nets['+3V3_CAPS'] = [
        pin_pos('U2', '2'),      # AMS1117 VO
        pin_pos('C2', '1'),      # Output cap 1
        pin_pos('C3', '1'),      # Output cap 2
    ]

    # === ESP32 CONNECTIONS ===
    nets['EN_NET'] = [
        pin_pos('U1', '3'),      # ESP32 EN
        pin_pos('R1', '2'),      # Pullup bottom
        pin_pos('C4', '1'),      # EN cap top
        pin_pos('SW2', '2'),     # Reset button
    ]

    nets['IO0_NET'] = [
        pin_pos('U1', '25'),     # ESP32 IO0
        pin_pos('R2', '2'),      # Pullup bottom
        pin_pos('SW1', '2'),     # Boot button
    ]

    nets['IO4_TO_R3'] = [
        pin_pos('U1', '26'),     # ESP32 IO4
        pin_pos('R3', '1'),      # Base resistor top
    ]

    nets['IO5_TO_R5'] = [
        pin_pos('U1', '29'),     # ESP32 IO5
        pin_pos('R5', '1'),      # LED resistor
    ]

    nets['UART_TX'] = [
        pin_pos('U1', '35'),     # ESP32 TXD0
        pin_pos('U3', '25'),     # CP2102N RXD
    ]

    # UART_RX needs 3-segment route to avoid U3:DTR at (76.2, 93.98)
    rx_start = pin_pos('U1', '34')   # ESP32 RXD0 -> (180.34, 93.98)
    rx_end = pin_pos('U3', '26')     # CP2102N TXD -> (76.2, 86.36)
    nets['UART_RX'] = [
        rx_start,
        (78.74, rx_start[1]),        # Horizontal to x=78.74 (avoids DTR at x=76.2)
        (78.74, rx_end[1]),          # Vertical at x=78.74
        rx_end,                       # Short horizontal to TXD pin
    ]

    # === USB DATA ===
    nets['USB_DP'] = [
        pin_pos('J1', 'A6'),     # USB D+
        pin_pos('U3', '4'),      # CP2102N D+
    ]

    nets['USB_DM'] = [
        pin_pos('J1', 'A7'),     # USB D-
        pin_pos('U3', '5'),      # CP2102N D-
    ]

    # === RELAY DRIVER ===
    nets['RELAY_DRIVE'] = [
        pin_pos('R3', '2'),      # Base resistor bottom
        pin_pos('Q1', '2'),      # BC817 base
    ]

    nets['RELAY_COIL_LO'] = [
        pin_pos('Q1', '3'),      # BC817 collector
        pin_pos('K1', '1'),      # Relay coil-
        pin_pos('D1', '2'),      # Flyback anode
    ]

    # === RELAY OUTPUT ===
    nets['RELAY_COM'] = [
        pin_pos('K1', '5'),      # Relay COM
        pin_pos('J2', '1'),      # Terminal 1
    ]

    nets['RELAY_NO'] = [
        pin_pos('K1', '4'),      # Relay NO
        pin_pos('J2', '2'),      # Terminal 2
    ]

    # === STATUS LEDs ===
    nets['LED_PWR'] = [
        pin_pos('R4', '1'),      # Power LED resistor
        pin_pos('D2', '2'),      # D2 anode
    ]

    nets['LED_RELAY'] = [
        pin_pos('R5', '2'),      # Relay LED resistor
        pin_pos('D3', '2'),      # D3 anode
    ]

    return nets


def build_power_wires():
    """Build wires connecting non-coincident power symbols to component pins."""
    wires = []

    # GND wires (non-coincident power symbols)
    wires.append(((119.38, 48.26), pin_pos('D2', '1')))
    wires.append(((210.82, 99.06), pin_pos('D3', '1')))
    wires.append(((25.40, 66.04), pin_pos('J1', 'S1')))

    # +5V wires
    fb1_pin2 = pin_pos('FB1', '2')
    if abs(fb1_pin2[0] - 67.31) > 0.01 or abs(fb1_pin2[1] - 43.18) > 0.01:
        wires.append(((67.31, 43.18), fb1_pin2))

    wires.append(((236.22, 69.85), pin_pos('D1', '1')))
    wires.append(((50.80, 114.30), pin_pos('U3', '8')))

    # +3V3 wires (non-coincident)
    r4_pin2 = pin_pos('R4', '2')
    if abs(r4_pin2[0] - 143.51) > 0.01 or abs(r4_pin2[1] - 48.26) > 0.01:
        wires.append(((143.51, 48.26), r4_pin2))

    r1_pin1 = pin_pos('R1', '1')
    if abs(r1_pin1[0] - 139.7) > 0.01 or abs(r1_pin1[1] - 80.01) > 0.01:
        wires.append(((139.7, 80.01), r1_pin1))

    r2_pin1 = pin_pos('R2', '1')
    if abs(r2_pin1[0] - 193.04) > 0.01 or abs(r2_pin1[1] - 104.14) > 0.01:
        wires.append(((193.04, 104.14), r2_pin1))

    c5_pin1 = pin_pos('C5', '1')
    if abs(c5_pin1[0] - 154.94) > 0.01 or abs(c5_pin1[1] - 74.93) > 0.01:
        wires.append(((154.94, 74.93), c5_pin1))

    return wires


# ============================================================
# WIRE GENERATION
# ============================================================

def make_wire_sexp(x1, y1, x2, y2):
    """Generate a KiCad wire S-expression."""
    uid = next_uuid()
    return (
        f'  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))\n'
        f'    (stroke (width 0) (type default))\n'
        f'    (uuid {uid})\n'
        f'  )'
    )


def make_junction_sexp(x, y):
    """Generate a junction S-expression."""
    uid = next_uuid()
    return (
        f'  (junction (at {x} {y}) (diameter 0) (color 0 0 0 0)\n'
        f'    (uuid {uid})\n'
        f'  )'
    )


def make_noconnect_sexp(x, y):
    """Generate a no-connect flag S-expression."""
    uid = next_uuid()
    return f'  (no_connect (at {x} {y}) (uuid {uid}))'


def generate_net_wires(positions):
    """Generate wires connecting a chain of positions (Manhattan routing)."""
    wires = []
    junctions = []

    for i in range(len(positions) - 1):
        x1, y1 = positions[i]
        x2, y2 = positions[i + 1]

        if abs(x1 - x2) < 0.01 and abs(y1 - y2) < 0.01:
            continue

        if abs(x1 - x2) < 0.01 or abs(y1 - y2) < 0.01:
            wires.append(make_wire_sexp(x1, y1, x2, y2))
        else:
            mid_x, mid_y = x2, y1
            wires.append(make_wire_sexp(x1, y1, mid_x, mid_y))
            wires.append(make_wire_sexp(mid_x, mid_y, x2, y2))

        if i > 0:
            jx, jy = positions[i]
            junctions.append(make_junction_sexp(jx, jy))

    return wires, junctions


# ============================================================
# S-EXPRESSION PARSING HELPERS
# ============================================================

def find_block_end(text, start):
    """Find the closing paren of the S-expression starting at 'start'.
    Returns index of the closing paren."""
    depth = 0
    in_string = False
    for i in range(start, len(text)):
        c = text[i]
        if c == '"' and (i == 0 or text[i - 1] != '\\'):
            in_string = not in_string
        elif not in_string:
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    return i
    return -1


def extract_top_blocks(content):
    """Extract all top-level S-expression blocks from kicad_sch content.
    Returns list of (block_type, block_text) tuples."""
    blocks = []

    # Skip the opening (kicad_sch ...) line
    first_newline = content.index('\n')
    i = first_newline + 1

    while i < len(content):
        # Skip whitespace
        while i < len(content) and content[i] in ' \t\n\r':
            i += 1
        if i >= len(content) or content[i] == ')':
            break
        if content[i] != '(':
            i += 1
            continue

        end = find_block_end(content, i)
        if end == -1:
            break

        block = content[i:end + 1]

        # Categorize
        if block.startswith('(uuid'):
            blocks.append(('uuid', block))
        elif block.startswith('(paper'):
            blocks.append(('paper', block))
        elif block.startswith('(title_block'):
            blocks.append(('title_block', block))
        elif block.startswith('(lib_symbols'):
            blocks.append(('lib_symbols', block))
        elif block.startswith('(symbol (lib_id'):
            blocks.append(('symbol', block))
        elif block.startswith('(text'):
            blocks.append(('text', block))
        elif block.startswith('(wire'):
            blocks.append(('wire', block))
        elif block.startswith('(junction'):
            blocks.append(('junction', block))
        elif block.startswith('(no_connect'):
            blocks.append(('no_connect', block))
        elif block.startswith('(symbol_instances'):
            blocks.append(('symbol_instances', block))
        elif block.startswith('(sheet_instances'):
            blocks.append(('sheet_instances', block))
        elif block.startswith('(version') or block.startswith('(generator') or block.startswith('(embedded_fonts'):
            blocks.append(('skip_header', block))  # Regenerated by rebuild
        else:
            blocks.append(('other', block))

        i = end + 1

    return blocks


# ============================================================
# KICAD 9 FORMAT TRANSFORMATIONS
# ============================================================

def upgrade_lib_symbols(block):
    """Add (exclude_from_sim no) to each library symbol definition.
    Idempotent: strips existing exclude_from_sim lines first."""
    # Strip any existing exclude_from_sim lines
    block = re.sub(r'\n\s*\(exclude_from_sim [a-z]+\)', '', block)
    # Add fresh exclude_from_sim after each top-level symbol declaration
    result = re.sub(
        r'(\(symbol "[^"]+"\s+\(in_bom yes\)\s+\(on_board yes\))',
        r'\1\n      (exclude_from_sim no)',
        block
    )
    return result


def upgrade_placed_symbol(block, root_uuid):
    """Transform a placed symbol to KiCad 9 format:
    1. Add (exclude_from_sim no) before (in_bom yes)
    2. Add (instances ...) block inside the symbol
    """
    # Extract UUID
    uuid_m = re.search(r'\(uuid ([0-9a-f-]+)\)', block)
    sym_uuid = uuid_m.group(1) if uuid_m else "unknown"

    # Extract Reference
    ref_m = re.search(r'\(property "Reference" "([^"]*)"', block)
    ref = ref_m.group(1) if ref_m else "?"

    # Extract unit
    unit_m = re.search(r'\(unit (\d+)\)', block)
    unit = unit_m.group(1) if unit_m else "1"

    # 1. Add exclude_from_sim before (in_bom yes)
    if '(exclude_from_sim' not in block:
        block = block.replace(
            '(in_bom yes) (on_board yes)',
            '(exclude_from_sim no)\n    (in_bom yes) (on_board yes)'
        )

    # 2. Add instances block before the closing paren (if not already present)
    if '(instances' in block:
        return block

    instances_block = (
        f'\n    (instances\n'
        f'      (project ""\n'
        f'        (path "/{root_uuid}"\n'
        f'          (reference "{ref}") (unit {unit})\n'
        f'        )\n'
        f'      )\n'
        f'    )'
    )

    # Insert before the final closing paren
    last_paren = block.rindex(')')
    block = block[:last_paren] + instances_block + '\n  )'

    return block


# ============================================================
# MAIN REBUILD
# ============================================================

def main():
    print("=" * 60)
    print("Schematic Rebuild Tool (KiCad 9 Format)")
    print("=" * 60)

    content = SCHEMATIC.read_text(encoding='utf-8')

    # Step 1: Extract root UUID
    uuid_m = re.search(r'\(uuid ([0-9a-f-]+)\)', content)
    root_uuid = uuid_m.group(1) if uuid_m else "00000000-0000-0000-0000-000000000000"
    print(f"\n1. Root UUID: {root_uuid}")

    # Step 2: Parse all top-level blocks
    print("\n2. Parsing file structure...")
    blocks = extract_top_blocks(content)
    block_types = {}
    for btype, _ in blocks:
        block_types[btype] = block_types.get(btype, 0) + 1
    for btype, count in block_types.items():
        print(f"   {btype}: {count}")

    # Step 3: Compute pin positions and verify
    print("\n3. Computing pin positions...")
    tests = [
        ('J1', 'A4', 38.10, 43.18),
        ('FB1', '1', 59.69, 43.18),
        ('FB1', '2', 67.31, 43.18),
        ('U1', '3', 149.86, 88.90),
        ('U1', '35', 180.34, 91.44),
        ('U1', '34', 180.34, 93.98),
        ('U1', '25', 180.34, 114.30),
        ('U3', '25', 76.20, 88.90),
        ('U3', '26', 76.20, 86.36),
        ('Q1', '2', 228.60, 99.06),
    ]

    all_ok = True
    for ref, pin, exp_x, exp_y in tests:
        ax, ay = pin_pos(ref, pin)
        dx, dy = abs(ax - exp_x), abs(ay - exp_y)
        if dx >= 0.02 or dy >= 0.02:
            all_ok = False
            print(f"   MISMATCH {ref}:{pin} = ({ax}, {ay}) expected ({exp_x}, {exp_y})")

    if all_ok:
        print("   All 10 pin position checks passed")

    # Step 4: Build netlist and generate wires
    print("\n4. Building netlist...")
    nets = build_netlist()
    power_wires = build_power_wires()
    print(f"   {len(nets)} signal nets, {len(power_wires)} power wires")

    print("\n5. Generating wires...")
    all_wires = []
    all_junctions = []

    for net_name, positions in nets.items():
        wires, junctions = generate_net_wires(positions)
        all_wires.extend(wires)
        all_junctions.extend(junctions)

    for pwr_pos, comp_pos in power_wires:
        px, py = pwr_pos
        cx, cy = comp_pos
        if abs(px - cx) > 0.01 or abs(py - cy) > 0.01:
            if abs(px - cx) < 0.01 or abs(py - cy) < 0.01:
                all_wires.append(make_wire_sexp(px, py, cx, cy))
            else:
                all_wires.append(make_wire_sexp(px, py, cx, py))
                all_wires.append(make_wire_sexp(cx, py, cx, cy))

    print(f"   {len(all_wires)} wire segments, {len(all_junctions)} junctions")

    # No-connect flags
    no_connects = []
    nc_pins = [
        ('U3', '27'),   # DTR
        ('U3', '28'),   # RTS
        ('K1', '3'),    # Relay NC
    ]
    for ref, pin in nc_pins:
        x, y = pin_pos(ref, pin)
        no_connects.append(make_noconnect_sexp(x, y))
    print(f"   {len(no_connects)} no-connect flags")

    # Step 6: Assemble KiCad 9 output
    print("\n6. Assembling KiCad 9 format output...")

    parts = []

    # KiCad 9 header
    parts.append('(kicad_sch')
    parts.append('  (version 20250114)')
    parts.append('  (generator "eeschema")')
    parts.append('  (generator_version "9.0")')

    # Process extracted blocks
    symbols_added = 0
    for btype, block in blocks:
        if btype == 'uuid':
            parts.append(f'  {block}')
        elif btype == 'paper':
            parts.append(f'  {block}')
        elif btype == 'title_block':
            parts.append(f'  {block}')
        elif btype == 'lib_symbols':
            parts.append(f'  {upgrade_lib_symbols(block)}')
        elif btype == 'symbol':
            parts.append(f'  {upgrade_placed_symbol(block, root_uuid)}')
            symbols_added += 1
        elif btype == 'text':
            parts.append(f'  {block}')
        elif btype in ('wire', 'junction', 'no_connect', 'symbol_instances', 'sheet_instances', 'skip_header'):
            # Skip old wires, junctions, no-connects, symbol_instances, sheet_instances,
            # and header fields (version/generator/embedded_fonts) - all regenerated
            pass
        else:
            parts.append(f'  {block}')

    print(f"   Upgraded {symbols_added} placed symbols")

    # Add generated wires
    parts.append('')
    for w in all_wires:
        parts.append(w)

    # Add junctions
    if all_junctions:
        parts.append('')
        for j in all_junctions:
            parts.append(j)

    # Add no-connects
    if no_connects:
        parts.append('')
        for nc in no_connects:
            parts.append(nc)

    # Sheet instances
    parts.append('')
    parts.append('  (sheet_instances')
    parts.append('    (path "/" (page "1"))')
    parts.append('  )')

    # KiCad 9 footer
    parts.append('')
    parts.append('  (embedded_fonts no)')

    # Close root kicad_sch
    parts.append(')')
    parts.append('')

    output = '\n'.join(parts)

    # Validate S-expression balance
    depth = 0
    for ch in output:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth < 0:
                print("   ERROR: Extra closing paren!")
                break

    if depth == 0:
        print("   S-expression: BALANCED")
    elif depth > 0:
        print(f"   ERROR: {depth} unclosed parens!")

    # Write
    SCHEMATIC.write_text(output, encoding='utf-8')
    print(f"   Written to {SCHEMATIC.name}")

    # Summary
    print("\n" + "=" * 60)
    print("REBUILD COMPLETE (KiCad 9 format)")
    print(f"  Format: version 20250114 + generator_version 9.0")
    print(f"  Symbols: {symbols_added} (with instances)")
    print(f"  Wires: {len(all_wires)}")
    print(f"  Junctions: {len(all_junctions)}")
    print(f"  No-connects: {len(no_connects)}")
    print("=" * 60)


if __name__ == '__main__':
    main()
