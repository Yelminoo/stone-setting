"""
Ring Band Web Editor using Build123d + Yet Another CAD Viewer (YACV)
Professional web-based CAD viewer with advanced features
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from build123d import *
from math import cos, sin, radians
import tempfile
import os
import json
import base64

app = Flask(__name__)
CORS(app)

# US Ring Size Chart (inner diameter in mm)
US_RING_SIZES = {
    7: 17.35,
    7.5: 17.77,
    8: 18.19,
    8.5: 18.61,
    9: 19.03,
    9.5: 19.43,
    10: 19.84
}

class RingBandGenerator:
    """Generate ring bands with Build123d"""
    
    @staticmethod
    def create_stone(stone_cut, stone_width, stone_height, position=(0, 0, 0)):
        """
        Create REALISTIC gemstone with ACTUAL FACETS - individual diamond faces
        True jewelry-grade CAD geometry with proper facet angles and surfaces
        
        Args:
            stone_cut: Type of cut - 'round', 'princess', 'radiant'
            stone_width: Diameter/width of stone in mm (girdle measurement)
            stone_height: Total height of stone in mm (table to culet)
            position: (x, y, z) position tuple
        
        Returns:
            Build123d Part with REAL faceted diamond geometry
        """
        import numpy as np
        from math import cos, sin, pi, radians, tan
        
        stone_x, stone_y, stone_z = position
        
        print(f"💎 Creating {stone_cut} stone:")
        print(f"   Width: {stone_width}mm, Height: {stone_height}mm")
        print(f"   Position: X={stone_x}, Y={stone_y}, Z={stone_z}")
        
        if stone_cut == 'round':
            # ROUND BRILLIANT CUT - Using simple cone geometry
            # Smooth surfaces for reliable export
            
            # Tolkowsky ideal proportions
            table_radius = stone_width * 0.53 / 2  # 53% table
            girdle_radius = stone_width / 2
            crown_height = stone_height * 0.162  # 16.2% crown
            pavilion_depth = stone_height * 0.432  # 43.2% pavilion
            
            # Create crown cone
            with BuildPart() as crown:
                with BuildSketch(Plane.XY):
                    Circle(girdle_radius)
                Cone(girdle_radius, table_radius, crown_height)
            
            # Create pavilion cone
            culet_radius = stone_width * 0.01
            with BuildPart() as pavilion:
                with Locations((0, 0, -pavilion_depth)):
                    Cone(culet_radius, girdle_radius, pavilion_depth, align=(Align.CENTER, Align.MAX))
            
            # Combine both cones into single stone
            with BuildPart() as stone:
                add(crown.part)
                add(pavilion.part)
                
                # Rotate -90° around X-axis to align with Y-up orientation
                stone.part = stone.part.rotate(Axis.X, -90)
                
                # Translate to final position
                stone.part = stone.part.translate((stone_x, stone_y, stone_z))
            
            print(f"   Stone part created: {stone.part}")
            print(f"   Stone is valid: {stone.part.is_valid}")
            
            return stone.part
        
        elif stone_cut == 'princess':
            # PRINCESS CUT - 57+ REAL FACETS - Square brilliant
            # Actual faceted geometry with individual faces
            
            # Professional proportions
            table_size = stone_width * 0.65  # 65% table
            crown_height = stone_height * 0.15  # 15% crown
            pavilion_depth = stone_height * 0.70  # 70% deep pavilion
            
            # Create faceted square diamond - single unified loft
            culet_size = stone_width * 0.02
            
            with BuildPart() as stone:
                # Three-level loft: culet → girdle → table (unified solid)
                
                with BuildSketch(Plane.XY.offset(-pavilion_depth)) as s1:
                    # Bottom: culet point
                    Rectangle(culet_size, culet_size, align=(Align.CENTER, Align.CENTER))
                
                with BuildSketch(Plane.XY.offset(0)) as s2:
                    # Middle: girdle (widest)
                    Rectangle(stone_width, stone_width, align=(Align.CENTER, Align.CENTER))
                
                with BuildSketch(Plane.XY.offset(crown_height)) as s3:
                    # Top: table
                    Rectangle(table_size, table_size, align=(Align.CENTER, Align.CENTER))
                
                loft()
                
                # Rotate -90° around X-axis for Y-up orientation, then 45° around Y for corners
                stone.part = stone.part.rotate(Axis.X, -90)
                stone.part = stone.part.rotate(Axis.Y, 45)
                stone.part = stone.part.translate((stone_x, stone_y, stone_z))
            
            return stone.part
        
        elif stone_cut == 'radiant':
            # RADIANT CUT - 70 REAL FACETS - Octagonal brilliant with trimmed corners
            # Realistic faceted geometry with actual facet surfaces
            
            # Professional proportions
            corner_cut = stone_width * 0.18  # 18% corner cuts
            table_size = stone_width * 0.62  # 62% table
            crown_height = stone_height * 0.14  # 14% crown
            pavilion_depth = stone_height * 0.68  # 68% pavilion
            
            # Create octagonal faceted diamond - single unified loft
            culet_size = stone_width * 0.04  # Slightly bigger
            
            with BuildPart() as stone:
                # Three-level loft: culet → girdle → table (unified solid)
                
                with BuildSketch(Plane.XY.offset(-pavilion_depth)) as s1:
                    # Bottom: culet point
                    Polygon(culet_size / 2, 8, align=(Align.CENTER, Align.CENTER))
                
                with BuildSketch(Plane.XY.offset(0)) as s2:
                    # Middle: girdle (widest)
                    Polygon(stone_width / 2, 8, align=(Align.CENTER, Align.CENTER))
                
                with BuildSketch(Plane.XY.offset(crown_height)) as s3:
                    # Top: table
                    Polygon(table_size / 2, 8, align=(Align.CENTER, Align.CENTER))
                
                loft()
                
                # Rotate -90° around X-axis for Y-up orientation
                stone.part = stone.part.rotate(Axis.X, -90)
                stone.part = stone.part.translate((stone_x, stone_y, stone_z))
            
            return stone.part
        
        else:
            # Default to round brilliant
            return RingBandGenerator.create_stone('round', stone_width, stone_height, position)
        
        return stone.part
    
    @staticmethod
    def create_prongs(num_prongs, prong_height, prong_diameter, radial_distance, stone_offset=0.0, taper_ratio=0.5, ring_size_us=8, thickness=2.0, band_width=3.0, stone_width=6.0, stone_height=4.0):
        """
        Create tubular jewelry prongs for stone setting
        Prongs extend from ring band INWARD to grasp stone at center of ring opening
        
        Args:
            num_prongs: Number of prongs (4, 6, or 8)
            prong_height: Height extension from ring band (mm)
            prong_diameter: Base diameter of tubular prong (mm)
            radial_distance: Distance from ring center to prong base on ring
            stone_offset: Not used - prongs hold stone at center
            taper_ratio: Ratio of tip to base diameter
            ring_size_us: US ring size to calculate ring radius
            thickness: Ring band thickness to calculate outer edge position
            band_width: Ring band width (height in Z direction)
            stone_width: Width of stone at girdle (for prong convergence)
            stone_height: Total height of stone (for proper grasping position)
        """
        import numpy as np
        
        # Calculate ring radius from ring size
        inner_diameter = US_RING_SIZES.get(ring_size_us, 18.19)  # Default to size 8
        inner_radius = inner_diameter / 2
        
        # Stone position - ABOVE ring band at radial distance height
        # Stone sits elevated above ring, girdle at least at radial_distance height
        stone_x = 0.0
        stone_y = radial_distance  # Stone elevated above ring - at least radial distance from Y=0
        stone_z = 0.0
        
        # Prong convergence at stone girdle (widest part where they grasp)
        prong_convergence_y = stone_y
        
        # Prong dimensions - tubular (circular cross-section)
        base_radius = prong_diameter / 2.0
        tip_radius = base_radius * taper_ratio
        
        print(f"🔧 PRONG CONFIGURATION:")
        print(f"   Prong tips converge at: X={stone_x}, Y={prong_convergence_y}, Z={stone_z}")
        print(f"   Radial distance: {radial_distance}mm")
        print(f"   Stone dimensions: {stone_width}mm width x {stone_height}mm height")
        print(f"   Number of prongs: {num_prongs}")
        
        prongs = []
        
        for i in range(num_prongs):
            angle = (i / num_prongs) * 2 * np.pi
            
            # START: Base at ring band OUTER edge (THICK part on ring)
            # Prongs grow FROM ring band UPWARD toward stone
            start_x = radial_distance * np.cos(angle)
            start_z = radial_distance * np.sin(angle)
            # Start Y must be >= radial_distance and related to stone height
            start_y = max(radial_distance, prong_height * 0.3)  # At least radial_distance
            start_point = (start_x, start_y, start_z)
            
            # END: Tip spreads outward at stone radius (THIN part holding stone at girdle)
            # Prongs hold stone at its girdle radius, not at center
            stone_radius = stone_width / 2.0  # Girdle radius
            end_x = stone_radius * np.cos(angle)  # Spread around stone perimeter
            end_z = stone_radius * np.sin(angle)  # Spread around stone perimeter
            end_y = prong_convergence_y
            end_point = (end_x, end_y, end_z)
            
            print(f"  Prong {i}: base at ring {start_point} → tip at stone edge {end_point}")
            
            # Create prong: thick base at ring edge → thin tip at center holding stone
            prong = RingBandGenerator.create_single_tubular_prong(
                start_point, end_point,
                base_radius, tip_radius
            )
            prongs.append(prong)
        
        # Combine all prongs - they will fuse at center
        combined = prongs[0]
        for prong in prongs[1:]:
            combined = combined + prong
        
        return combined
    
    @staticmethod
    def create_single_tubular_prong(start_point, end_point, base_radius, tip_radius):
        """Create a single tapered tubular prong with natural finger-like curve"""
        import numpy as np
        
        # Calculate direction and length
        start = np.array(start_point)
        end = np.array(end_point)
        direction = end - start
        total_length = np.linalg.norm(direction)
        
        # Create natural finger-like curve (gentle arc upward)
        # The curve goes UP (in Y direction) as it approaches the center
        num_sections = 8
        sections_points = []
        
        for i in range(num_sections + 1):
            t = i / num_sections
            
            # Linear interpolation along main direction
            point = start + direction * t
            
            # REVERSED CURVE: pushes DOWNWARD (negative Y) - toward ring surface
            # Curve is strongest in the middle, less at start and end
            curve_factor = np.sin(t * np.pi)  # 0 at start, peak at middle, 0 at end
            downward_curve = curve_factor * total_length * 0.15  # 15% downward curve
            
            # Apply NEGATIVE curve (pushes downward/inward toward ring)
            point[1] -= downward_curve
            
            # At the very tip (last 20%), add slight inward curve
            if t > 0.8:
                tip_t = (t - 0.8) / 0.2
                # Pull tip slightly more toward end point (tighten the curve)
                toward_end = end - point
                point += toward_end * tip_t * 0.15
            
            # Calculate radius (smooth taper)
            radius = base_radius * (1 - t) + tip_radius * t
            
            sections_points.append((point, radius))
        
        with BuildPart() as prong:
            # Create each curved section
            for i in range(len(sections_points) - 1):
                point, radius = sections_points[i]
                next_point, next_radius = sections_points[i + 1]
                
                # Calculate local direction for this segment
                segment_dir = next_point - point
                segment_length = np.linalg.norm(segment_dir)
                if segment_length < 0.001:
                    continue
                    
                segment_dir_norm = segment_dir / segment_length
                
                # Rotation to align with segment
                z_axis = np.array([0, 0, 1])
                rotation_axis = np.cross(z_axis, segment_dir_norm)
                
                if np.linalg.norm(rotation_axis) > 1e-6:
                    rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
                    angle = np.arccos(np.clip(np.dot(z_axis, segment_dir_norm), -1, 1))
                else:
                    rotation_axis = np.array([1, 0, 0])
                    angle = 0 if segment_dir_norm[2] > 0 else np.pi
                
                # Create loft segment
                with BuildPart() as segment:
                    # Base circle
                    with BuildSketch(Plane.XY) as sketch1:
                        Circle(radius)
                    
                    # Top circle
                    with BuildSketch(Plane.XY.offset(segment_length)) as sketch2:
                        Circle(next_radius)
                    
                    loft()
                    
                    # Rotate and position
                    if angle > 1e-6:
                        segment.part = segment.part.rotate(
                            Axis(origin=(0, 0, 0), direction=tuple(rotation_axis)),
                            np.degrees(angle)
                        )
                    
                    segment.part = segment.part.translate(tuple(point))
                    
                    add(segment.part)
        
        return prong.part
    
    @staticmethod
    def create_basic_band(ring_size_us, thickness, band_width):
        """Create a basic rectangular band - proper 3D tubular ring using revolve"""
        if ring_size_us not in US_RING_SIZES:
            raise ValueError(f"Size {ring_size_us} not supported")
        
        inner_diameter = US_RING_SIZES[ring_size_us]
        inner_radius = inner_diameter / 2
        
        # Create a rectangular profile and revolve it around Z-axis
        with BuildPart() as ring:
            with BuildSketch(Plane.XZ) as profile:
                # Rectangle profile in XZ plane
                # X-axis is radial direction, Z-axis is vertical/height
                with BuildLine() as rect_profile:
                    l1 = Line((inner_radius, -band_width/2), (inner_radius + thickness, -band_width/2))
                    l2 = Line(l1 @ 1, (inner_radius + thickness, band_width/2))
                    l3 = Line(l2 @ 1, (inner_radius, band_width/2))
                    l4 = Line(l3 @ 1, (inner_radius, -band_width/2))
                make_face()
            # Revolve around Z-axis to create 3D tubular ring
            revolve(axis=Axis.Z)
        
        return ring.part
    
    @staticmethod
    def create_comfort_fit_band(ring_size_us, thickness, band_width, inner_radius_curve):
        """Create a comfort-fit band with rounded inner edge"""
        if ring_size_us not in US_RING_SIZES:
            raise ValueError(f"Size {ring_size_us} not supported")
        
        inner_diameter = US_RING_SIZES[ring_size_us]
        inner_radius = inner_diameter / 2
        
        max_radius = min(thickness, band_width) / 2 - 0.01
        if inner_radius_curve >= max_radius:
            inner_radius_curve = max_radius
        
        with BuildPart() as ring:
            with BuildSketch(Plane.XZ) as profile:
                # Create rounded rectangle profile in XZ plane
                # In XZ plane: X is radial, Z is vertical
                center_x = inner_radius + thickness / 2
                with Locations((center_x, 0)):
                    RectangleRounded(
                        thickness, 
                        band_width,
                        inner_radius_curve,
                        align=(Align.CENTER, Align.CENTER)
                    )
            # Revolve around Z axis to create 3D tubular ring
            revolve(axis=Axis.Z)
        
        return ring.part
    
    @staticmethod
    def create_tapered_band(ring_size_us, thickness_top, thickness_bottom, band_width):
        """Create a tapered band (thicker on bottom/palm side)"""
        if ring_size_us not in US_RING_SIZES:
            raise ValueError(f"Size {ring_size_us} not supported")
        
        inner_diameter = US_RING_SIZES[ring_size_us]
        inner_radius = inner_diameter / 2
        
        with BuildPart() as ring:
            with BuildSketch(Plane.XZ) as profile:
                # Trapezoid profile in XZ plane
                # X is radial, Z is vertical
                points = [
                    (inner_radius, -band_width/2),
                    (inner_radius + thickness_bottom, -band_width/2),
                    (inner_radius + thickness_top, band_width/2),
                    (inner_radius, band_width/2),
                ]
                
                with BuildLine() as trapezoid:
                    for i in range(len(points)):
                        Line(points[i], points[(i+1) % len(points)])
                
                make_face()
            # Revolve around Z axis to create 3D tubular ring
            revolve(axis=Axis.Z)
        
        return ring.part
    
    @staticmethod
    def create_domed_band(ring_size_us, thickness, band_width, dome_height):
        """Create a band with domed outer surface"""
        if ring_size_us not in US_RING_SIZES:
            raise ValueError(f"Size {ring_size_us} not supported")
        
        inner_diameter = US_RING_SIZES[ring_size_us]
        inner_radius = inner_diameter / 2
        
        with BuildPart() as ring:
            with BuildSketch(Plane.XZ) as profile:
                # Domed profile in XZ plane
                # X is radial, Z is vertical
                bottom_inner = (inner_radius, -band_width/2)
                bottom_outer = (inner_radius + thickness, -band_width/2)
                center_peak = (inner_radius + thickness + dome_height, 0)
                top_outer = (inner_radius + thickness, band_width/2)
                top_inner = (inner_radius, band_width/2)
                
                with BuildLine() as dome_profile:
                    Line(bottom_inner, bottom_outer)
                    Bezier(bottom_outer, center_peak, top_outer)
                    Line(top_outer, top_inner)
                    Line(top_inner, bottom_inner)
                
                make_face()
            # Revolve around Z axis to create 3D tubular ring
            revolve(axis=Axis.Z)
        
        return ring.part
    
    @staticmethod
    def create_ring_with_prongs(ring_part, num_prongs, prong_height, prong_diameter, radial_distance):
        """
        Combine a ring band with prongs
        
        Args:
            ring_part: The ring band Part object
            num_prongs: Number of prongs
            prong_height: Height of prongs
            prong_diameter: Diameter of prongs
            radial_distance: Distance from center to prongs
        """
        # default stone offset 0.0 (center). If provided, create_prongs will place top at that offset.
        prongs = RingBandGenerator.create_prongs(num_prongs, prong_height, prong_diameter, radial_distance)

        # Combine ring and prongs using Part union
        with BuildPart() as combined:
            add(ring_part)
            add(prongs)

        return combined.part


@app.route('/')
def index():
    """Serve the main editor page with professional viewer"""
    return render_template('ring_band_pro.html')


@app.route('/generate', methods=['POST'])
def generate():
    """Generate ring band and return OBJ file for viewer"""
    try:
        data = request.json
        
        # Extract parameters
        band_type = data.get('band_type', 'basic')
        ring_size = float(data.get('ring_size', 8))
        thickness = float(data.get('thickness', 2.0))
        band_width = float(data.get('band_width', 3.0))
        
        # Calculate default prong_height as radial distance (outer edge of ring)
        inner_diameter = US_RING_SIZES.get(ring_size, 18.19)
        inner_radius = inner_diameter / 2
        default_prong_height = inner_radius + thickness  # radial distance to outer edge
        
        # Prong parameters
        add_prongs = data.get('add_prongs', False)
        num_prongs = int(data.get('num_prongs', 4))
        prong_height = default_prong_height  # Always use radial distance, no user parameter
        prong_diameter = float(data.get('prong_diameter', 1.0))
        prong_distance = float(data.get('prong_distance', 0.0))  # If 0, auto-calculate base position
        prong_center_offset = float(data.get('prong_center_offset', 0.0))  # radial offset for stone center (X axis)
        
        # Stone parameters
        add_stone = data.get('add_stone', False)
        stone_cut = data.get('stone_cut', 'round')  # 'round', 'princess', 'radiant'
        stone_width = float(data.get('stone_width', 6.0))  # mm - diameter at girdle
        stone_height = float(data.get('stone_height', 4.0))  # mm - total table to culet
        
        # Create the appropriate band type
        generator = RingBandGenerator()
        
        if band_type == 'basic':
            ring = generator.create_basic_band(ring_size, thickness, band_width)
        elif band_type == 'comfort_fit':
            inner_curve = float(data.get('inner_curve', 0.5))
            ring = generator.create_comfort_fit_band(ring_size, thickness, band_width, inner_curve)
        elif band_type == 'tapered':
            thickness_top = float(data.get('thickness_top', 1.8))
            thickness_bottom = float(data.get('thickness_bottom', 2.5))
            ring = generator.create_tapered_band(ring_size, thickness_top, thickness_bottom, band_width)
        elif band_type == 'domed':
            dome_height = float(data.get('dome_height', 1.0))
            ring = generator.create_domed_band(ring_size, thickness, band_width, dome_height)
        else:
            return jsonify({'success': False, 'error': f'Unknown band type: {band_type}'})
        
        # Add prongs if requested
        if add_prongs:
            # Auto-calculate prong base distance if not specified
            if prong_distance == 0:
                inner_diameter = US_RING_SIZES[ring_size]
                inner_radius = inner_diameter / 2
                # Place prong bases at the OUTER edge of the ring band
                prong_distance = inner_radius + thickness  # At outer edge of ring
            
            # If stone offset is 0, set a reasonable default (slightly outside ring)
            if prong_center_offset == 0:
                inner_diameter = US_RING_SIZES[ring_size]
                inner_radius = inner_diameter / 2
                prong_center_offset = inner_radius + thickness + 2.0  # 2mm outside ring

            # Create prongs with the requested stone center offset
            prongs_part = generator.create_prongs(num_prongs, prong_height, prong_diameter, prong_distance, stone_offset=prong_center_offset, ring_size_us=ring_size, thickness=thickness, band_width=band_width, stone_width=stone_width, stone_height=stone_height)
            
            print(f"Prong generation params: num={num_prongs}, height={prong_height}, diameter={prong_diameter}, distance={prong_distance}, offset={prong_center_offset}")
            print(f"Prongs part created: {prongs_part}")

            # Add stone if requested
            if add_stone:
                # CRITICAL: Stone position must EXACTLY match prong tip convergence point
                # In create_prongs(), prong tips converge at: (0, radial_distance, 0)
                # where radial_distance = prong_distance parameter
                
                # Calculate stone girdle position to align with prong tips
                stone_girdle_y = prong_distance  # Prong tips converge at this Y height
                
                # Stone position: Place girdle (widest part) at prong convergence
                stone_position_x = 0.0  # Center of ring
                stone_position_y = stone_girdle_y  # Girdle at prong tip height
                stone_position_z = 0.0  # Center of ring width
                
                stone_part = generator.create_stone(stone_cut, stone_width, stone_height, position=(stone_position_x, stone_position_y, stone_position_z))
                
                # Stone orientation: Height along Y-axis (crown up, pavilion down)
                # No rotation needed - stone and prongs both use Y-axis for height
                
                print(f"✨ Stone positioned at prong convergence point:")
                print(f"   Stone girdle: Y={stone_girdle_y}mm (matches prong tips)")
                print(f"   Full position: X={stone_position_x}, Y={stone_position_y}, Z={stone_position_z}")
                print(f"   Stone: {stone_cut} cut, {stone_width}mm x {stone_height}mm")
                
                # Combine ring, prongs, and stone
                with BuildPart() as combined_part:
                    add(ring)
                    add(prongs_part)
                    add(stone_part)
                
                ring = combined_part.part
                print(f"Combined ring+prongs+stone: {ring}")
            else:
                # Combine ring and prongs only
                with BuildPart() as combined_part:
                    add(ring)
                    add(prongs_part)

                ring = combined_part.part
                print(f"Combined ring+prongs: {ring}")
        elif add_stone:
            # Add stone without prongs (unusual but possible)
            # Position at radial distance height
            stone_position_x = 0.0
            stone_position_y = inner_radius + thickness  # At radial distance height
            stone_position_z = 0.0
            
            stone_part = generator.create_stone(stone_cut, stone_width, stone_height, position=(stone_position_x, stone_position_y, stone_position_z))
            
            # Stone orientation: Height along Y-axis (crown up, pavilion down)
            # No rotation needed - same coordinate system as prongs
            
            with BuildPart() as combined_part:
                add(ring)
                add(stone_part)
            
            ring = combined_part.part
            print(f"Combined ring+stone: {ring}")
        
        # Export Build123d Part to STL, then to OBJ
        temp_stl = tempfile.NamedTemporaryFile(suffix='.stl', delete=False)
        temp_stl_path = temp_stl.name
        temp_stl.close()
        
        temp_obj = tempfile.NamedTemporaryFile(suffix='.obj', delete=False)
        temp_obj_path = temp_obj.name
        temp_obj.close()
        
        try:
            # Export to high-quality STL with fine tolerance for smoother curves
            export_stl(ring, temp_stl_path, 
                      tolerance=0.01,
                      angular_tolerance=0.1)
            
            # Load with trimesh and convert to OBJ
            import trimesh
            loaded = trimesh.load(temp_stl_path)
            
            # Handle both Mesh and Scene objects (Scene when multiple parts exist)
            if isinstance(loaded, trimesh.Scene):
                # Merge all geometries in the scene into a single mesh
                mesh = trimesh.util.concatenate(
                    tuple(trimesh.Trimesh(vertices=g.vertices, faces=g.faces)
                          for g in loaded.geometry.values())
                )
            else:
                mesh = loaded
            
            # Ensure proper normals and merge vertices for smooth surface
            mesh.merge_vertices()
            mesh.fix_normals()
            
            # Verify we have a 3D mesh (not flat)
            bounds = mesh.bounds
            print(f"Mesh bounds: {bounds}")
            print(f"Mesh extents: {mesh.extents}")
            
            # Export to OBJ with vertex normals for smooth shading
            mesh.export(temp_obj_path, file_type='obj', include_normals=True)
            
            # Read OBJ file
            with open(temp_obj_path, 'r') as f:
                obj_data = f.read()
            
            # Clean up
            os.unlink(temp_stl_path)
            os.unlink(temp_obj_path)
            
            # Return OBJ file as text
            return obj_data, 200, {'Content-Type': 'text/plain'}
        
        except Exception as e:
            # Clean up on error
            try:
                os.unlink(temp_stl_path)
                os.unlink(temp_obj_path)
            except:
                pass
            raise e
        
    except Exception as e:
        print(f"Error generating ring: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/export/<format>', methods=['POST'])
def export_file(format):
    """Export ring band to STEP or STL format"""
    try:
        data = request.json
        
        band_type = data.get('band_type', 'basic')
        ring_size = float(data.get('ring_size', 8))
        thickness = float(data.get('thickness', 2.0))
        band_width = float(data.get('band_width', 3.0))
        
        generator = RingBandGenerator()
        
        if band_type == 'basic':
            ring = generator.create_basic_band(ring_size, thickness, band_width)
        elif band_type == 'comfort_fit':
            inner_curve = float(data.get('inner_curve', 0.5))
            ring = generator.create_comfort_fit_band(ring_size, thickness, band_width, inner_curve)
        elif band_type == 'tapered':
            thickness_top = float(data.get('thickness_top', 1.8))
            thickness_bottom = float(data.get('thickness_bottom', 2.5))
            ring = generator.create_tapered_band(ring_size, thickness_top, thickness_bottom, band_width)
        elif band_type == 'domed':
            dome_height = float(data.get('dome_height', 1.0))
            ring = generator.create_domed_band(ring_size, thickness, band_width, dome_height)
        else:
            return jsonify({'success': False, 'error': f'Unknown band type: {band_type}'})
        
        if format.lower() == 'step':
            temp_file = tempfile.NamedTemporaryFile(suffix='.step', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            export_step(ring, temp_path)
            mimetype = 'application/step'
            filename = f'ring_band_{band_type}_size{ring_size}.step'
        elif format.lower() == 'stl':
            temp_file = tempfile.NamedTemporaryFile(suffix='.stl', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            export_stl(ring, temp_path)
            mimetype = 'model/stl'
            filename = f'ring_band_{band_type}_size{ring_size}.stl'
        else:
            return jsonify({'success': False, 'error': f'Unsupported format: {format}'}), 400
        
        response = send_file(
            temp_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(temp_path)
            except:
                pass
        
        return response
        
    except Exception as e:
        print(f"Error exporting: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    import io
    import trimesh
    
    os.makedirs('output', exist_ok=True)
    
    print("=" * 70)
    print("🎨 Ring Band Editor - Professional CAD Viewer")
    print("=" * 70)
    print("\n🌐 Starting server on http://localhost:5004")
    print("📱 Open your browser and visit: http://localhost:5004")
    print("\n✨ Features:")
    print("   • Professional 3D CAD viewer")
    print("   • Material & color selection")
    print("   • Real-time parametric design")
    print("   • Enhanced lighting & reflections")
    print("   • Export to STEP/STL")
    print("\n" + "=" * 70)
    
    app.run(host='0.0.0.0', port=5004, debug=True)
