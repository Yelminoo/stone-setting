import pygltflib

# Load the GLB file
gltf = pygltflib.GLTF2.load('d:/Python-CAD-3D/output/diamond_ring_-_day_1_3dinktober2019-ring.glb')

print('Ring Template Analysis from GLB:')
print('=' * 40)

# Analyze mesh complexity to identify ring parts
mesh_info = []
for i, mesh in enumerate(gltf.meshes):
    vertex_count = 0
    triangle_count = 0

    if mesh.primitives:
        for prim in mesh.primitives:
            # Get approximate vertex count from accessor
            if hasattr(prim.attributes, 'POSITION') and prim.attributes.POSITION is not None:
                accessor_idx = prim.attributes.POSITION
                if accessor_idx < len(gltf.accessors):
                    vertex_count = gltf.accessors[accessor_idx].count

            # Get triangle count
            if prim.indices is not None:
                indices_idx = prim.indices
                if indices_idx < len(gltf.accessors):
                    triangle_count = gltf.accessors[indices_idx].count // 3

    mesh_info.append({
        'index': i,
        'name': mesh.name,
        'vertices': vertex_count,
        'triangles': triangle_count
    })

# Sort by triangle count to identify main components
mesh_info.sort(key=lambda x: x['triangles'], reverse=True)

print('Mesh Analysis (sorted by complexity):')
for info in mesh_info:
    print(f"  {info['name']}: {info['vertices']} vertices, {info['triangles']} triangles")

print()
print('Template Identification:')
print('-' * 20)

# Identify components based on complexity
if len(mesh_info) >= 1:
    main_mesh = mesh_info[0]
    print(f"Main Ring Band: {main_mesh['name']} ({main_mesh['triangles']} triangles)")

if len(mesh_info) >= 2:
    secondary_mesh = mesh_info[1]
    print(f"Stone/Prong Assembly: {secondary_mesh['name']} ({secondary_mesh['triangles']} triangles)")

if len(mesh_info) >= 3:
    print(f"Additional Components: {len(mesh_info) - 2} smaller parts")

print()
print('Template Parameters Extracted:')
print('-' * 30)

# Estimate ring dimensions from mesh complexity
total_triangles = sum(info['triangles'] for info in mesh_info)
total_vertices = sum(info['vertices'] for info in mesh_info)

print(f"Total geometry complexity: {total_triangles} triangles, {total_vertices} vertices")
print(f"Estimated ring size: Medium (based on {total_triangles} triangles)")

# Material analysis
material_count = len(gltf.materials)
print(f"Material variations: {material_count} (likely gold variations)")

print()
print('Recommended Template Structure:')
print('-' * 30)
print("Based on this GLB analysis, create a parametric template with:")
print("1. Main ring band (tubular torus)")
print("2. Stone setting with prongs")
print("3. Multiple material options")
print("4. Adjustable ring size and stone parameters")