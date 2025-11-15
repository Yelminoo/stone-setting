"""
Parametric Stone Setting Generator
Creates designer and production-ready GLB files for jewelry manufacturing.

Features:
- Multiple stone shapes (round, princess, radiant)
- Customizable prong configurations (2, 4, 6, 8 prongs)
- Tapered prongs with collision detection
- Watertight/manifold geometry for production
- Designer version with stone visualization
- Production version with extended prongs for manufacturing
"""

import trimesh
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Optional


def create_brilliant_cut_diamond(radius: float, depth: float, segments: int = 8) -> trimesh.Trimesh:
    """
    Create a brilliant cut round diamond with proper faceting.
    
    Args:
        radius: Diamond radius at girdle (mm)
        depth: Total diamond depth (mm)
        segments: Number of segments for faceting (default: 8 for visible facets)
    
    Returns:
        trimesh.Trimesh: Diamond geometry
    """
    vertices = []
    faces = []
    
    # Brilliant cut proportions
    table_radius = radius * 0.53  # Table is ~53% of diameter
    crown_height = depth * 0.35   # Crown is ~35% of total depth
    pavilion_depth = depth * 0.65 # Pavilion is ~65% of total depth
    girdle_radius = radius
    
    # Key Y positions (table at TOP, culet at BOTTOM)
    table_y = crown_height
    girdle_y = 0
    culet_y = -pavilion_depth
    
    # 1. Table center
    vertices.append([0, table_y, 0])
    table_center_idx = 0
    
    # 2. Table edge (octagonal)
    table_start_idx = len(vertices)
    for i in range(segments):
        angle = (i / segments) * 2 * np.pi
        vertices.append([
            table_radius * np.cos(angle),
            table_y,
            table_radius * np.sin(angle)
        ])
    
    # 3. Crown-Girdle edge
    crown_start_idx = len(vertices)
    for i in range(segments):
        angle = (i / segments) * 2 * np.pi
        vertices.append([
            girdle_radius * np.cos(angle) * 0.85,
            table_y * 0.5,
            girdle_radius * np.sin(angle) * 0.85
        ])
    
    # 4. Girdle (widest part)
    girdle_start_idx = len(vertices)
    for i in range(segments):
        angle = (i / segments) * 2 * np.pi
        vertices.append([
            girdle_radius * np.cos(angle),
            girdle_y,
            girdle_radius * np.sin(angle)
        ])
    
    # 5. Pavilion facets
    pavilion_start_idx = len(vertices)
    for i in range(segments):
        angle = (i / segments) * 2 * np.pi
        vertices.append([
            girdle_radius * np.cos(angle) * 0.5,
            culet_y * 0.5,
            girdle_radius * np.sin(angle) * 0.5
        ])
    
    # 6. Culet (bottom point)
    vertices.append([0, culet_y, 0])
    culet_idx = len(vertices) - 1
    
    # Create faces
    # Table facets
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append([table_center_idx, table_start_idx + i, table_start_idx + next_i])
    
    # Crown facets (table edge to crown-girdle)
    for i in range(segments):
        next_i = (i + 1) % segments
        crown_idx = i
        crown_next = next_i
        
        faces.append([table_start_idx + i, crown_start_idx + crown_idx, table_start_idx + next_i])
        faces.append([table_start_idx + next_i, crown_start_idx + crown_idx, crown_start_idx + crown_next])
    
    # Star and bezel facets (crown to girdle)
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append([crown_start_idx + i, girdle_start_idx + i, crown_start_idx + next_i])
        faces.append([crown_start_idx + next_i, girdle_start_idx + i, girdle_start_idx + next_i])
    
    # Pavilion facets (girdle to pavilion)
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append([girdle_start_idx + i, pavilion_start_idx + i, girdle_start_idx + next_i])
        faces.append([girdle_start_idx + next_i, pavilion_start_idx + i, pavilion_start_idx + next_i])
    
    # Pavilion to culet (bottom point)
    for i in range(segments):
        next_i = (i + 1) % segments
        faces.append([pavilion_start_idx + i, culet_idx, pavilion_start_idx + next_i])
    
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
    return mesh


def create_princess_cut_diamond(size: float, depth: float) -> trimesh.Trimesh:
    """
    Create a princess cut (square) diamond with pointed pavilion.
    
    Args:
        size: Square side length (mm)
        depth: Total diamond depth (mm)
    
    Returns:
        trimesh.Trimesh: Diamond geometry
    """
    vertices = []
    faces = []
    
    # Princess cut proportions
    table_size = size * 0.65
    crown_height = depth * 0.30
    pavilion_depth = depth * 0.70
    
    # Key Y positions (table at TOP, culet at BOTTOM)
    table_y = crown_height
    girdle_y = 0
    culet_y = -pavilion_depth
    
    # 1. Table center
    vertices.append([0, table_y, 0])
    table_center_idx = 0
    
    # 2. Table corners (square)
    half_table = table_size / 2
    table_start_idx = len(vertices)
    corners = [
        [half_table, table_y, half_table],
        [-half_table, table_y, half_table],
        [-half_table, table_y, -half_table],
        [half_table, table_y, -half_table]
    ]
    vertices.extend(corners)
    
    # 3. Girdle corners (square)
    half_girdle = size / 2
    girdle_start_idx = len(vertices)
    corners = [
        [half_girdle, girdle_y, half_girdle],
        [-half_girdle, girdle_y, half_girdle],
        [-half_girdle, girdle_y, -half_girdle],
        [half_girdle, girdle_y, -half_girdle]
    ]
    vertices.extend(corners)
    
    # 4. Pavilion points
    half_pavilion = size * 0.3
    pavilion_start_idx = len(vertices)
    corners = [
        [half_pavilion, culet_y * 0.5, half_pavilion],
        [-half_pavilion, culet_y * 0.5, half_pavilion],
        [-half_pavilion, culet_y * 0.5, -half_pavilion],
        [half_pavilion, culet_y * 0.5, -half_pavilion]
    ]
    vertices.extend(corners)
    
    # 5. Culet (point at bottom)
    vertices.append([0, culet_y, 0])
    culet_idx = len(vertices) - 1
    
    # Create faces - Table
    for i in range(4):
        next_i = (i + 1) % 4
        faces.append([table_center_idx, table_start_idx + i, table_start_idx + next_i])
    
    # Crown facets (table to girdle)
    for i in range(4):
        next_i = (i + 1) % 4
        faces.append([table_start_idx + i, girdle_start_idx + i, table_start_idx + next_i])
        faces.append([table_start_idx + next_i, girdle_start_idx + i, girdle_start_idx + next_i])
    
    # Pavilion facets (girdle to pavilion points)
    for i in range(4):
        next_i = (i + 1) % 4
        faces.append([girdle_start_idx + i, pavilion_start_idx + i, girdle_start_idx + next_i])
        faces.append([girdle_start_idx + next_i, pavilion_start_idx + i, pavilion_start_idx + next_i])
    
    # Pavilion to culet
    for i in range(4):
        next_i = (i + 1) % 4
        faces.append([pavilion_start_idx + i, culet_idx, pavilion_start_idx + next_i])
    
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
    return mesh


def create_radiant_cut_diamond(length: float, width: float, depth: float) -> trimesh.Trimesh:
    """
    Create a radiant cut (rectangular with cut corners) diamond.
    
    Args:
        length: Diamond length (mm)
        width: Diamond width (mm)
        depth: Total diamond depth (mm)
    
    Returns:
        trimesh.Trimesh: Diamond geometry
    """
    vertices = []
    faces = []
    
    # Radiant cut proportions
    table_length = length * 0.65
    table_width = width * 0.65
    crown_height = depth * 0.32
    pavilion_depth = depth * 0.68
    corner_cut = min(length, width) * 0.15
    
    # Key Y positions (table at TOP, culet at BOTTOM)
    table_y = crown_height
    girdle_y = 0
    culet_y = -pavilion_depth
    
    half_l = length / 2
    half_w = width / 2
    half_tl = table_length / 2
    half_tw = table_width / 2
    
    # 1. Table center
    vertices.append([0, table_y, 0])
    table_center_idx = 0
    
    # 2. Table octagon (8 points - rectangle with cut corners)
    table_start_idx = len(vertices)
    table_points = [
        [half_tl - corner_cut * 0.5, table_y, half_tw],
        [-half_tl + corner_cut * 0.5, table_y, half_tw],
        [-half_tl, table_y, half_tw - corner_cut * 0.5],
        [-half_tl, table_y, -half_tw + corner_cut * 0.5],
        [-half_tl + corner_cut * 0.5, table_y, -half_tw],
        [half_tl - corner_cut * 0.5, table_y, -half_tw],
        [half_tl, table_y, -half_tw + corner_cut * 0.5],
        [half_tl, table_y, half_tw - corner_cut * 0.5]
    ]
    vertices.extend(table_points)
    
    # 3. Girdle octagon
    girdle_start_idx = len(vertices)
    girdle_points = [
        [half_l - corner_cut, girdle_y, half_w],
        [-half_l + corner_cut, girdle_y, half_w],
        [-half_l, girdle_y, half_w - corner_cut],
        [-half_l, girdle_y, -half_w + corner_cut],
        [-half_l + corner_cut, girdle_y, -half_w],
        [half_l - corner_cut, girdle_y, -half_w],
        [half_l, girdle_y, -half_w + corner_cut],
        [half_l, girdle_y, half_w - corner_cut]
    ]
    vertices.extend(girdle_points)
    
    # 4. Culet
    vertices.append([0, culet_y, 0])
    culet_idx = len(vertices) - 1
    
    # Create faces - Table
    for i in range(8):
        next_i = (i + 1) % 8
        faces.append([table_center_idx, table_start_idx + i, table_start_idx + next_i])
    
    # Crown facets
    for i in range(8):
        next_i = (i + 1) % 8
        faces.append([table_start_idx + i, girdle_start_idx + i, table_start_idx + next_i])
        faces.append([table_start_idx + next_i, girdle_start_idx + i, girdle_start_idx + next_i])
    
    # Pavilion facets
    for i in range(8):
        next_i = (i + 1) % 8
        faces.append([girdle_start_idx + i, culet_idx, girdle_start_idx + next_i])
    
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
    return mesh


def create_tapered_prong(
    start_point: np.ndarray,
    end_point: np.ndarray,
    base_width: float,
    base_depth: float,
    top_width: float,
    top_depth: float,
    angle: float,
    segments: int = 30
) -> trimesh.Trimesh:
    """
    Create a single tapered prong with claw-like orientation.
    Simplified version that matches JavaScript ExtrudeGeometry behavior.
    
    Args:
        start_point: Prong start position (base at centerpiece)
        end_point: Prong end position (tip near stone)
        base_width: Width at base (narrow edge, tangential) (mm)
        base_depth: Depth at base (wide surface, radial) (mm)
        top_width: Width at top (narrow edge) (mm)
        top_depth: Depth at top (wide surface) (mm)
        angle: Angular position around ring (radians)
        segments: Number of segments along prong length
    
    Returns:
        trimesh.Trimesh: Prong geometry
    """
    vertices = []
    faces = []
    
    # Calculate prong direction and length
    direction = end_point - start_point
    prong_length = np.linalg.norm(direction)
    direction_normalized = direction / prong_length
    
    # Radial direction (points from center toward stone at this angle)
    radial_direction = np.array([np.cos(angle), 0, np.sin(angle)])
    
    # Tangent direction (perpendicular to radial, goes around the ring)
    tangent_direction = np.array([-np.sin(angle), 0, np.cos(angle)])
    
    # Create cross-section: simple rectangle with 4 corners
    # We'll create segments along the prong path
    corners_per_section = 4
    
    for seg in range(segments + 1):
        t = seg / segments  # 0 at base, 1 at tip
        
        # Position along prong
        position = start_point + direction * t
        
        # Apply tapering (matching JavaScript: scaleX = 1 + (ratio - 1) * t)
        taper_ratio_width = top_width / base_width
        taper_ratio_depth = top_depth / base_depth
        scale_x = 1 + (taper_ratio_width - 1) * t
        scale_y = 1 + (taper_ratio_depth - 1) * t
        
        # Calculate dimensions at this position
        half_width = (base_width / 2) * scale_x
        half_depth = (base_depth / 2) * scale_y
        
        # 4 corners of rectangle (in local 2D coordinates)
        # X = tangent (width), Y = radial (depth)
        local_corners = [
            [-half_width, -half_depth],
            [half_width, -half_depth],
            [half_width, half_depth],
            [-half_width, half_depth]
        ]
        
        # Transform to world coordinates
        for corner in local_corners:
            # Build world position: base + tangent*x + radial*y
            world_pos = position + tangent_direction * corner[0] + radial_direction * corner[1]
            vertices.append(world_pos)
    
    # Create faces between segments
    for seg in range(segments):
        base_idx = seg * corners_per_section
        top_idx = (seg + 1) * corners_per_section
        
        for i in range(corners_per_section):
            next_i = (i + 1) % corners_per_section
            
            # Two triangles per quad
            faces.append([base_idx + i, base_idx + next_i, top_idx + i])
            faces.append([top_idx + i, base_idx + next_i, top_idx + next_i])
    
    # Cap the ends
    # Base cap
    faces.append([0, 1, 2])
    faces.append([0, 2, 3])
    
    # Top cap
    top_start = segments * corners_per_section
    faces.append([top_start, top_start + 2, top_start + 1])
    faces.append([top_start, top_start + 3, top_start + 2])
    
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
    return mesh


def create_parametric_stone_setting(
    stone_shape: str = 'round',
    stone_length: float = 6.0,
    stone_width: float = 6.0,
    stone_depth: float = 7.2,
    prong_count: int = 4,
    prong_thickness_base: float = 0.4,
    prong_thickness_top: float = 0.3,
    setting_height: float = 3.0,
    ring_size: float = 17.0,
    ring_thickness: float = 2.0,
    production_prong_extension: float = 2.0,
    output_dir: str = 'output'
) -> Tuple[str, str]:
    """
    Create parametric stone setting with designer and production versions.
    
    Args:
        stone_shape: Shape of stone ('round', 'princess', 'radiant')
        stone_length: Stone length in mm
        stone_width: Stone width in mm
        stone_depth: Stone depth in mm
        prong_count: Number of prongs (2, 4, 6, or 8)
        prong_thickness_base: Prong thickness at base in mm
        prong_thickness_top: Prong thickness at top in mm
        setting_height: Distance from ring to stone in mm
        ring_size: Ring inner diameter in mm
        ring_thickness: Ring band thickness in mm
        production_prong_extension: Extra prong length for manufacturing in mm
        output_dir: Output directory for GLB files
    
    Returns:
        Tuple[str, str]: Paths to (designer_file, production_file)
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Calculate ring parameters
    ring_radius = ring_size / 2
    
    # 1. Create Ring Band (torus)
    ring_mesh = trimesh.creation.torus(
        major_radius=ring_radius,
        minor_radius=ring_thickness / 2,
        major_sections=64,
        minor_sections=32
    )
    
    # 2. Calculate positions (matching JavaScript logic exactly)
    centerpiece_distance = ring_radius
    centerpiece_y = centerpiece_distance
    
    # Stone Y position = radius + ring tube thickness + height above ring
    stone_y = ring_radius + ring_thickness + setting_height
    
    # Calculate stone size (max of length/width)
    stone_size = max(stone_length, stone_width)
    
    # Calculate prong spread radius
    prong_spread_radius = stone_size / 2
    
    # Stone radius (at widest girdle point)
    # Add 0.2mm clearance between prongs and stone
    stone_radius = prong_spread_radius - 0.2  # Prongs positioned 0.2mm away from stone edge
    
    # 3. Create Stone
    if stone_shape == 'princess':
        square_size = stone_radius * 2
        stone_mesh = create_princess_cut_diamond(square_size, stone_depth)
        # For square stones, prongs at corners need diagonal radius
        actual_prong_spread_radius = (square_size / 2) * np.sqrt(2) + 0.2
    elif stone_shape == 'radiant':
        stone_mesh = create_radiant_cut_diamond(stone_length, stone_width, stone_depth)
        actual_prong_spread_radius = prong_spread_radius
    else:  # round/brilliant
        stone_mesh = create_brilliant_cut_diamond(stone_radius, stone_depth)
        actual_prong_spread_radius = prong_spread_radius
    
    # Position stone above ring
    stone_mesh.apply_translation([0, stone_y, 0])
    
    # Calculate stone bounds
    crown_height = stone_depth * 0.35
    pavilion_depth = stone_depth * 0.65
    stone_bottom_y = stone_y - pavilion_depth
    stone_top_y = stone_y + crown_height
    stone_girdle_y = stone_y
    
    # Collision detection formulas (matching JavaScript)
    min_safe_height = 1.5
    vertical_collision_threshold = pavilion_depth - ring_thickness + min_safe_height
    horizontal_collision_threshold = stone_radius + (prong_thickness_base / 2) + 0.2
    
    # Check collisions
    has_vertical_collision = setting_height < vertical_collision_threshold
    has_horizontal_collision = actual_prong_spread_radius < horizontal_collision_threshold
    
    # 4. Create Prongs (matching JavaScript logic)
    prong_meshes = []
    prong_meshes_extended = []
    
    centerpiece_point = np.array([0, centerpiece_y, 0])
    
    # Claw dimensions (narrow edge tangential, wide surface radial)
    claw_width_base = prong_thickness_base * 0.5
    claw_depth_base = prong_thickness_base
    claw_width_top = prong_thickness_top * 0.5
    claw_depth_top = prong_thickness_top
    
    for i in range(prong_count):
        angle = (i / prong_count) * 2 * np.pi
        
        # Designer version: prongs end at stone (matching JavaScript)
        end_x = actual_prong_spread_radius * np.cos(angle)
        end_z = actual_prong_spread_radius * np.sin(angle)
        end_point = np.array([end_x, stone_y, end_z])
        
        prong = create_tapered_prong(
            centerpiece_point,
            end_point,
            claw_width_base,
            claw_depth_base,
            claw_width_top,
            claw_depth_top,
            angle
        )
        prong_meshes.append(prong)
        
        # Production version: extend prongs for manufacturing
        end_point_extended = np.array([end_x, stone_y + production_prong_extension, end_z])
        
        prong_extended = create_tapered_prong(
            centerpiece_point,
            end_point_extended,
            claw_width_base,
            claw_depth_base,
            claw_width_top * 0.7,  # Taper more for extended section
            claw_depth_top * 0.7,
            angle
        )
        prong_meshes_extended.append(prong_extended)
    
    # 5. Combine meshes
    # Designer version (with stone)
    designer_meshes = [ring_mesh, stone_mesh] + prong_meshes
    designer_combined = trimesh.util.concatenate(designer_meshes)
    
    # Production version (without stone, extended prongs)
    production_meshes = [ring_mesh] + prong_meshes_extended
    production_combined = trimesh.util.concatenate(production_meshes)
    
    # Make production version watertight/manifold
    # Fill holes and fix normals
    trimesh.repair.fill_holes(production_combined)
    trimesh.repair.fix_normals(production_combined)
    production_combined.merge_vertices()
    
    # 6. Export GLB files
    designer_filename = f'stone_setting_designer_{stone_shape}_{prong_count}prong.glb'
    production_filename = f'stone_setting_production_{stone_shape}_{prong_count}prong.glb'
    
    designer_path = output_path / designer_filename
    production_path = output_path / production_filename
    
    designer_combined.export(str(designer_path))
    production_combined.export(str(production_path))
    
    print(f"✅ Created designer version: {designer_path}")
    print(f"✅ Created production version: {production_path}")
    print(f"\nSettings:")
    print(f"  Stone: {stone_shape} ({stone_length}x{stone_width}x{stone_depth}mm)")
    print(f"  Prongs: {prong_count} prongs")
    print(f"  Prong thickness: {prong_thickness_base}mm base, {prong_thickness_top}mm top")
    print(f"  Setting height: {setting_height}mm")
    print(f"  Ring size: {ring_size}mm (inner diameter)")
    
    # Check for collisions
    has_vertical_collision = setting_height < vertical_collision_threshold
    has_horizontal_collision = stone_radius < horizontal_collision_threshold
    
    if has_vertical_collision or has_horizontal_collision:
        print(f"\n⚠️  Collision Warnings:")
        if has_vertical_collision:
            print(f"  - Vertical: Setting height {setting_height:.2f}mm < {vertical_collision_threshold:.2f}mm required")
        if has_horizontal_collision:
            print(f"  - Horizontal: Stone radius {stone_radius:.2f}mm, needs {horizontal_collision_threshold:.2f}mm clearance")
        print(f"  Consider adjusting parameters to prevent collisions.")
    
    return str(designer_path), str(production_path)


# Example usage
if __name__ == "__main__":
    # Example 1: Classic 4-prong round setting
    print("=" * 60)
    print("Example 1: Classic 4-Prong Round Setting")
    print("=" * 60)
    create_parametric_stone_setting(
        stone_shape='round',
        stone_length=6.0,
        stone_width=6.0,
        stone_depth=7.2,
        prong_count=4,
        prong_thickness_base=0.4,
        prong_thickness_top=0.3,
        setting_height=4.5,
        ring_size=17.0,
        ring_thickness=2.0
    )
    
    print("\n" + "=" * 60)
    print("Example 2: Princess Cut 6-Prong Setting")
    print("=" * 60)
    create_parametric_stone_setting(
        stone_shape='princess',
        stone_length=5.5,
        stone_width=5.5,
        stone_depth=6.5,
        prong_count=6,
        prong_thickness_base=0.35,
        prong_thickness_top=0.25,
        setting_height=4.0,
        ring_size=17.0,
        ring_thickness=2.0
    )
    
    print("\n" + "=" * 60)
    print("Example 3: Radiant Cut 8-Prong Setting")
    print("=" * 60)
    create_parametric_stone_setting(
        stone_shape='radiant',
        stone_length=7.0,
        stone_width=5.0,
        stone_depth=6.0,
        prong_count=8,
        prong_thickness_base=0.3,
        prong_thickness_top=0.2,
        setting_height=3.5,
        ring_size=17.0,
        ring_thickness=2.0
    )
    
    print("\n" + "=" * 60)
    print("All stone settings created successfully!")
    print("=" * 60)
