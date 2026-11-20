import math
import json

C = 299792458.0  # Speed of light (m/s)

def calculate_scaled_radar(
    dish_diameter_m=1.2,
    freq_ghz=10.525,
    tx_power_watts=25.0,
    ac_mains_volts=520.0,
    ac_phases=3,
    pa_efficiency=0.35,      # 35% solid-state X-band PA efficiency
    aperture_efficiency=0.55 # 55% parabolic dish efficiency
):
    wavelength_m = C / (freq_ghz * 1e9)

    # 1. Dynamic RF Antenna & EIRP Physics
    # Gain G = eta * (pi * D / lambda)^2
    gain_linear = aperture_efficiency * ((math.pi * dish_diameter_m) / wavelength_m) ** 2
    gain_dbi = round(10.0 * math.log10(gain_linear), 2)
    beamwidth_deg = round(70.0 * (wavelength_m / dish_diameter_m), 2)

    tx_power_dbm = round(10.0 * math.log10(tx_power_watts * 1000.0), 2)
    cable_loss_db = 1.5
    eirp_dbm = round(tx_power_dbm + gain_dbi - cable_loss_db, 2)
    eirp_watts = round((10 ** (eirp_dbm / 10.0)) / 1000.0, 2)

    # 2. Dynamic Industrial AC Mains Power & Thermal Load (240V / 510V / 520V)
    # Total DC input required by RF Power Amplifier + Hex Logic Bus (150W overhead)
    rf_dc_draw_watts = tx_power_watts / pa_efficiency
    total_system_watts = rf_dc_draw_watts + 150.0
    waste_heat_watts = total_system_watts - tx_power_watts
    heat_btu_hr = round(waste_heat_watts * 3.41214, 1)

    power_factor = 0.95
    psu_efficiency = 0.92
    ac_apparent_va = total_system_watts / (power_factor * psu_efficiency)

    if ac_phases == 3:
        # Three-phase line current: I = VA / (sqrt(3) * V_LL)
        ac_current_amps = round(ac_apparent_va / (math.sqrt(3) * ac_mains_volts), 2)
    else:
        # Single-phase line current: I = VA / V
        ac_current_amps = round(ac_apparent_va / ac_mains_volts, 2)

    # 3. Dynamic Structural & OpenSCAD Scaling (Wind Load @ 120 mph / 53.6 m/s)
    dish_area_m2 = math.pi * ((dish_diameter_m / 2.0) ** 2)
    wind_force_newtons = round(0.613 * (53.6 ** 2) * 1.4 * dish_area_m2, 1)

    scad_params = {
        "dish_diameter": round(dish_diameter_m * 1000.0, 1),
        "focal_length": round((dish_diameter_m * 1000.0) * 0.40, 1), # Constant f/D = 0.4
        "dish_thickness": round(max(4.0, dish_diameter_m * 6.5), 1),
        "strut_thickness": round(max(9.0, dish_diameter_m * 14.0), 1),
        "mast_diameter": round(max(50.8, dish_diameter_m * 85.0), 1)
    }

    return {
        "rf_scaling_summary": {
            "dish_diameter_m": dish_diameter_m,
            "frequency_ghz": freq_ghz,
            "tx_power_watts": tx_power_watts,
            "tx_power_dbm": tx_power_dbm,
            "antenna_gain_dbi": gain_dbi,
            "beamwidth_3db_deg": beamwidth_deg,
            "eirp_dbm": eirp_dbm,
            "eirp_watts": eirp_watts
        },
        "electrical_and_thermal": {
            "ac_input_voltage_v": ac_mains_volts,
            "ac_phases": ac_phases,
            "estimated_line_current_amps": ac_current_amps,
            "total_dc_draw_watts": round(total_system_watts, 1),
            "thermal_dissipation_watts": round(waste_heat_watts, 1),
            "cooling_required_btu_hr": heat_btu_hr
        },
        "structural_and_scad": {
            "max_wind_load_newtons_120mph": wind_force_newtons,
            "openscad_dimensions_mm": scad_params
        }
    }

if __name__ == "__main__":
    # Example: 1.2m Dish, 25W TX, running on 520V 3-Phase Tower Power
    result = calculate_scaled_radar(
        dish_diameter_m=1.2,
        tx_power_watts=25.0,
        ac_mains_volts=520.0,
        ac_phases=3
    )
    print(json.dumps(result, indent=4))

    # Automatically write updated CAD dimensions for OpenSCAD
    with open("site_overrides.scad", "w") as f:
        for k, v in result["structural_and_scad"]["openscad_dimensions_mm"].items():
            f.write(f"{k} = {v};\n")
