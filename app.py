"""
Flask web server for the Parametric Stone Setting Generator UI
Provides REST API endpoints for the web interface
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import json
import os
from pathlib import Path
from parametric_setting_core import generate_stone_setting

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
            'ring_thickness': 2.0
        }
        
        for key, value in defaults.items():
            if key not in params:
                params[key] = value
        
        # Generate file paths
        designer_path = output_dir / "designer.glb"
        production_path = output_dir / "production.glb"
        
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
            designer_filename=str(designer_path),
            production_filename=str(production_path)
        )
        
        return jsonify({
            'success': True,
            'designer_file': 'output/designer.glb',
            'production_file': 'output/production.glb',
            'message': 'Stone setting generated successfully'
        })
        
    except Exception as e:
        print(f"Error generating stone setting: {e}")
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

if __name__ == '__main__':
    print("🚀 Starting Parametric Stone Setting Generator Server")
    print("📱 Web UI: http://localhost:5000")
    print("🔧 API: http://localhost:5000/generate")
    print("👁️ Viewer: http://localhost:5000/view.html")
    
    app.run(debug=True, host='0.0.0.0', port=5000)