"""
Ring utilities extracted from the parametric stone setting generator.
Provides ring builders only so the main generator can be prong-free if desired.

Functions:
- create_ring_base
- create_manual_ring
- create_rounded_ring

This module is intentionally minimal and has no prong/stone logic.
"""

import numpy as np
import trimesh
from pathlib import Path


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
        # translate so the top of the tube sits slightly below z=0 (taking
        # the actual tube radius into account). This aligns the visible top
        # surface similar to the flat-ring variant while preserving overlap
        # for prong bases.
        translate_z = -(tube_r + ring_penetration)
        tor.apply_translation([0, 0, translate_z])
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


if __name__ == '__main__':
    # quick test: export a sample ring to output/
    out = Path('output')
    out.mkdir(exist_ok=True)
    ring = create_ring_base(outer_radius=10.0, inner_radius=8.0, height=2.0, ring_penetration=0.2, profile='rounded')
    scene = trimesh.Scene([ring])
    path = out / 'ring_utils_example.glb'
    with open(path, 'wb') as f:
        f.write(scene.export(file_type='glb'))
    print('Wrote', path)
