"""
Interactive Stone Setting Editor - Python Version
Real-time parameter adjustment with 3D preview
"""

from flask import Flask, render_template, request, jsonify, send_file
from stone_setting_simple import create_stone_setting
import os
import tempfile
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create upload directory
os.makedirs('uploads', exist_ok=True)
os.makedirs('output', exist_ok=True)

# Store current parameters (updated by editor)
current_params = {
    'stone_size': 6.0,
    'stone_depth': 7.2,
    'prong_count': 4,
    'prong_thickness_base': 0.4,
    'prong_thickness_top': 0.3,
    'setting_height': 3.0,
    'ring_size': 8.5,
    'ring_thickness': 1.0,
    'stone_shape': 'round'
}

# Store last generated parameters
last_params = current_params.copy()

@app.route('/')
def index():
    return render_template('editor.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate stone setting with current parameters"""
    global last_params
    try:
        data = request.json
        
        # Update parameters
        params = {
            'stone_size': float(data.get('stoneSize', 6.0)),
            'stone_depth': float(data.get('stoneDepth', 7.2)),
            'prong_count': int(data.get('prongCount', 4)),
            'prong_thickness_base': float(data.get('prongThicknessBase', 0.4)),
            'prong_thickness_top': float(data.get('prongThicknessTop', 0.3)),
            'setting_height': float(data.get('settingHeight', 3.0)),
            'ring_size': float(data.get('ringSize', 8.5)),
            'ring_thickness': float(data.get('ringThickness', 1.0)),
            'stone_shape': data.get('stoneShape', 'round')
        }
        
        # Store parameters for download
        last_params = params.copy()
        
        # Generate mesh with separate components for different materials
        from stone_setting_simple import create_ring, create_brilliant_cut_diamond, create_princess_cut_diamond, create_radiant_cut_diamond, create_prongs
        import trimesh
        import numpy as np
        
        ring_size = params['ring_size']
        ring_thickness = params['ring_thickness']
        stone_size = params['stone_size']
        stone_depth = params['stone_depth']
        setting_height = params['setting_height']
        stone_shape = params['stone_shape']
        
        # Create components separately
        ring_mesh = create_ring(ring_size, ring_thickness)
        
        centerpiece_y = ring_size
        stone_y = ring_size + ring_thickness + setting_height
        prong_spread_radius = stone_size / 2
        
        # Adjust prong spread to account for prong thickness
        prong_spread_radius += (params['prong_thickness_base'] / 2)
        
        stone_radius = prong_spread_radius - 0.25  # Minimal clearance
        
        # Create stone based on shape
        actual_prong_spread_radius = prong_spread_radius
        
        if stone_shape == 'round':
            stone_mesh = create_brilliant_cut_diamond(stone_radius, stone_depth)
        elif stone_shape == 'princess':
            stone_size_actual = stone_size - 0.1
            stone_mesh = create_princess_cut_diamond(stone_size_actual, stone_depth)
            # Rotate so corners align with prongs
            prong_count = params['prong_count']
            rotation_angle = (np.pi / prong_count)
            rotation_matrix = trimesh.transformations.rotation_matrix(rotation_angle, [0, 1, 0])
            stone_mesh.apply_transform(rotation_matrix)
            actual_prong_spread_radius = (stone_size / 2) * np.sqrt(2) + 0.1 + (params['prong_thickness_base'] / 2)
        elif stone_shape == 'radiant':
            stone_size_actual = stone_size - 0.1
            stone_mesh = create_radiant_cut_diamond(stone_size_actual, stone_depth)
            # Rotate so corners align with prongs
            prong_count = params['prong_count']
            rotation_angle = (np.pi / prong_count)
            rotation_matrix = trimesh.transformations.rotation_matrix(rotation_angle, [0, 1, 0])
            stone_mesh.apply_transform(rotation_matrix)
            actual_prong_spread_radius = (stone_size / 2) * np.sqrt(2) + 0.1 + (params['prong_thickness_base'] / 2)
        else:
            stone_mesh = create_brilliant_cut_diamond(stone_radius, stone_depth)
        
        stone_mesh.apply_translation([0, stone_y, 0])
        
        prong_config = {
            'count': params['prong_count'],
            'thickness_base': params['prong_thickness_base'],
            'thickness_top': params['prong_thickness_top'],
        }
        config_full = {
            'ringSize': ring_size,
            'ringThickness': ring_thickness,
            'stoneSize': stone_size,
            'stoneDepth': stone_depth,
            'prongCount': params['prong_count'],
            'prongThicknessBase': params['prong_thickness_base'],
            'prongThicknessTop': params['prong_thickness_top'],
            'stoneHeightAboveRing': setting_height,
            'stoneShape': stone_shape
        }
        prongs_mesh = create_prongs(config_full, centerpiece_y, stone_y, actual_prong_spread_radius)
        
        # Create scene with named objects for material identification
        scene = trimesh.Scene()
        scene.add_geometry(ring_mesh, node_name='ring', geom_name='ring')
        scene.add_geometry(stone_mesh, node_name='stone', geom_name='stone')
        scene.add_geometry(prongs_mesh, node_name='prongs', geom_name='prongs')
        
        # Save to temp file
        output_path = 'output/current_setting.glb'
        os.makedirs('output', exist_ok=True)
        scene.export(output_path)
        
        total_vertices = len(ring_mesh.vertices) + len(stone_mesh.vertices) + len(prongs_mesh.vertices)
        total_faces = len(ring_mesh.faces) + len(stone_mesh.faces) + len(prongs_mesh.faces)
        
        return jsonify({
            'success': True,
            'file': 'current_setting.glb',
            'vertices': total_vertices,
            'faces': total_faces
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/model/<filename>')
def get_model(filename):
    """Serve the GLB file"""
    file_path = os.path.join('output', filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='model/gltf-binary')
    return "File not found", 404

@app.route('/api/download/<version>')
def download_file(version):
    """Download designer or production version with current editor parameters"""
    try:
        from stone_setting_simple import create_ring, create_brilliant_cut_diamond, create_princess_cut_diamond, create_radiant_cut_diamond, create_prongs
        import trimesh
        
        # Use last generated parameters from editor
        params = last_params.copy()
        ring_size = params['ring_size']
        ring_thickness = params['ring_thickness']
        stone_size = params['stone_size']
        stone_depth = params['stone_depth']
        setting_height = params['setting_height']
        stone_shape = params['stone_shape']
        prong_count = params['prong_count']
        prong_thickness_base = params['prong_thickness_base']
        prong_thickness_top = params['prong_thickness_top']
        
        # Create components
        ring_mesh = create_ring(ring_size, ring_thickness)
        
        centerpiece_y = ring_size
        stone_y = ring_size + ring_thickness + setting_height
        prong_spread_radius = stone_size / 2
        
        # Adjust prong spread to account for prong thickness
        prong_spread_radius += (prong_thickness_base / 2)
        
        stone_radius = prong_spread_radius - 0.25
        
        # Create stone based on shape
        actual_prong_spread_radius = prong_spread_radius
        
        if stone_shape == 'round':
            stone_mesh = create_brilliant_cut_diamond(stone_radius, stone_depth)
        elif stone_shape == 'princess':
            stone_size_actual = stone_size - 0.1
            stone_mesh = create_princess_cut_diamond(stone_size_actual, stone_depth)
            rotation_angle = (np.pi / prong_count)
            rotation_matrix = trimesh.transformations.rotation_matrix(rotation_angle, [0, 1, 0])
            stone_mesh.apply_transform(rotation_matrix)
            actual_prong_spread_radius = (stone_size / 2) * np.sqrt(2) + 0.1 + (prong_thickness_base / 2)
        elif stone_shape == 'radiant':
            stone_size_actual = stone_size - 0.1
            stone_mesh = create_radiant_cut_diamond(stone_size_actual, stone_depth)
            rotation_angle = (np.pi / prong_count)
            rotation_matrix = trimesh.transformations.rotation_matrix(rotation_angle, [0, 1, 0])
            stone_mesh.apply_transform(rotation_matrix)
            actual_prong_spread_radius = (stone_size / 2) * np.sqrt(2) + 0.1 + (prong_thickness_base / 2)
        else:
            stone_mesh = create_brilliant_cut_diamond(stone_radius, stone_depth)
        
        stone_mesh.apply_translation([0, stone_y, 0])
        
        config_full = {
            'ringSize': ring_size,
            'ringThickness': ring_thickness,
            'stoneSize': stone_size,
            'stoneDepth': stone_depth,
            'prongCount': prong_count,
            'prongThicknessBase': prong_thickness_base,
            'prongThicknessTop': prong_thickness_top,
            'stoneHeightAboveRing': setting_height,
            'stoneShape': stone_shape
        }
        prongs_mesh = create_prongs(config_full, centerpiece_y, stone_y, actual_prong_spread_radius)
        
        if version == 'designer':
            # Designer version: includes stone
            scene = trimesh.Scene()
            scene.add_geometry(ring_mesh, node_name='ring', geom_name='ring')
            scene.add_geometry(stone_mesh, node_name='stone', geom_name='stone')
            scene.add_geometry(prongs_mesh, node_name='prongs', geom_name='prongs')
            
            output_path = 'output/designer_version.glb'
            scene.export(output_path)
            
            return send_file(output_path, 
                           mimetype='model/gltf-binary',
                           as_attachment=True,
                           download_name='stone_setting_designer.glb')
        
        elif version == 'production':
            # Production version: no stone, watertight, extended prongs
            # Extend prongs by 2mm
            import numpy as np
            prongs_extended = prongs_mesh.copy()
            
            # Find top vertices and extend upward
            vertices = prongs_extended.vertices
            max_y = vertices[:, 1].max()
            top_mask = vertices[:, 1] > (max_y - 0.5)
            vertices[top_mask, 1] += 2.0  # Extend by 2mm
            prongs_extended.vertices = vertices
            
            # Combine ring and prongs
            combined = trimesh.util.concatenate([ring_mesh, prongs_extended])
            
            # Make watertight
            trimesh.repair.fill_holes(combined)
            trimesh.repair.fix_normals(combined)
            
            output_path = 'output/production_version.glb'
            combined.export(output_path)
            
            return send_file(output_path,
                           mimetype='model/gltf-binary',
                           as_attachment=True,
                           download_name='stone_setting_production.glb')
        
        return "Invalid version", 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print("=" * 60)
    print("🎨 Interactive Stone Setting Editor")
    print("=" * 60)
    print("Open in browser: http://127.0.0.1:5001")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5001)
