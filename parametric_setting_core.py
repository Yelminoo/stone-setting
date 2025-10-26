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

def create_ring_base(outer_radius, inner_radius, height, sections=64):
    """
    Create a ring (torus-like) base with a hole in the middle for finger.
    outer_radius: outer edge of the ring
    inner_radius: inner hole radius (for finger)
    height: thickness of the ring band
    """
    # Create outer cylinder
    outer = trimesh.creation.cylinder(radius=outer_radius, height=height, sections=sections)
    # Create inner cylinder (hole)
    inner = trimesh.creation.cylinder(radius=inner_radius, height=height*2, sections=sections)
    
    # Position both at z=0 base
    outer.apply_translation([0, 0, -outer.bounds[0,2]])
    inner.apply_translation([0, 0, -inner.bounds[0,2] - height*0.5])  # center the hole
    
    # Subtract inner from outer to create ring
    try:
        ring = outer.difference(inner)
        if ring is None or len(ring.vertices) == 0:
            # If boolean operation fails, create manual ring
            return create_manual_ring(outer_radius, inner_radius, height, sections)
        return ring
    except:
        # Fallback to manual ring creation
        return create_manual_ring(outer_radius, inner_radius, height, sections)

def create_manual_ring(outer_radius, inner_radius, height, sections=64):
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
    mesh.process()
    return mesh

def create_prong_base(base_style, prong_positions, base_width, base_height, gallery_radius=None):
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
            base_cylinder.apply_translation([pos[0], pos[1], -base_height])
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
        
        gallery_ring.apply_translation([0, 0, -base_height])
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
    designer_filename='setting_designer.glb',
    production_filename='setting_production.glb',
    prong_taper_sections=36,
    production_prong_extra=1.5      # mm extra prong height for production
):
    """
    Build the setting meshes and export two GLB files.

    Returns tuple (designer_path, production_path).
    """
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

    # ---- Prong generation ----
    # Prong radial positions: place prongs evenly around an ellipse perimeter
    rx = stone_length / 2.0 + 0.05  # small offset so prongs sit outside stone
    ry = stone_width / 2.0 + 0.05
    angles = np.linspace(0, 2*np.pi, prong_count, endpoint=False)
    
    # Calculate prong positions for base creation
    prong_positions = []
    prongs = []
    
    for i, ang in enumerate(angles):
        # center position
        cx = rx * np.cos(ang)
        cy = ry * np.sin(ang)
        prong_positions.append([cx, cy])
        
        # prong dimensions (frustum) - starts from prong base height
        r_bottom = prong_thickness_base / 2.0
        r_top = prong_thickness_top / 2.0
        h = setting_height
        fr = create_frustum(r_bottom, r_top, h, sections=prong_taper_sections)
        # translate to position; prong starts from base top (z=0)
        fr.apply_translation([cx, cy, 0.0])

        # rotate so prong faces toward the stone center: we tilt a little inward
        # compute vector from prong center to stone center in XY
        inward = np.array([-cx, -cy, 0.0])
        inward_norm = np.linalg.norm(inward[:2])
        if inward_norm > 1e-6:
            # tilt angle small (e.g., 8 degrees), create rotation about axis perpendicular to inward vector
            tilt_deg = 8.0
            # axis = cross([0,0,1], inward_xy)
            axis = np.cross(np.array([0,0,1.0]), np.append(inward[:2], 0.0))
            axis = axis / (np.linalg.norm(axis)+1e-12)
            angle_rad = np.deg2rad(tilt_deg)
            fr.apply_translation(-np.array([cx, cy, 0.0]))  # to origin
            rotation_matrix = trimesh.transformations.rotation_matrix(angle_rad, axis)
            fr.apply_transform(rotation_matrix)
            fr.apply_translation(np.array([cx, cy, 0.0]))

        prongs.append(fr)
    
    # Create prong bases
    if gallery_radius is None:
        # Auto-calculate gallery radius
        gallery_radius = np.mean([np.sqrt(pos[0]**2 + pos[1]**2) for pos in prong_positions])
    
    prong_bases = create_prong_base(
        prong_base_style, 
        prong_positions, 
        prong_base_width, 
        prong_base_height,
        gallery_radius
    )

    # Create base according to type
    base_meshes = []
    if base_type == 'ring':
        # Full ring base (with hole for finger)
        ring_base = create_ring_base(ring_outer_radius, ring_inner_radius, ring_thickness)
        ring_base.apply_translation([0, 0, -ring_thickness])
        base_meshes.append(ring_base)
    elif base_type == 'minimal':
        # Small circular platform just to connect prongs
        base_thickness = 0.6
        base_radius = max(stone_length, stone_width) / 2.0 + 1.0
        minimal_base = trimesh.creation.cylinder(radius=base_radius, height=base_thickness, sections=32)
        minimal_base.apply_translation([0, 0, -base_thickness])
        base_meshes.append(minimal_base)
    # if base_type == 'none', no base is created

    # designer scene: stone + prongs + prong_bases + base (if any)
    designer_meshes = base_meshes + prong_bases + prongs + [stone]
    # color base and prongs (metal)
    for m in designer_meshes:
        if m is stone:
            continue
        m.visual.vertex_colors = np.tile(np.array([200,190,170,255]), (len(m.vertices),1))

    # Build designer scene
    scene_designer = trimesh.Scene(designer_meshes)
    # export GLB
    glb_bytes = scene_designer.export(file_type='glb')
    with open(designer_filename, 'wb') as f:
        f.write(glb_bytes)
    print("Saved designer GLB:", designer_filename)

    # ---------------------
    # production version
    # ---------------------
    # increase prong height
    prong_height_prod = setting_height + production_prong_extra
    prongs_prod = []
    for i, ang in enumerate(angles):
        cx = rx * np.cos(ang)
        cy = ry * np.sin(ang)
        r_bottom = prong_thickness_base / 2.0
        r_top = prong_thickness_top / 2.0
        fr = create_frustum(r_bottom, r_top, prong_height_prod, sections=prong_taper_sections)
        fr.apply_translation([cx, cy, 0.0])
        # tilt same as before
        inward = np.array([-cx, -cy, 0.0])
        inward_norm = np.linalg.norm(inward[:2])
        if inward_norm > 1e-6:
            tilt_deg = 8.0
            axis = np.cross(np.array([0,0,1.0]), np.append(inward[:2], 0.0))
            axis = axis / (np.linalg.norm(axis)+1e-12)
            angle_rad = np.deg2rad(tilt_deg)
            fr.apply_translation(-np.array([cx, cy, 0.0]))
            rotation_matrix = trimesh.transformations.rotation_matrix(angle_rad, axis)
            fr.apply_transform(rotation_matrix)
            fr.apply_translation(np.array([cx, cy, 0.0]))

        # Make small cut at underside for better seating - here just ensure base sits flush (no boolean)
        prongs_prod.append(fr)
    
    # Create prong bases for production (same as designer)
    prong_bases_prod = create_prong_base(
        prong_base_style, 
        prong_positions, 
        prong_base_width, 
        prong_base_height * 1.1,  # Slightly taller for production
        gallery_radius
    )

    # production base (slightly thicker for manufacturing)
    base_prod_meshes = []
    if base_type == 'ring':
        ring_base_prod = create_ring_base(ring_outer_radius, ring_inner_radius, ring_thickness * 1.1)
        ring_base_prod.apply_translation([0, 0, -ring_thickness * 1.1])
        base_prod_meshes.append(ring_base_prod)
    elif base_type == 'minimal':
        base_thickness = 0.6
        base_radius = max(stone_length, stone_width) / 2.0 + 1.0
        minimal_base_prod = trimesh.creation.cylinder(radius=base_radius, height=base_thickness*1.1, sections=32)
        minimal_base_prod.apply_translation([0, 0, -base_thickness*1.1])
        base_prod_meshes.append(minimal_base_prod)

    # combine all production meshes into a single mesh and attempt repair
    all_prod = trimesh.util.concatenate(base_prod_meshes + prong_bases_prod + prongs_prod)
    all_prod.process()  # basic processing
    # attempt fill holes and repair normals
    try:
        all_prod.repair.fix_normals()
        all_prod.repair.fill_holes()
        all_prod.remove_duplicate_faces()
        all_prod.remove_unreferenced_vertices()
        all_prod.process()
    except Exception:
        # repair utilities may not fully work for all cases; continue with what we have
        pass

    # Export production GLB
    scene_prod = trimesh.Scene([all_prod])
    glb_bytes_p = scene_prod.export(file_type='glb')
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