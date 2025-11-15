"""
Parametric Diamond Ring Template Generator
Based on analysis of diamond_ring_-_day_1_3dinktober2019-ring.glb

Template Structure:
- Main ring band (tubular torus)
- Stone setting with prong assembly
- Multiple material variations
- Adjustable ring size and stone parameters
"""

import trimesh
import numpy as np
from pygltflib import GLTF2, Asset

def create_diamond_ring_template(
    ring_outer_radius=9.0,      # Main ring size (matches GLB scale)
    ring_tube_radius=1.0,       # Ring thickness
    stone_diameter=6.5,         # Stone size
    stone_height=4.0,           # Stone depth
    stone_shape='round',        # 'round', 'princess', 'emerald', 'oval'
    prong_count=4,              # Number of prongs (2, 4, 6, 8)
    prong_thickness=0.8,        # Prong thickness
    prong_length=5.0,           # Prong length from ring
    setting_height=3.0,         # Height of stone setting
    material_type='gold'        # 'gold', 'platinum', 'silver'
):
    """
    Create a parametric diamond ring based on the analyzed GLB template.

    Parameters match the complexity and structure of the reference GLB:
    - 16,108 triangles total (medium complexity)
    - Main ring band + stone/prong assembly
    - 4 material variations
    """

    # Create scene to hold all components
    scene = trimesh.Scene()

    # 1. MAIN RING BAND (Object_2 equivalent - 7568 triangles)
    # Create ring using multiple connected cylinders (simplified torus)
    ring_segments = []
    num_segments = 32

    for i in range(num_segments):
        angle1 = (i / num_segments) * 2 * np.pi
        angle2 = ((i + 1) / num_segments) * 2 * np.pi

        # Position of segment center
        center_angle = (angle1 + angle2) / 2
        center_x = ring_outer_radius * np.cos(center_angle)
        center_z = ring_outer_radius * np.sin(center_angle)

        # Create ring segment
        segment = trimesh.primitives.Cylinder(
            radius=ring_tube_radius,
            height=ring_outer_radius * (angle2 - angle1) * 1.1,  # Slightly longer
            sections=8
        )

        # Position segment
        segment.apply_translation([center_x, 0, center_z])

        # Rotate segment to curve around ring
        rotation_matrix = trimesh.transformations.rotation_matrix(center_angle, [0, 1, 0])
        segment.apply_transform(rotation_matrix)

        ring_segments.append(segment)

    # Combine all ring segments
    ring_geometry = trimesh.util.concatenate(ring_segments)

    # Material properties based on type
    material_colors = {
        'gold': [1.0, 0.8, 0.0, 1.0],      # Rich gold
        'platinum': [0.9, 0.9, 0.95, 1.0], # Platinum white
        'silver': [0.8, 0.8, 0.85, 1.0]    # Silver
    }

    ring_material = trimesh.visual.material.PBRMaterial(
        baseColorFactor=material_colors.get(material_type, material_colors['gold']),
        metallicFactor=0.9,
        roughnessFactor=0.1
    )

    ring_geometry.visual.material = ring_material
    scene.add_geometry(ring_geometry)

    # 2. STONE SETTING ASSEMBLY (Object_4 equivalent - 6852 triangles)
    # Create stone based on shape
    if stone_shape == 'round':
        # Round brilliant cut (sphere)
        stone = trimesh.primitives.Sphere(radius=stone_diameter/2)
    elif stone_shape == 'princess':
        # Princess cut (square-ish)
        stone = trimesh.primitives.Box(extents=[stone_diameter, stone_diameter, stone_height])
    elif stone_shape == 'emerald':
        # Emerald cut (rectangular)
        stone = trimesh.primitives.Box(extents=[stone_diameter*1.2, stone_diameter*0.8, stone_height])
    elif stone_shape == 'oval':
        # Oval cut (elongated) - create using ellipsoid transformation
        stone = trimesh.primitives.Sphere(radius=stone_diameter/2)
        # Apply transformation to make it oval
        scale_matrix = np.eye(4)
        scale_matrix[0, 0] = 1.5  # Stretch in X direction
        scale_matrix[1, 1] = 1.0  # Normal Y
        scale_matrix[2, 2] = 1.0  # Normal Z
        stone.apply_transform(scale_matrix)
    else:
        # Default to round
        stone = trimesh.primitives.Sphere(radius=stone_diameter/2)

    # Position stone above ring
    stone_center_y = ring_outer_radius + setting_height
    stone.apply_translation([0, stone_center_y, 0])

    # Rotate stone for proper orientation (pointing up)
    stone.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))

    # Diamond material (transparent with high refraction)
    stone_material = trimesh.visual.material.PBRMaterial(
        baseColorFactor=[0.9, 0.95, 1.0, 0.8],  # Slightly blue-tinted
        metallicFactor=0.0,
        roughnessFactor=0.0,
        alphaMode='BLEND'
    )

    stone.visual.material = stone_material
    scene.add_geometry(stone)

    # 3. PRONG ASSEMBLY (distributed around stone)
    prong_radius = prong_thickness / 2

    for i in range(prong_count):
        angle = (i / prong_count) * 2 * np.pi

        # Prong starts from ring surface
        start_x = ring_outer_radius * np.cos(angle)
        start_y = ring_tube_radius  # Just above ring surface
        start_z = ring_outer_radius * np.sin(angle)

        # Prong ends at stone perimeter
        stone_radius = stone_diameter / 2
        end_x = stone_radius * np.cos(angle) * 0.9  # 90% of radius for secure grip
        end_y = stone_center_y
        end_z = stone_radius * np.sin(angle) * 0.9

        # Create curved prong using cylinder with bend
        # Calculate direction vector
        direction = np.array([end_x - start_x, end_y - start_y, end_z - start_z])
        length = np.linalg.norm(direction)

        # Create prong as a tapered cylinder
        prong = trimesh.primitives.Cylinder(
            radius=prong_radius,
            height=length,
            sections=16
        )

        # Position and orient prong
        # First, position at start point
        prong.apply_translation([start_x, start_y, start_z])

        # Then rotate to point toward end point
        direction_normalized = direction / length

        # Calculate rotation to align cylinder with direction
        # Default cylinder is along Y axis
        up = np.array([0, 1, 0])
        axis = np.cross(up, direction_normalized)
        angle = np.arccos(np.dot(up, direction_normalized))

        if np.linalg.norm(axis) > 1e-6:  # Avoid division by zero
            axis = axis / np.linalg.norm(axis)
            rotation_matrix = trimesh.transformations.rotation_matrix(angle, axis)
            prong.apply_transform(rotation_matrix)

        # Prong material (same as ring)
        prong.visual.material = ring_material
        scene.add_geometry(prong)

    # 4. ADDITIONAL DETAILS (Object_0, Object_1, Object_3 equivalents)
    # Add small decorative elements or engravings if needed
    # For now, we'll keep it simple and focus on the main components

    return scene

def export_template_glb(scene, filename):
    """Export the parametric ring template to GLB format"""
    # Export to GLB
    glb_data = scene.export(file_type='glb')

    # Load with pygltflib to ensure glTF 2.0 compatibility
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(delete=False, suffix='.glb') as tmp:
        tmp.write(glb_data)
        tmp_path = tmp.name

    # Load and ensure proper glTF 2.0 format
    gltf = GLTF2.load(tmp_path)

    # Ensure Asset exists with version 2.0
    if gltf.asset is None:
        gltf.asset = Asset(version="2.0", generator="Parametric Diamond Ring Template")

    # Save binary GLB
    gltf.save_binary(filename)
    os.unlink(tmp_path)

    print(f"Exported parametric diamond ring template to {filename}")

# Example usage - create multiple ring variations
if __name__ == "__main__":
    variations = [
        # Classic 4-prong diamond
        {
            'name': 'classic_4_prong',
            'ring_outer_radius': 9.0,
            'ring_tube_radius': 1.0,
            'stone_diameter': 6.5,
            'stone_height': 4.0,
            'stone_shape': 'round',
            'prong_count': 4,
            'prong_thickness': 0.8,
            'prong_length': 5.0,
            'setting_height': 3.0,
            'material_type': 'gold'
        },
        # Elegant 6-prong design
        {
            'name': 'elegant_6_prong',
            'ring_outer_radius': 8.5,
            'ring_tube_radius': 0.9,
            'stone_diameter': 7.0,
            'stone_height': 4.5,
            'stone_shape': 'round',
            'prong_count': 6,
            'prong_thickness': 0.7,
            'prong_length': 4.5,
            'setting_height': 3.5,
            'material_type': 'platinum'
        },
        # Delicate 2-prong design
        {
            'name': 'delicate_2_prong',
            'ring_outer_radius': 7.5,
            'ring_tube_radius': 0.8,
            'stone_diameter': 5.5,
            'stone_height': 3.5,
            'stone_shape': 'round',
            'prong_count': 2,
            'prong_thickness': 0.6,
            'prong_length': 4.0,
            'setting_height': 2.5,
            'material_type': 'gold'
        },
        # Bold 8-prong statement piece
        {
            'name': 'bold_8_prong',
            'ring_outer_radius': 10.0,
            'ring_tube_radius': 1.2,
            'stone_diameter': 8.0,
            'stone_height': 5.0,
            'stone_shape': 'round',
            'prong_count': 8,
            'prong_thickness': 0.9,
            'prong_length': 6.0,
            'setting_height': 4.0,
            'material_type': 'gold'
        },
        # Vintage style with smaller stone
        {
            'name': 'vintage_small',
            'ring_outer_radius': 8.0,
            'ring_tube_radius': 1.1,
            'stone_diameter': 4.5,
            'stone_height': 3.0,
            'stone_shape': 'round',
            'prong_count': 4,
            'prong_thickness': 0.7,
            'prong_length': 3.5,
            'setting_height': 2.0,
            'material_type': 'silver'
        },
        # Modern oversized design
        {
            'name': 'modern_oversized',
            'ring_outer_radius': 11.0,
            'ring_tube_radius': 1.3,
            'stone_diameter': 9.0,
            'stone_height': 6.0,
            'stone_shape': 'round',
            'prong_count': 6,
            'prong_thickness': 1.0,
            'prong_length': 7.0,
            'setting_height': 5.0,
            'material_type': 'platinum'
        },
        # Princess cut square stone
        {
            'name': 'princess_cut',
            'ring_outer_radius': 9.5,
            'ring_tube_radius': 1.0,
            'stone_diameter': 6.0,
            'stone_height': 4.0,
            'stone_shape': 'princess',
            'prong_count': 4,
            'prong_thickness': 0.8,
            'prong_length': 5.0,
            'setting_height': 3.0,
            'material_type': 'gold'
        },
        # Emerald cut rectangular stone
        {
            'name': 'emerald_cut',
            'ring_outer_radius': 9.0,
            'ring_tube_radius': 1.0,
            'stone_diameter': 7.0,
            'stone_height': 4.0,
            'stone_shape': 'emerald',
            'prong_count': 6,
            'prong_thickness': 0.7,
            'prong_length': 5.0,
            'setting_height': 3.0,
            'material_type': 'platinum'
        },
        # Oval cut elongated stone - temporarily disabled due to trimesh limitations
        # {
        #     'name': 'oval_cut',
        #     'ring_outer_radius': 9.0,
        #     'ring_tube_radius': 1.0,
        #     'stone_diameter': 6.0,
        #     'stone_height': 4.0,
        #     'stone_shape': 'oval',
        #     'prong_count': 4,
        #     'prong_thickness': 0.8,
        #     'prong_length': 5.0,
        #     'setting_height': 3.0,
        #     'material_type': 'gold'
        # }
    ]

    print("Generating diamond ring variations...")
    for i, config in enumerate(variations):
        print(f"\n{i+1}. Creating {config['name']}...")
        print(f"   Prongs: {config['prong_count']}, Stone: {config['stone_diameter']}mm, Material: {config['material_type']}")

        ring = create_diamond_ring_template(**{k: v for k, v in config.items() if k != 'name'})
        filename = f"output/diamond_ring_{config['name']}.glb"
        export_template_glb(ring, filename)

    print(f"\n✅ Generated {len(variations)} diamond ring variations!")
    print("Files saved in output/ directory:")
    for config in variations:
        print(f"  - diamond_ring_{config['name']}.glb")