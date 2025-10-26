"""
Mesh Concept Explanation with Examples
=====================================

A mesh is like building a 3D model with paper triangles - each triangle is a "face"
"""

import numpy as np
import trimesh

# Example 1: Simple Triangle (Single Face)
print("=== EXAMPLE 1: Single Triangle ===")

# Define 3 points in 3D space (vertices)
vertices = np.array([
    [0, 0, 0],    # Point A: bottom-left
    [1, 0, 0],    # Point B: bottom-right  
    [0.5, 1, 0]   # Point C: top-center
])

# Define which vertices connect to form a triangle (face)
faces = np.array([
    [0, 1, 2]     # Connect vertex 0->1->2 (counter-clockwise)
])

# Create the mesh
triangle_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

print(f"Vertices: {len(triangle_mesh.vertices)} points")
print(f"Faces: {len(triangle_mesh.faces)} triangles")
print(f"Area: {triangle_mesh.area:.2f}")

# Export to see it
triangle_mesh.export('output/single_triangle.glb')

# Example 2: Square made of 2 Triangles
print("\n=== EXAMPLE 2: Square (2 Triangles) ===")

# 4 corners of a square
square_vertices = np.array([
    [0, 0, 0],    # Bottom-left
    [1, 0, 0],    # Bottom-right
    [1, 1, 0],    # Top-right
    [0, 1, 0]     # Top-left
])

# A square needs 2 triangles to be represented
square_faces = np.array([
    [0, 1, 2],    # Triangle 1: bottom-left -> bottom-right -> top-right
    [0, 2, 3]     # Triangle 2: bottom-left -> top-right -> top-left
])

square_mesh = trimesh.Trimesh(vertices=square_vertices, faces=square_faces)

print(f"Vertices: {len(square_mesh.vertices)} points")
print(f"Faces: {len(square_mesh.faces)} triangles")
print(f"Area: {square_mesh.area:.2f}")

square_mesh.export('output/square_mesh.glb')

# Example 3: Why Triangles? (Not Quads)
print("\n=== EXAMPLE 3: Why Triangles, Not Rectangles? ===")

# Problem: 4 points might not be in the same plane!
warped_vertices = np.array([
    [0, 0, 0],      # Bottom-left
    [1, 0, 0],      # Bottom-right
    [1, 1, 0.5],    # Top-right (lifted up!)
    [0, 1, 0]       # Top-left
])

# If we tried to make this a single "quad", it would be twisted/warped
# But with triangles, each face is always flat!
warped_faces = np.array([
    [0, 1, 2],    # Triangle 1: always flat
    [0, 2, 3]     # Triangle 2: always flat
])

warped_mesh = trimesh.Trimesh(vertices=warped_vertices, faces=warped_faces)
warped_mesh.export('output/warped_mesh.glb')

print("Triangles solve the 'warped quad' problem!")

# Example 4: Complex Shape (Pyramid)
print("\n=== EXAMPLE 4: Pyramid (Multiple Triangles) ===")

# 5 vertices: 4 base corners + 1 top point
pyramid_vertices = np.array([
    # Base (square)
    [0, 0, 0],    # 0: bottom-left
    [1, 0, 0],    # 1: bottom-right
    [1, 1, 0],    # 2: top-right
    [0, 1, 0],    # 3: top-left
    # Peak
    [0.5, 0.5, 1] # 4: peak
])

# 6 triangular faces
pyramid_faces = np.array([
    # Base (2 triangles)
    [0, 2, 1],    # Base triangle 1 (note: flipped for correct normal)
    [0, 3, 2],    # Base triangle 2
    # Sides (4 triangles)
    [0, 1, 4],    # Front face
    [1, 2, 4],    # Right face  
    [2, 3, 4],    # Back face
    [3, 0, 4]     # Left face
])

pyramid_mesh = trimesh.Trimesh(vertices=pyramid_vertices, faces=pyramid_faces)

print(f"Vertices: {len(pyramid_mesh.vertices)} points")
print(f"Faces: {len(pyramid_mesh.faces)} triangles")
print(f"Volume: {pyramid_mesh.volume:.2f}")

pyramid_mesh.export('output/pyramid_mesh.glb')

# Example 5: Mesh Analysis
print("\n=== EXAMPLE 5: Mesh Properties ===")

# Create a simple cube for analysis
cube = trimesh.creation.box(extents=[1, 1, 1])

print(f"Cube vertices: {len(cube.vertices)}")
print(f"Cube faces: {len(cube.faces)}")
print(f"Cube edges: {len(cube.edges)}")
print(f"Cube volume: {cube.volume:.2f}")
print(f"Cube surface area: {cube.area:.2f}")
print(f"Is watertight (closed): {cube.is_watertight}")

# Look at the actual data
print(f"\nFirst 4 vertices:")
print(cube.vertices[:4])
print(f"\nFirst 2 faces (triangles):")
print(cube.faces[:2])

cube.export('output/cube_analysis.glb')

print("\n=== All examples exported to output/ folder ===")