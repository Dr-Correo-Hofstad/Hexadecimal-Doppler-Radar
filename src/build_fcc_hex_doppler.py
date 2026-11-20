import argparse
import json
import math

# ==============================================================================
# FCC PART 5 EXPERIMENTAL & RT HEXADECIMAL FABRICATION PARAMETERS
# ==============================================================================
FCC_RF_SPECS = {
    "band_name": "X-Band Radiolocation / Weather Test",
    "center_freq_ghz": 10.525,
    "occupied_bandwidth_mhz": 50.0,
    "emission_designator": "50M0F3N",  # FMCW / Doppler unmodulated/FM pulse
    "tx_power_dbm": 20.0,              # 100 mW (0.1 W) low-power experimental TX
    "antenna_gain_dbi": 24.0,          # 60cm parabolic dish @ 10.525 GHz (~55% eff)
    "cable_loss_db": 1.5,
    "eirp_dbm": 42.5,                  # 20 + 24 - 1.5 = 42.5 dBm (~17.8 W EIRP)
    "harmonic_attenuation_db": 65.0    # Enforced via 7th-order Chebyshev LPF
}

RT_FABRICATION_RULES = {
    "pcb_substrate": "Rogers RO4350B (RF Top) + FR4-HighTg (Hex Logic)",
    "rf_dielectric_er": 3.48,
    "rf_substrate_thickness_mm": 0.508, # 20 mil core for 50-ohm microstrip
    "microstrip_50ohm_width_mm": 1.12,  # Calculated for RO4350B 20mil
    "copper_weight_oz": 2,
    "guard_ring_enabled": True,
    "thermal_interface": "RTPhaseChangeThermalInterface",
    "hex_logic_levels_v": [round(i * 0.0625, 4) for i in range(16)]
}

def generate_kicad_sexpr_netlist():
    """Generates a valid KiCad S-Expression (.net) file with RF & Hex stages."""
    netlist_content = """(export (version "E")
  (design
    (source "build_fcc_hex_doppler.py")
    (tool "RT-Hex-KiCad-Compiler v2.0")
  )
  (components
    (comp (ref "U1")
      (value "X_BAND_VCO_TRANSCEIVER")
      (footprint "Package_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm")
    )
    (comp (ref "FL1")
      (value "CHEBYSHEV_LPF_11GHZ_HARMONIC_SUPPRESS")
      (footprint "Filter:Filter_Mini-Circuits_FV1206")
    )
    (comp (ref "U2")
      (value "CIRCULATOR_ISOLATOR_10_5GHZ")
      (footprint "RF_Module:RF_Circulator_SMT_10mm")
    )
    (comp (ref "J1")
      (value "SMA_ANTENNA_FEEDHORN_50OHM")
      (footprint "Connector_Coaxial:SMA_Amphenol_132289_EdgeMount")
    )
    (comp (ref "U3")
      (value "IQ_DOWNCONVERTER_MIXER")
      (footprint "Package_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm")
    )
    (comp (ref "U4")
      (value "DUAL_IF_LNA_1MHZ_BANDWIDTH")
      (footprint "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")
    )
    (comp (ref "U5")
      (value "RT_HEX_16STATE_QUANTIZER_0V_1V")
      (footprint "Package_QFP:LQFP-64_10x10mm_P0.5mm")
    )
    (comp (ref "U6")
      (value "RT_SATCOM_TELEMETRY_BRIDGE")
      (footprint "Package_BGA:BGA-144_10x10mm_Layout12x12_P0.8mm")
    )
  )
  (nets
    (net (code "1") (name "RF_TX_RAW_50OHM")
      (node (ref "U1") (pin "12"))
      (node (ref "FL1") (pin "1"))
    )
    (net (code "2") (name "RF_TX_FILTERED_50OHM")
      (node (ref "FL1") (pin "2"))
      (node (ref "U2") (pin "1"))
    )
    (net (code "3") (name "RF_ANTENNA_PORT_50OHM")
      (node (ref "U2") (pin "2"))
      (node (ref "J1") (pin "1"))
    )
    (net (code "4") (name "RF_RX_ECHO_50OHM")
      (node (ref "U2") (pin "3"))
      (node (ref "U3") (pin "4"))
    )
    (net (code "5") (name "IF_I_ANALOG_GUARDED")
      (node (ref "U3") (pin "10"))
      (node (ref "U4") (pin "3"))
    )
    (net (code "6") (name "IF_Q_ANALOG_GUARDED")
      (node (ref "U3") (pin "11"))
      (node (ref "U4") (pin "5"))
    )
    (net (code "7") (name "HEX_STATE_BUS_I_0V_1V")
      (node (ref "U4") (pin "1"))
      (node (ref "U5") (pin "14"))
    )
    (net (code "8") (name "HEX_STATE_BUS_Q_0V_1V")
      (node (ref "U4") (pin "7"))
      (node (ref "U5") (pin "15"))
    )
    (net (code "9") (name "RT_HEX_PARALLEL_OUT")
      (node (ref "U5") (pin "32"))
      (node (ref "U6") (pin "A4"))
    )
    (net (code "10") (name "GND_RF_SHIELD_GUARD")
      (node (ref "U1") (pin "33"))
      (node (ref "FL1") (pin "3"))
      (node (ref "U2") (pin "4"))
      (node (ref "J1") (pin "2"))
      (node (ref "U3") (pin "25"))
      (node (ref "U4") (pin "4"))
      (node (ref "U5") (pin "64"))
      (node (ref "U6") (pin "G7"))
    )
  )
)"""
    return netlist_content

def generate_fcc_exhibit():
    """Generates the technical exhibit data required for FCC Form 442."""
    wavelength_m = 0.299792458 / FCC_RF_SPECS["center_freq_ghz"]
    dish_dia_m = 0.60
    # Approximate 3dB beamwidth = 70 * lambda / D
    beamwidth_deg = round(70.0 * (wavelength_m / dish_dia_m), 2)
    
    exhibit = {
        "document_type": "FCC Form 442 Technical Exhibit - Experimental Doppler Radar",
        "rf_parameters": FCC_RF_SPECS,
        "antenna_characteristics": {
            "type": "Prime-Focus Parabolic Dish with Circular Waveguide Feedhorn",
            "diameter_m": dish_dia_m,
            "3db_beamwidth_degrees": beamwidth_deg,
            "polarization": "Linear Vertical",
            "front_to_back_ratio_db": 32.0
        },
        "pcb_compliance_architecture": RT_FABRICATION_RULES
    }
    return exhibit

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile FCC-Ready Hex Doppler Netlist & Exhibit")
    parser.add_argument("--net-out", type=str, default="fcc_hex_doppler.net", help="KiCad Netlist output")
    parser.add_argument("--fcc-out", type=str, default="fcc_form442_exhibit.json", help="FCC Technical Exhibit JSON")
    args = parser.parse_args()

    with open(args.net_out, "w") as f:
        f.write(generate_kicad_sexpr_netlist())
    
    with open(args.fcc_out, "w") as f:
        json.dump(generate_fcc_exhibit(), f, indent=4)

    print(f"[SUCCESS] Generated KiCad Netlist: {args.net_out}")
    print(f"[SUCCESS] Generated FCC Form 442 Exhibit: {args.fcc_out}")
