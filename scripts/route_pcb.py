"""
Route PCB for ESP32 Simple IoT Switch using KiCad pcbnew Python API.

v3 - Complete redesign:
  - Board enlarged to 80x60mm (ESP32+relay need space)
  - ESP32 at top-right with antenna keepout extending off board top
  - No explicit keepout zones (ESP32 footprint has built-in antenna keepout)
  - Components spread to avoid courtyard overlaps
  - Minimal B.Cu usage (only UART and IO4 cross-board routes)
  - GND plane on B.Cu with strategic vias
  - All traces routed with proper clearance (0.2mm min)

Must be run with KiCad's Python:
  C:\\Users\\james\\AppData\\Local\\Programs\\KiCad\\9.0\\bin\\python.exe route_pcb.py
"""

import pcbnew
import os

# ============================================================
# CONSTANTS
# ============================================================

NM = 1_000_000  # 1mm in nanometers
FP_BASE = r'C:\Users\james\AppData\Local\Programs\KiCad\9.0\share\kicad\footprints'
PCB_OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       'production', 'ESP32_Simple_IoT.kicad_pcb')

BOARD_W = 80.0
BOARD_H = 60.0

F_Cu = pcbnew.F_Cu
B_Cu = pcbnew.B_Cu
Edge_Cuts = pcbnew.Edge_Cuts

# Trace widths
PWR_W = 0.5   # Power traces
SIG_W = 0.25  # Signal traces

# Via sizes
VIA_SIZE = 0.6
VIA_DRILL = 0.3
VIA_PWR_SIZE = 0.8
VIA_PWR_DRILL = 0.4

# ============================================================
# NET DEFINITIONS
# ============================================================

NET_NAMES = [
    '',            # 0
    'GND',         # 1
    '+5V',         # 2
    '+3V3',        # 3
    'USB_D+',      # 4
    'USB_D-',      # 5
    'ESP_TX',      # 6
    'ESP_RX',      # 7
    'ESP_EN',      # 8
    'ESP_IO0',     # 9
    'ESP_IO4',     # 10
    'ESP_IO5',     # 11
    'RELAY_COIL',  # 12
    'VBUS',        # 13
    'LED_PWR',     # 14
    'LED_RELAY',   # 15
    'RELAY_BASE',  # 16
    'RELAY_COM',   # 17
    'RELAY_NO',    # 18
]

# ============================================================
# COMPONENT PLACEMENT v3
# ============================================================
#
# Board: 80x60mm
#
# Layout zones:
#   TOP-LEFT  (x=0-35, y=0-25):  Power supply, LEDs, voltage reg
#   LEFT      (x=0-20, y=25-45): USB connector, CP2102N
#   BOT-LEFT  (x=0-35, y=40-60): Relay driver, relay, diode
#   CENTER    (x=35-50, y=25-55): Buttons, EN/IO0 passives
#   RIGHT     (x=45-75, y=2-28):  ESP32 module (antenna at top)
#   BOT-RIGHT (x=60-80, y=40-60): Output terminal
#
# ESP32 at (60, 15): antenna keepout at y<5.2 for x=[36,84]
#   Module body: x=[50.25, 69.75], y=[5.20, 25.51]
#   Left-side pads (x~51.25): pins 1-14
#   Right-side pads (x~68.75): pins 25-38
#   Bottom pads (y~24.51): pins 15-24
#   Thermal pad 39: center (~57.79, 12.56)

COMPONENTS = [
    # ref, lib_dir, fp_name, x, y, rot
    # Power supply area (top-left, y=4-16)
    ('J1',  'Connector_USB',      'USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal', 6, 30, 0),
    ('FB1', 'Inductor_SMD',       'L_0805_2012Metric',            18, 8, 0),
    ('U2',  'Package_TO_SOT_SMD', 'SOT-223-3_TabPin2',            26, 8, 0),
    ('C1',  'Capacitor_SMD',      'C_0805_2012Metric',            18, 4, 0),
    ('C2',  'Capacitor_SMD',      'C_0805_2012Metric',            33, 4, 0),
    ('C3',  'Capacitor_SMD',      'C_0805_2012Metric',            33, 12, 0),

    # USB-UART bridge (left side, below USB)
    ('U3',  'Package_DFN_QFN',    'QFN-28-1EP_5x5mm_P0.5mm_EP3.35x3.35mm', 16, 44, 0),

    # ESP32 module (right side, antenna pointing UP off board)
    # At (60,12): keepout y<2.2 (off board), body y=[2.2, 22.5]
    ('U1',  'RF_Module',          'ESP32-WROOM-32',               60, 12, 0),

    # ESP32 support passives (left of ESP32 body x<50.25)
    ('C5',  'Capacitor_SMD',      'C_0805_2012Metric',            47, 6, 0),
    ('R1',  'Resistor_SMD',       'R_0805_2012Metric',            47, 10, 0),
    ('C4',  'Capacitor_SMD',      'C_0805_2012Metric',            44, 15, 0),
    ('R2',  'Resistor_SMD',       'R_0805_2012Metric',            47, 20, 0),

    # Buttons (bottom-center, spread apart)
    ('SW1', 'Button_Switch_SMD',  'SW_SPST_TL3342',              48, 56, 0),
    ('SW2', 'Button_Switch_SMD',  'SW_SPST_TL3342',              60, 56, 0),

    # Relay driver (bottom-left)
    ('R3',  'Resistor_SMD',       'R_0805_2012Metric',            14, 52, 0),
    ('Q1',  'Package_TO_SOT_SMD', 'SOT-23',                       8, 52, 0),
    ('K1',  'Relay_THT',          'Relay_SPDT_SANYOU_SRD_Series_Form_C', 22, 50, 0),
    ('D1',  'Diode_THT',          'D_DO-41_SOD81_P10.16mm_Horizontal', 8, 36, 0),

    # Output terminal (bottom-right)
    ('J2',  'Connector_Phoenix_MC', 'PhoenixContact_MC_1,5_2-G-3.81_1x02_P3.81mm_Horizontal', 72, 52, 0),

    # LEDs (top-left corner, horizontal pairs)
    ('D2',  'LED_SMD',            'LED_0805_2012Metric',          9, 4, 0),
    ('R4',  'Resistor_SMD',       'R_0805_2012Metric',            13, 4, 0),
    ('D3',  'LED_SMD',            'LED_0805_2012Metric',          6, 16, 0),
    ('R5',  'Resistor_SMD',       'R_0805_2012Metric',            10, 16, 0),
]

MOUNTING_HOLES = [
    ('H1', 3, 3),
    ('H2', 77, 12),   # Moved down to avoid ESP32 antenna keepout
    ('H3', 3, 57),
    ('H4', 77, 40),   # Well above J2 connector to avoid overlap
]

# ============================================================
# PAD-TO-NET ASSIGNMENTS
# ============================================================

PAD_NETS = {
    # USB Connector J1
    ('J1', 'A1'): 'GND', ('J1', 'A4'): 'VBUS',
    # A5/B5 are CC pins — left unrouted (float OK for power-only USB-C)
    ('J1', 'A6'): 'USB_D+', ('J1', 'A7'): 'USB_D-',
    ('J1', 'A8'): 'GND',   # SBU1 — assign GND for routing
    ('J1', 'S1'): 'GND', ('J1', 'B1'): 'GND',
    ('J1', 'B4'): 'VBUS',  # B4 shares position with A9
    ('J1', 'B8'): 'GND',   # SBU2
    ('J1', 'B12'): 'GND', ('J1', 'A12'): 'GND',
    ('J1', 'A9'): 'VBUS', ('J1', 'B9'): 'VBUS',

    # Ferrite Bead FB1
    ('FB1', '1'): 'VBUS', ('FB1', '2'): '+5V',

    # AMS1117 U2: 1=GND, 2=VOUT(+3V3), 3=VIN(+5V), tab=VOUT
    ('U2', '1'): 'GND', ('U2', '2'): '+3V3', ('U2', '3'): '+5V',

    # Caps
    ('C1', '1'): '+5V', ('C1', '2'): 'GND',
    ('C2', '1'): '+3V3', ('C2', '2'): 'GND',
    ('C3', '1'): '+3V3', ('C3', '2'): 'GND',
    ('C5', '1'): '+3V3', ('C5', '2'): 'GND',
    ('C4', '1'): 'ESP_EN', ('C4', '2'): 'GND',

    # CP2102N U3 (QFN-28)
    ('U3', '3'): 'GND', ('U3', '4'): 'USB_D+', ('U3', '5'): 'USB_D-',
    ('U3', '6'): '+3V3', ('U3', '7'): '+3V3', ('U3', '8'): '+5V',
    ('U3', '25'): 'ESP_TX', ('U3', '26'): 'ESP_RX',
    ('U3', '29'): 'GND',

    # ESP32 U1
    ('U1', '1'): 'GND', ('U1', '2'): '+3V3', ('U1', '3'): 'ESP_EN',
    ('U1', '25'): 'ESP_IO0', ('U1', '26'): 'ESP_IO4',
    ('U1', '29'): 'ESP_IO5',
    ('U1', '34'): 'ESP_RX', ('U1', '35'): 'ESP_TX',
    ('U1', '38'): 'GND', ('U1', '39'): 'GND',

    # EN circuit
    ('R1', '1'): '+3V3', ('R1', '2'): 'ESP_EN',
    # IO0 circuit
    ('R2', '1'): '+3V3', ('R2', '2'): 'ESP_IO0',

    # Buttons: pin 1 = GND, pin 2 = signal
    ('SW1', '1'): 'GND', ('SW1', '2'): 'ESP_IO0',
    ('SW2', '1'): 'GND', ('SW2', '2'): 'ESP_EN',

    # Relay driver
    ('R3', '1'): 'ESP_IO4', ('R3', '2'): 'RELAY_BASE',
    ('Q1', '1'): 'GND', ('Q1', '2'): 'RELAY_BASE', ('Q1', '3'): 'RELAY_COIL',

    # Relay
    ('K1', '1'): 'RELAY_COIL', ('K1', '2'): '+5V',
    ('K1', '4'): 'RELAY_NO', ('K1', '5'): 'RELAY_COM',

    # Flyback diode
    ('D1', '1'): '+5V', ('D1', '2'): 'RELAY_COIL',

    # Output terminal
    ('J2', '1'): 'RELAY_COM', ('J2', '2'): 'RELAY_NO',

    # LEDs
    ('D2', '1'): 'GND', ('D2', '2'): 'LED_PWR',
    ('R4', '1'): 'LED_PWR', ('R4', '2'): '+3V3',
    ('D3', '1'): 'GND', ('D3', '2'): 'LED_RELAY',
    ('R5', '1'): 'ESP_IO5', ('R5', '2'): 'LED_RELAY',
}

# ============================================================
# HELPERS
# ============================================================

def mm(val):
    return int(val * NM)

def point(x_mm, y_mm):
    return pcbnew.VECTOR2I(mm(x_mm), mm(y_mm))

_pad_cache = {}

def get_pad_pos(board, ref, pad_num):
    """Get absolute position of a pad."""
    key = (ref, pad_num)
    if key in _pad_cache:
        return _pad_cache[key]
    for fp in board.GetFootprints():
        if fp.GetReference() == ref:
            for pad in fp.Pads():
                if pad.GetNumber() == pad_num:
                    pos = pad.GetPosition()
                    result = (pos.x / NM, pos.y / NM)
                    _pad_cache[key] = result
                    return result
    return None

def pp(board, ref, pad):
    """Shorthand for get_pad_pos with error reporting."""
    pos = get_pad_pos(board, ref, pad)
    if pos is None:
        print(f"  WARNING: pad {ref}:{pad} not found!")
        return (0, 0)
    return pos

def add_track(board, net, layer, width, x1, y1, x2, y2):
    """Add a single track segment."""
    if abs(x1 - x2) < 0.001 and abs(y1 - y2) < 0.001:
        return
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(point(x1, y1))
    track.SetEnd(point(x2, y2))
    track.SetWidth(mm(width))
    track.SetLayer(layer)
    track.SetNet(net)
    board.Add(track)

def add_via(board, net, x, y, size=VIA_SIZE, drill=VIA_DRILL):
    """Add a through-hole via."""
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(point(x, y))
    via.SetViaType(pcbnew.VIATYPE_THROUGH)
    via.SetWidth(mm(size))
    via.SetDrill(mm(drill))
    via.SetNet(net)
    board.Add(via)

def route_polyline(board, net, layer, width, points):
    """Route a series of connected track segments."""
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        add_track(board, net, layer, width, x1, y1, x2, y2)

def route_manhattan(board, net, layer, width, p1, p2, horiz_first=True):
    """Route an L-shaped Manhattan path between two points."""
    x1, y1 = p1
    x2, y2 = p2
    if abs(x1 - x2) < 0.01 and abs(y1 - y2) < 0.01:
        return
    if abs(x1 - x2) < 0.01 or abs(y1 - y2) < 0.01:
        add_track(board, net, layer, width, x1, y1, x2, y2)
    elif horiz_first:
        add_track(board, net, layer, width, x1, y1, x2, y1)
        add_track(board, net, layer, width, x2, y1, x2, y2)
    else:
        add_track(board, net, layer, width, x1, y1, x1, y2)
        add_track(board, net, layer, width, x1, y2, x2, y2)

def route_via_bridge(board, net, layer_start, layer_end, width, p1, p2,
                     via_offset_start=1.5, via_offset_end=1.5, horiz_first=True,
                     via_size=VIA_SIZE, via_drill=VIA_DRILL):
    """Route between two points using a layer change via vias.

    p1 -> short stub on layer_start -> via -> route on layer_end -> via -> short stub on layer_start -> p2
    """
    x1, y1 = p1
    x2, y2 = p2

    # Determine via positions (offset from endpoints)
    if abs(x2 - x1) > abs(y2 - y1):
        # Predominantly horizontal route
        dx = via_offset_start if x2 > x1 else -via_offset_start
        v1 = (x1 + dx, y1)
        dx = via_offset_end if x1 > x2 else -via_offset_end
        v2 = (x2 + dx, y2)
    else:
        # Predominantly vertical route
        dy = via_offset_start if y2 > y1 else -via_offset_start
        v1 = (x1, y1 + dy)
        dy = via_offset_end if y1 > y2 else -via_offset_end
        v2 = (x2, y2 + dy)

    # Start stub on layer_start
    add_track(board, net, layer_start, width, x1, y1, v1[0], v1[1])
    add_via(board, net, v1[0], v1[1], via_size, via_drill)
    # Main route on layer_end
    route_manhattan(board, net, layer_end, width, v1, v2, horiz_first=horiz_first)
    # End stub on layer_start
    add_via(board, net, v2[0], v2[1], via_size, via_drill)
    add_track(board, net, layer_start, width, v2[0], v2[1], x2, y2)


# ============================================================
# ROUTING
# ============================================================

def route_all(board, net_map):
    """Route all traces using planned non-crossing 2-layer strategy.

    B.Cu channel plan (horizontal channels at fixed Y, vertical feeds at unique X):
      y=6:  ESP_IO5  (x=66 -> x=12)
      y=27: ESP_IO4  (x=64 -> x=16)
      y=32: ESP_RX   (x=65 -> x=18)
      y=34: ESP_TX   (x=67 -> x=24)
    All other routes on F.Cu with short B.Cu hops where needed.
    """

    def net(name):
        return net_map[name]

    def p(ref, pad):
        return pp(board, ref, pad)

    # ==========================================================
    # POWER TRACES ON F.Cu (0.5mm)
    # ==========================================================

    # VBUS: J1:A4 -> FB1:1 (left side, going up)
    p_vbus = p('J1', 'A4')
    p_fb1_1 = p('FB1', '1')
    route_polyline(board, net('VBUS'), F_Cu, PWR_W, [
        p_vbus,
        (p_vbus[0], p_fb1_1[1]),  # Vertical up
        p_fb1_1,                   # Horizontal to FB1
    ])

    # +5V: FB1:2 -> C1:1 via y=6 (avoids VBUS horizontal at y=8 AND C1:2 GND at y=4)
    pa, pb = p('FB1', '2'), p('C1', '1')
    route_polyline(board, net('+5V'), F_Cu, PWR_W, [
        pa, (pa[0], 6), (pb[0], 6), pb,  # Down to y=6, left to C1:1 x, down to C1:1
    ])
    # +5V: C1:1 -> U2:3 via y=2.75 (0.275mm clearance to C1:2 GND pad at y=3.275)
    pc = p('U2', '3')
    route_polyline(board, net('+5V'), F_Cu, PWR_W, [
        pb, (pb[0], 2.75), (20, 2.75), (20, pc[1]), pc,  # x=20 avoids U2:1 GND via
    ])

    # +3V3: U2:2 -> C2:1
    pa = p('U2', '2')
    pb = p('C2', '1')
    route_manhattan(board, net('+3V3'), F_Cu, PWR_W, pa, pb, horiz_first=True)
    # C2:1 -> C3:1
    pc = p('C3', '1')
    route_manhattan(board, net('+3V3'), F_Cu, PWR_W, pb, pc, horiz_first=False)

    # +3V3 -> C5:1 (ESP32 bypass) via y=2.75 (0.275mm clearance to C2:2 GND pad at y=3.275)
    pd = p('C5', '1')
    route_polyline(board, net('+3V3'), F_Cu, PWR_W, [
        pb, (pb[0], 2.75), (pd[0], 2.75), pd   # Up to y=2.75, across, down to C5
    ])

    # +3V3 -> U1:2 (ESP32 3V3 pin) via y=4.75 (0.275mm clearance to C5:2 GND pad at y=5.275)
    pe = p('U1', '2')
    route_polyline(board, net('+3V3'), F_Cu, PWR_W, [
        pd, (pd[0], 4.75), (pe[0], 4.75), pe,  # Down to y=4.75, across, up to U1:2
    ])

    # +3V3 -> R1:1, R2:1 (vertical chain at x~47)
    pr1 = p('R1', '1')
    pr2 = p('R2', '1')
    add_track(board, net('+3V3'), F_Cu, SIG_W, pd[0], pd[1], pr1[0], pr1[1])
    add_track(board, net('+3V3'), F_Cu, SIG_W, pr1[0], pr1[1], pr2[0], pr2[1])

    # +3V3 -> R4:2 (LED resistor, top-left) - route via y=2 to avoid +5V/C1 at y=4
    pr4 = p('R4', '2')
    route_polyline(board, net('+3V3'), F_Cu, PWR_W, [
        pb,                     # From C2:1 = (32.05, 4)
        (pb[0], 2),             # Up to y=2
        (pr4[0], 2),            # Horizontal at y=2 (above +5V at y=4)
        pr4,                    # Down to R4:2 = (13.91, 4)
    ])

    # +3V3 -> U3:6 (CP2102N VDD) - route down left side on B.Cu, short F.Cu stub at U3
    pu3_vdd = p('U3', '6')
    # Via from C3 area down, B.Cu vertical to near U3 (avoids crossing USB data)
    via_3v3_start = (pc[0] - 2, pc[1] + 4)  # y=16 to avoid +5V relay corridor at y=14.30
    add_track(board, net('+3V3'), F_Cu, PWR_W, pc[0], pc[1], via_3v3_start[0], via_3v3_start[1])
    add_via(board, net('+3V3'), via_3v3_start[0], via_3v3_start[1], VIA_PWR_SIZE, VIA_PWR_DRILL)
    # B.Cu to close to U3:6, then short F.Cu stub (avoids long F.Cu near USB_D- pad)
    via_3v3_end = (10, 45)  # Far enough from USB_D- via at (11.55, 44.5)
    route_polyline(board, net('+3V3'), B_Cu, PWR_W, [
        via_3v3_start,
        (5, via_3v3_start[1]),      # Left to x=5
        (5, via_3v3_end[1]),        # Down to y=45
        via_3v3_end,                # Right to x=10
    ])
    add_via(board, net('+3V3'), via_3v3_end[0], via_3v3_end[1], VIA_PWR_SIZE, VIA_PWR_DRILL)
    # F.Cu: via (10,45) -> south to y=46 -> across to x=13.55 -> up through U3:7/U3:6
    # y=46 clears USB_D- via at (11.55,45) and stays below +5V F.Cu at y=47
    pu3_7 = p('U3', '7')
    route_polyline(board, net('+3V3'), F_Cu, PWR_W, [
        via_3v3_end,                  # (10, 45)
        (via_3v3_end[0], 46),         # (10, 46) south past USB_D- via
        (pu3_vdd[0], 46),            # (13.55, 46) across
        (pu3_7[0], pu3_7[1]),         # (13.55, 45.5) U3:7 pad
        (pu3_vdd[0], pu3_vdd[1]),     # (13.55, 45) U3:6 pad
    ])

    # +5V -> U3:8 (REGIN) - via down on B.Cu
    pu3_reg = p('U3', '8')
    u2_vin = p('U2', '3')
    via_5v_u3_start = (u2_vin[0] + 2, u2_vin[1] + 2)
    add_track(board, net('+5V'), F_Cu, PWR_W, u2_vin[0], u2_vin[1], via_5v_u3_start[0], via_5v_u3_start[1])
    add_via(board, net('+5V'), via_5v_u3_start[0], via_5v_u3_start[1], VIA_PWR_SIZE, VIA_PWR_DRILL)
    # Route +5V to U3:8 via B.Cu corridor at x=13 (east of VBUS F.Cu at x=12, avoids J1 NPTH)
    # x=13: 1mm from VBUS at x=12, 2mm from ESP_IO4 at x=15, 1.45mm from USB_D- at x=11.55
    # F.Cu hop at y=15-17 to cross +3V3 B.Cu horizontal at y=16
    via_5v_u3_end = (10, 49)
    route_polyline(board, net('+5V'), B_Cu, PWR_W, [
        via_5v_u3_start,
        (13, via_5v_u3_start[1]),    # Left to x=13
        (13, 15),                     # South to y=15 (before +3V3 at y=16)
    ])
    add_via(board, net('+5V'), 13, 15, VIA_PWR_SIZE, VIA_PWR_DRILL)
    add_track(board, net('+5V'), F_Cu, PWR_W, 13, 15, 13, 17)  # F.Cu hop over +3V3 at y=16
    add_via(board, net('+5V'), 13, 17, VIA_PWR_SIZE, VIA_PWR_DRILL)
    route_polyline(board, net('+5V'), B_Cu, PWR_W, [
        (13, 17),                     # Resume B.Cu at y=17
        (13, via_5v_u3_end[1]),      # South to y=49
        via_5v_u3_end,               # Left to x=10
    ])
    add_via(board, net('+5V'), via_5v_u3_end[0], via_5v_u3_end[1], VIA_PWR_SIZE, VIA_PWR_DRILL)
    # F.Cu: (10,49) -> (11,49) -> (11,47) -> (14.5,47) -> U3:8 (14.5,46.45)
    # L-shape avoids ESP_IO4 F.Cu at y=48 (x=13.09-15) and GND stitch via at (12,48)
    route_polyline(board, net('+5V'), F_Cu, PWR_W, [
        via_5v_u3_end,              # (10, 49)
        (11, 49),                   # Right to x=11
        (11, 47),                   # Up to y=47 (below ESP_IO4 at y=48)
        (pu3_reg[0], 47),           # Right to U3:8 x at y=47
        (pu3_reg[0], pu3_reg[1]),   # Up to U3:8 (14.5, 46.45)
    ])

    # +5V -> relay area (K1:2 coil+ and D1:1 cathode) on B.Cu
    pk1_coilp = p('K1', '2')
    pd1_k = p('D1', '1')
    via_5v_relay = (u2_vin[0] - 2, u2_vin[1] + 4)
    add_track(board, net('+5V'), F_Cu, PWR_W, u2_vin[0], u2_vin[1], via_5v_relay[0], via_5v_relay[1])
    add_via(board, net('+5V'), via_5v_relay[0], via_5v_relay[1], VIA_PWR_SIZE, VIA_PWR_DRILL)
    via_5v_relay_end = (pk1_coilp[0], pk1_coilp[1] - 3)
    # +5V relay corridor: horizontal to x=8, then vertical with F.Cu hops over crossings
    add_track(board, net('+5V'), B_Cu, PWR_W, via_5v_relay[0], via_5v_relay[1], 8, via_5v_relay[1])
    # Segment 1: B.Cu y=14.3 to y=15 (before +3V3 at y=16)
    add_track(board, net('+5V'), B_Cu, PWR_W, 8, via_5v_relay[1], 8, 15)
    # Hop 1: F.Cu over +3V3 horizontal at y=16
    add_via(board, net('+5V'), 8, 15, VIA_PWR_SIZE, VIA_PWR_DRILL)
    add_track(board, net('+5V'), F_Cu, PWR_W, 8, 15, 8, 18.5)
    add_via(board, net('+5V'), 8, 18.5, VIA_PWR_SIZE, VIA_PWR_DRILL)
    # Segment 2: B.Cu y=18.5 to y=28.5 (before USB_D- at y=29.32)
    add_track(board, net('+5V'), B_Cu, PWR_W, 8, 18.5, 8, 28.5)
    # Hop 2: F.Cu over USB_D- horizontal at y=29.32
    add_via(board, net('+5V'), 8, 28.5, VIA_PWR_SIZE, VIA_PWR_DRILL)
    add_track(board, net('+5V'), F_Cu, PWR_W, 8, 28.5, 8, 30.5)
    add_via(board, net('+5V'), 8, 30.5, VIA_PWR_SIZE, VIA_PWR_DRILL)
    # Segment 3: B.Cu y=30.5 to y=43 (before +3V3 at y=45, avoids USB_D+ at y=44)
    add_track(board, net('+5V'), B_Cu, PWR_W, 8, 30.5, 8, 43)
    # Hop 3: F.Cu over USB_D+ (y=44) and +3V3 (y=45)
    add_via(board, net('+5V'), 8, 43, VIA_PWR_SIZE, VIA_PWR_DRILL)
    add_track(board, net('+5V'), F_Cu, PWR_W, 8, 43, 8, 46)
    add_via(board, net('+5V'), 8, 46, VIA_PWR_SIZE, VIA_PWR_DRILL)
    # Segment 4: B.Cu y=46 to relay, then horizontal to K1 area
    route_polyline(board, net('+5V'), B_Cu, PWR_W, [
        (8, 46), (8, via_5v_relay_end[1]), via_5v_relay_end,
    ])
    add_via(board, net('+5V'), via_5v_relay_end[0], via_5v_relay_end[1], VIA_PWR_SIZE, VIA_PWR_DRILL)
    add_track(board, net('+5V'), F_Cu, PWR_W, via_5v_relay_end[0], via_5v_relay_end[1], pk1_coilp[0], pk1_coilp[1])
    # +5V to flyback diode D1:1 at (8, 36) from K1:2 at (23.95, 56.05)
    # Route on F.Cu to x=8, via to B.Cu, broken segments reusing hops at y=44/46
    add_track(board, net('+5V'), F_Cu, PWR_W, pk1_coilp[0], pk1_coilp[1], 8, pk1_coilp[1])
    add_via(board, net('+5V'), 8, pk1_coilp[1], VIA_PWR_SIZE, VIA_PWR_DRILL)
    # B.Cu from (8,56.05) to (8,46) — does NOT cross +3V3 at y=45 (stops at y=46)
    add_track(board, net('+5V'), B_Cu, PWR_W, 8, pk1_coilp[1], 8, 46)
    # F.Cu hop at y=43-46 already placed by relay corridor above
    # B.Cu from (8,43) to (8,36) — above +3V3/USB_D+, no crossing
    add_track(board, net('+5V'), B_Cu, PWR_W, 8, 43, 8, pd1_k[1])
    add_via(board, net('+5V'), 8, pd1_k[1], VIA_PWR_SIZE, VIA_PWR_DRILL)
    add_track(board, net('+5V'), F_Cu, PWR_W, 8, pd1_k[1], pd1_k[0], pd1_k[1])

    # ==========================================================
    # USB DATA ON F.Cu (left side, J1 -> U3)
    # ==========================================================
    # Route USB_D+ and D- as L-shapes avoiding GND traces
    p_dp_j = p('J1', 'A6')
    p_dp_u = p('U3', '4')
    # Route at y=42, approach U3:4 via x=9 (left of GND via at x=10.05 and GND trace y=43.5)
    route_polyline(board, net('USB_D+'), F_Cu, SIG_W, [
        p_dp_j,
        (p_dp_j[0], 42),          # Vertical down to y=42
        (9, 42),                   # Horizontal to x=9
        (9, p_dp_u[1]),           # Down to U3:4 y=44
        p_dp_u,                    # Right to U3:4 pad at (13.55, 44)
    ])

    p_dm_j = p('J1', 'A7')
    p_dm_u = p('U3', '5')
    # USB D- via B.Cu hop to avoid crossing D+ (both go to same U3 x=13.55)
    # Extend B.Cu to near U3 so F.Cu stub is short and doesn't cross D+ at y=44
    dm_via1 = (7, p_dm_j[1] + 3)              # Shifted right for USB_D+ clearance (>0.25mm)
    dm_via2 = (p_dm_u[0] - 2, p_dm_u[1] + 0.5) # y=45 clears USB_D+ at y=44 (0.575mm gap)
    add_track(board, net('USB_D-'), F_Cu, SIG_W, p_dm_j[0], p_dm_j[1], dm_via1[0], dm_via1[1])
    add_via(board, net('USB_D-'), dm_via1[0], dm_via1[1])
    route_manhattan(board, net('USB_D-'), B_Cu, SIG_W, dm_via1, dm_via2, horiz_first=True)
    add_via(board, net('USB_D-'), dm_via2[0], dm_via2[1])
    # F.Cu stub: via (11.55,45) -> down to (11.55,44.5) -> right to U3:5 (13.55,44.5)
    route_polyline(board, net('USB_D-'), F_Cu, SIG_W, [
        dm_via2, (dm_via2[0], p_dm_u[1]), p_dm_u,
    ])

    # ==========================================================
    # UART via B.Cu CHANNELS (non-crossing plan)
    # ==========================================================
    # TX channel: y=34, from x=67 to x=24
    # RX channel: y=32, from x=65 to x=18

    p_tx_esp = p('U1', '35')  # Right side of ESP32
    p_tx_u3 = p('U3', '25')   # Left side of U3

    # ESP_TX: stub -> via at (67, pin_y) -> down to y=34 -> left to x=24 -> via -> stub to U3
    via_tx_r = (67, p_tx_esp[1])
    add_track(board, net('ESP_TX'), F_Cu, SIG_W, p_tx_esp[0], p_tx_esp[1], via_tx_r[0], via_tx_r[1])
    add_via(board, net('ESP_TX'), via_tx_r[0], via_tx_r[1])
    via_tx_l = (24, 34)
    route_polyline(board, net('ESP_TX'), B_Cu, SIG_W, [
        via_tx_r, (via_tx_r[0], 34), via_tx_l,
    ])
    add_via(board, net('ESP_TX'), via_tx_l[0], via_tx_l[1])
    # Route TX to U3:25 from ABOVE
    # RX occupies: F.Cu x=16 from y=32→40, then x=15.5 from y=40→41.55
    # TX must avoid x=16 from y=32-40 (RX territory) and x=16.5 (pad 24)
    # Strategy: arrive at x=17 (clear of RX at x=16), via bridge to B.Cu at y=38,
    # route on B.Cu from x=17 to x=16 at y=40.5, pop back to F.Cu, down to pad
    route_polyline(board, net('ESP_TX'), F_Cu, SIG_W, [
        via_tx_l,                       # (24, 34)
        (25, 34),                       # Right to x=25
        (25, 38),                       # Down to y=38
        (17, 38),                       # Left to x=17 (1mm from RX at x=16)
    ])
    # Via bridge at x=17, hop to x=16.5 on B.Cu (0.5mm offset from RX at x=16 for clearance)
    add_via(board, net('ESP_TX'), 17, 38)
    route_polyline(board, net('ESP_TX'), B_Cu, SIG_W, [
        (17, 38), (17, 40.5), (16.5, 40.5),  # Down then left to x=16.5
    ])
    add_via(board, net('ESP_TX'), 16.5, 40.5)
    route_polyline(board, net('ESP_TX'), F_Cu, SIG_W, [
        (16.5, 40.5), (p_tx_u3[0], 40.5), (p_tx_u3[0], p_tx_u3[1]),
    ])

    # ESP_RX: stub -> via at (65, pin_y) -> down to y=32 -> left to x=18 -> via -> stub to U3
    p_rx_esp = p('U1', '34')
    p_rx_u3 = p('U3', '26')
    via_rx_r = (65, p_rx_esp[1])
    add_track(board, net('ESP_RX'), F_Cu, SIG_W, p_rx_esp[0], p_rx_esp[1], via_rx_r[0], via_rx_r[1])
    add_via(board, net('ESP_RX'), via_rx_r[0], via_rx_r[1])
    via_rx_l = (16, 32)
    route_polyline(board, net('ESP_RX'), B_Cu, SIG_W, [
        via_rx_r, (via_rx_r[0], 32), via_rx_l,
    ])
    add_via(board, net('ESP_RX'), via_rx_l[0], via_rx_l[1])
    # Route RX to U3:26: x=16 gives 2.16mm clearance from D1:2 at x=18.16
    route_polyline(board, net('ESP_RX'), F_Cu, SIG_W, [
        via_rx_l,                      # (16, 32)
        (via_rx_l[0], 40),             # Down to y=40
        (p_rx_u3[0], 40),             # Left to U3:26 x = 15.5
        p_rx_u3,                       # Down to U3:26 = (15.5, 41.55)
    ])

    # ==========================================================
    # ESP_IO4 via B.Cu CHANNEL y=27
    # ==========================================================
    p_io4 = p('U1', '26')
    p_r3_1 = p('R3', '1')
    via_io4_r = (64, p_io4[1])
    add_track(board, net('ESP_IO4'), F_Cu, SIG_W, p_io4[0], p_io4[1], via_io4_r[0], via_io4_r[1])
    add_via(board, net('ESP_IO4'), via_io4_r[0], via_io4_r[1])
    # IO4: stay on B.Cu all the way to y=48 at x=15 (avoids crossing RX, TX, RELAY_COIL)
    # x=15 is clear of all B.Cu horizontals in y=27-48 range
    via_io4_l = (15, 48)
    route_polyline(board, net('ESP_IO4'), B_Cu, SIG_W, [
        via_io4_r, (via_io4_r[0], 27), (15, 27), via_io4_l,
    ])
    add_via(board, net('ESP_IO4'), via_io4_l[0], via_io4_l[1])
    # Short F.Cu stub to R3:1 at (13.09, 52)
    route_polyline(board, net('ESP_IO4'), F_Cu, SIG_W, [
        via_io4_l,                     # (15, 48)
        (p_r3_1[0], 48),              # Left to R3:1 x at y=48
        p_r3_1,                        # Down to R3:1 = (13.09, 52)
    ])

    # ==========================================================
    # ESP_IO5 via B.Cu CHANNEL y=6
    # ==========================================================
    p_io5 = p('U1', '29')
    p_r5_1 = p('R5', '1')
    via_io5_r = (66, p_io5[1])
    add_track(board, net('ESP_IO5'), F_Cu, SIG_W, p_io5[0], p_io5[1], via_io5_r[0], via_io5_r[1])
    add_via(board, net('ESP_IO5'), via_io5_r[0], via_io5_r[1])
    via_io5_l = (7, 7)
    route_polyline(board, net('ESP_IO5'), B_Cu, SIG_W, [
        via_io5_r, (via_io5_r[0], 7), via_io5_l,
    ])
    add_via(board, net('ESP_IO5'), via_io5_l[0], via_io5_l[1])
    # F.Cu stub: go right then via-bridge over VBUS at y=8 to reach R5:1 at y=16
    route_polyline(board, net('ESP_IO5'), F_Cu, SIG_W, [
        via_io5_l,                                     # (7, 7)
        (p_r5_1[0], 7),                                # Right to R5:1 x at y=7
    ])
    # Via bridge over VBUS (y=8 horizontal from x=3.6 to x=16.94)
    add_via(board, net('ESP_IO5'), p_r5_1[0], 7)
    add_track(board, net('ESP_IO5'), B_Cu, SIG_W, p_r5_1[0], 7, p_r5_1[0], 9)
    add_via(board, net('ESP_IO5'), p_r5_1[0], 9)
    route_polyline(board, net('ESP_IO5'), F_Cu, SIG_W, [
        (p_r5_1[0], 9),                               # Above VBUS
        p_r5_1,                                        # Down to R5:1 at (9.09, 16)
    ])

    # ==========================================================
    # EN / IO0 CIRCUIT ON F.Cu
    # ==========================================================

    # ESP_EN: R1:2 -> C4:1 (C4 at (44,15), left of +3V3 chain at x=46.09)
    p_r1_2 = p('R1', '2')
    p_c4_1 = p('C4', '1')
    # Route: R1:2 down to y=13, B.Cu bridge over +3V3 chain (x=46.09), then F.Cu down to C4:1
    route_polyline(board, net('ESP_EN'), F_Cu, SIG_W, [
        p_r1_2, (p_r1_2[0], 13),    # Down from R1:2 (47.91,10) to y=13
    ])
    add_via(board, net('ESP_EN'), p_r1_2[0], 13)
    add_track(board, net('ESP_EN'), B_Cu, SIG_W, p_r1_2[0], 13, 43, 13)  # B.Cu hop over +3V3
    add_via(board, net('ESP_EN'), 43, 13)
    route_polyline(board, net('ESP_EN'), F_Cu, SIG_W, [
        (43, 13), (43, p_c4_1[1]), p_c4_1,  # Down to C4:1 (43.05, 15)
    ])

    # ESP_EN: R1:2 -> U1:3 via x=49 corridor (avoiding ESP32 side pins)
    p_en = p('U1', '3')
    route_polyline(board, net('ESP_EN'), F_Cu, SIG_W, [
        p_r1_2,
        (49, p_r1_2[1]),    # Right to x=49 (gap between passives and ESP32 body)
        (49, p_en[1]),       # Up to EN pin Y
        p_en,                # Short hop to pin
    ])

    # ESP_EN: C4:1 -> SW2:2
    # C4:1 at (43.05, 15). Route left of +3V3, then via B.Cu to SW2
    p_sw2_2 = p('SW2', '2')
    via_en_top = (40, 36)
    # F.Cu: C4:1 left to x=40, then down to y=36
    route_polyline(board, net('ESP_EN'), F_Cu, SIG_W, [
        p_c4_1, (40, p_c4_1[1]), via_en_top,
    ])
    add_via(board, net('ESP_EN'), via_en_top[0], via_en_top[1])
    via_en_bot = (p_sw2_2[0], p_sw2_2[1] - 2)
    route_polyline(board, net('ESP_EN'), B_Cu, SIG_W, [
        via_en_top,
        (via_en_bot[0], 36),  # Horizontal to SW2 x at y=36
        via_en_bot,            # Vertical down to near SW2
    ])
    add_via(board, net('ESP_EN'), via_en_bot[0], via_en_bot[1])
    add_track(board, net('ESP_EN'), F_Cu, SIG_W, via_en_bot[0], via_en_bot[1], p_sw2_2[0], p_sw2_2[1])

    # ESP_IO0: R2:2 -> U1:25 via F.Cu route below ESP32 body
    # Routes at y=26 (below ESP32 bottom pins at y~24.5) to avoid all B.Cu channel crossings
    p_r2_2 = p('R2', '2')
    p_io0 = p('U1', '25')
    route_polyline(board, net('ESP_IO0'), F_Cu, SIG_W, [
        p_r2_2,                       # (47.91, 20)
        (48, p_r2_2[1]),              # Right to x=48
        (48, 26),                     # Down to y=26 (below ESP32 bottom pins)
        (70, 26),                     # Right past ESP32 right-side pins
        (70, p_io0[1]),               # Up to IO0 pin Y
        p_io0,                        # Left to U1:25
    ])

    # ESP_IO0: R2:2 -> SW1:2 via F.Cu corridor at x=42 then B.Cu below all channels
    p_sw1_2 = p('SW1', '2')
    via_io0_top = (42, 38)
    route_polyline(board, net('ESP_IO0'), F_Cu, SIG_W, [
        p_r2_2,
        (p_r2_2[0], 22),     # Down to y=22 (below R2:1 +3V3 pad at y=20)
        (42, 22),             # Horizontal left to x=42
        via_io0_top,          # Vertical down to y=38 (below all B.Cu channels)
    ])
    add_via(board, net('ESP_IO0'), via_io0_top[0], via_io0_top[1])
    via_io0_bot = (p_sw1_2[0], p_sw1_2[1] - 2)
    route_polyline(board, net('ESP_IO0'), B_Cu, SIG_W, [
        via_io0_top,
        (via_io0_bot[0], 38),  # Horizontal to SW1 x at y=38
        via_io0_bot,            # Vertical down to near SW1
    ])
    add_via(board, net('ESP_IO0'), via_io0_bot[0], via_io0_bot[1])
    add_track(board, net('ESP_IO0'), F_Cu, SIG_W, via_io0_bot[0], via_io0_bot[1], p_sw1_2[0], p_sw1_2[1])

    # ==========================================================
    # RELAY DRIVER ON F.Cu (bottom-left, local routes)
    # ==========================================================

    # RELAY_BASE: R3:2 -> Q1:2 - route at y=53.5 to clear R3:1 pad bottom edge
    p_r3_2 = p('R3', '2')
    p_q1_2 = p('Q1', '2')
    route_polyline(board, net('RELAY_BASE'), F_Cu, SIG_W, [
        p_r3_2, (p_r3_2[0], 53.5), (p_q1_2[0], 53.5), p_q1_2,
    ])

    # RELAY_COIL: Q1:3 -> K1:1 via B.Cu bridge (avoids ESP_RX, ESP_TX, all F.Cu crossings)
    p_q1_3 = p('Q1', '3')
    p_k1_1 = p('K1', '1')
    add_track(board, net('RELAY_COIL'), F_Cu, SIG_W, p_q1_3[0], p_q1_3[1], p_q1_3[0], 50)
    add_via(board, net('RELAY_COIL'), p_q1_3[0], 50)
    add_track(board, net('RELAY_COIL'), B_Cu, SIG_W, p_q1_3[0], 50, p_k1_1[0], 50)
    add_via(board, net('RELAY_COIL'), p_k1_1[0], 50)
    # K1:1 via is at same position as pad, so it connects directly

    # RELAY_COIL: D1:2 (anode) -> K1:1 via B.Cu bridge
    # D1:2 at (18.16,36), K1:1 at (22,50)
    # Route: D1:2 right to x=21, via to B.Cu, left to x=20, down to y=50, via, F.Cu to K1:1
    p_d1_2 = p('D1', '2')
    add_track(board, net('RELAY_COIL'), F_Cu, SIG_W, p_d1_2[0], p_d1_2[1], 21, p_d1_2[1])
    add_via(board, net('RELAY_COIL'), 21, p_d1_2[1])
    route_polyline(board, net('RELAY_COIL'), B_Cu, SIG_W, [
        (21, p_d1_2[1]),          # (21, 36)
        (20, p_d1_2[1]),          # Left to x=20 (extra clearance from K1:1 PTH at x=22)
        (20, p_k1_1[1]),          # (20, 50) down
    ])
    add_via(board, net('RELAY_COIL'), 20, p_k1_1[1])
    add_track(board, net('RELAY_COIL'), F_Cu, SIG_W, 20, p_k1_1[1], p_k1_1[0], p_k1_1[1])

    # ==========================================================
    # LED LOCAL ROUTES ON F.Cu
    # ==========================================================

    # LED_PWR: R4:1 -> D2:2 (horizontal pair at y=4)
    route_manhattan(board, net('LED_PWR'), F_Cu, SIG_W,
                    p('R4', '1'), p('D2', '2'), horiz_first=True)

    # LED_RELAY: R5:2 -> D3:2 (route at y=19.5 to avoid +5V F.Cu hop at x=8, y=15-18.5)
    route_polyline(board, net('LED_RELAY'), F_Cu, SIG_W, [
        p('R5', '2'),              # (10.91, 16)
        (p('R5', '2')[0], 19.5),   # Down 3.5mm
        (p('D3', '2')[0], 19.5),   # Horizontal at y=19.5 (below +5V via at y=18.5)
        p('D3', '2'),              # Up to D3:2 = (6.94, 16)
    ])

    # ==========================================================
    # RELAY OUTPUTS ON F.Cu (bottom, horizontal to J2)
    # ==========================================================

    p_k1_5 = p('K1', '5')
    p_j2_1 = p('J2', '1')
    p_k1_4 = p('K1', '4')
    p_j2_2 = p('J2', '2')

    # RELAY_COM: K1:5 -> J2:1
    route_polyline(board, net('RELAY_COM'), F_Cu, PWR_W, [
        p_k1_5,
        (p_k1_5[0], p_j2_1[1]),  # Match J2 Y first
        p_j2_1,                    # Horizontal to J2
    ])

    # RELAY_NO: K1:4 -> J2:2 (offset Y to avoid crossing COM)
    route_polyline(board, net('RELAY_NO'), F_Cu, PWR_W, [
        p_k1_4,
        (p_k1_4[0], p_k1_4[1] + 4),  # Down 4mm
        (p_j2_2[0], p_k1_4[1] + 4),   # Horizontal
        p_j2_2,                         # Up to J2
    ])

    # ==========================================================
    # GND CONNECTIONS (manually placed vias at safe positions)
    # ==========================================================

    # Each GND pad gets a via at a SPECIFIC position verified to not overlap other traces
    gnd_via_plan = [
        # (ref, pad, via_x_offset, via_y_offset) relative to pad
        ('C1', '2', 0, 0),      # Via right at pad (surrounded by +5V, only safe option)
        ('C2', '2', 0, 2),      # Below C2 (away from +3V3 horizontal at y=4)
        ('C3', '2', 0, -2),     # Above C3 (away from +3V3 via start)
        ('C5', '2', 0, 2),      # Below C5:2 at y=8 (avoids +3V3 horizontal at y=5)
        ('C4', '2', -3, 2),     # Far left-below of C4:2 (clear of U1 with C4 at (44,15))
        ('U2', '1', -2, 0),     # Left of U2 GND (away from +3V3 pin 2)
        ('U3', '3', -3.5, -1.5),  # Left and above U3:3 (avoids USB_D+ at y=44)
        ('U3', '29', 0, 0),     # Via at pad position (avoids track through U3 right-side pads)
        ('Q1', '1', -2, 0),     # Left of Q1 (away from relay traces)
        ('D2', '1', 0, 2),      # Below D2
        ('D3', '1', 0, -2),     # Above D3 at y=14 (clears +5V B.Cu at y=12.3)
    ]

    for ref, pad_num, dx, dy in gnd_via_plan:
        pos = get_pad_pos(board, ref, pad_num)
        if pos is None:
            continue
        px, py = pos
        vx, vy = px + dx, py + dy
        # Use SIG_W for pad-to-via stubs (bulk current via B.Cu zone, reduces clearance issues)
        add_track(board, net('GND'), F_Cu, SIG_W, px, py, vx, vy)
        add_via(board, net('GND'), vx, vy)

    # Connect U3 GND pads: U3:3 at (13.55,43.5) to U3:29 at (16,44)
    # Both pads connect to B.Cu GND zone via their respective vias
    # U3:3 via at (10.05,42) — short track from pad
    # U3:29 via at (20,44) — track goes right from pad
    # Connect pads directly: (13.55,43.5) -> (16,43.5) -> (16,44) [U3:29 pad]
    pu3_3 = p('U3', '3')
    pu3_29 = p('U3', '29')
    route_polyline(board, net('GND'), F_Cu, SIG_W, [
        (pu3_3[0], pu3_3[1]),         # U3:3 pad = (13.55, 43.5)
        (pu3_29[0], pu3_3[1]),         # Right to U3:29 x at U3:3 y
        (pu3_29[0], pu3_29[1]),        # Down to U3:29
    ])

    # ESP32 GND pads: pin 1, 38 (side pads)
    for pad_num in ['1', '38']:
        pos = get_pad_pos(board, 'U1', pad_num)
        if pos:
            add_via(board, net('GND'), pos[0], pos[1])

    # ESP32 thermal pad 39 - sparse vias (every 5th to avoid drill_out_of_range)
    for fp in board.GetFootprints():
        if fp.GetReference() == 'U1':
            pad39_positions = []
            for pad in fp.Pads():
                if pad.GetNumber() == '39':
                    pos = pad.GetPosition()
                    pad39_positions.append((pos.x / NM, pos.y / NM))
            if pad39_positions:
                for i, (px, py) in enumerate(pad39_positions):
                    if i % 5 == 0:
                        add_via(board, net('GND'), px, py)
            break

    # J1 USB GND - each pad gets via SOUTH to B.Cu GND plane (no F.Cu chains)
    p_b12 = p('J1', 'B12')
    p_b8 = p('J1', 'B8')
    p_a8 = p('J1', 'A8')
    p_a12 = p('J1', 'A12')
    # Shield pad connections (short, local)
    add_track(board, net('GND'), F_Cu, SIG_W, p_b12[0], p_b12[1], 1.68, 26.89)  # B12 -> S1
    add_track(board, net('GND'), F_Cu, SIG_W, p_a12[0], p_a12[1], 10.32, 26.89) # A12 -> S1
    # Each GND pad drops south to a via (below VBUS, avoids +5V corridor at x=3/8)
    for gnd_pos in [p_b12, p_b8, p_a8, p_a12]:
        # Skip B12 (x=2.8) — too close to +5V B.Cu at x=3; use S1 connection instead
        if abs(gnd_pos[0] - p_b12[0]) < 0.1:
            continue
        # A12 (x=9.2) needs special routing to avoid J1 NPTH at (8.89, 27.395)
        if abs(gnd_pos[0] - p_a12[0]) < 0.1:
            # Route right then south to clear NPTH and USB_D- B.Cu at y=29.32
            route_polyline(board, net('GND'), F_Cu, SIG_W, [
                gnd_pos, (10.5, gnd_pos[1]), (10.5, 31),
            ])
            add_via(board, net('GND'), 10.5, 31)
        else:
            add_track(board, net('GND'), F_Cu, SIG_W, gnd_pos[0], gnd_pos[1], gnd_pos[0], 28)
            add_via(board, net('GND'), gnd_pos[0], 28)

    # J1 VBUS - A4/B9 already connected via main trace to FB1
    # A9/B4 connects via separate F.Cu route to VBUS horizontal at y=8
    p_a9 = p('J1', 'A9')
    route_polyline(board, net('VBUS'), F_Cu, PWR_W, [
        p_a9,                         # (8.4, 26.32)
        (p_a9[0], 25),                # Up to y=25 (above J1 pad tops at ~25.55)
        (12, 25),                     # Right to x=12 (past LED area)
        (12, 8),                      # Up to VBUS horizontal at y=8
    ])

    # Button GND connections (bridge duplicate pads + via)
    for ref in ['SW1', 'SW2']:
        for fp in board.GetFootprints():
            if fp.GetReference() == ref:
                pad_positions = {}
                for pad in fp.Pads():
                    num = pad.GetNumber()
                    pos = (pad.GetPosition().x / NM, pad.GetPosition().y / NM)
                    pad_positions.setdefault(num, []).append(pos)
                for num, positions in pad_positions.items():
                    net_name = PAD_NETS.get((ref, num), '')
                    if not net_name or net_name not in net_map:
                        continue
                    if len(positions) >= 2:
                        pp1, pp2 = positions[0], positions[1]
                        add_track(board, net_map[net_name], F_Cu, SIG_W,
                                  pp1[0], pp1[1], pp2[0], pp2[1])
                    if num == '1' and positions:
                        # Use second pad position to avoid IO0/EN B.Cu traces at positions[0].x
                        px, py = positions[-1]
                        add_via(board, net('GND'), px, py + 2)  # Below button, away from RELAY_COM
                        add_track(board, net('GND'), F_Cu, PWR_W, px, py, px, py + 2)
                break

    print(f"   Routing complete")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("PCB Router v3 - ESP32 Simple IoT Switch")
    print("  Board: 80x60mm, 2-layer")
    print("=" * 60)

    # Step 1: Create new board
    print("\n1. Creating new board...")
    board = pcbnew.NewBoard(PCB_OUT)
    settings = board.GetDesignSettings()
    settings.SetBoardThickness(mm(1.6))
    settings.m_TrackMinWidth = mm(0.15)
    settings.m_ViasMinSize = mm(0.4)
    settings.m_MinThroughDrill = mm(0.15)  # Allow ESP32 thermal pad 0.2mm holes

    # Step 2: Define nets
    print("\n2. Defining nets...")
    net_map = {}
    for i, name in enumerate(NET_NAMES):
        n = pcbnew.NETINFO_ITEM(board, name, i)
        board.Add(n)
        net_map[name] = n
    print(f"   {len(NET_NAMES)} nets defined")

    # Step 3: Load and place footprints
    print("\n3. Loading and placing footprints...")
    for ref, lib_name, fp_name, x, y, rot in COMPONENTS:
        lib_path = os.path.join(FP_BASE, lib_name + '.pretty')
        fp = pcbnew.FootprintLoad(lib_path, fp_name)
        if fp is None:
            print(f"   ERROR: Could not load {lib_name}:{fp_name}")
            continue

        fp.SetReference(ref)
        fp.SetPosition(point(x, y))
        if rot != 0:
            fp.SetOrientationDegrees(rot)

        # Assign nets to pads
        assigned = 0
        for pad in fp.Pads():
            pad_num = pad.GetNumber()
            key = (ref, pad_num)
            if key in PAD_NETS:
                net_name = PAD_NETS[key]
                if net_name in net_map:
                    pad.SetNet(net_map[net_name])
                    assigned += 1
            elif pad_num == '' and ref == 'U3':
                # QFN exposed pad fragments share pad 29 net (GND)
                if ('U3', '29') in PAD_NETS:
                    pad.SetNet(net_map[PAD_NETS[('U3', '29')]])
                    assigned += 1

        board.Add(fp)
        print(f"   {ref}: at ({x},{y}) rot={rot} [{assigned} nets]")

    # Mounting holes
    for ref, x, y in MOUNTING_HOLES:
        lib_path = os.path.join(FP_BASE, 'MountingHole.pretty')
        fp = pcbnew.FootprintLoad(lib_path, 'MountingHole_2.7mm_M2.5')
        if fp:
            fp.SetReference(ref)
            fp.SetPosition(point(x, y))
            board.Add(fp)

    # Diagnostic: print all pad positions for precise routing
    print("\n   PAD POSITIONS:")
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        for pad in fp.Pads():
            num = pad.GetNumber()
            pos = pad.GetPosition()
            px, py = pos.x / NM, pos.y / NM
            net_name = pad.GetNet().GetNetname() if pad.GetNet() else ''
            if net_name:
                print(f"   {ref}:{num} = ({px:.2f}, {py:.2f}) net={net_name}")

    # Step 4: Board outline
    print("\n4. Drawing board outline...")
    outline = pcbnew.PCB_SHAPE(board)
    outline.SetShape(pcbnew.SHAPE_T_RECT)
    outline.SetStart(point(0, 0))
    outline.SetEnd(point(BOARD_W, BOARD_H))
    outline.SetLayer(Edge_Cuts)
    outline.SetWidth(mm(0.15))
    board.Add(outline)

    # Step 5: GND zone on B.Cu (covers entire board)
    print("\n5. Adding GND zone on B.Cu...")
    zone = pcbnew.ZONE(board)
    zone.SetNet(net_map['GND'])
    zone.SetLayer(B_Cu)
    zone.SetIsRuleArea(False)
    zone.SetDoNotAllowTracks(False)
    zone.SetDoNotAllowVias(False)
    zone.SetDoNotAllowPads(False)
    zone.SetDoNotAllowCopperPour(False)
    zone_ol = zone.Outline()
    zone_ol.NewOutline()
    zone_ol.Append(mm(0.5), mm(0.5))
    zone_ol.Append(mm(BOARD_W - 0.5), mm(0.5))
    zone_ol.Append(mm(BOARD_W - 0.5), mm(BOARD_H - 0.5))
    zone_ol.Append(mm(0.5), mm(BOARD_H - 0.5))
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    zone.SetThermalReliefGap(mm(0.3))
    zone.SetThermalReliefSpokeWidth(mm(0.5))
    zone.SetMinThickness(mm(0.25))
    board.Add(zone)

    # NO explicit antenna keepout zones — the ESP32-WROOM-32 footprint
    # has a built-in rule area for the antenna keepout that moves with
    # the component. With ESP32 at (60, 15), the keepout is at
    # y < 5.2 for x = [36, 84] — mostly off the top of the board.

    # Step 6: GND via stitching (perimeter + strategic interior)
    print("\n6. Adding GND via stitching...")
    stitch = [
        # Perimeter
        (9, 5), (35, 5),  # Removed (20,5) - was on +5V track at x=20
        (14, 48), (12, 55),  # x=14 avoids +5V B.Cu at x=12.5; y=48 avoids +3V3 route at y=46
        # Removed (12, 25) — conflicts with VBUS A9 route at y=25
        (40, 55), (60, 55), (75, 55),
        (75, 40), (75, 25),
        # Interior strategic points (between component groups)
        (20, 20), (35, 20), (35, 35),
        (50, 42), (65, 42),  # Moved below ESP_EN (y=36) and ESP_IO0 (y=38) B.Cu corridors
        (20, 35),
    ]
    for vx, vy in stitch:
        add_via(board, net_map['GND'], vx, vy)
    print(f"   {len(stitch)} GND stitching vias")

    # Step 7: Route all traces
    print("\n7. Routing traces...")
    route_all(board, net_map)

    # Step 8: Fill zones and save
    print("\n8. Filling zones and saving...")
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(PCB_OUT, board)
    print(f"   Saved to {PCB_OUT}")

    # Summary
    fps = board.GetFootprints()
    tracks = board.GetTracks()
    n_tracks = sum(1 for t in tracks if type(t).__name__ == 'PCB_TRACK')
    n_vias = sum(1 for t in tracks if type(t).__name__ == 'PCB_VIA')
    print(f"\n{'=' * 60}")
    print(f"PCB ROUTING v3 COMPLETE")
    print(f"  Board: {BOARD_W}x{BOARD_H}mm")
    print(f"  Footprints: {len(fps)}")
    print(f"  Tracks: {n_tracks}, Vias: {n_vias}")
    print(f"  Zones: {len(board.Zones())}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
