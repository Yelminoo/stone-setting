import pygltflib
import numpy as np

# Load the GLB file
gltf = pygltflib.GLTF2.load('d:/Python-CAD-3D/output/diamond_ring_-_day_1_3dinktober2019-ring.glb')

print('GLB Structure Analysis:')
print(f'Number of meshes: {len(gltf.meshes)}')
print(f'Number of nodes: {len(gltf.nodes)}')
print(f'Number of scenes: {len(gltf.scenes)}')
print(f'Number of materials: {len(gltf.materials)}')
print()

print('Meshes:')
for i, mesh in enumerate(gltf.meshes):
    print(f'  Mesh {i}: {mesh.name}')
    if mesh.primitives:
        for j, prim in enumerate(mesh.primitives):
            print(f'    Primitive {j}: mode={prim.mode}')
            if hasattr(prim.attributes, 'POSITION'):
                pos_accessor_idx = prim.attributes.POSITION
                if pos_accessor_idx is not None and pos_accessor_idx < len(gltf.accessors):
                    accessor = gltf.accessors[pos_accessor_idx]
                    vertex_count = accessor.count
                    print(f'      POSITION: {vertex_count} vertices')
            if prim.indices is not None:
                indices_accessor_idx = prim.indices
                if indices_accessor_idx < len(gltf.accessors):
                    indices_accessor = gltf.accessors[indices_accessor_idx]
                    triangle_count = indices_accessor.count // 3
                    print(f'      TRIANGLES: {triangle_count}')
            if prim.material is not None:
                print(f'      Material index: {prim.material}')
print()

print('Nodes:')
for i, node in enumerate(gltf.nodes):
    print(f'  Node {i}: {node.name}')
    if hasattr(node, 'mesh') and node.mesh is not None:
        print(f'    Mesh index: {node.mesh}')
    if hasattr(node, 'translation') and node.translation:
        print(f'    Position: {node.translation}')
    if hasattr(node, 'rotation') and node.rotation:
        print(f'    Rotation: {node.rotation}')
    if hasattr(node, 'scale') and node.scale:
        print(f'    Scale: {node.scale}')
print()

print('Materials:')
for i, mat in enumerate(gltf.materials):
    mat_name = mat.name if hasattr(mat, 'name') and mat.name else f'Material_{i}'
    print(f'  Material {i}: {mat_name}')
    if hasattr(mat, 'pbrMetallicRoughness') and mat.pbrMetallicRoughness:
        pbr = mat.pbrMetallicRoughness
        if hasattr(pbr, 'baseColorFactor') and pbr.baseColorFactor:
            color = pbr.baseColorFactor[:3]  # RGB values
            print(f'    Base color: {color}')
        if hasattr(pbr, 'metallicFactor'):
            print(f'    Metallic: {pbr.metallicFactor}')
        if hasattr(pbr, 'roughnessFactor'):
            print(f'    Roughness: {pbr.roughnessFactor}')
print()

print('Scene Analysis:')
if gltf.scenes:
    scene = gltf.scenes[0]  # Default scene
    print(f'Scene nodes: {scene.nodes}')
    for node_idx in scene.nodes:
        if node_idx < len(gltf.nodes):
            node = gltf.nodes[node_idx]
            print(f'  Root node {node_idx}: {node.name}')