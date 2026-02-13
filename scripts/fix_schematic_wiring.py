#!/usr/bin/env python3
"""
Fix schematic wiring by computing exact pin positions and generating
correct wire connections.

This script:
1. Parses lib_symbol definitions to get pin offsets
2. Parses symbol instances to get placements (position + rotation)
3. Computes absolute pin endpoint positions on the sheet
4. Removes old wires, junctions, labels, no-connects
5. Generates new wire segments connecting pins per the netlist
6. Writes the corrected schematic
"""

import re
import math
import copy
from pathlib import Path

SCHEMATIC = Path(__file__).parent.parent / "production" / "ESP32_Simple_IoT.kicad_sch"


def parse_sexp_block(text, start_keyword, offset=0):
    """Find a top-level s-expression block starting with (keyword ...) and return its text."""
    idx = text.find(f'({start_keyword}', offset)
    if idx == -1:
        return None, -1, -1
    depth = 0
    end = idx
    for i in range(idx, len(text)):
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return text[idx:end], idx, end


def parse_lib_pins(sym_text):
    """Extract pins from a lib_symbol definition."""
    pins = []
    pin_pat = re.compile(
        r'\(pin\s+(\w+)\s+(\w+)\s+\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)\s+'
        r'\(length\s+([-\d.]+)\).*?'
        r'\(name\s+"([^"]*)".*?\).*?'
        r'\(number\s+"([^"]*)".*?\)',
        re.DOTALL
    )
    for m in pin_pat.finditer(sym_text):
        pins.append({
            'type': m.group(1),
            'x': float(m.group(3)),
            'y': float(m.group(4)),
            'rot': float(m.group(5)) if m.group(5) else 0,
            'length': float(m.group(6)),
            'name': m.group(7),
            'number': m.group(8),
        })
    return pins


def parse_lib_symbols(content):
    """Parse all lib_symbol definitions."""
    lib_text, _, _ = parse_sexp_block(content, 'lib_symbols')
    if not lib_text:
        return {}

    symbols = {}
    # Find top-level symbols (indented 4 spaces under lib_symbols)
    for m in re.finditer(r'\n    \(symbol "([^"]+)"', lib_text):
        name = m.group(1)
        # Skip sub-symbols (contain _ followed by digits)
        if re.search(r'_\d+_\d+$', name):
            continue
        block, _, _ = parse_sexp_block(lib_text, f'symbol "{name}"', m.start())
        if block:
            symbols[name] = parse_lib_pins(block)
    return symbols


def rotate_point(x, y, angle_deg):
    """Rotate point (x,y) by angle_deg clockwise (KiCad convention)."""
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    return (x * cos_a + y * sin_a, -x * sin_a + y * cos_a)


def compute_pin_endpoint(sym_x, sym_y, sym_rot, pin_x, pin_y, pin_rot, pin_length):
    """
    Compute the wire-connectable endpoint of a pin.

    In KiCad schematics:
    - lib_symbol pin (at x y rot) gives the pin's position relative to symbol center
    - pin rotation gives the direction the pin extends FROM the symbol body
    - The wire endpoint is at the END of the pin (away from the symbol body)
    - Pin endpoint = symbol_pos + rotate(pin_pos, symbol_rot)
      where pin_pos already includes length in the lib definition

    KiCad schematic Y-axis: positive = downward on screen
    Symbol rotation is applied to all pin positions
    """
    # The pin (at x y) in the lib_symbol is where the connectable end is
    # (the end where wires attach). The pin extends inward by pin_length.
    # So the pin endpoint (where wires connect) is at (pin_x, pin_y) relative to symbol center.

    # Apply symbol rotation to the pin position
    if sym_rot != 0:
        px, py = rotate_point(pin_x, pin_y, sym_rot)
    else:
        px, py = pin_x, pin_y

    # KiCad schematic: Y increases downward, but lib symbols use Y-up
    # When placed on sheet, the pin Y is negated
    abs_x = sym_x + px
    abs_y = sym_y - py

    return round(abs_x, 2), round(abs_y, 2)


def parse_symbol_instances(content):
    """Parse all placed symbol instances from the schematic."""
    instances = []
    # Match symbol blocks with lib_id
    sym_pat = re.compile(
        r'\(symbol\s+\(lib_id\s+"([^"]+)"\)\s+\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)',
        re.DOTALL
    )
    prop_pat = re.compile(r'\(property\s+"(Reference|Value)"\s+"([^"]*)"')

    # Find all component symbols (after lib_symbols section)
    lib_end_text = '  (lib_symbols'
    lib_block, _, lib_end_idx = parse_sexp_block(content, 'lib_symbols')
    search_area = content[lib_end_idx:]

    for m in sym_pat.finditer(search_area):
        lib_id = m.group(1)
        x = float(m.group(2))
        y = float(m.group(3))
        rot = float(m.group(4)) if m.group(4) else 0

        # Get the full symbol block to extract properties
        block_start = search_area.rfind('\n', 0, m.start()) + 1
        block, _, _ = parse_sexp_block(search_area, 'symbol (lib_id', block_start)
        if not block:
            continue

        props = {}
        for pm in prop_pat.finditer(block):
            props[pm.group(1)] = pm.group(2)

        # Get mirror info
        mirror_x = '(mirror x)' in block
        mirror_y = '(mirror y)' in block

        instances.append({
            'lib_id': lib_id,
            'x': x,
            'y': y,
            'rot': rot,
            'mirror_x': mirror_x,
            'mirror_y': mirror_y,
            'ref': props.get('Reference', '?'),
            'value': props.get('Value', ''),
        })

    return instances


def compute_all_pin_positions(instances, lib_symbols):
    """Compute absolute pin positions for all symbol instances."""
    pin_map = {}  # {ref: {pin_number: (x, y)}}

    for inst in instances:
        ref = inst['ref']
        lib_id = inst['lib_id']
        pins = lib_symbols.get(lib_id, [])

        if not pins:
            continue

        pin_map[ref] = {}
        for pin in pins:
            ex, ey = compute_pin_endpoint(
                inst['x'], inst['y'], inst['rot'],
                pin['x'], pin['y'], pin['rot'], pin['length']
            )

            # Handle mirror
            if inst['mirror_x']:
                ey = 2 * inst['y'] - ey
            if inst['mirror_y']:
                ex = 2 * inst['x'] - ex

            pin_map[ref][pin['number']] = (ex, ey)
            pin_map[ref][f"_{pin['name']}"] = (ex, ey)  # Also index by name

        if ref not in ('#PWR', '?'):
            print(f"  {ref} ({lib_id}) at ({inst['x']}, {inst['y']}) rot={inst['rot']}:")
            for pnum, pos in sorted(pin_map[ref].items()):
                if not pnum.startswith('_'):
                    print(f"    Pin {pnum}: ({pos[0]}, {pos[1]})")

    return pin_map


# ============================================================
# NETLIST DEFINITION
# ============================================================
# This defines how pins connect together. Each entry is a net
# (set of pins that are electrically connected).

def define_netlist():
    """
    Define the electrical connections for the ESP32 Simple IoT Switch.
    Returns a list of nets, each net is a list of (ref, pin_number) tuples.
    """
    nets = {
        # Power path: USB -> Ferrite -> +5V
        'VBUS': [('J1', 'A4'), ('FB1', '1')],
        '+5V': [('FB1', '2'), ('C1', '1'), ('U2', '3'),  # FB out -> C1 -> AMS1117 VI
                ('K1', '2'), ('D1', '1')],                  # Also to relay coil+ and flyback cathode
        '+3V3': [('U2', '2'), ('C2', '1'), ('C3', '1'),   # AMS1117 out -> caps
                 ('C5', '1'), ('R1', '1'), ('R2', '1'),    # ESP32 decoupling, pullups
                 ('R4', '1')],                              # Power LED resistor

        # Ground bus (all connect via GND power symbols on the schematic)
        # KiCad handles GND connections through power symbols, not explicit wires
        # But we still need wires from component GND pins to the GND power symbols

        # ESP32 connections
        'EN_NET': [('R1', '2'), ('C4', '1'), ('SW2', '1')],  # EN pullup + cap + button
        'IO0_NET': [('R2', '2'), ('SW1', '1')],               # IO0 pullup + button

        # UART bridge
        'ESP_TX': [('U1', '35')],   # ESP32 TXD0 - label connection
        'ESP_RX': [('U1', '34')],   # ESP32 RXD0 - label connection
        'CP_RXD': [('U3', '25')],   # CP2102N RXD - label connection
        'CP_TXD': [('U3', '26')],   # CP2102N TXD - label connection

        # USB data
        'USB_DP': [('J1', 'A6'), ('U3', '4')],   # D+
        'USB_DM': [('J1', 'A7'), ('U3', '5')],   # D-

        # Relay driver
        'RELAY_DRIVE': [('R3', '2'), ('Q1', '2')],   # R3 -> BC817 base
        'RELAY_COIL_LO': [('Q1', '3'), ('K1', '1'), ('D1', '2')],  # Collector -> coil- and flyback anode

        # Relay output
        'RELAY_COM': [('K1', '5'), ('J2', '1')],   # COM -> terminal 1
        'RELAY_NO': [('K1', '4'), ('J2', '2')],    # NO -> terminal 2

        # Status LEDs
        'LED_PWR': [('R4', '2'), ('D2', '2')],     # R4 -> D2 anode (power LED)
        'LED_RELAY': [('R5', '2'), ('D3', '2')],   # R5 -> D3 anode (relay LED)

        # GPIO connections
        'IO4': [('U1', '26'), ('R3', '1')],        # ESP32 IO4 -> relay driver resistor
        'IO5': [('U1', '29'), ('R5', '1')],        # ESP32 IO5 -> relay LED resistor
    }
    return nets


def snap_to_grid(val, grid=1.27):
    """Snap a coordinate to KiCad's default schematic grid."""
    return round(round(val / grid) * grid, 2)


def generate_wire(x1, y1, x2, y2, uuid_base, wire_idx):
    """Generate a KiCad wire s-expression."""
    uuid = f"50000001-0001-{wire_idx:04x}-0001-000000000001"
    # Route with Manhattan (horizontal + vertical) segments
    wires = []
    if abs(x1 - x2) < 0.01 or abs(y1 - y2) < 0.01:
        # Already horizontal or vertical
        wires.append(
            f'  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))\n'
            f'    (stroke (width 0) (type default))\n'
            f'    (uuid "{uuid}")\n'
            f'  )'
        )
    else:
        # L-shaped route: horizontal first, then vertical
        mid_x = x2
        mid_y = y1
        uuid2 = f"50000001-0001-{wire_idx:04x}-0002-000000000001"
        wires.append(
            f'  (wire (pts (xy {x1} {y1}) (xy {mid_x} {mid_y}))\n'
            f'    (stroke (width 0) (type default))\n'
            f'    (uuid "{uuid}")\n'
            f'  )'
        )
        wires.append(
            f'  (wire (pts (xy {mid_x} {mid_y}) (xy {x2} {y2}))\n'
            f'    (stroke (width 0) (type default))\n'
            f'    (uuid "{uuid2}")\n'
            f'  )'
        )
    return wires


def generate_junction(x, y, junc_idx):
    """Generate a junction at a point where 3+ wires meet."""
    uuid = f"60000001-0001-{junc_idx:04x}-0001-000000000001"
    return (
        f'  (junction (at {x} {y}) (diameter 0) (color 0 0 0 0)\n'
        f'    (uuid "{uuid}")\n'
        f'  )'
    )


def generate_net_label(x, y, angle, name, label_idx):
    """Generate a net label."""
    uuid = f"70000001-0001-{label_idx:04x}-0001-000000000001"
    return (
        f'  (label "{name}" (at {x} {y} {angle}) (fields_autoplaced)\n'
        f'    (effects (font (size 1.27 1.27)) (justify left bottom))\n'
        f'    (uuid "{uuid}")\n'
        f'  )'
    )


def generate_no_connect(x, y, nc_idx):
    """Generate a no-connect flag."""
    uuid = f"80000001-0001-{nc_idx:04x}-0001-000000000001"
    return (
        f'  (no_connect (at {x} {y}) (uuid "{uuid}"))'
    )


def main():
    print("=" * 60)
    print("Schematic Wiring Fixer")
    print("=" * 60)

    content = SCHEMATIC.read_text(encoding='utf-8')

    # Parse lib symbols
    print("\nParsing lib symbols...")
    lib_symbols = parse_lib_symbols(content)
    print(f"  Found {len(lib_symbols)} symbol definitions")

    # Parse symbol instances
    print("\nParsing symbol instances...")
    instances = parse_symbol_instances(content)
    print(f"  Found {len(instances)} placed symbols")

    # Filter to just component instances (not power symbols)
    components = [i for i in instances if not i['lib_id'].startswith('power:')]
    power_syms = [i for i in instances if i['lib_id'].startswith('power:')]
    print(f"  Components: {len(components)}, Power symbols: {len(power_syms)}")

    # Compute pin positions
    print("\nComputing pin positions...")
    pin_map = compute_all_pin_positions(instances, lib_symbols)

    # Print power symbol positions
    print("\nPower symbols:")
    for ps in power_syms:
        ref = ps['ref']
        if ref in pin_map:
            for pnum, pos in pin_map[ref].items():
                if not pnum.startswith('_'):
                    print(f"  {ref} ({ps['value']}): ({pos[0]}, {pos[1]})")

    # Define netlist
    print("\nDefining netlist...")
    nets = define_netlist()
    print(f"  Defined {len(nets)} nets")

    # Verify all referenced pins exist
    missing = []
    for net_name, connections in nets.items():
        for ref, pin in connections:
            if ref not in pin_map:
                missing.append(f"  {net_name}: component {ref} not found")
            elif pin not in pin_map[ref]:
                available = [k for k in pin_map[ref] if not k.startswith('_')]
                missing.append(f"  {net_name}: {ref} pin {pin} not found (available: {available})")

    if missing:
        print(f"\nMISSING PINS ({len(missing)}):")
        for m in missing:
            print(m)
    else:
        print("  All pins found!")

    # Generate wires
    print("\nGenerating wires...")
    wire_idx = 1
    all_wires = []
    junctions = []
    junc_idx = 1

    for net_name, connections in nets.items():
        if len(connections) < 2:
            continue  # Single-pin nets (labels) handled separately

        # Get pin positions for this net
        positions = []
        for ref, pin in connections:
            if ref in pin_map and pin in pin_map[ref]:
                positions.append(pin_map[ref][pin])

        if len(positions) < 2:
            continue

        # Connect pins in chain (first to second, second to third, etc.)
        for i in range(len(positions) - 1):
            x1, y1 = positions[i]
            x2, y2 = positions[i + 1]
            wires = generate_wire(x1, y1, x2, y2, "wire", wire_idx)
            all_wires.extend(wires)
            wire_idx += 1

        # Add junction if 3+ pins on same net
        if len(positions) > 2:
            # Junction at the second point (where chain branches)
            for i in range(1, len(positions) - 1):
                jx, jy = positions[i]
                junctions.append(generate_junction(jx, jy, junc_idx))
                junc_idx += 1

    print(f"  Generated {wire_idx - 1} wire connections")
    print(f"  Generated {junc_idx - 1} junctions")

    # Generate labels for UART connections
    labels = []
    label_idx = 1
    # ESP_TX label at U1 pin 35
    if 'U1' in pin_map and '35' in pin_map['U1']:
        x, y = pin_map['U1']['35']
        labels.append(generate_net_label(x, y, 0, "ESP_TX", label_idx))
        label_idx += 1
    # ESP_RX label at U1 pin 34
    if 'U1' in pin_map and '34' in pin_map['U1']:
        x, y = pin_map['U1']['34']
        labels.append(generate_net_label(x, y, 0, "ESP_RX", label_idx))
        label_idx += 1
    # ESP_TX label at U3 pin 25 (RXD receives TX)
    if 'U3' in pin_map and '25' in pin_map['U3']:
        x, y = pin_map['U3']['25']
        labels.append(generate_net_label(x, y, 180, "ESP_TX", label_idx))
        label_idx += 1
    # ESP_RX label at U3 pin 26 (TXD sends to RX)
    if 'U3' in pin_map and '26' in pin_map['U3']:
        x, y = pin_map['U3']['26']
        labels.append(generate_net_label(x, y, 180, "ESP_RX", label_idx))
        label_idx += 1

    print(f"  Generated {label_idx - 1} net labels")

    # Generate no-connect flags
    no_connects = []
    nc_idx = 1
    nc_pins = [
        ('U3', '27'),  # DTR
        ('U3', '28'),  # RTS
        ('K1', '3'),   # NC contact
    ]
    for ref, pin in nc_pins:
        if ref in pin_map and pin in pin_map[ref]:
            x, y = pin_map[ref][pin]
            no_connects.append(generate_no_connect(x, y, nc_idx))
            nc_idx += 1

    print(f"  Generated {nc_idx - 1} no-connect flags")

    # Now reconstruct the schematic
    print("\nRewriting schematic...")

    # Find where to insert new wires (after all symbol blocks, before symbol_instances)
    # Remove existing wires, junctions, labels, no_connects
    lines = content.split('\n')
    new_lines = []
    skip = False
    removed = 0

    for line in lines:
        stripped = line.strip()
        # Remove existing wires, junctions, labels, no_connects
        if stripped.startswith('(wire ') or stripped.startswith('(junction ') or \
           stripped.startswith('(label ') or stripped.startswith('(no_connect '):
            # Start skipping this block
            depth = line.count('(') - line.count(')')
            if depth <= 0:
                removed += 1
                continue  # Single-line item, skip it
            skip = True
            removed += 1
            continue

        if skip:
            depth_change = line.count('(') - line.count(')')
            # We're inside a multi-line block being removed
            # Track depth - when we return to 0, stop skipping
            if ')' in line:
                skip = False
            continue

        new_lines.append(line)

    print(f"  Removed {removed} existing wire/junction/label/no_connect entries")

    # Find insertion point (before symbol_instances)
    insert_idx = -1
    for i, line in enumerate(new_lines):
        if '(symbol_instances' in line:
            insert_idx = i
            break

    if insert_idx == -1:
        # Insert before the last closing paren
        insert_idx = len(new_lines) - 1

    # Build insertion block
    insert_block = []
    insert_block.append('')
    insert_block.append('  ;; ===== WIRE CONNECTIONS =====')
    insert_block.extend(all_wires)
    insert_block.append('')
    insert_block.append('  ;; ===== JUNCTIONS =====')
    insert_block.extend(junctions)
    insert_block.append('')
    insert_block.append('  ;; ===== NET LABELS =====')
    insert_block.extend(labels)
    insert_block.append('')
    insert_block.append('  ;; ===== NO-CONNECT FLAGS =====')
    insert_block.extend(no_connects)
    insert_block.append('')

    # Wait - we learned that KiCad doesn't support ;; comments!
    # Remove them
    insert_block = [line for line in insert_block if not line.strip().startswith(';;')]

    # Insert
    new_lines[insert_idx:insert_idx] = insert_block

    # Write
    new_content = '\n'.join(new_lines)
    SCHEMATIC.write_text(new_content, encoding='utf-8')
    print(f"  Written {len(new_content)} bytes to {SCHEMATIC.name}")
    print(f"  Total wires: {wire_idx - 1}")

    print("\n" + "=" * 60)
    print("DONE - Run ERC to verify")
    print("=" * 60)


if __name__ == '__main__':
    main()
