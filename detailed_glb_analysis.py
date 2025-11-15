import pygltflib
import numpy as np
import struct

# Load the GLB file
gltf = pygltflib.GLTF2.load('d:/Python-CAD-3D/output/diamond_ring_-_day_1_3dinktober2019-ring.glb')

print('Detailed Mesh Analysis:')
print('=' * 50)

def get_accessor_data(gltf, accessor_idx):
    """Extract data from a GLTF accessor"""
    if accessor_idx >= len(gltf.accessors):
        return None

    accessor = gltf.accessors[accessor_idx]
    buffer_view = gltf.bufferViews[accessor.bufferView]
    buffer = gltf.buffers[buffer_view.buffer]

    # Get the data from buffer
    data = buffer.uri if hasattr(buffer, 'uri') and buffer.uri else gltf.binary_blob()
    if isinstance(data, str) and data.startswith('data:'):
        # Base64 encoded data
        import base64
        data = base64.b64decode(data.split(',')[1])

    # Extract the relevant portion
    start = buffer_view.byteOffset if buffer_view.byteOffset else 0
    length = buffer_view.byteLength
    buffer_data = data[start:start + length]

    # Parse based on component type and type
    component_size = {
        5120: 1,  # BYTE
        5121: 1,  # UNSIGNED_BYTE
        5122: 2,  # SHORT
        5123: 2,  # UNSIGNED_SHORT
        5125: 4,  # UNSIGNED_INT
        5126: 4,  # FLOAT
    }.get(accessor.componentType, 4)

    num_components = {
        'SCALAR': 1,
        'VEC2': 2,
        'VEC3': 3,
        'VEC4': 4,
        'MAT2': 4,
        'MAT3': 9,
        'MAT4': 16,
    }.get(accessor.type, 1)

    element_size = component_size * num_components
    count = accessor.count

    # Unpack the data
    if accessor.componentType == 5126:  # FLOAT
        fmt = f'<{count * num_components}f'
        values = struct.unpack(fmt, buffer_data)
        return np.array(values).reshape(count, num_components)
    else:
        return None

for i, mesh in enumerate(gltf.meshes):
    print(f'\nMesh {i}: {mesh.name}')
    print('-' * 20)

    if mesh.primitives:
        for j, prim in enumerate(mesh.primitives):
            print(f'  Primitive {j}:')

            # Get vertex positions
            if hasattr(prim.attributes, 'POSITION') and prim.attributes.POSITION is not None:
                positions = get_accessor_data(gltf, prim.attributes.POSITION)
                if positions is not None:
                    print(f'    Vertices: {len(positions)}')
                    print(f'    Position range X: {positions[:, 0].min():.3f} to {positions[:, 0].max():.3f}')
                    print(f'    Position range Y: {positions[:, 1].min():.3f} to {positions[:, 1].max():.3f}')
                    print(f'    Position range Z: {positions[:, 2].min():.3f} to {positions[:, 2].max():.3f}')

                    # Calculate approximate dimensions
                    dims = np.ptp(positions, axis=0)  # peak-to-peak (max - min)
                    print(f'    Approximate dimensions: {dims[0]:.3f} x {dims[1]:.3f} x {dims[2]:.3f}')

                    # Calculate center
                    center = np.mean(positions, axis=0)
                    print(f'    Center: ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})')
                else:
                    print('    Could not extract position data')

            # Get triangle count
            if prim.indices is not None:
                indices = get_accessor_data(gltf, prim.indices)
                if indices is not None:
                    triangle_count = len(indices) // 3
                    print(f'    Triangles: {triangle_count}')
                else:
                    print('    Could not extract index data')

print('\n' + '=' * 50)
print('Node Hierarchy Analysis:')
print('=' * 50)

def print_node_tree(node_idx, indent=0):
    if node_idx >= len(gltf.nodes):
        return

    node = gltf.nodes[node_idx]
    prefix = '  ' * indent
    node_name = node.name if node.name else f'Node_{node_idx}'

    print(f'{prefix}{node_name}')

    if hasattr(node, 'mesh') and node.mesh is not None:
        mesh = gltf.meshes[node.mesh]
        mesh_name = mesh.name if mesh.name else f'Mesh_{node.mesh}'
        print(f'{prefix}  └─ Mesh: {mesh_name}')

    if hasattr(node, 'translation') and node.translation:
        print(f'{prefix}  └─ Position: {node.translation}')

    if hasattr(node, 'rotation') and node.rotation:
        print(f'{prefix}  └─ Rotation: {node.rotation}')

    if hasattr(node, 'scale') and node.scale:
        print(f'{prefix}  └─ Scale: {node.scale}')

    if hasattr(node, 'children') and node.children:
        for child_idx in node.children:
            print_node_tree(child_idx, indent + 1)

# Print the scene hierarchy
if gltf.scenes:
    scene = gltf.scenes[0]
    print(f'Scene root nodes: {scene.nodes}')
    for root_node_idx in scene.nodes:
        print_node_tree(root_node_idx)