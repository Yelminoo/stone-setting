"""
Simple Stone Setting Generator - Direct port from interactive_editor.html
Replicates EXACTLY what the JavaScript does, nothing more.
"""

import trimesh
import numpy as np


def create_ring(ring_size, ring_thickness):
    """Create a simple torus ring"""
    ring = trimesh.creation.torus(
        major_radius=ring_size,
        minor_radius=ring_thickness,
        major_sections=64,
        minor_sections=32
    )
    return ring


def create_princess_cut_diamond(size, depth):
    """Create princess cut diamond (square)"""
    vertices = []
    faces = []
    
    # Proportions
    crown_height = depth * 0.35
    pavilion_depth = depth * 0.65
    
    table_size = size * 0.7
    half_size = size / 2
    half_table = table_size / 2
    
    # Y positions
    table_y = crown_height
    girdle_y = 0
    culet_y = -pavilion_depth
    
    # Table vertices (square)
    table_vertices = [
        [half_table, table_y, half_table],
        [-half_table, table_y, half_table],
        [-half_table, table_y, -half_table],
        [half_table, table_y, -half_table]
    ]
    vertices.extend(table_vertices)
    
    # Girdle vertices (square)
    girdle_vertices = [
        [half_size, girdle_y, half_size],
        [-half_size, girdle_y, half_size],
        [-half_size, girdle_y, -half_size],
        [half_size, girdle_y, -half_size]
    ]
    vertices.extend(girdle_vertices)
    
    # Culet point
    vertices.append([0, culet_y, 0])
    culet_idx = 8
    
    # Table face
    faces.append([0, 1, 2])
    faces.append([0, 2, 3])
    
    # Crown facets
    for i in range(4):
        next_i = (i + 1) % 4
        faces.append([i, i + 4, next_i])
        faces.append([next_i, i + 4, next_i + 4])
    
    # Pavilion facets
    for i in range(4):
        next_i = (i + 1) % 4
        faces.append([i + 4, culet_idx, next_i + 4])
    
    return trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))


def create_radiant_cut_diamond(size, depth):
    """Create radiant cut diamond (square with beveled corners)"""
    vertices = []
    faces = []
    
    # Proportions
    crown_height = depth * 0.35
    pavilion_depth = depth * 0.65
    
    table_size = size * 0.65
    half_size = size / 2
    half_table = table_size / 2
    corner_cut = size * 0.15  # Bevel amount
    
    # Y positions
    table_y = crown_height
    girdle_y = 0
    culet_y = -pavilion_depth
    
    # Table vertices (octagon - beveled square)
    table_vertices = [
        [half_table - corner_cut, table_y, half_table],
        [-(half_table - corner_cut), table_y, half_table],
        [-half_table, table_y, half_table - corner_cut],
        [-half_table, table_y, -(half_table - corner_cut)],
        [-(half_table - corner_cut), table_y, -half_table],
        [half_table - corner_cut, table_y, -half_table],
        [half_table, table_y, -(half_table - corner_cut)],
        [half_table, table_y, half_table - corner_cut]
    ]
    vertices.extend(table_vertices)
    
    # Girdle vertices (octagon)
    girdle_vertices = [
        [half_size - corner_cut, girdle_y, half_size],
        [-(half_size - corner_cut), girdle_y, half_size],
        [-half_size, girdle_y, half_size - corner_cut],
        [-half_size, girdle_y, -(half_size - corner_cut)],
        [-(half_size - corner_cut), girdle_y, -half_size],
        [half_size - corner_cut, girdle_y, -half_size],
        [half_size, girdle_y, -(half_size - corner_cut)],
        [half_size, girdle_y, half_size - corner_cut]
    ]
    vertices.extend(girdle_vertices)
    
    # Culet point
    vertices.append([0, culet_y, 0])
    culet_idx = 16
    
    # Table faces (fan from center)
    for i in range(8):
        next_i = (i + 1) % 8
        if i == 0:
            vertices.insert(0, [0, table_y, 0])
            culet_idx = 17
        faces.append([0, i + 1, next_i + 1])
    
    # Crown facets
    for i in range(8):
        next_i = (i + 1) % 8
        faces.append([i + 1, i + 9, next_i + 1])
        faces.append([next_i + 1, i + 9, next_i + 9])
    
    # Pavilion facets
    for i in range(8):
        next_i = (i + 1) % 8
        faces.append([i + 9, culet_idx, next_i + 9])
    
    return trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))


def create_brilliant_cut_diamond(radius, depth):
    """Create brilliant cut diamond - matching JS exactly"""
    vertices = []
    faces = []
    
    # Proportions
    table_radius = radius * 0.53
    crown_height = depth * 0.35
    pavilion_depth = depth * 0.65
    girdle_radius = radius
    
    # Y positions (table at TOP, culet at BOTTOM)
    table_y = crown_height
    girdle_y = 0
    culet_y = -pavilion_depth
    
    segments = 8  # Large facets
    
    # 1. Table center
    vertices.append([0, table_y, 0])
    table_center_idx = 0
    
    # 2. Table edge
    table_start_idx = 1
    for i in range(segments):
        angle = (i / segments) * 2 * np.pi
        vertices.append([
            table_radius * np.cos(angle),
            table_y,
            table_radius * np.sin(angle)
        ])
    
    # 3. Crown-Girdle edge
    crown_start_idx = 1 + segments
    for i in range(segments):
        angle = (i / segments) * 2 * np.pi
        vertices.append([
            girdle_radius * np.cos(angle) * 0.85,
            table_y * 0.5,
            girdle_radius * np.sin(angle) * 0.85
        ])
    
    # 4. Girdle
    girdle_start_idx = 1 + segments * 2
    for i in range(segments):
        angle = (i / segments) * 2 * np.pi
        vertices.append([
            girdle_radius * np.cos(angle),
            girdle_y,
            girdle_radius * np.sin(angle)
        ])
    
    # 5. Pavilion
    pavilion_start_idx = 1 + segments * 3
    for i in range(segments):
        angle = (i / segments) * 2 * np.pi
        vertices.append([
            girdle_radius * np.cos(angle) * 0.5,
            culet_y * 0.5,
            girdle_radius * np.sin(angle) * 0.5
        ])
    
    # 6. Culet
    vertices.append([0, culet_y, 0])
    culet_idx = len(vertices) - 1
    
    # Create faces (matching JS exactly)
    # Table facets
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append([table_center_idx, table_start_idx + i, table_start_idx + next_i])
    
    # Crown facets
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append([table_start_idx + i, crown_start_idx + i, table_start_idx + next_i])
        faces.append([table_start_idx + next_i, crown_start_idx + i, crown_start_idx + next_i])
    
    # Crown to girdle
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append([crown_start_idx + i, girdle_start_idx + i, crown_start_idx + next_i])
        faces.append([crown_start_idx + next_i, girdle_start_idx + i, girdle_start_idx + next_i])
    
    # Pavilion facets
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append([girdle_start_idx + i, pavilion_start_idx + i, girdle_start_idx + next_i])
        faces.append([girdle_start_idx + next_i, pavilion_start_idx + i, pavilion_start_idx + next_i])
    
    # To culet
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append([pavilion_start_idx + i, culet_idx, pavilion_start_idx + next_i])
    
    return trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))


def create_prongs(config, centerpiece_y, stone_y, actual_prong_spread_radius):
    """Create prongs - matching JS exactly"""
    
    prong_thickness_base = config.get('prongThicknessBase', 0.4)
    prong_thickness_top = config.get('prongThicknessTop', 0.3)
    prong_count = config.get('prongCount', 4)
    
    # Claw dimensions
    claw_width_base = prong_thickness_base * 0.5
    claw_depth_base = prong_thickness_base
    claw_width_top = prong_thickness_top * 0.5
    claw_depth_top = prong_thickness_top
    
    centerpiece_point = np.array([0, centerpiece_y, 0])
    
    all_prongs = []
    
    for i in range(prong_count):
        angle = (i / prong_count) * 2 * np.pi
        
        # End point at stone girdle (stone center y position)
        # Prongs should reach the stone's girdle which is at the stone center height
        end_x = actual_prong_spread_radius * np.cos(angle)
        end_z = actual_prong_spread_radius * np.sin(angle)
        # Extend prongs slightly above stone center to ensure contact
        end_point = np.array([end_x, stone_y + 0.5, end_z])  # +0.5mm above center
        
        # Create prong
        prong = create_single_prong(
            centerpiece_point,
            end_point,
            claw_width_base,
            claw_depth_base,
            claw_width_top,
            claw_depth_top,
            angle
        )
        all_prongs.append(prong)
    
    # Merge all prongs
    merged = trimesh.util.concatenate(all_prongs)
    return merged


def create_single_prong(start, end, width_base, depth_base, width_top, depth_top, angle, segments=30):
    """Create single tapered prong - SIMPLE version matching JS ExtrudeGeometry"""
    
    vertices = []
    faces = []
    
    # Direction and length
    direction = end - start
    length = np.linalg.norm(direction)
    
    # Coordinate system
    radial_dir = np.array([np.cos(angle), 0, np.sin(angle)])
    tangent_dir = np.array([-np.sin(angle), 0, np.cos(angle)])
    
    # Create cross-sections along prong
    for seg in range(segments + 1):
        t = seg / segments  # 0 to 1
        
        # Position along prong
        pos = start + direction * t
        
        # Tapering (matching JS: scaleX = 1 + (ratio - 1) * t)
        scale_w = 1 + (width_top / width_base - 1) * t
        scale_d = 1 + (depth_top / depth_base - 1) * t
        
        half_w = (width_base / 2) * scale_w
        half_d = (depth_base / 2) * scale_d
        
        # 4 corners: tangent (X), radial (Y)
        corners = [
            [-half_w, -half_d],
            [half_w, -half_d],
            [half_w, half_d],
            [-half_w, half_d]
        ]
        
        # To world space
        for c in corners:
            world_pos = pos + tangent_dir * c[0] + radial_dir * c[1]
            vertices.append(world_pos)
    
    # Faces between segments
    for seg in range(segments):
        b = seg * 4
        t = (seg + 1) * 4
        
        for i in range(4):
            n = (i + 1) % 4
            faces.append([b + i, b + n, t + i])
            faces.append([t + i, b + n, t + n])
    
    # Caps
    faces.append([0, 1, 2])
    faces.append([0, 2, 3])
    
    top = segments * 4
    faces.append([top, top + 2, top + 1])
    faces.append([top, top + 3, top + 2])
    
    return trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))


def create_stone_setting(
    stone_size=6.0,
    stone_depth=7.2,
    prong_count=4,
    prong_thickness_base=0.4,
    prong_thickness_top=0.3,
    setting_height=3.0,
    ring_size=8.5,
    ring_thickness=1.0,
    stone_shape='round'
):
    """
    Create stone setting - matching interactive_editor.html EXACTLY
    
    All measurements in mm.
    """
    
    # Config object (like JS)
    config = {
        'ringSize': ring_size,
        'ringThickness': ring_thickness,
        'stoneSize': stone_size,
        'stoneDepth': stone_depth,
        'prongCount': prong_count,
        'prongThicknessBase': prong_thickness_base,
        'prongThicknessTop': prong_thickness_top,
        'stoneHeightAboveRing': setting_height,
        'stoneShape': stone_shape
    }
    
    # 1. Create Ring (JS: TorusGeometry)
    ring_mesh = create_ring(ring_size, ring_thickness)
    
    # 2. Calculate positions (matching JS exactly)
    centerpiece_distance = ring_size
    centerpiece_y = centerpiece_distance
    
    stone_height_above_ring = setting_height
    stone_y = ring_size + ring_thickness + stone_height_above_ring
    
    # 3. Calculate stone size and prong positioning
    prong_spread_radius = stone_size / 2
    
    # Adjust prong spread to account for prong thickness (push prongs outward)
    prong_thickness_base = config.get('prongThicknessBase', 0.4)
    prong_spread_radius += (prong_thickness_base / 2)  # Add half base thickness
    
    stone_radius = prong_spread_radius - 0.25  # Minimal clearance (was 0.4)
    stone_depth_val = stone_depth
    
    # 4. Create Stone based on shape
    actual_prong_spread_radius = prong_spread_radius
    
    if stone_shape == 'round':
        stone_mesh = create_brilliant_cut_diamond(stone_radius, stone_depth_val)
    elif stone_shape == 'princess':
        # Princess cut uses diagonal radius
        stone_size_actual = stone_size - 0.5  # Very small clearance for princess
        stone_mesh = create_princess_cut_diamond(stone_size_actual, stone_depth_val)
        # Rotate stone so corners align with prongs
        # For 4 prongs: rotate by 45 degrees so corners point to prongs
        prong_count = config.get('prongCount', 4)
        rotation_angle = (np.pi / prong_count)  # Half prong angle offset
        rotation_matrix = trimesh.transformations.rotation_matrix(rotation_angle, [0, 1, 0])
        stone_mesh.apply_transform(rotation_matrix)
        # Adjust prong spread for square corners (diagonal + minimal clearance + prong thickness)
        actual_prong_spread_radius = (stone_size / 2) * np.sqrt(2) + 0.1 + (prong_thickness_base / 2)
    elif stone_shape == 'radiant':
        # Radiant cut (beveled square) - needs less clearance since corners are cut
        stone_size_actual = stone_size - 0.05  # Minimal clearance for radiant
        stone_mesh = create_radiant_cut_diamond(stone_size_actual, stone_depth_val)
        # Rotate stone so beveled corners align with prongs
        prong_count = config.get('prongCount', 4)
        rotation_angle = (np.pi / prong_count)  # Half prong angle offset
        rotation_matrix = trimesh.transformations.rotation_matrix(rotation_angle, [0, 1, 0])
        stone_mesh.apply_transform(rotation_matrix)
        # Radiant has beveled corners, so use less than full diagonal
        actual_prong_spread_radius = (stone_size / 2) * 1.3 + (prong_thickness_base / 2)  # Less than sqrt(2)
    else:
        # Default to round
        stone_mesh = create_brilliant_cut_diamond(stone_radius, stone_depth_val)
    
    # Position stone
    stone_mesh.apply_translation([0, stone_y, 0])
    
    # 5. Create Prongs
    prongs_mesh = create_prongs(config, centerpiece_y, stone_y, actual_prong_spread_radius)
    
    # 6. Export as separate objects with metadata for material assignment
    import trimesh.exchange.gltf
    
    # Add visual properties as metadata
    ring_mesh.visual = trimesh.visual.ColorVisuals()
    ring_mesh.metadata['name'] = 'ring'
    
    stone_mesh.visual = trimesh.visual.ColorVisuals()
    stone_mesh.metadata['name'] = 'stone'
    
    prongs_mesh.visual = trimesh.visual.ColorVisuals()
    prongs_mesh.metadata['name'] = 'prongs'
    
    # Create scene with separate meshes
    scene = trimesh.Scene()
    scene.add_geometry(ring_mesh, node_name='ring', geom_name='ring')
    scene.add_geometry(stone_mesh, node_name='stone', geom_name='stone')
    scene.add_geometry(prongs_mesh, node_name='prongs', geom_name='prongs')
    
    return scene


# Test
if __name__ == "__main__":
    print("Creating stone setting (matching interactive_editor.html)...")
    
    mesh = create_stone_setting(
        stone_size=6.0,
        stone_depth=7.2,
        prong_count=4,
        prong_thickness_base=0.4,
        prong_thickness_top=0.3,
        setting_height=3.0,
        ring_size=8.5,
        ring_thickness=1.0
    )
    
    # Export
    scene.export('output/stone_setting_simple.glb')
    print(f"✅ Created: output/stone_setting_simple.glb")
    print(f"   Geometries: {len(scene.geometry)}")
