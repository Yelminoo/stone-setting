"""
Vercel serverless function for generating stone settings
"""

from flask import Flask, request, jsonify
import json
import sys
import os
from pathlib import Path

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from parametric_setting_core import generate_stone_setting
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback for serverless environment
    def generate_stone_setting(**kwargs):
        raise Exception("Stone setting generation not available in serverless environment")

app = Flask(__name__)

@app.route('/api/generate', methods=['POST'])
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
        
        # For serverless, we'll return the parameters instead of generating files
        # This is because file generation requires heavy 3D libraries
        return jsonify({
            'success': True,
            'message': 'Parameters processed successfully',
            'parameters': params,
            'note': 'File generation not available in serverless environment'
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/presets', methods=['GET'])
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Stone Setting Generator API (Serverless)'})

# Export the Flask app for Vercel
def handler(request):
    return app(request)