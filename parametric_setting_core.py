"""
Parametric stone setting generator (trimesh + numpy)

Outputs two GLB files:
 - designer: includes the stone (for visualization)
 - production: no stone, prongs taller, attempts to be watertight

Requires:
    pip install trimesh numpy pygltflib
"""

import numpy as np
import trimesh
from trimesh.exchange import gltf


# -----------------------
# Helper geometry builders
# -----------------------
def create_frustum(radius_bottom, radius_top, height, sections=48):
    """
    Create a conical frustum (axis along +Z), centered on XY at base z=0.
    Returns a trimesh.Trimesh mesh.
    """
    theta = np.linspace(0, 2*np.pi, sections, endpoint=False)
    cb = np.column_stack([radius_bottom * np.cos(theta), radius_bottom * np.sin(theta), np.zeros_like(theta)])
    ct = np.column_stack([radius_top * np.cos(theta), radius_top * np.sin(theta), np.full_like(theta, height)])
    vertices = np.vstack([cb, ct, [0,0,0], [0,0,height]])  # add base & top centers
    nb = len(cb)
    faces = []

    base_center = 2*nb
    top_center = 2*nb + 1

    # side faces
    for i in range(nb):
        i2 = (i + 1) % nb
        a = i
        b = i2
        c = nb + i
        d = nb + i2
        faces.append([a, c, b])
        faces.append([b, c, d])
    # base cap (triangles)
    for i in range(nb):
        i2 = (i + 1) % nb
        faces.append([base_center, i2, i])
    # top cap
    for i in range(nb):
        i2 = (i + 1) % nb
        faces.append([top_center, nb + i, nb + i2])

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    mesh.remove_duplicate_faces()
    mesh.remove_unreferenced_vertices()
    mesh.process()  # run basic repair
    return mesh

def create_round_stone(diameter_x, diameter_y, depth, sections=64):
    """
    Approximate a round gemstone as a sphere-like ellipsoid scaled to (diameter_x, diameter_y, depth).
    Centered with bottom at z=0 (so z extent from 0 to depth).
    """
    # create a unit sphere and scale
    sphere = trimesh.creation.icosphere(subdivisions=4, radius=0.5)  # radius .5 so diameter == 1
    # scale to desired diameters (x,y) and depth
    sx = diameter_x
    sy = diameter_y
    sz = depth
    sphere.apply_scale([sx, sy, sz])
    # move sphere so bottom rests at z=0 (sphere's centroid at origin; extents/2 below)
    minz = sphere.bounds[0,2]
    sphere.apply_translation([0,0,-minz])
    return sphere

def create_prism_box(length, width, height):
    box = trimesh.creation.box(extents=(length, width, height))
    # box is centered; move bottom to z=0
    minz = box.bounds[0,2]
    box.apply_translation([0,0,-minz])
    return box

def create_claw_cluster(base_angle, base_radius, *, count=4, spread_deg=30.0,
                        length=6.0, base_diameter=1.2, tip_diameter=0.6,
                        tilt_z_factor=0.25, sections=24):
    claws = []

    # rim point (anchor)
    bx = base_radius * np.cos(base_angle)
    by = base_radius * np.sin(base_angle)
    rim_point = np.array([bx, by, 0.0])
    center_point = np.array([0.0, 0.0, 0.0])

    # spread angles
    if count > 1:
        step = np.deg2rad(spread_deg) / (count - 1)
        start_offset = -0.5 * np.deg2rad(spread_deg)
    else:
        step = 0.0
        start_offset = 0.0

    for i in range(count):
        ang_off = start_offset + i * step

        # radial vector toward ring center
        radial_dir = center_point - rim_point
        radial_dir[:2] = rotate_2d(radial_dir[:2], ang_off)  # fan spread
        radial_dir[2] = tilt_z_factor * length  # slight upward tilt
        v = radial_dir / np.linalg.norm(radial_dir)

        # create frustum with base at origin
        fr = create_frustum(base_diameter, tip_diameter, length, sections=sections)
        # move frustum so base sits at origin
        fr.apply_translation([0, 0, length/2])

        # rotation from +Z to v
        z_axis = np.array([0,0,1])
        axis = np.cross(z_axis, v)
        axis_len = np.linalg.norm(axis)
        if axis_len < 1e-9:
            rot = np.eye(4)
        else:
            axis /= axis_len
            angle = np.arccos(np.clip(np.dot(z_axis, v), -1.0, 1.0))
            rot = trimesh.transformations.rotation_matrix(angle, axis)

        fr.apply_transform(rot)
        # translate base to rim anchor
        fr.apply_translation(rim_point)

        claws.append(fr)

    return claws

def rotate_2d(vec, angle_rad):
    """Rotate a 2D vector by angle (radians)."""
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    x, y = vec
    return np.array([c*x - s*y, s*x + c*y])


def create_ring_base(outer_radius, inner_radius, height, ring_penetration=0.2, sections=64, profile='rounded', ring_tube_radius=None):
    """
    Create a ring (torus-like) base with a hole in the middle for finger.
    outer_radius: outer edge of the ring
    inner_radius: inner hole radius (for finger)
    height: thickness of the ring band
    """
    # If a rounded/tubular profile is requested, delegate to the rounded ring
    # builder which creates a torus-like solid band (non-hollow feeling).
    if profile and profile.lower() in ('rounded', 'round', 'torus', 'tubular'):
        return create_rounded_ring(outer_radius, inner_radius, height, ring_penetration=ring_penetration, sections=sections, tube_radius=ring_tube_radius)

    # Create outer cylinder (centered at origin), then translate so the top of
    # the band sits slightly below z=0 (negative) so prong bases placed at z=0
    # will overlap the band by RING_PENETRATION.
    outer = trimesh.creation.cylinder(radius=outer_radius, height=height, sections=sections)
    inner = trimesh.creation.cylinder(radius=inner_radius, height=height, sections=sections)

    # Translate both so band top is at z = -ring_penetration
    translate_z = -ring_penetration - (height / 2.0)
    outer.apply_translation([0, 0, translate_z])
    inner.apply_translation([0, 0, translate_z])

    # Subtract inner from outer to create ring
    try:
        ring = outer.difference(inner)
        if ring is None or len(ring.vertices) == 0:
            # If boolean operation fails, create manual ring
            return create_manual_ring(outer_radius, inner_radius, height, ring_penetration=ring_penetration, sections=sections)
        return ring
    except Exception:
        # Fallback to manual ring creation
        return create_manual_ring(outer_radius, inner_radius, height, ring_penetration=ring_penetration, sections=sections)

def create_manual_ring(outer_radius, inner_radius, height, ring_penetration=0.2, sections=64):
    """
    Manually create ring geometry when boolean operations fail
    """
    theta = np.linspace(0, 2*np.pi, sections, endpoint=False)
    
    # Outer ring vertices (bottom and top)
    outer_bottom = np.column_stack([outer_radius * np.cos(theta), outer_radius * np.sin(theta), np.zeros_like(theta)])
    outer_top = np.column_stack([outer_radius * np.cos(theta), outer_radius * np.sin(theta), np.full_like(theta, height)])
    
    # Inner ring vertices (bottom and top)  
    inner_bottom = np.column_stack([inner_radius * np.cos(theta), inner_radius * np.sin(theta), np.zeros_like(theta)])
    inner_top = np.column_stack([inner_radius * np.cos(theta), inner_radius * np.sin(theta), np.full_like(theta, height)])
    
    # Combine all vertices
    vertices = np.vstack([outer_bottom, outer_top, inner_bottom, inner_top])
    
    n = sections
    faces = []
    
    # Top surface (ring face)
    for i in range(n):
        i2 = (i + 1) % n
        # Outer triangle
        faces.append([i + n, i2 + n, i2 + 3*n])
        # Inner triangle  
        faces.append([i + n, i2 + 3*n, i + 3*n])
    
    # Bottom surface (ring face)
    for i in range(n):
        i2 = (i + 1) % n
        # Outer triangle
        faces.append([i, i2 + 2*n, i2])
        # Inner triangle
        faces.append([i, i + 2*n, i2 + 2*n])
    
    # Outer curved surface
    for i in range(n):
        i2 = (i + 1) % n
        faces.append([i, i + n, i2])
        faces.append([i2, i + n, i2 + n])
    
    # Inner curved surface
    for i in range(n):
        i2 = (i + 1) % n
        faces.append([i + 2*n, i2 + 2*n, i + 3*n])
        faces.append([i2 + 2*n, i2 + 3*n, i + 3*n])
    
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    mesh.remove_duplicate_faces()
    mesh.remove_unreferenced_vertices()
    # Shift mesh so the top of the band sits slightly below z=0 to allow
    # prong bases placed at z=0 to overlap and avoid visible gap.
    # Shift mesh so the top of the band sits slightly below z=0 to allow
    # prong bases placed at z=0 to overlap and avoid visible gap.
    mesh.apply_translation([0, 0, -height - ring_penetration])
    mesh.process()
    return mesh


def create_rounded_ring(outer_radius, inner_radius, height, ring_penetration=0.2, sections=128, segments=32, tube_radius=None):
    """
    Create a rounded (torus-like) ring band. Produces a tubular band whose
    major radius is the mean of outer/inner and minor radius (tube_radius)
    controls the curvature. If tube_radius is None it is derived from the
    gap between outer and inner radii.
    """
    # compute major/minor
    mean_r = (outer_radius + inner_radius) / 2.0
    # allow explicit tube radius (curvature) to be provided; otherwise derive
    if tube_radius is None:
        tube_r = max((outer_radius - inner_radius) / 2.0, 0.1)
    else:
        tube_r = max(float(tube_radius), 0.01)

    # Ensure the tube radius is large enough to span the radial gap between
    # inner and outer radii; otherwise there will be visible spaces at some
    # angles where the torus cross-section doesn't reach the inner wall.
    radial_gap = (outer_radius - inner_radius) / 2.0
    # If tube_radius was not provided, derive it to fill the radial gap and
    # approximately match the requested vertical thickness.
    if tube_radius is None:
        # prefer a tube radius that at least equals the radial gap; also try
        # to respect half the requested height so the band looks visually
        # consistent.
        tube_r = max(radial_gap, height / 2.0, 0.1)
    else:
        tube_r = max(float(tube_radius), radial_gap, 0.01)

    try:
        # trimesh has a torus builder in many versions
        tor = trimesh.creation.torus(radius=mean_r, tube_radius=tube_r, sections=sections, segments=segments)
        # Position torus horizontally at Z=0 (center of torus at Z=0)
        # No translation needed - torus is already centered at origin
        # This creates a horizontal tubular ring in the XY plane
        tor.process()
        return tor
    except Exception:
        # fallback: approximate torus by revolving a circle profile (manual lathe)
        theta = np.linspace(0, 2*np.pi, sections, endpoint=False)
        phi = np.linspace(0, 2*np.pi, segments, endpoint=False)
        verts = []
        faces = []
        for i, t in enumerate(theta):
            center_x = mean_r * np.cos(t)
            center_y = mean_r * np.sin(t)
            for j, p in enumerate(phi):
                x = center_x + tube_r * np.cos(p) * np.cos(t)
                y = center_y + tube_r * np.cos(p) * np.sin(t)
                z = tube_r * np.sin(p)
                verts.append([x, y, z])
        verts = np.array(verts)
        n_theta = len(theta)
        n_phi = len(phi)
        for i in range(n_theta):
            for j in range(n_phi):
                a = i * n_phi + j
                b = ((i + 1) % n_theta) * n_phi + j
                c = ((i + 1) % n_theta) * n_phi + ((j + 1) % n_phi)
                d = i * n_phi + ((j + 1) % n_phi)
                faces.append([a, b, d])
                faces.append([b, c, d])

        mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
        # For the manual lathe fallback use the same tube_r-derived translation
        mesh.apply_translation([0, 0, -(tube_r + ring_penetration)])
        mesh.remove_duplicate_faces()
        mesh.remove_unreferenced_vertices()
        mesh.process()
        return mesh

def create_prong_base(base_style, prong_positions, base_width, base_height, gallery_radius=None, ring_penetration=0.2):
    """
    Create prong base connections based on style
    base_style: 'individual', 'shared', 'gallery'
    prong_positions: list of [x, y] positions for prongs
    """
    base_meshes = []
    
    if base_style == 'individual':
        # Each prong gets its own cylindrical base
        for pos in prong_positions:
            base_cylinder = trimesh.creation.cylinder(
                radius=base_width/2, 
                height=base_height, 
                sections=16
            )
            # Position cylinder so its top sits at z=0 (so it overlaps ring band)
            base_cylinder.apply_translation([pos[0], pos[1], -base_height/2])
            base_meshes.append(base_cylinder)
    
    elif base_style == 'shared':
        # Create connection between adjacent prongs
        for i in range(len(prong_positions)):
            pos1 = prong_positions[i]
            pos2 = prong_positions[(i + 1) % len(prong_positions)]
            
            # Create a connecting bridge between prongs
            midpoint = [(pos1[0] + pos2[0])/2, (pos1[1] + pos2[1])/2]
            distance = np.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)
            
            # Create rectangular connector
            connector = trimesh.creation.box(extents=[distance, base_width, base_height])
            
            # Calculate rotation angle
            angle = np.arctan2(pos2[1] - pos1[1], pos2[0] - pos1[0])
            rotation_matrix = trimesh.transformations.rotation_matrix(angle, [0, 0, 1])
            
            connector.apply_transform(rotation_matrix)
            connector.apply_translation([midpoint[0], midpoint[1], -base_height/2])
            base_meshes.append(connector)
    
    elif base_style == 'gallery':
        # Create a gallery rail (ring) connecting all prongs
        if gallery_radius is None:
            # Calculate radius based on prong positions
            distances = [np.sqrt(pos[0]**2 + pos[1]**2) for pos in prong_positions]
            gallery_radius = np.mean(distances)
        
        # Create gallery ring
        gallery_ring = trimesh.creation.cylinder(
            radius=gallery_radius, 
            height=base_height,
            sections=64
        )
        
        # Create inner hole (make it a rail, not solid)
        inner_radius = gallery_radius - base_width
        if inner_radius > 0:
            inner_hole = trimesh.creation.cylinder(
                radius=inner_radius,
                height=base_height * 2,
                sections=64
            )
            inner_hole.apply_translation([0, 0, -base_height/2])

            try:
                gallery_ring = gallery_ring.difference(inner_hole)
                if gallery_ring is None:
                    # Fallback to solid ring if boolean fails
                    gallery_ring = trimesh.creation.cylinder(radius=gallery_radius, height=base_height, sections=64)
            except:
                # Fallback to solid ring
                gallery_ring = trimesh.creation.cylinder(radius=gallery_radius, height=base_height, sections=64)

            # Position gallery top slightly below z=0 to overlap prong bases
            gallery_ring.apply_translation([0, 0, -ring_penetration - (base_height / 2.0)])
            base_meshes.append(gallery_ring)
    
    return base_meshes

# -----------------------
# Main generator
# -----------------------
def generate_stone_setting(
    *,
    stone_shape='round',            # 'round', 'princess', 'radiant'
    stone_length=6.0,               # mm (x dimension)
    stone_width=6.0,                # mm (y dimension)
    stone_depth=4.0,                # mm (z dimension)
    prong_count=4,                  # 2,4,6,8
    prong_thickness_base=0.8,       # mm (diameter)
    prong_thickness_top=0.5,        # mm (diameter)
    setting_height=3.5,             # mm (visible height from bezel base)
    prong_base_style='individual',  # 'individual', 'shared', 'gallery'
    prong_base_width=1.2,           # mm (width of prong base connection)
    prong_base_height=1.0,          # mm (height of prong base/gallery)
    gallery_radius=None,            # mm (radius for gallery rail, auto if None)
    base_type='minimal',            # 'minimal', 'ring', 'none'
    ring_outer_radius=8.5,          # mm (outer edge of ring) - only if base_type='ring'
    ring_inner_radius=5.0,          # mm (finger hole radius) - only if base_type='ring'
    ring_thickness=2.0,             # mm (ring band thickness) - only if base_type='ring'
    ring_penetration=0.2,           # mm penetration so prong bases overlap ring
    ring_profile='rounded',         # 'flat' or 'rounded' (tubular) band profile
    ring_tube_radius=None,          # mm tube radius for rounded profile (None => auto)
    # optional rim claw cluster (fan) parameters
    rim_claw_cluster=False,
    rim_claw_count=4,
    rim_claw_spread_deg=30.0,
    rim_claw_length=6.0,
    rim_claw_base_diameter=1.2,
    rim_claw_tip_diameter=0.6,
    rim_claw_tilt_z_factor=0.25,
    rim_claw_base_angle_deg=0.0,
    prong_height_extension_factor=0.8,
    designer_filename='setting_designer.glb',
    production_filename='setting_production.glb',
    prong_taper_sections=36,
    production_prong_extra=1.5,     # mm extra prong height for production
    **kwargs
):
    """
    Build the setting meshes and export two GLB files.

    Returns tuple (designer_path, production_path).
    """
    print(f"\n{'='*60}")
    print(f"GENERATE STONE SETTING CALLED")
    print(f"kwargs = {kwargs}")
    print(f"{'='*60}\n")
    
    # ---- Stone mesh (designer only) ----
    if stone_shape.lower() == 'round':
        stone = create_round_stone(stone_length, stone_width, stone_depth)
    elif stone_shape.lower() in ('princess', 'radiant'):
        # approximate as a rectangular pavilion (box) centered on XY with bottom at z=0
        stone = create_prism_box(stone_length, stone_width, stone_depth)
        # optionally bevel/scale for radiant/princess characteristics (simple scale top)
        if stone_shape.lower() == 'radiant':
            # scale Z-top slightly to make a more "cut" look: scale top vertices
            verts = stone.vertices.copy()
            zmax = verts[:,2].max()
            top_mask = verts[:,2] > (zmax * 0.5)
            verts[top_mask,0:2] *= 0.9
            stone = trimesh.Trimesh(vertices=verts, faces=stone.faces, process=True)
    else:
        raise ValueError("Unsupported stone shape")

    # color the stone for designer export
    stone.visual.vertex_colors = np.tile(np.array([100,160,255,220]), (len(stone.vertices),1))
    
    # Name the stone for identification in editors
    stone.metadata['name'] = 'Stone'
    
    # NEW LAYOUT: Stone positioned ABOVE ring (not at center)
    # Stone rotation: X=90° to orient it correctly
    # Position: Y = slightly above ring outer diameter, Z = same as ring center
    stone_rotation = trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0])
    stone.apply_transform(stone_rotation)
    
    # Ring center is at z=0 for tubular ring, stone sits at same Z, but Y slightly above ring diameter
    stone_x_position = 0
    stone_y_position = ring_outer_radius + 0.5  # Just 0.5mm above ring outer radius
    stone_z_position = 0  # Same Z as ring center (horizontal alignment)
    
    stone.apply_translation([stone_x_position, stone_y_position, stone_z_position])
    
    # Print coordinate information
    print("\n=== OBJECT COORDINATES ===")
    print(f"Ring outer radius: {ring_outer_radius:.2f} mm")
    print(f"Ring center: (0, 0, 0) mm - Tubular horizontal orientation")
    print(f"Stone position: ({stone_x_position:.2f}, {stone_y_position:.2f}, {stone_z_position:.2f}) mm")
    print(f"Stone rotation: X=90° (oriented perpendicular)")
    print(f"Stone Y offset from ring: {stone_y_position:.2f} mm (above outer rim)")
    print("=========================\n")

    # ---- Prong generation ----
    # NEW: Prongs connect horizontally from stone sides to ring seamlessly
    # Stone is rotated 90° (lying on its side), so its perimeter is in XZ plane
    # Ring is horizontal torus at Y=0
    # Prongs connect from stone perimeter (at Y=stone_y_position) to ring surface (at Y≈0)
    prong_count = 4  # Default 4 prongs for symmetric connection
    angles = [i * (2 * np.pi / prong_count) for i in range(prong_count)]
    
    # Calculate prong positions for base creation
    prong_positions = []
    prongs = []
    debug_markers = bool(kwargs.get('debug_markers', False))
    debug_single_prong = bool(kwargs.get('debug_single_prong', False))
    
    print(f"DEBUG: debug_markers = {debug_markers}")
    print(f"DEBUG: debug_single_prong = {debug_single_prong}")
    print(f"DEBUG: Generating {prong_count} prongs connecting stone to ring")
    
    # Stone perimeter calculations (stone is rotated 90° around X)
    # After rotation, stone's "width" becomes its extent in X direction
    # and "length" becomes its extent in Z direction
    stone_radius_x = stone_width / 2.0  # horizontal extent
    stone_radius_z = stone_length / 2.0  # vertical extent (when rotated)
    
    for i, ang in enumerate(angles):
        # Prong START point: on stone perimeter (stone is at Y=stone_y_position)
        # Stone perimeter is in XZ plane (since stone is rotated 90° around X)
        prong_start_x = stone_radius_x * np.cos(ang)
        prong_start_y = stone_y_position  # stone's Y position
        prong_start_z = stone_radius_z * np.sin(ang)
        
        # Prong END point: on ring surface (ring is horizontal torus at Y≈0, Z=0)
        # Ring major radius is ring_outer_radius
        prong_end_x = ring_outer_radius * np.cos(ang)
        prong_end_y = 0.0  # ring is at Y=0
        prong_end_z = ring_outer_radius * np.sin(ang)
        
        # Store position for prong base creation (using XY coordinates at ring level)
        prong_positions.append([prong_end_x, prong_end_y])
        
        # Create prong as cylinder connecting start to end points
        # Calculate prong length and direction
        start_point = np.array([prong_start_x, prong_start_y, prong_start_z])
        end_point = np.array([prong_end_x, prong_end_y, prong_end_z])
        prong_vector = end_point - start_point
        prong_length = np.linalg.norm(prong_vector)
        prong_direction = prong_vector / (prong_length + 1e-12)
        
        # Create prong geometry (tapered cylinder)
        r_bottom = prong_thickness_base / 2.0
        r_top = prong_thickness_top / 2.0
        
        prong_mesh = create_frustum(r_bottom, r_top, prong_length, sections=prong_taper_sections)
        
        # Orient prong from start to end point
        # Default frustum is along Z-axis, need to rotate to prong_direction
        z_axis = np.array([0.0, 0.0, 1.0])
        axis = np.cross(z_axis, prong_direction)
        axis_len = np.linalg.norm(axis)
        
        if axis_len < 1e-9:
            # Parallel or anti-parallel - no rotation needed or 180° flip
            if prong_direction[2] < 0:
                rot = trimesh.transformations.rotation_matrix(np.pi, [1.0, 0.0, 0.0])
                prong_mesh.apply_transform(rot)
        else:
            axis = axis / axis_len
            angle = np.arccos(np.clip(np.dot(z_axis, prong_direction), -1.0, 1.0))
            rot = trimesh.transformations.rotation_matrix(angle, axis)
            prong_mesh.apply_transform(rot)
        
        # Position prong at start point (frustum base is at origin, centered)
        prong_center = start_point + prong_direction * (prong_length / 2.0)
        prong_mesh.apply_translation(prong_center)
        
        # Name the prong for identification
        prong_mesh.metadata['name'] = f'Prong_{i+1}'
        prongs.append(prong_mesh)
        
        # Optional debug markers to visualize prong endpoints
        if debug_markers:
            try:
                # Start point marker (red)
                start_marker = trimesh.creation.icosphere(subdivisions=2, radius=0.15)
                start_marker.apply_translation(start_point)
                start_marker.visual.vertex_colors = np.tile(np.array([255,0,0,255]), (len(start_marker.vertices),1))
                prongs.append(start_marker)
                
                # End point marker (green)
                end_marker = trimesh.creation.icosphere(subdivisions=2, radius=0.15)
                end_marker.apply_translation(end_point)
                end_marker.visual.vertex_colors = np.tile(np.array([0,255,0,255]), (len(end_marker.vertices),1))
                prongs.append(end_marker)
            except Exception:
                pass
    
    
    # Create prong bases
    if gallery_radius is None:
        # Auto-calculate gallery radius
        gallery_radius = np.mean([np.sqrt(pos[0]**2 + pos[1]**2) for pos in prong_positions])
    
    prong_bases = create_prong_base(
        prong_base_style, 
        prong_positions, 
        prong_base_width, 
        prong_base_height,
        gallery_radius,
        ring_penetration=ring_penetration
    )

    # Create base according to type
    base_meshes = []
    if base_type == 'ring':
        # Full ring base (with hole for finger)
        ring_base = create_ring_base(ring_outer_radius, ring_inner_radius, ring_thickness, ring_penetration=ring_penetration, sections=64, profile=ring_profile, ring_tube_radius=ring_tube_radius)
        ring_base.metadata['name'] = 'Ring_Base'
        # ring already positioned with its top slightly below z=0 in create_ring_base
        base_meshes.append(ring_base)
        # optional rim claw cluster attached to the ring rim
        if rim_claw_cluster:
            base_angle = np.deg2rad(rim_claw_base_angle_deg)
            # anchor slightly outside the exact outer radius to sit on rim
            anchor_radius = max(0.0, ring_outer_radius - 0.01)
            claws = create_claw_cluster(base_angle, anchor_radius, count=int(rim_claw_count), spread_deg=float(rim_claw_spread_deg), length=float(rim_claw_length), base_diameter=float(rim_claw_base_diameter), tip_diameter=float(rim_claw_tip_diameter), tilt_z_factor=float(rim_claw_tilt_z_factor), sections=prong_taper_sections)
            # add claws to designer meshes (they will be included in production separately)
            for c in claws:
                base_meshes.append(c)
    elif base_type == 'minimal':
        # Small circular platform just to connect prongs
        base_thickness = 0.6
        base_radius = max(stone_length, stone_width) / 2.0 + 1.0
        minimal_base = trimesh.creation.cylinder(radius=base_radius, height=base_thickness, sections=32)
        # Make minimal base top sit slightly below z=0 so prongs overlap
        minimal_base.apply_translation([0, 0, - (base_thickness / 2.0) - ring_penetration])
        base_meshes.append(minimal_base)
    # if base_type == 'none', no base is created

    # designer scene: stone + prongs + prong_bases + base (if any)
    designer_meshes = base_meshes + prong_bases + prongs + [stone]
    
    # Add coordinate axes for debugging (if debug_markers enabled)
    axis_meshes = []
    if debug_markers:
        print("DEBUG: Creating coordinate axes and reference planes...")
        axis_length = max(ring_outer_radius * 2, 15.0)
        print(f"DEBUG: Axis length = {axis_length:.2f} mm")
        
        # X-axis (red) - horizontal
        x_axis = trimesh.creation.cylinder(radius=0.15, height=axis_length, sections=8)
        x_axis.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
        x_axis.apply_translation([axis_length/2, 0, 0])
        axis_meshes.append(x_axis)
        
        # Y-axis (green) - horizontal
        y_axis = trimesh.creation.cylinder(radius=0.15, height=axis_length, sections=8)
        y_axis.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
        y_axis.apply_translation([0, axis_length/2, 0])
        axis_meshes.append(y_axis)
        
        # Z-axis (blue) - vertical
        z_axis = trimesh.creation.cylinder(radius=0.15, height=axis_length, sections=8)
        z_axis.apply_translation([0, 0, axis_length/2])
        axis_meshes.append(z_axis)
        
        # Origin marker (white sphere)
        origin = trimesh.creation.icosphere(subdivisions=2, radius=0.4)
        axis_meshes.append(origin)
        
        # Horizontal plane (XY plane at z=0) - semi-transparent gray
        plane_size = axis_length * 0.8
        horizontal_plane = trimesh.creation.box(extents=[plane_size, plane_size, 0.05])
        horizontal_plane.apply_translation([0, 0, 0])
        axis_meshes.append(horizontal_plane)
        
        # Vertical plane (XZ plane at y=0) - semi-transparent cyan
        vertical_plane_xz = trimesh.creation.box(extents=[plane_size, 0.05, plane_size])
        vertical_plane_xz.apply_translation([0, 0, plane_size/2])
        axis_meshes.append(vertical_plane_xz)
        
        # Ring top reference plane (at z = -ring_penetration)
        ring_plane = trimesh.creation.box(extents=[plane_size, plane_size, 0.05])
        ring_plane.apply_translation([0, 0, -ring_penetration])
        axis_meshes.append(ring_plane)
        
        print(f"DEBUG: Horizontal plane (XY) at z = 0.00 mm")
        print(f"DEBUG: Vertical plane (XZ) at y = 0.00 mm")
        print(f"DEBUG: Ring top plane at z = {-ring_penetration:.2f} mm")
    
    # color base and prongs (metal)
    for m in designer_meshes:
        if m is stone:
            continue
        m.visual.vertex_colors = np.tile(np.array([200,190,170,255]), (len(m.vertices),1))
    
    # Color axis meshes separately to avoid conflict
    if debug_markers and len(axis_meshes) >= 7:
        axis_meshes[0].visual.vertex_colors = np.tile(np.array([255, 0, 0, 255]), (len(axis_meshes[0].vertices), 1))    # X red
        axis_meshes[1].visual.vertex_colors = np.tile(np.array([0, 255, 0, 255]), (len(axis_meshes[1].vertices), 1))    # Y green
        axis_meshes[2].visual.vertex_colors = np.tile(np.array([0, 0, 255, 255]), (len(axis_meshes[2].vertices), 1))    # Z blue
        axis_meshes[3].visual.vertex_colors = np.tile(np.array([255, 255, 255, 255]), (len(axis_meshes[3].vertices), 1)) # Origin white
        axis_meshes[4].visual.vertex_colors = np.tile(np.array([128, 128, 128, 100]), (len(axis_meshes[4].vertices), 1)) # Horizontal plane gray
        axis_meshes[5].visual.vertex_colors = np.tile(np.array([0, 255, 255, 100]), (len(axis_meshes[5].vertices), 1))   # Vertical plane cyan
        axis_meshes[6].visual.vertex_colors = np.tile(np.array([255, 200, 0, 100]), (len(axis_meshes[6].vertices), 1))   # Ring plane yellow
        designer_meshes.extend(axis_meshes)

    # Build designer scene
    scene_designer = trimesh.Scene(designer_meshes)
    
    # Export to GLB and ensure it's glTF 2.0 compatible
    glb_bytes = scene_designer.export(file_type='glb')
    
    # Post-process to fix glTF version if needed
    try:
        from pygltflib import GLTF2, Asset
        import tempfile
        import os
        
        # Write to temp file, load, fix, and re-save
        with tempfile.NamedTemporaryFile(delete=False, suffix='.glb') as tmp:
            tmp.write(glb_bytes)
            tmp_path = tmp.name
        
        # Load and fix version
        gltf = GLTF2.load(tmp_path)
        
        # Ensure asset exists and set version
        if gltf.asset is None:
            gltf.asset = Asset(version="2.0", generator="Trimesh + Python")
        else:
            gltf.asset.version = "2.0"
            if not hasattr(gltf.asset, 'generator') or not gltf.asset.generator:
                gltf.asset.generator = "Trimesh + Python"
        
        # Save to final destination
        gltf.save_binary(designer_filename)
        
        # Clean up temp file
        os.unlink(tmp_path)
        print("Saved designer GLB (glTF 2.0):", designer_filename)
    except Exception as e:
        print(f"Note: GLB post-processing failed ({e}), using original")
        with open(designer_filename, 'wb') as f:
            f.write(glb_bytes)
        print("Saved designer GLB:", designer_filename)

    # ---------------------
    # production version
    # ---------------------
    # production prongs (height increased and extra for manufacturing)
    prongs_prod = []
    for i, ang in enumerate(angles):
        # use prong anchor positions calculated earlier so ring-base anchors are respected
        cx, cy = prong_positions[i]
        r_bottom = prong_thickness_base / 2.0
        r_top = prong_thickness_top / 2.0

        # compute stone radius at this angle (same logic as designer) to extend prong
        a = stone_length / 2.0
        b = stone_width / 2.0
        if stone_shape.lower() == 'round':
            denom = np.sqrt((b * np.cos(ang))**2 + (a * np.sin(ang))**2)
            if denom > 1e-9:
                stone_radius_at_angle = (a * b) / denom
            else:
                stone_radius_at_angle = max(a, b)
        else:
            cosang = abs(np.cos(ang))
            sinang = abs(np.sin(ang))
            t_x = a / cosang if cosang > 1e-9 else float('inf')
            t_y = b / sinang if sinang > 1e-9 else float('inf')
            stone_radius_at_angle = min(t_x, t_y)

        current_anchor_radius = np.sqrt(cx*cx + cy*cy)
        stone_gap = max(0.0, current_anchor_radius - stone_radius_at_angle)
        extra_height = stone_gap * prong_height_extension_factor

        prong_height_prod = setting_height + production_prong_extra + extra_height

        fr = create_frustum(r_bottom, r_top, prong_height_prod, sections=prong_taper_sections)
        # place at rim top (prong base z)
        base_z = 0.0
        fr.apply_translation([cx, cy, base_z])

        # Aim toward the stone top for production prongs
        stone_target_z = max(0.5, stone_depth * 0.75)
        anchor = np.array([cx, cy, base_z])
        target = np.array([0.0, 0.0, stone_target_z]) - anchor
        target = target / (np.linalg.norm(target) + 1e-12)
        axis = np.cross(np.array([0, 0, 1]), target)
        axis_len = np.linalg.norm(axis)
        if axis_len < 1e-9:
            rot = np.eye(4)
        else:
            axis /= axis_len
            angle = np.arccos(np.clip(np.dot([0, 0, 1], target), -1, 1))
            rot = trimesh.transformations.rotation_matrix(angle, axis)
            fr.apply_translation(-np.array([cx, cy, base_z]))
            fr.apply_transform(rot)
            fr.apply_translation(np.array([cx, cy, base_z]))

        # Make small cut at underside for better seating - here just ensure base sits flush (no boolean)
        prongs_prod.append(fr)
    
    # Create prong bases for production (same as designer)
    prong_bases_prod = create_prong_base(
        prong_base_style, 
        prong_positions, 
        prong_base_width, 
        prong_base_height * 1.1,  # Slightly taller for production
        gallery_radius,
        ring_penetration=ring_penetration
    )

    # production base (slightly thicker for manufacturing)
    base_prod_meshes = []
    if base_type == 'ring':
        ring_base_prod = create_ring_base(ring_outer_radius, ring_inner_radius, ring_thickness * 1.1, ring_penetration=ring_penetration, sections=64, profile=ring_profile, ring_tube_radius=ring_tube_radius)
        # create_ring_base already positions the ring with slight penetration
        base_prod_meshes.append(ring_base_prod)
        # add production claws (slightly longer/taller for manufacturing)
        if rim_claw_cluster:
            base_angle = np.deg2rad(rim_claw_base_angle_deg)
            anchor_radius = max(0.0, ring_outer_radius - 0.01)
            claws_prod = create_claw_cluster(base_angle, anchor_radius, count=int(rim_claw_count), spread_deg=float(rim_claw_spread_deg), length=float(rim_claw_length) + 1.5, base_diameter=float(rim_claw_base_diameter), tip_diameter=float(rim_claw_tip_diameter), tilt_z_factor=float(rim_claw_tilt_z_factor), sections=prong_taper_sections)
            for c in claws_prod:
                base_prod_meshes.append(c)
    elif base_type == 'minimal':
        base_thickness = 0.6
        base_radius = max(stone_length, stone_width) / 2.0 + 1.0
        minimal_base_prod = trimesh.creation.cylinder(radius=base_radius, height=base_thickness*1.1, sections=32)
        minimal_base_prod.apply_translation([0, 0, - (base_thickness*1.1 / 2.0) - ring_penetration])
        base_prod_meshes.append(minimal_base_prod)

    # Attempt to boolean-union ring + prong bases + prongs to create a single
    # watertight production mesh. Boolean ops can be slow and sometimes fail,
    # so fallback to simple concatenation if necessary.
    try:
        # try union of all production pieces
        pieces_to_union = []
        for m in base_prod_meshes + prong_bases_prod:
            pieces_to_union.append(m)
        # add prongs as separate mesh pieces
        for p in prongs_prod:
            pieces_to_union.append(p)

        unioned = trimesh.boolean.union(pieces_to_union, engine='scad')
        if unioned is None:
            # try another engine fallback
            unioned = trimesh.boolean.union(pieces_to_union)
        if unioned is not None:
            all_prod = unioned
            all_prod.process()
        else:
            # fallback concatenate
            all_prod = trimesh.util.concatenate(base_prod_meshes + prong_bases_prod + prongs_prod)
            all_prod.process()
    except Exception as e:
        print(f"Boolean union failed ({e}), falling back to concatenation")
        all_prod = trimesh.util.concatenate(base_prod_meshes + prong_bases_prod + prongs_prod)
        try:
            all_prod.process()
        except Exception:
            pass

    # Export production GLB
    scene_prod = trimesh.Scene([all_prod])
    glb_bytes_p = scene_prod.export(file_type='glb')
    
    # Post-process to fix glTF version if needed
    try:
        from pygltflib import GLTF2, Asset
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.glb') as tmp:
            tmp.write(glb_bytes_p)
            tmp_path = tmp.name
        
        gltf_prod = GLTF2.load(tmp_path)
        
        # Ensure asset exists and set version
        if gltf_prod.asset is None:
            gltf_prod.asset = Asset(version="2.0", generator="Trimesh + Python")
        else:
            gltf_prod.asset.version = "2.0"
            if not hasattr(gltf_prod.asset, 'generator') or not gltf_prod.asset.generator:
                gltf_prod.asset.generator = "Trimesh + Python"
        
        gltf_prod.save_binary(production_filename)
        os.unlink(tmp_path)
        print("Saved production GLB (glTF 2.0):", production_filename)
    except Exception as e:
        print(f"Note: Production GLB post-processing failed ({e}), using original")
        with open(production_filename, 'wb') as f:
            f.write(glb_bytes_p)
        print("Saved production GLB:", production_filename)

    return designer_filename, production_filename

# -----------------------
# Example usage
# -----------------------
if __name__ == "__main__":
    # quick test - pure stone setting (no ring base)
    generate_stone_setting(
        stone_shape='round',
        stone_length=6.5,
        stone_width=6.5,
        stone_depth=4.0,
        prong_count=6,
        prong_thickness_base=0.9,
        prong_thickness_top=0.6,
        setting_height=3.2,
        base_type='minimal',  # Just minimal base for prong connection
        designer_filename='example_designer.glb',
        production_filename='example_production.glb'
    )
    print("Example stone setting generated.")