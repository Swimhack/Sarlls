"""
Patch: Move D1 flyback diode away from K1 relay to prevent seating interference.
D1 (DO-41) at (30, 40) sits under K1 relay body. Move to (30, 34) for clearance.
"""
import sys
sys.path.insert(0, r"C:\Users\james\AppData\Local\Programs\KiCad\9.0\lib\python3\dist-packages")
import pcbnew

PCB_PATH = r"C:\STRICKLAND\Strickland Technology Marketing\Sarlls\production\ESP32_Simple_IoT.kicad_pcb"

board = pcbnew.LoadBoard(PCB_PATH)

# Find D1
d1 = None
for fp in board.GetFootprints():
    if fp.GetReference() == "D1":
        d1 = fp
        break

if not d1:
    print("ERROR: D1 not found")
    sys.exit(1)

old_pos = d1.GetPosition()
old_x = pcbnew.ToMM(old_pos.x)
old_y = pcbnew.ToMM(old_pos.y)
print(f"D1 current position: ({old_x}, {old_y})")

# Move D1 from (30, 40) to (30, 34) — 6mm north, clears K1 relay body
new_y = 34.0
new_pos = pcbnew.VECTOR2I(pcbnew.FromMM(old_x), pcbnew.FromMM(new_y))
d1.SetPosition(new_pos)
print(f"D1 moved to: ({old_x}, {new_y})")

# Delete traces connected to D1 pads so they can be re-routed
d1_nets = set()
for pad in d1.Pads():
    net = pad.GetNet()
    if net:
        d1_nets.add(net.GetNetname())
print(f"D1 nets: {d1_nets}")

# Find and remove traces that connected to D1's old pad positions
# Old pad positions were approximately (30, 40) and (40.16, 40)
tracks_to_remove = []
for track in board.GetTracks():
    if not isinstance(track, pcbnew.PCB_TRACK):
        continue
    start = track.GetStart()
    end = track.GetEnd()
    sx, sy = pcbnew.ToMM(start.x), pcbnew.ToMM(start.y)
    ex, ey = pcbnew.ToMM(end.x), pcbnew.ToMM(end.y)

    # Check if track endpoint is near D1's OLD pad positions
    for px, py in [(30.0, 40.0), (40.16, 40.0)]:
        for tx, ty in [(sx, sy), (ex, ey)]:
            if abs(tx - px) < 0.5 and abs(ty - py) < 0.5:
                tracks_to_remove.append(track)
                break

print(f"Removing {len(tracks_to_remove)} traces connected to D1 old position")
for t in tracks_to_remove:
    board.Remove(t)

# Add new traces from D1's new pad positions to nearby net points
# D1 pad 1 (+5V) at (30, 34), pad 2 (RELAY_COIL) at (40.16, 34)
# We need to connect these to the existing +5V and RELAY_COIL nets

# Find the net codes
net_5v = board.FindNet("+5V")
net_coil = board.FindNet("RELAY_COIL")

if not net_5v or not net_coil:
    # Try alternate net names
    for net in board.GetNetInfo().NetsByName():
        print(f"  Net: {net}")
    print("WARNING: Could not find +5V or RELAY_COIL nets")
else:
    # Route D1:1 (+5V) - short vertical trace from (30, 34) down to where old trace was
    # Then horizontal to connect to existing +5V network
    t1 = pcbnew.PCB_TRACK(board)
    t1.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(30.0), pcbnew.FromMM(34.0)))
    t1.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(30.0), pcbnew.FromMM(40.0)))
    t1.SetWidth(pcbnew.FromMM(0.4))
    t1.SetLayer(pcbnew.F_Cu)
    t1.SetNet(net_5v)
    board.Add(t1)

    # Route D1:2 (RELAY_COIL) - short vertical trace
    t2 = pcbnew.PCB_TRACK(board)
    t2.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(40.16), pcbnew.FromMM(34.0)))
    t2.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(40.16), pcbnew.FromMM(40.0)))
    t2.SetWidth(pcbnew.FromMM(0.4))
    t2.SetLayer(pcbnew.F_Cu)
    t2.SetNet(net_coil)
    board.Add(t2)

    print("Added vertical trace stubs from new D1 position to old routing points")

# Save
pcbnew.SaveBoard(PCB_PATH, board)
print(f"Saved: {PCB_PATH}")
