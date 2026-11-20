import json
import sys

def compile_site_package(site_file="site_config.json", exhibit_file="fcc_form442_exhibit.json"):
    with open(site_file, "r") as f:
        site = json.load(f)
    with open(exhibit_file, "r") as f:
        exhibit = json.load(f)

    # 1. Automated FAA 200-foot (60.96m) Obstruction Check
    tower_h = site["tower_and_mounting"]["overall_tower_height_agl_m"]
    if tower_h >= 60.96:
        site["tower_and_mounting"]["faa_notification_required"] = True
        print("[WARNING] Tower height >= 60.96m (200ft). FAA Form 7460-1 filing required!")

    # 2. Merge RF Exhibit + Site Data for Attorney Review
    full_filing = {
        "filing_summary": "FCC Part 5 Experimental Radiolocation / Weather Radar Package",
        "site_configuration": site,
        "technical_rf_exhibit": exhibit
    }

    with open("fcc_complete_submission.json", "w") as f:
        json.dump(full_filing, f, indent=4)

    # 3. Export OpenSCAD Override Header for Field Bracket Printing/Machining
    mast_d = site["tower_and_mounting"]["mast_outer_diameter_mm"]
    elev = site["antenna_alignment"]["elevation_tilt_deg"]
    scad_header = (
        f"// Auto-generated from {site_file} - Do not edit manually\n"
        f"mast_diameter = {mast_d};\n"
        f"elevation_angle = {elev};\n"
    )
    with open("site_overrides.scad", "w") as f:
        f.write(scad_header)

    print("[SUCCESS] Compiled fcc_complete_submission.json and site_overrides.scad")

if __name__ == "__main__":
    compile_site_package()
