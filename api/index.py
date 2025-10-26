"""
Vercel serverless function for stone setting API
"""

from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'status': 'healthy', 
                'service': 'Stone Setting Generator API (Serverless)'
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/api/presets':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
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
            
            self.wfile.write(json.dumps(presets).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/generate':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                params = json.loads(post_data.decode('utf-8'))
                
                # Validate required parameters
                required_params = [
                    'stone_shape', 'stone_length', 'stone_width', 'stone_depth',
                    'prong_count', 'prong_thickness_base', 'prong_thickness_top', 'setting_height'
                ]
                
                for param in required_params:
                    if param not in params:
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        response = {'error': f'Missing required parameter: {param}'}
                        self.wfile.write(json.dumps(response).encode())
                        return
                
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
                
                # Return processed parameters
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    'success': True,
                    'message': 'Parameters processed successfully',
                    'parameters': params,
                    'note': 'File generation not available in serverless environment'
                }
                
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {'error': str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()