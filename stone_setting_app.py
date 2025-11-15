"""
Flask Web Application for Parametric Stone Setting Generator
Interactive UI for creating custom jewelry stone settings
"""

from flask import Flask, render_template, request, jsonify, send_file
from parametric_stone_setting import create_parametric_stone_setting
import os
from pathlib import Path
import tempfile
import shutil

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Store session output directory
OUTPUT_DIR = Path('output')
OUTPUT_DIR.mkdir(exist_ok=True)

@app.route('/')
def index():
    """Render the main interface"""
    return render_template('stone_setting_interface.html')

@app.route('/generate', methods=['POST'])
def generate_setting():
    """Generate stone setting based on parameters"""
    try:
        # Get parameters from request
        data = request.json
        
        stone_shape = data.get('stoneShape', 'round')
        stone_length = float(data.get('stoneLength', 6.0))
        stone_width = float(data.get('stoneWidth', 6.0))
        stone_depth = float(data.get('stoneDepth', 7.2))
        prong_count = int(data.get('prongCount', 4))
        prong_thickness_base = float(data.get('prongThicknessBase', 0.4))
        prong_thickness_top = float(data.get('prongThicknessTop', 0.3))
        setting_height = float(data.get('settingHeight', 3.0))
        ring_size = float(data.get('ringSize', 17.0))
        ring_thickness = float(data.get('ringThickness', 2.0))
        
        # Generate the stone setting
        designer_path, production_path = create_parametric_stone_setting(
            stone_shape=stone_shape,
            stone_length=stone_length,
            stone_width=stone_width,
            stone_depth=stone_depth,
            prong_count=prong_count,
            prong_thickness_base=prong_thickness_base,
            prong_thickness_top=prong_thickness_top,
            setting_height=setting_height,
            ring_size=ring_size,
            ring_thickness=ring_thickness,
            output_dir=str(OUTPUT_DIR)
        )
        
        # Calculate collision warnings
        ring_radius = ring_size / 2
        pavilion_depth = stone_depth * 0.65
        vertical_collision_threshold = pavilion_depth - ring_thickness / 2 + 1.5
        
        stone_radius = max(stone_length, stone_width) / 2
        horizontal_collision_threshold = stone_radius + (prong_thickness_base / 2) + 0.2
        
        has_vertical_collision = setting_height < vertical_collision_threshold
        has_horizontal_collision = stone_radius < horizontal_collision_threshold
        
        warnings = []
        if has_vertical_collision:
            warnings.append(f"Vertical: Setting height {setting_height:.2f}mm < {vertical_collision_threshold:.2f}mm required")
        if has_horizontal_collision:
            warnings.append(f"Horizontal: Stone radius {stone_radius:.2f}mm, needs {horizontal_collision_threshold:.2f}mm clearance")
        
        return jsonify({
            'success': True,
            'designer_file': os.path.basename(designer_path),
            'production_file': os.path.basename(production_path),
            'warnings': warnings
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated GLB file"""
    file_path = OUTPUT_DIR / filename
    if file_path.exists():
        return send_file(str(file_path), as_attachment=True)
    else:
        return "File not found", 404

@app.route('/preview/<filename>')
def preview_file(filename):
    """Stream file for preview"""
    file_path = OUTPUT_DIR / filename
    if file_path.exists():
        return send_file(str(file_path), mimetype='model/gltf-binary')
    else:
        return "File not found", 404

if __name__ == '__main__':
    print("=" * 60)
    print("🎨 Stone Setting Generator - Web Interface")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    print("Starting server...")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
