# Hexadecimal-Doppler-Radar
X-Band (10.525 GHz) Doppler weather radar architecture utilizing 16-state (0.0V–1.0V) hexadecimal analog logic. Includes parametric OpenSCAD dish/choke-feedhorn CAD, KiCad netlist compilers, and FCC Part 5 (Form 442) technical exhibits for FireProve tower integration.

# RT-Hex Doppler Weather Radar Platform

**X-Band (10.525 GHz) Doppler Weather Radar Architecture powered by 16-State (0.0V–1.0V) Hexadecimal Analog Logic.**

Designed for integration onto **FireProve** drone telemetry towers, this repository provides a unified hardware, CAD, and regulatory compiler. Field installers configure site-specific variables (GPS, tower height, dish diameter, RF output power, and 240V–520V AC mains supply) in a validated JSON file to automatically generate:
1. **KiCad S-Expression Netlists (`.net`)** with impedance-controlled RF front-ends and heavy-copper power rails.
2. **Parametric OpenSCAD Geometry (`site_overrides.scad`)** for parabolic reflectors, scalar choke-ring feedhorns, and tower mast brackets.
3. **FCC Part 5 (Form 442) Technical Exhibits (`fcc_complete_submission.json`)** complete with EIRP link budgets, OET Bulletin 65 MPE exclusion zones, and FAA obstruction checks.

---

## Repository Structure

```text
├── compile_radar_build.py        # Unified schema validator, physics engine, & netlist/CAD compiler
├── fcc_hex_doppler_radar.scad    # Parametric OpenSCAD model (parabolic dish, choke horn, radome, mount)
├── site_config.json              # Field installer configuration (NAD83 GPS, tower height, power/dish scale)
├── site_config.schema.json       # Draft-07 JSON Schema enforcing physical, electrical, and RF limits
├── requirements.txt              # Python dependencies (jsonschema)
└── README.md                     # Documentation & build instructions
```

*(Running `compile_radar_build.py` generates `fcc_hex_doppler.net`, `site_overrides.scad`, and `fcc_complete_submission.json`.)*

---

## Prerequisites & Installation

Ensure you have **Python 3.9+**, **KiCad 7/8+**, and **OpenSCAD** installed.

```bash
git clone https://github.com
cd RT-Hex-Doppler-Radar
pip install jsonschema
```

---

## Field Installer & Build Workflow

### 1. Configure Site & Power Scaling (`site_config.json`)
Edit `site_config.json` with your tower's physical and electrical parameters before compiling:

* **`geographic_coordinates_nad83`**: Decimal and DMS latitude/longitude plus ground elevation (AMSL).
* **`tower_and_mounting`**: Overall tower height (AGL), radar radiation center height, and mast outer diameter. *(Towers $\ge$ 60.96 m / 200 ft automatically trigger an FAA Form 7460-1 alert.)*
* **`hardware_and_power_scaling`**:
  * `dish_diameter_m`: Scales reflector diameter, focal length ($f/D = 0.40$), strut thickness, and 120 mph wind-load calculations.
  * `tx_power_watts`: Scales RF output power, EIRP, MPE safe-exposure distances, and KiCad PCB copper weight (2oz for $<50\text{W}$, 4oz for $\ge 50\text{W}$).
  * `ac_mains_volts` & `ac_phases`: Supports **240V single-phase** through **480V / 510V / 520V three-phase** industrial tower feeds. (Voltages $>250\text{V}$ automatically enforce 3-phase validation.)

### 2. Run the Unified Build Compiler
Execute the build script to validate your configuration and generate all CAD, PCB, and legal outputs:

```bash
python compile_radar_build.py
```

Optional CLI flags allow custom file paths:
```bash
python compile_radar_build.py --site site_config.json --net-out fcc_hex_doppler.net --fcc-out fcc_complete_submission.json
```

### 3. OpenSCAD 3D Rendering & Fabrication
1. Ensure `include <site_overrides.scad>` is present at the top of `fcc_hex_doppler_radar.scad`.
2. Open `fcc_hex_doppler_radar.scad` in **OpenSCAD** and press **F5** (Preview) or **F6** (Render).
3. Export `.STL` / `.STEP` files for CNC/3D fabrication of the scalar choke feedhorn and mast mount, and export orthogonal PNG views (Front, Side, Isometric) for your FCC mechanical exhibit.

### 4. KiCad PCB Import
1. Open **KiCad PCB Editor** and create a new board project.
2. Select **File $\rightarrow$ Import $\rightarrow$ Netlist...** and load the generated `fcc_hex_doppler.net`.
3. Follow the **RT Infrastructure Fabrication Rules** during layout:
   * **RF Top Layer:** Rogers RO4350B (20 mil core, $\varepsilon_r = 3.48$, $1.12\text{ mm}$ trace width for $50\,\Omega$ microstrip).
   * **Analog Hex Guarding:** Surround all `IF_I`, `IF_Q`, and `0.0V–1.0V` (`0.0625V` step) hexadecimal comparator lines with stitched `GND_RF_SHIELD_GUARD` via fences.
   * **Thermal Armor:** Mount `RTPhaseChangeThermalInterface` pads and 3D vapor chamber heatsinks on the RF Power Amplifier (`U1`) and AC-DC rectifier (`PS1`).

---

## Dynamic Scaling Reference Tiers

| Configuration Tier | Dish Diameter | TX Power | Antenna Gain | Total EIRP | Tower Mains Input | Est. Line Current |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Micro Drone Tower** | 0.6 m | 0.1 W (20 dBm) | 24.0 dBi | 17.8 W (42.5 dBm) | 240V (1-Phase) | ~0.7 A |
| **Tier 2: Regional Weather** | 1.2 m | 25 W (44 dBm) | 30.0 dBi | 17.8 kW (72.5 dBm) | 520V (3-Phase) | ~0.3 A / phase |
| **Tier 3: High-Power Array** | 2.4 m | 250 W (54 dBm) | 36.0 dBi | 708 kW (88.5 dBm) | 520V (3-Phase) | ~1.1 A / phase |

---

## FCC Part 5 (Form 442) Filing Checklist

Before transmitting outdoors, provide your regulatory attorney with:
1. **`fcc_complete_submission.json`**: Contains verified NAD83 coordinates, emission designator (`50M0F3N`), occupied bandwidth (`50 MHz`), EIRP, harmonic suppression (`65 dB` via Chebyshev LPF), and OET Bulletin 65 MPE safe-exposure radii.
2. **KiCad Schematics & Gerber/PDF Plots**: Exported from `fcc_hex_doppler.net` showing the low-pass harmonic filter (`FL1`) and circulator/isolator (`U2`) ahead of the antenna port.
3. **OpenSCAD Orthogonal Renders**: Showing the quarter-wave scalar choke ring and rim shroud used for sidelobe suppression.
4. **Narrative Statement of Experiment**: Explaining the comparative evaluation of **16-state (0.0V–1.0V) analog hexadecimal quantization** against standard binary ADC Doppler signal processing.

---

## License

Copyright (c) 2026 Revolutionary Technology Company. All rights reserved.
