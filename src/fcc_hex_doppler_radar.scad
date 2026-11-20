// ============================================================================
// RT-Hex X-Band (10.525 GHz) Doppler Weather Radar Dish & Tower Assembly
// Designed for FireProve Tower Integration & FCC Form 442 Mechanical Spec
// ============================================================================
include <site_overrides.scad>

$fn = 120;

// --- Core RF & Mechanical Dimensions (mm) ---
dish_diameter = 600.0;      // 60 cm reflector (approx 3.3 deg beamwidth @ 10.525 GHz)
focal_length = 240.0;       // f/D ratio = 0.40 (optimal illumination)
dish_thickness = 4.0;
rim_lip_height = 18.0;      // Sidelobe suppression shroud lip

// X-Band Waveguide & Choke Ring Dimensions (lambda = 28.48 mm)
wg_inner_dia = 22.86;       // Standard WR-90 / circular X-band throat
wg_wall = 2.5;
choke_ring_dia = 58.0;      // Quarter-wave scalar choke ring for sidelobe reduction
choke_depth = 7.12;         // lambda / 4

// FireProve Tower Mast & Gimbal
mast_diameter = 50.8;       // 2-inch schedule 40 mast pipe
elevation_angle = 15.0;     // Tilt angle above horizon (degrees)

// --- Modules ---

module parabolic_reflector() {
    r_max = dish_diameter / 2;
    steps = 50;
    z_rim = (r_max * r_max) / (4 * focal_length);

    union() {
        // Parabolic dish body
        rotate_extrude() {
            polygon(points = concat(
                [for (i = [0 : steps])
                    let (r = (r_max / steps) * i, z = (r * r) / (4 * focal_length))
                    [r, z]
                ],
                [for (i = [steps : -1 : 0])
                    let (r = (r_max / steps) * i, z = ((r * r) / (4 * focal_length)) + dish_thickness)
                    [r, z]
                ]
            ));
        }
        // Sidelobe suppression rim shroud
        translate([0, 0, z_rim])
            difference() {
                cylinder(h = rim_lip_height, r = r_max, center = false);
                translate([0, 0, -1])
                    cylinder(h = rim_lip_height + 2, r = r_max - dish_thickness, center = false);
            }
    }
}

module scalar_feedhorn_and_hex_box() {
    translate([0, 0, focal_length]) {
        // 1. Waveguide Horn Throat (pointing down at vertex)
        difference() {
            cylinder(h = 65, d = wg_inner_dia + (wg_wall * 2), center = true);
            cylinder(h = 67, d = wg_inner_dia, center = true);
        }

        // 2. Quarter-Wave Scalar Choke Ring (reduces back/side radiation)
        translate([0, 0, -25])
            difference() {
                cylinder(h = choke_depth + 3, d = choke_ring_dia, center = true);
                translate([0, 0, -2])
                    cylinder(h = choke_depth + 2, d = choke_ring_dia - 6, center = true);
                cylinder(h = choke_depth + 6, d = wg_inner_dia + (wg_wall * 2), center = true);
            }

        // 3. Shielded RF + Hex-Logic Transceiver Housing (Faraday Cage)
        translate([0, 0, 52]) {
            difference() {
                cube([95, 95, 42], center = true);
                cube([87, 87, 34], center = true); // Hollow cavity for Rogers/FR4 PCB
            }
            // RT Phase-Change Thermal Heatsink Fins on top
            for (x = [-36 : 12 : 36]) {
                translate([x, 0, 26])
                    cube([4, 88, 12], center = true);
            }
        }
    }
}

module feed_struts() {
    r_mount = (dish_diameter / 2) * 0.88;
    z_mount = (r_mount * r_mount) / (4 * focal_length);

    for (ang =) {
        rotate([0, 0, ang]) {
            hull() {
                translate([r_mount, 0, z_mount])
                    sphere(d = 9);
                translate([0, 0, focal_length + 35])
                    sphere(d = 9);
            }
        }
    }
}

module dielectric_radome() {
    r_max = dish_diameter / 2;
    z_rim = (r_max * r_max) / (4 * focal_length) + rim_lip_height;
    
    // Low-loss PTFE/Polycarbonate protective dome
    %translate([0, 0, z_rim])
        difference() {
            sphere(r = r_max);
            sphere(r = r_max - 2.5);
            translate([0, 0, -r_max])
                cube([r_max * 2.2, r_max * 2.2, r_max * 2], center = true);
        }
}

module elevation_tower_bracket() {
    // Rear backing plate attached to dish vertex
    translate([0, 0, -25])
        cube([140, 140, 15], center = true);

    // Mast clamp collar
    translate([0, 0, -85])
        difference() {
            union() {
                cube([90, 90, 90], center = true);
                rotate([90, 0, 0])
                    cylinder(h = 110, d = mast_diameter + 24, center = true);
            }
            rotate([90, 0, 0])
                cylinder(h = 120, d = mast_diameter, center = true);
        }
}

// --- Full Tilted Radar Assembly ---
rotate([elevation_angle, 0, 0]) {
    color("Silver") parabolic_reflector();
    color("Gold") scalar_feedhorn_and_hex_box();
    color("DimGray") feed_struts();
    dielectric_radome();
}
color("SteelBlue") elevation_tower_bracket();
