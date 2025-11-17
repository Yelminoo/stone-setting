"""
Simple Ring Band Generator
Control ring by US standard sizes (7-10) and thickness tapering inward
"""

import trimesh
import numpy as np

# US Ring Size Chart (inner diameter in mm)
US_RING_SIZES = {
    7: 17.35,
    7.5: 17.75,
    8: 18.19,
    8.5: 18.53,
    9: 19.03,
    9.5: 19.41,
    10: 19.84
}

def create_ring_band(
    ring_size_us=8,
    thickness_outer=2.0,  # Thickness at outer edge (mm)
    thickness_inner=1.5,  # Thickness at inner edge (mm) - creates taper
    band_width=3.0        # Width (height) of the band (mm)
):
    """
    Create a ring band with US standard sizing and thickness taper
    
    Parameters:
    - ring_size_us: US ring size (7, 7.5, 8, 8.5, 9, 9.5, 10)
    - thickness_outer: Thickness at outer edge (mm)
    - thickness_inner: Thickness at inner edge (mm) - smaller = taper inward
    - band_width: Height of the band (mm)
    
    Returns:
    - trimesh.Trimesh: The ring band mesh
    """
    
    # Get inner diameter from US size chart
    if ring_size_us not in US_RING_SIZES:
        raise ValueError(f"Ring size {ring_size_us} not supported. Use: {list(US_RING_SIZES.keys())}")
    
    inner_diameter = US_RING_SIZES[ring_size_us]
    inner_radius = inner_diameter / 2
    
    # Calculate radii for the band profile
    # Inner edge of band
    r_inner = inner_radius
    # Outer edge of band (adds thickness)
    r_outer = inner_radius + thickness_outer
    
    # Create cross-section profile (tapered rectangle)
    # The taper means the band gets thinner toward the inside
    segments_profile = 4  # Rectangle
    segments_circle = 64  # Smoothness around the ring
    
    vertices = []
    faces = []
    
    # Create vertices for the tapered band
    for i in range(segments_circle):
        angle = (i / segments_circle) * 2 * np.pi
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        
        # Bottom inner corner (thinner)
        vertices.append([
            r_inner * cos_a,
            -band_width / 2,
            r_inner * sin_a
        ])
        
        # Top inner corner (thinner)
        vertices.append([
            r_inner * cos_a,
            band_width / 2,
            r_inner * sin_a
        ])
        
        # Top outer corner (thicker)
        vertices.append([
            r_outer * cos_a,
            band_width / 2,
            r_outer * sin_a
        ])
        
        # Bottom outer corner (thicker)
        vertices.append([
            r_outer * cos_a,
            -band_width / 2,
            r_outer * sin_a
        ])
    
    # Create faces
    for i in range(segments_circle):
        next_i = (i + 1) % segments_circle
        
        base = i * 4
        next_base = next_i * 4
        
        # Inner surface
        faces.append([base + 0, base + 1, next_base + 0])
        faces.append([next_base + 0, base + 1, next_base + 1])
        
        # Outer surface
        faces.append([base + 2, base + 3, next_base + 2])
        faces.append([next_base + 2, base + 3, next_base + 3])
        
        # Top surface
        faces.append([base + 1, base + 2, next_base + 1])
        faces.append([next_base + 1, base + 2, next_base + 2])
        
        # Bottom surface
        faces.append([base + 3, base + 0, next_base + 3])
        faces.append([next_base + 3, base + 0, next_base + 0])
    
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
    
    # Print info
    print(f"✅ Ring Band Created:")
    print(f"   US Size: {ring_size_us}")
    print(f"   Inner Diameter: {inner_diameter:.2f} mm")
    print(f"   Inner Radius: {inner_radius:.2f} mm")
    print(f"   Thickness (outer): {thickness_outer:.2f} mm")
    print(f"   Thickness (inner): {thickness_inner:.2f} mm")
    print(f"   Band Width: {band_width:.2f} mm")
    print(f"   Vertices: {len(mesh.vertices)}")
    print(f"   Faces: {len(mesh.faces)}")
    
    return mesh


def create_tapered_ring_band(
    ring_size_us=8,
    thickness_top=2.0,     # Thickness at top of band
    thickness_bottom=2.5,  # Thickness at bottom of band (can be thicker)
    band_width=3.0         # Width (height) of the band (mm)
):
    """
    Create a ring band with thickness that increases toward the inner (bottom)
    This creates a comfortable fit with more material on the palm side
    
    Parameters:
    - ring_size_us: US ring size (7, 7.5, 8, 8.5, 9, 9.5, 10)
    - thickness_top: Thickness at top/outer of band (mm)
    - thickness_bottom: Thickness at bottom/inner (mm) - typically larger
    - band_width: Height of the band (mm)
    """
    
    if ring_size_us not in US_RING_SIZES:
        raise ValueError(f"Ring size {ring_size_us} not supported. Use: {list(US_RING_SIZES.keys())}")
    
    inner_diameter = US_RING_SIZES[ring_size_us]
    inner_radius = inner_diameter / 2
    
    segments = 64
    vertices = []
    faces = []
    
    # Create ring with variable thickness
    for i in range(segments):
        angle = (i / segments) * 2 * np.pi
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        
        # Bottom half (palm side) - thicker
        y_bottom = -band_width / 2
        r_inner_bottom = inner_radius
        r_outer_bottom = inner_radius + thickness_bottom
        
        # Top half (back of hand) - thinner
        y_top = band_width / 2
        r_inner_top = inner_radius
        r_outer_top = inner_radius + thickness_top
        
        # 4 corners of the cross-section
        # Bottom inner
        vertices.append([r_inner_bottom * cos_a, y_bottom, r_inner_bottom * sin_a])
        # Top inner
        vertices.append([r_inner_top * cos_a, y_top, r_inner_top * sin_a])
        # Top outer
        vertices.append([r_outer_top * cos_a, y_top, r_outer_top * sin_a])
        # Bottom outer
        vertices.append([r_outer_bottom * cos_a, y_bottom, r_outer_bottom * sin_a])
    
    # Create faces
    for i in range(segments):
        next_i = (i + 1) % segments
        base = i * 4
        next_base = next_i * 4
        
        # Inner surface
        faces.append([base + 0, base + 1, next_base + 0])
        faces.append([next_base + 0, base + 1, next_base + 1])
        
        # Outer surface
        faces.append([base + 2, base + 3, next_base + 2])
        faces.append([next_base + 2, base + 3, next_base + 3])
        
        # Top surface
        faces.append([base + 1, base + 2, next_base + 1])
        faces.append([next_base + 1, base + 2, next_base + 2])
        
        # Bottom surface
        faces.append([base + 3, base + 0, next_base + 3])
        faces.append([next_base + 3, base + 0, next_base + 0])
    
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
    
    print(f"✅ Tapered Ring Band Created:")
    print(f"   US Size: {ring_size_us}")
    print(f"   Inner Diameter: {inner_diameter:.2f} mm")
    print(f"   Thickness (top): {thickness_top:.2f} mm")
    print(f"   Thickness (bottom): {thickness_bottom:.2f} mm")
    print(f"   Taper: {thickness_bottom - thickness_top:.2f} mm increase toward inner")
    
    return mesh


if __name__ == "__main__":
    print("=" * 60)
    print("💍 Ring Band Generator - US Standard Sizes")
    print("=" * 60)
    
    # Example 1: Basic uniform band
    print("\n1. Basic Ring Band (US Size 8):")
    ring1 = create_ring_band(
        ring_size_us=8,
        thickness_outer=2.0,
        thickness_inner=2.0,
        band_width=3.0
    )
    ring1.export('output/ring_band_size8.glb')
    print("   Saved: output/ring_band_size8.glb")
    
    # Example 2: Tapered band (thicker toward palm)
    print("\n2. Tapered Ring Band (US Size 9):")
    ring2 = create_tapered_ring_band(
        ring_size_us=9,
        thickness_top=1.8,
        thickness_bottom=2.5,
        band_width=4.0
    )
    ring2.export('output/ring_band_tapered_size9.glb')
    print("   Saved: output/ring_band_tapered_size9.glb")
    
    # Example 3: Size comparison
    print("\n3. Generating size comparison (7, 8, 9, 10):")
    for size in [7, 8, 9, 10]:
        ring = create_ring_band(
            ring_size_us=size,
            thickness_outer=2.0,
            thickness_inner=2.0,
            band_width=3.0
        )
        ring.export(f'output/ring_band_size{size}.glb')
        print(f"   Saved: output/ring_band_size{size}.glb")
    
    print("\n" + "=" * 60)
    print("✨ All ring bands generated!")
    print("=" * 60)
