"""
Stone Setting Generator using build123d
Modern CAD library with parametric modeling

IMPORTANT: This file uses the EXACT SAME formulas and clearances as stone_setting_simple.py
All calculations for stone sizing, prong positioning, and clearances are identical.
The only difference is the CAD library used (build123d vs trimesh).
"""

from build123d import *
import numpy as np

def create_ring_b3d(inner_radius, thickness):
    """Create a ring using build123d"""
    with BuildPart() as ring:
        with BuildSketch() as cross_section:
            Circle(thickness / 2)
        
        revolve(axis=Axis.Z, revolution_arc=360)
        with Locations((inner_radius + thickness/2, 0, 0)):
            add(ring.part)
    
    return ring.part


def create_brilliant_cut_diamond_b3d(radius, depth):
    """Create a brilliant cut diamond using build123d"""
    crown_height = depth * 0.35
    pavilion_height = depth * 0.65
    table_size = radius * 0.6
    
    with BuildPart() as diamond:
        # Crown (top part)
        with BuildSketch(Plane.XY.offset(crown_height)) as crown_sketch:
            Circle(table_size)  # Table (top facet)
        
        with BuildSketch(Plane.XY) as girdle_sketch:
            Circle(radius)  # Girdle (widest part)
        
        loft()
        
        # Pavilion (bottom part)
        with BuildSketch(Plane.XY) as girdle_sketch2:
            Circle(radius)
        
        with BuildSketch(Plane.XY.offset(-pavilion_height)) as culet_sketch:
            Circle(radius * 0.05)  # Culet (bottom point)
        
        loft()
    
    return diamond.part


def create_princess_cut_diamond_b3d(size, depth):
    """Create a princess cut (square) diamond"""
    crown_height = depth * 0.35
    pavilion_height = depth * 0.65
    table_size = size * 0.6
    
    with BuildPart() as diamond:
        # Crown
        with BuildSketch(Plane.XY.offset(crown_height)) as crown:
            Rectangle(table_size, table_size, align=(Align.CENTER, Align.CENTER))
        
        with BuildSketch(Plane.XY) as girdle:
            Rectangle(size, size, align=(Align.CENTER, Align.CENTER))
        
        loft()
        
        # Pavilion
        with BuildSketch(Plane.XY) as girdle2:
            Rectangle(size, size, align=(Align.CENTER, Align.CENTER))
        
        with BuildSketch(Plane.XY.offset(-pavilion_height)) as culet:
            Rectangle(size * 0.1, size * 0.1, align=(Align.CENTER, Align.CENTER))
        
        loft()
    
    return diamond.part


def create_radiant_cut_diamond_b3d(size, depth):
    """Create a radiant cut (beveled square/octagon) diamond"""
    crown_height = depth * 0.35
    pavilion_height = depth * 0.65
    bevel = size * 0.15
    
    with BuildPart() as diamond:
        # Create octagon shape (square with beveled corners)
        def octagon_points(s, bevel):
            half = s / 2
            return [
                (half, half - bevel),
                (half - bevel, half),
                (-half + bevel, half),
                (-half, half - bevel),
                (-half, -half + bevel),
                (-half + bevel, -half),
                (half - bevel, -half),
                (half, -half + bevel)
            ]
        
        # Crown
        with BuildSketch(Plane.XY.offset(crown_height)) as crown:
            with BuildLine() as table_outline:
                Polyline(*octagon_points(size * 0.6, bevel * 0.6), close=True)
            make_face()
        
        with BuildSketch(Plane.XY) as girdle:
            with BuildLine() as girdle_outline:
                Polyline(*octagon_points(size, bevel), close=True)
            make_face()
        
        loft()
        
        # Pavilion
        with BuildSketch(Plane.XY) as girdle2:
            with BuildLine() as girdle_outline2:
                Polyline(*octagon_points(size, bevel), close=True)
            make_face()
        
        with BuildSketch(Plane.XY.offset(-pavilion_height)) as culet:
            Circle(size * 0.05)
        
        loft()
    
    return diamond.part


def create_single_prong_b3d(start_point, end_point, base_width, base_depth, top_width, top_depth):
    """Create a single tapered prong using build123d"""
    
    # Calculate direction and length
    direction = np.array(end_point) - np.array(start_point)
    length = np.linalg.norm(direction)
    direction_normalized = direction / length
    
    # Create transformation to align prong
    z_axis = np.array([0, 0, 1])
    rotation_axis = np.cross(z_axis, direction_normalized)
    
    if np.linalg.norm(rotation_axis) > 1e-6:
        rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
        angle = np.arccos(np.clip(np.dot(z_axis, direction_normalized), -1, 1))
    else:
        rotation_axis = np.array([1, 0, 0])
        angle = 0 if direction_normalized[2] > 0 else np.pi
    
    with BuildPart() as prong:
        # Create base rectangle
        with BuildSketch(Plane.XY) as base:
            Rectangle(base_width, base_depth, align=(Align.CENTER, Align.CENTER))
        
        # Create top rectangle
        with BuildSketch(Plane.XY.offset(length)) as top:
            Rectangle(top_width, top_depth, align=(Align.CENTER, Align.CENTER))
        
        loft()
        
        # Apply rotation and translation
        if angle > 1e-6:
            prong.part = prong.part.rotate(
                Axis(origin=(0, 0, 0), direction=rotation_axis), 
                np.degrees(angle)
            )
        
        prong.part = prong.part.translate(start_point)
    
    return prong.part


def create_prongs_b3d(config, centerpiece_y, stone_y, prong_spread_radius):
    """Create all prongs"""
    prong_count = config['prongCount']
    base_width = config['prongThicknessBase']
    base_depth = config['prongThicknessBase']
    top_width = config['prongThicknessTop']
    top_depth = config['prongThicknessTop']
    
    ring_size = config['ringSize']
    
    prongs = []
    
    for i in range(prong_count):
        angle = (i / prong_count) * 2 * np.pi
        
        # Start point at ring edge
        start_x = ring_size * np.cos(angle)
        start_z = ring_size * np.sin(angle)
        start_y = centerpiece_y
        start_point = (start_x, start_y, start_z)
        
        # End point at stone perimeter, slightly above stone center
        end_x = prong_spread_radius * np.cos(angle)
        end_z = prong_spread_radius * np.sin(angle)
        end_y = stone_y + 0.5  # 0.5mm above stone center
        end_point = (end_x, end_y, end_z)
        
        prong = create_single_prong_b3d(
            start_point, end_point,
            base_width, base_depth,
            top_width, top_depth
        )
        prongs.append(prong)
    
    # Combine all prongs
    combined = prongs[0]
    for prong in prongs[1:]:
        combined = combined + prong
    
    return combined


def create_stone_setting_b3d(
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
    Create a complete stone setting using build123d
    
    Parameters:
    - stone_size: Diameter for round, side length for square (mm)
    - stone_depth: Total depth of stone (mm)
    - prong_count: Number of prongs (typically 4 or 6)
    - prong_thickness_base: Width at base (mm)
    - prong_thickness_top: Width at top (mm)
    - setting_height: Height of stone above ring (mm)
    - ring_size: Inner radius of ring (mm)
    - ring_thickness: Cross-section diameter of ring band (mm)
    - stone_shape: 'round', 'princess', or 'radiant'
    """
    
    # Create ring
    ring = create_ring_b3d(ring_size, ring_thickness)
    
    # Calculate positions (MATCHING stone_setting_simple.py EXACTLY)
    centerpiece_distance = ring_size
    centerpiece_y = centerpiece_distance
    
    stone_height_above_ring = setting_height
    stone_y = ring_size + ring_thickness + stone_height_above_ring
    
    # Calculate stone size and prong positioning (MATCHING stone_setting_simple.py)
    prong_spread_radius = stone_size / 2
    
    # Adjust prong spread to account for prong thickness (push prongs outward)
    prong_spread_radius += (prong_thickness_base / 2)  # Add half base thickness
    
    stone_radius = prong_spread_radius - 0.25  # Minimal clearance (matching trimesh version)
    
    # Create Stone based on shape (MATCHING stone_setting_simple.py formulas)
    actual_prong_spread = prong_spread_radius
    
    if stone_shape == 'round':
        stone = create_brilliant_cut_diamond_b3d(stone_radius, stone_depth)
    elif stone_shape == 'princess':
        # Princess cut uses diagonal radius (MATCHING trimesh version)
        stone_size_actual = stone_size - 0.5  # Very small clearance for princess
        stone = create_princess_cut_diamond_b3d(stone_size_actual, stone_depth)
        # Rotate stone so corners align with prongs (MATCHING trimesh version)
        rotation_angle_deg = np.degrees(np.pi / prong_count)  # Half prong angle offset
        stone = stone.rotate(Axis.Y, rotation_angle_deg)
        # Adjust prong spread for square corners (MATCHING trimesh version)
        actual_prong_spread = (stone_size / 2) * np.sqrt(2) + 0.1 + (prong_thickness_base / 2)
    elif stone_shape == 'radiant':
        # Radiant cut (beveled square) - MATCHING trimesh version
        stone_size_actual = stone_size - 0.05  # Minimal clearance for radiant
        stone = create_radiant_cut_diamond_b3d(stone_size_actual, stone_depth)
        # Rotate stone so beveled corners align with prongs (MATCHING trimesh version)
        rotation_angle_deg = np.degrees(np.pi / prong_count)  # Half prong angle offset
        stone = stone.rotate(Axis.Y, rotation_angle_deg)
        # Radiant has beveled corners (MATCHING trimesh version)
        actual_prong_spread = (stone_size / 2) * 1.3 + (prong_thickness_base / 2)  # Less than sqrt(2)
    else:
        # Default to round
        stone = create_brilliant_cut_diamond_b3d(stone_radius, stone_depth)
    
    # Position stone
    stone = stone.translate((0, stone_y, 0))
    
    # Create prongs (MATCHING stone_setting_simple.py)
    config = {
        'prongCount': prong_count,
        'prongThicknessBase': prong_thickness_base,
        'prongThicknessTop': prong_thickness_top,
        'ringSize': ring_size
    }
    prongs = create_prongs_b3d(config, centerpiece_y, stone_y, actual_prong_spread)
    
    return ring, stone, prongs


def export_to_step(ring, stone, prongs, filename="stone_setting_b3d.step"):
    """Export to STEP format"""
    from build123d import export_step
    combined = ring + stone + prongs
    export_step(combined, filename)
    print(f"✅ Exported to {filename}")
    return filename


def export_to_stl(ring, stone, prongs, filename="stone_setting_b3d.stl"):
    """Export to STL format"""
    from build123d import export_stl
    combined = ring + stone + prongs
    export_stl(combined, filename)
    print(f"✅ Exported to {filename}")
    return filename


if __name__ == "__main__":
    print("=" * 60)
    print("🔷 Stone Setting Generator - build123d Version")
    print("=" * 60)
    
    # Generate with default parameters
    ring, stone, prongs = create_stone_setting_b3d(
        stone_size=6.0,
        stone_depth=7.2,
        prong_count=4,
        prong_thickness_base=0.4,
        prong_thickness_top=0.3,
        setting_height=3.0,
        ring_size=8.5,
        ring_thickness=1.0,
        stone_shape='round'
    )
    
    # Export
    export_to_step(ring, stone, prongs, "output/stone_setting_b3d.step")
    export_to_stl(ring, stone, prongs, "output/stone_setting_b3d.stl")
    
    print("\n✨ Generation complete!")
    print("=" * 60)
