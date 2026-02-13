"""Check which KiCad footprint libraries are available."""
import os

fp_base = r'C:\Users\james\AppData\Local\Programs\KiCad\9.0\share\kicad\footprints'
libs = os.listdir(fp_base)

# Map of our footprints: library_name -> footprint_name
FOOTPRINTS = {
    'Connector_USB': 'USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal',
    'Inductor_SMD': 'L_0805_2012Metric',
    'Package_TO_SOT_SMD': ['SOT-223-3_TabPin2', 'SOT-23'],
    'Capacitor_SMD': 'C_0805_2012Metric',
    'Package_DFN_QFN': 'QFN-28-1EP_5x5mm_P0.5mm_EP3.35x3.35mm',
    'RF_Module': 'ESP32-WROOM-32',
    'Resistor_SMD': 'R_0805_2012Metric',
    'Button_Switch_SMD': 'SW_SPST_TL3342',
    'Relay_THT': 'Relay_SPDT_SANYOU_SRD_Series_Form_C',
    'Diode_THT': 'D_DO-41_SOD81_P10.16mm_Horizontal',
    'Connector_Phoenix_MC': 'PhoenixContact_MC_1,5_2-G-3.81_1x02_P3.81mm_Horizontal',
    'LED_SMD': 'LED_0805_2012Metric',
    'MountingHole': 'MountingHole_2.7mm_M2.5',
}

import pcbnew

for lib_name, fp_names in FOOTPRINTS.items():
    pretty = lib_name + '.pretty'
    lib_path = os.path.join(fp_base, pretty)

    if not os.path.isdir(lib_path):
        print(f'MISSING LIB: {lib_name}')
        continue

    if isinstance(fp_names, str):
        fp_names = [fp_names]

    for fp_name in fp_names:
        try:
            fp = pcbnew.FootprintLoad(lib_path, fp_name)
            if fp:
                pads = list(fp.Pads())
                print(f'OK: {lib_name}:{fp_name} -> {len(pads)} pads')
                for pad in pads:
                    num = pad.GetNumber()
                    px = pad.GetPosition().x / 1e6
                    py = pad.GetPosition().y / 1e6
                    sx = pad.GetSize().x / 1e6
                    sy = pad.GetSize().y / 1e6
                    print(f'    Pad {num}: ({px:.3f}, {py:.3f}) size ({sx:.3f}x{sy:.3f})')
            else:
                print(f'NONE: {lib_name}:{fp_name}')
        except Exception as e:
            print(f'ERROR: {lib_name}:{fp_name} -> {e}')
