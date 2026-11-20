import json
import sys
from jsonschema import validate, ValidationError

def validate_installer_config(site_file="site_config.json", schema_file="site_config.schema.json"):
    with open(site_file, "r") as f:
        site_data = json.load(f)
    with open(schema_file, "r") as f:
        schema_data = json.load(f)

    try:
        validate(instance=site_data, schema=schema_data)
    except ValidationError as err:
        print(f"[ERROR] Invalid installer config in {site_file}: {err.message}")
        sys.exit(1)

    # Cross-field physical sanity check
    tower_h = site_data["tower_and_mounting"]["overall_tower_height_agl_m"]
    radar_h = site_data["tower_and_mounting"]["radar_radiation_center_agl_m"]
    if radar_h > tower_h:
        print(f"[ERROR] Radar height ({radar_h}m) cannot exceed overall tower height ({tower_h}m).")
        sys.exit(1)

    print("[VALIDATED] site_config.json passed all schema and physical checks.")
    return site_data
