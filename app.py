"""
Flask web server for the Parametric Stone Setting Generator UI
Provides REST API endpoints for the web interface
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import json
import os
from pathlib import Path
from parametric_setting_core import generate_stone_setting, create_ring_base, create_claw_cluster
import trimesh
import numpy as np
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Ensure output directory exists
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

@app.route('/')
def index():
    """Serve the main UI page"""
    return send_file('ui.html')

@app.route('/view.html')
def viewer():
    """Serve the 3D viewer page"""
    return send_file('view.html')


@app.route('/ring.html')
def ring_page():
    """Serve the focused ring generator page"""
    # Use send_from_directory with the app file directory to avoid cwd issues
    return send_from_directory(os.path.dirname(__file__), 'ring.html')

@app.route('/editor.html')
def editor_page():
    """Serve the interactive 3D editor page"""
    return send_file('interactive_editor.html')

@app.route('/original_ring_geometry.json')
def original_ring_geometry():
    """Serve the original ring geometry data"""
    return send_file('original_ring_geometry.json')

@app.route('/test_geometry.html')
def test_geometry_page():
    """Serve the geometry test page"""
    return send_file('test_geometry.html')

@app.route('/parametric_editor.html')
def parametric_editor_page():
    """Serve the parametric editor with X,Y,Z controls"""
    return send_file('parametric_editor.html')

@app.route('/realtime.html')
def realtime_editor_page():
    """Serve the real-time parametric editor with Python backend integration"""
    return send_file('realtime_editor.html')

@app.route('/output/<filename>')
def serve_output(filename):
    """Serve generated GLB files"""
    return send_from_directory('output', filename)

@app.route('/examples/<filename>')
def serve_examples(filename):
    """Serve example parameter files"""
    return send_from_directory('examples', filename)

@app.route('/generate', methods=['POST'])
def generate():
    """Generate stone setting from parameters"""
    try:
        params = request.get_json()
        
        # Validate required parameters
        required_params = [
            'stone_shape', 'stone_length', 'stone_width', 'stone_depth',
            'prong_count', 'prong_thickness_base', 'prong_thickness_top', 'setting_height'
        ]
        
        for param in required_params:
            if param not in params:
                return jsonify({'error': f'Missing required parameter: {param}'}), 400
        
        # Set default values for optional parameters
        defaults = {
            'prong_base_style': 'gallery',
            'prong_base_width': 1.2,
            'prong_base_height': 1.0,
            'gallery_radius': None,
            'base_type': 'minimal',
            'ring_outer_radius': 8.5,
            'ring_inner_radius': 5.0,
            'ring_thickness': 2.0,
            'rim_claw_cluster': False,
            'rim_claw_count': 4,
            'rim_claw_spread_deg': 30.0,
            'rim_claw_length': 6.0,
            'rim_claw_base_diameter': 1.2,
            'rim_claw_tip_diameter': 0.6,
            'rim_claw_tilt_z_factor': 0.25,
            'rim_claw_base_angle_deg': 0.0,
            'ring_profile': 'rounded',
            'ring_tube_radius': None,
            'ring_penetration': 0.2
        }
        
        for key, value in defaults.items():
            if key not in params:
                params[key] = value
        
        # Generate file paths (timestamped to avoid collisions)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        designer_path = output_dir / f"designer_{timestamp}.glb"
        production_path = output_dir / f"production_{timestamp}.glb"
        
        # Generate the stone setting
        generate_stone_setting(
            stone_shape=params['stone_shape'],
            stone_length=float(params['stone_length']),
            stone_width=float(params['stone_width']),
            stone_depth=float(params['stone_depth']),
            prong_count=int(params['prong_count']),
            prong_thickness_base=float(params['prong_thickness_base']),
            prong_thickness_top=float(params['prong_thickness_top']),
            setting_height=float(params['setting_height']),
            prong_base_style=params['prong_base_style'],
            prong_base_width=float(params['prong_base_width']),
            prong_base_height=float(params['prong_base_height']),
            gallery_radius=float(params['gallery_radius']) if params['gallery_radius'] else None,
            base_type=params['base_type'],
            ring_outer_radius=float(params['ring_outer_radius']),
            ring_inner_radius=float(params['ring_inner_radius']),
            ring_thickness=float(params['ring_thickness']),
            ring_penetration=float(params.get('ring_penetration', 0.2)),
            ring_profile=params.get('ring_profile', 'rounded'),
            ring_tube_radius=(float(params['ring_tube_radius']) if params.get('ring_tube_radius') not in (None, '', 'null') else None),
            rim_claw_cluster=bool(params.get('rim_claw_cluster', False)),
            rim_claw_count=int(params.get('rim_claw_count', 4)),
            rim_claw_spread_deg=float(params.get('rim_claw_spread_deg', 30.0)),
            rim_claw_length=float(params.get('rim_claw_length', 6.0)),
            rim_claw_base_diameter=float(params.get('rim_claw_base_diameter', 1.2)),
            rim_claw_tip_diameter=float(params.get('rim_claw_tip_diameter', 0.6)),
            rim_claw_tilt_z_factor=float(params.get('rim_claw_tilt_z_factor', 0.25)),
            rim_claw_base_angle_deg=float(params.get('rim_claw_base_angle_deg', 0.0)),
            debug_markers=bool(params.get('debug_markers', False)),
            debug_single_prong=bool(params.get('debug_single_prong', False)),
            designer_filename=str(designer_path),
            production_filename=str(production_path)
        )
        # Optionally upload outputs to S3 if environment is configured
        s3_bucket = os.environ.get('S3_BUCKET')
        designer_url = None
        production_url = None

        def upload_to_s3(local_path, key):
            try:
                s3_client = boto3.client('s3',
                                         aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                                         aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                                         region_name=os.environ.get('AWS_REGION'))
                s3_client.upload_file(str(local_path), s3_bucket, key)
                return f"https://{s3_bucket}.s3.amazonaws.com/{key}"
            except (BotoCoreError, ClientError) as e:
                print(f"S3 upload failed: {e}")
                return None

        if s3_bucket:
            designer_key = f"designer_{timestamp}.glb"
            production_key = f"production_{timestamp}.glb"
            designer_url = upload_to_s3(designer_path, designer_key)
            production_url = upload_to_s3(production_path, production_key)

        # Also create consistent non-timestamped filenames so the UI (which expects
        # /output/designer.glb and /output/production.glb) can load the latest files.
        try:
            import shutil
            shutil.copy(str(designer_path), str(output_dir / "designer.glb"))
            shutil.copy(str(production_path), str(output_dir / "production.glb"))
        except Exception as e:
            print(f"Warning: failed to copy outputs to stable filenames: {e}")

        response = {
            'success': True,
            'designer_file': str(designer_path),
            'production_file': str(production_path),
            'designer_file_stable': 'output/designer.glb',
            'production_file_stable': 'output/production.glb',
            'message': 'Stone setting generated successfully'
        }

        if designer_url:
            response['designer_url'] = designer_url
        if production_url:
            response['production_url'] = production_url

        return jsonify(response)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error generating stone setting: {e}")
        print(f"Full traceback:\n{error_details}")
        return jsonify({'error': str(e), 'details': error_details}), 500


@app.route('/generate_ring', methods=['POST'])
def generate_ring():
    """Generate a ring-only GLB (no stone/prongs) from ring parameters."""
    try:
        params = request.get_json() or {}

        # required ring params
        outer = float(params.get('ring_outer_radius', 10.5))
        inner = float(params.get('ring_inner_radius', 8.0))
        thickness = float(params.get('ring_thickness', 2.0))
        ring_penetration = float(params.get('ring_penetration', 0.2))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        designer_path = output_dir / f"ring_designer_{timestamp}.glb"
        production_path = output_dir / f"ring_production_{timestamp}.glb"

        # build ring mesh
        ring_profile = params.get('ring_profile', 'rounded')
        ring_tube_radius = params.get('ring_tube_radius')
        if ring_tube_radius in (None, '', 'null'):
            ring_tube_radius = None
        else:
            try:
                ring_tube_radius = float(ring_tube_radius)
            except Exception:
                ring_tube_radius = None

        # build ring mesh
        ring = create_ring_base(outer, inner, thickness, ring_penetration=ring_penetration, profile=ring_profile, ring_tube_radius=ring_tube_radius)

        # simple production variation (thicker band)
        ring_prod = create_ring_base(outer, inner, thickness * 1.1, ring_penetration=ring_penetration, profile=ring_profile, ring_tube_radius=ring_tube_radius)

        # optional rim claw cluster for ring-only export
        if params.get('rim_claw_cluster'):
            try:
                rim_count = int(params.get('rim_claw_count', 4))
                rim_spread = float(params.get('rim_claw_spread_deg', 30.0))
                rim_length = float(params.get('rim_claw_length', 6.0))
                rim_base_d = float(params.get('rim_claw_base_diameter', 1.2))
                rim_tip_d = float(params.get('rim_claw_tip_diameter', 0.6))
                rim_tilt = float(params.get('rim_claw_tilt_z_factor', 0.25))
                rim_angle = float(params.get('rim_claw_base_angle_deg', 0.0))
                claws = create_claw_cluster(np.deg2rad(rim_angle), max(0.0, outer - 0.01), count=rim_count, spread_deg=rim_spread, length=rim_length, base_diameter=rim_base_d, tip_diameter=rim_tip_d, tilt_z_factor=rim_tilt, sections=32)
                claws_prod = create_claw_cluster(np.deg2rad(rim_angle), max(0.0, outer - 0.01), count=rim_count, spread_deg=rim_spread, length=rim_length + 1.5, base_diameter=rim_base_d, tip_diameter=rim_tip_d, tilt_z_factor=rim_tilt, sections=32)
            except Exception as e:
                print('Failed to create rim claws for ring-only export', e)

        # export
        try:
            designer_meshes = [ring]
            production_meshes = [ring_prod]
            # If claws were created above, include them (claws variable may exist)
            if 'claws' in locals() and claws:
                for c in claws:
                    designer_meshes.append(c)
            if 'claws_prod' in locals() and claws_prod:
                for c in claws_prod:
                    production_meshes.append(c)

            scene = trimesh.Scene(designer_meshes)
            with open(designer_path, 'wb') as f:
                f.write(scene.export(file_type='glb'))
            scene_p = trimesh.Scene(production_meshes)
            with open(production_path, 'wb') as f:
                f.write(scene_p.export(file_type='glb'))
        except Exception as e:
            print('Ring export failed', e)
            return jsonify({'error': str(e)}), 500

        # copy to stable filenames
        try:
            import shutil
            shutil.copy(str(designer_path), str(output_dir / 'designer.glb'))
            shutil.copy(str(production_path), str(output_dir / 'production.glb'))
        except Exception as e:
            print('Warning: failed to copy stable ring outputs', e)

        return jsonify({
            'success': True,
            'designer_file': str(designer_path),
            'production_file': str(production_path),
            'designer_file_stable': 'output/designer.glb',
            'production_file_stable': 'output/production.glb'
        })

    except Exception as e:
        print('Error in generate_ring', e)
        return jsonify({'error': str(e)}), 500

@app.route('/presets', methods=['GET'])
def get_presets():
    """Get available preset configurations"""
    presets = {
        'solitaire': {
            'name': 'Classic Solitaire',
            'description': 'Traditional 4-prong round diamond setting',
            'params': {
                'stone_shape': 'round',
                'stone_length': 6.5,
                'stone_width': 6.5,
                'stone_depth': 4.0,
                'prong_count': 4,
                'prong_thickness_base': 0.8,
                'prong_thickness_top': 0.5,
                'setting_height': 3.5,
                'prong_base_style': 'gallery',
                'prong_base_width': 1.0,
                'prong_base_height': 0.8,
                'base_type': 'ring',
                'ring_outer_radius': 8.5,
                'ring_inner_radius': 5.0,
                'ring_thickness': 2.0
            }
        },
        'halo': {
            'name': 'Halo Setting',
            'description': 'Modern 6-prong setting for halo rings',
            'params': {
                'stone_shape': 'round',
                'stone_length': 5.0,
                'stone_width': 5.0,
                'stone_depth': 3.5,
                'prong_count': 6,
                'prong_thickness_base': 0.6,
                'prong_thickness_top': 0.3,
                'setting_height': 2.8,
                'prong_base_style': 'individual',
                'prong_base_width': 0.8,
                'prong_base_height': 0.6,
                'base_type': 'minimal'
            }
        },
        'vintage': {
            'name': 'Vintage Princess',
            'description': 'Art deco inspired princess cut setting',
            'params': {
                'stone_shape': 'princess',
                'stone_length': 6.0,
                'stone_width': 6.0,
                'stone_depth': 4.2,
                'prong_count': 4,
                'prong_thickness_base': 1.0,
                'prong_thickness_top': 0.6,
                'setting_height': 4.0,
                'prong_base_style': 'shared',
                'prong_base_width': 1.4,
                'prong_base_height': 1.2,
                'base_type': 'ring',
                'ring_outer_radius': 9.0,
                'ring_inner_radius': 5.2,
                'ring_thickness': 2.5
            }
        }
    }
    
    return jsonify(presets)

@app.route('/export', methods=['POST'])
def export_params():
    """Export parameters as JSON file"""
    try:
        params = request.get_json()
        
        # Create export filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stone_setting_params_{timestamp}.json"
        filepath = output_dir / filename
        
        # Save parameters
        with open(filepath, 'w') as f:
            json.dump(params, f, indent=2)
        
        return send_file(str(filepath), as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Stone Setting Generator API'})

@app.route('/update_transform', methods=['POST'])
def update_transform():
    """Real-time update of object transforms (position, rotation, scale)"""
    try:
        data = request.get_json()
        object_name = data.get('object_name')
        transform = data.get('transform', {})
        
        # Store transform in session or temporary storage
        # For now, just validate and return
        position = transform.get('position', {'x': 0, 'y': 0, 'z': 0})
        rotation = transform.get('rotation', {'x': 0, 'y': 0, 'z': 0})
        scale = transform.get('scale', {'x': 1, 'y': 1, 'z': 1})
        
        return jsonify({
            'success': True,
            'object_name': object_name,
            'transform': {
                'position': position,
                'rotation': rotation,
                'scale': scale
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save_preset', methods=['POST'])
def save_preset():
    """Save current parameters as a named preset"""
    try:
        data = request.get_json()
        preset_name = data.get('name', 'custom_preset')
        params = data.get('params', {})
        description = data.get('description', '')
        
        # Create presets directory if it doesn't exist
        presets_dir = Path("presets")
        presets_dir.mkdir(exist_ok=True)
        
        # Save preset
        preset_file = presets_dir / f"{preset_name}.json"
        preset_data = {
            'name': preset_name,
            'description': description,
            'params': params,
            'created': datetime.now().isoformat()
        }
        
        with open(preset_file, 'w') as f:
            json.dump(preset_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Preset "{preset_name}" saved successfully',
            'file': str(preset_file)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/load_preset/<preset_name>', methods=['GET'])
def load_preset(preset_name):
    """Load a saved preset by name"""
    try:
        preset_file = Path("presets") / f"{preset_name}.json"
        
        if not preset_file.exists():
            return jsonify({'error': 'Preset not found'}), 404
        
        with open(preset_file, 'r') as f:
            preset_data = json.load(f)
        
        return jsonify({
            'success': True,
            'preset': preset_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/list_presets', methods=['GET'])
def list_presets():
    """List all saved presets"""
    try:
        presets_dir = Path("presets")
        presets_dir.mkdir(exist_ok=True)
        
        presets = []
        for preset_file in presets_dir.glob("*.json"):
            try:
                with open(preset_file, 'r') as f:
                    preset_data = json.load(f)
                    presets.append({
                        'name': preset_data.get('name', preset_file.stem),
                        'description': preset_data.get('description', ''),
                        'created': preset_data.get('created', ''),
                        'file': preset_file.name
                    })
            except Exception as e:
                print(f"Error loading preset {preset_file}: {e}")
        
        return jsonify({
            'success': True,
            'presets': presets
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_preset/<preset_name>', methods=['DELETE'])
def delete_preset(preset_name):
    """Delete a saved preset"""
    try:
        preset_file = Path("presets") / f"{preset_name}.json"
        
        if not preset_file.exists():
            return jsonify({'error': 'Preset not found'}), 404
        
        preset_file.unlink()
        
        return jsonify({
            'success': True,
            'message': f'Preset "{preset_name}" deleted successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/live_preview', methods=['POST'])
def live_preview():
    """Generate a quick preview GLB for real-time parameter changes"""
    try:
        params = request.get_json()
        
        # Use simplified geometry for faster generation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        preview_path = output_dir / f"preview_{timestamp}.glb"
        
        # Generate with reduced quality for speed
        generate_stone_setting(
            stone_shape=params.get('stone_shape', 'round'),
            stone_length=float(params.get('stone_length', 6.5)),
            stone_width=float(params.get('stone_width', 6.5)),
            stone_depth=float(params.get('stone_depth', 4.0)),
            prong_count=int(params.get('prong_count', 4)),
            prong_thickness_base=float(params.get('prong_thickness_base', 0.8)),
            prong_thickness_top=float(params.get('prong_thickness_top', 0.5)),
            setting_height=float(params.get('setting_height', 3.5)),
            prong_base_style=params.get('prong_base_style', 'gallery'),
            prong_base_width=float(params.get('prong_base_width', 1.2)),
            prong_base_height=float(params.get('prong_base_height', 1.0)),
            gallery_radius=float(params['gallery_radius']) if params.get('gallery_radius') else None,
            base_type=params.get('base_type', 'ring'),
            ring_outer_radius=float(params.get('ring_outer_radius', 8.5)),
            ring_inner_radius=float(params.get('ring_inner_radius', 5.0)),
            ring_thickness=float(params.get('ring_thickness', 2.0)),
            ring_penetration=float(params.get('ring_penetration', 0.2)),
            ring_profile=params.get('ring_profile', 'rounded'),
            ring_tube_radius=(float(params['ring_tube_radius']) if params.get('ring_tube_radius') not in (None, '', 'null') else None),
            debug_markers=bool(params.get('debug_markers', False)),
            designer_filename=str(preview_path),
            production_filename=None  # Skip production for preview
        )
        
        # Copy to stable preview filename
        stable_preview = output_dir / "preview.glb"
        import shutil
        shutil.copy(str(preview_path), str(stable_preview))
        
        return jsonify({
            'success': True,
            'preview_file': 'output/preview.glb',
            'timestamp': timestamp
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/batch_generate', methods=['POST'])
def batch_generate():
    """Generate multiple variations based on parameter ranges"""
    try:
        data = request.get_json()
        base_params = data.get('base_params', {})
        variations = data.get('variations', [])
        
        results = []
        
        for i, variation in enumerate(variations):
            # Merge base params with variation
            params = {**base_params, **variation}
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            designer_path = output_dir / f"batch_{i}_{timestamp}.glb"
            
            try:
                generate_stone_setting(
                    stone_shape=params.get('stone_shape', 'round'),
                    stone_length=float(params.get('stone_length', 6.5)),
                    stone_width=float(params.get('stone_width', 6.5)),
                    stone_depth=float(params.get('stone_depth', 4.0)),
                    prong_count=int(params.get('prong_count', 4)),
                    prong_thickness_base=float(params.get('prong_thickness_base', 0.8)),
                    prong_thickness_top=float(params.get('prong_thickness_top', 0.5)),
                    setting_height=float(params.get('setting_height', 3.5)),
                    base_type=params.get('base_type', 'ring'),
                    ring_outer_radius=float(params.get('ring_outer_radius', 8.5)),
                    ring_inner_radius=float(params.get('ring_inner_radius', 5.0)),
                    ring_thickness=float(params.get('ring_thickness', 2.0)),
                    ring_profile=params.get('ring_profile', 'rounded'),
                    designer_filename=str(designer_path),
                    production_filename=None
                )
                
                results.append({
                    'index': i,
                    'success': True,
                    'file': str(designer_path),
                    'params': variation
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'success': False,
                    'error': str(e),
                    'params': variation
                })
        
        return jsonify({
            'success': True,
            'total': len(variations),
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Production-friendly run: read PORT from env and disable debug unless explicitly set
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    print("🚀 Starting Parametric Stone Setting Generator Server")
    print(f"📱 Web UI: http://localhost:{port}")
    print(f"🔧 API: http://localhost:{port}/generate")
    print(f"👁️ Viewer: http://localhost:{port}/view.html")
    print(f"🎨 Interactive Editor: http://localhost:{port}/editor.html")
    print(f"🎛️ Parametric Editor (X,Y,Z): http://localhost:{port}/parametric_editor.html")
    print(f"⚡ Real-Time Editor: http://localhost:{port}/realtime.html")
    print(f"📚 Features: Presets, Live Preview, Transform Sync, Batch Generation")
    
    # When deployed with a production server (gunicorn), this block won't run.
    app.run(debug=debug, host='0.0.0.0', port=port)