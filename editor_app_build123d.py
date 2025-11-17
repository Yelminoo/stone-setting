"""
Interactive Stone Setting Editor - build123d Version
Real-time parameter adjustment with 3D preview using build123d
"""

from flask import Flask, render_template, request, jsonify, send_file
from stone_setting_build123d import create_stone_setting_b3d
from build123d import export_stl
import os
import numpy as np
import trimesh
import tempfile

app = Flask(__name__)

# Create output directory
os.makedirs('output', exist_ok=True)

# Store last generated parameters
last_params = {
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

@app.route('/')
def index():
    return render_template('editor.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate stone setting with current parameters using build123d"""
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
        
        # Generate using build123d
        ring, stone, prongs = create_stone_setting_b3d(**params)
        
        # Convert each part to STL then load with trimesh
        temp_ring = tempfile.NamedTemporaryFile(suffix='.stl', delete=False)
        temp_stone = tempfile.NamedTemporaryFile(suffix='.stl', delete=False)
        temp_prongs = tempfile.NamedTemporaryFile(suffix='.stl', delete=False)
        
        # Close the files immediately so they can be written to
        temp_ring_path = temp_ring.name
        temp_stone_path = temp_stone.name
        temp_prongs_path = temp_prongs.name
        temp_ring.close()
        temp_stone.close()
        temp_prongs.close()
        
        try:
            # Export each part separately to STL
            export_stl(ring, temp_ring_path)
            export_stl(stone, temp_stone_path)
            export_stl(prongs, temp_prongs_path)
            
            # Load with trimesh
            ring_mesh = trimesh.load(temp_ring_path)
            stone_mesh = trimesh.load(temp_stone_path)
            prongs_mesh = trimesh.load(temp_prongs_path)
            
            # Create scene with named nodes for material assignment
            scene = trimesh.Scene()
            scene.add_geometry(ring_mesh, node_name='ring', geom_name='ring')
            scene.add_geometry(stone_mesh, node_name='stone', geom_name='stone')
            scene.add_geometry(prongs_mesh, node_name='prongs', geom_name='prongs')
            
            # Export to GLB
            output_path = 'output/current_setting.glb'
            scene.export(output_path)
            
            # Get mesh statistics
            total_vertices = len(ring_mesh.vertices) + len(stone_mesh.vertices) + len(prongs_mesh.vertices)
            total_faces = len(ring_mesh.faces) + len(stone_mesh.faces) + len(prongs_mesh.faces)
            
            return jsonify({
                'success': True,
                'file': 'current_setting.glb',
                'vertices': int(total_vertices),
                'faces': int(total_faces)
            })
            
        finally:
            # Clean up temp files
            try:
                os.unlink(temp_ring_path)
            except:
                pass
            try:
                os.unlink(temp_stone_path)
            except:
                pass
            try:
                os.unlink(temp_prongs_path)
            except:
                pass
        
    except Exception as e:
        import traceback
        traceback.print_exc()
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
    """Download designer or production version"""
    try:
        params = last_params.copy()
        
        ring, stone, prongs = create_stone_setting_b3d(**params)
        
        # Convert to trimesh via STL
        temp_ring = tempfile.NamedTemporaryFile(suffix='.stl', delete=False)
        temp_stone = tempfile.NamedTemporaryFile(suffix='.stl', delete=False)
        temp_prongs = tempfile.NamedTemporaryFile(suffix='.stl', delete=False)
        
        # Close files immediately
        temp_ring_path = temp_ring.name
        temp_stone_path = temp_stone.name
        temp_prongs_path = temp_prongs.name
        temp_ring.close()
        temp_stone.close()
        temp_prongs.close()
        
        try:
            export_stl(ring, temp_ring_path)
            export_stl(stone, temp_stone_path)
            export_stl(prongs, temp_prongs_path)
            
            ring_mesh = trimesh.load(temp_ring_path)
            stone_mesh = trimesh.load(temp_stone_path)
            prongs_mesh = trimesh.load(temp_prongs_path)
            
            if version == 'designer':
                # Designer version: includes stone
                scene = trimesh.Scene()
                scene.add_geometry(ring_mesh, node_name='ring')
                scene.add_geometry(stone_mesh, node_name='stone')
                scene.add_geometry(prongs_mesh, node_name='prongs')
                
                output_path = 'output/designer_version_b3d.glb'
                scene.export(output_path)
                
                return send_file(output_path,
                               mimetype='model/gltf-binary',
                               as_attachment=True,
                               download_name='stone_setting_designer_b3d.glb')
            
            elif version == 'production':
                # Production version: no stone
                combined = trimesh.util.concatenate([ring_mesh, prongs_mesh])
                
                output_path = 'output/production_version_b3d.glb'
                combined.export(output_path)
                
                return send_file(output_path,
                               mimetype='model/gltf-binary',
                               as_attachment=True,
                               download_name='stone_setting_production_b3d.glb')
            
            return "Invalid version", 400
            
        finally:
            try:
                os.unlink(temp_ring_path)
            except:
                pass
            try:
                os.unlink(temp_stone_path)
            except:
                pass
            try:
                os.unlink(temp_prongs_path)
            except:
                pass
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print("=" * 60)
    print("🔷 Interactive Stone Setting Editor - build123d")
    print("=" * 60)
    print("Open in browser: http://127.0.0.1:5002")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5002)
