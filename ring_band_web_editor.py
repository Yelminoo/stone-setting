"""
Ring Band Web Editor using Build123d
Interactive web interface for designing ring bands with real-time 3D preview
Uses OCP tessellation for web viewing
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from build123d import *
import tempfile
import os
import json
import trimesh
import numpy as np

app = Flask(__name__)
CORS(app)

# US Ring Size Chart (inner diameter in mm)
US_RING_SIZES = {
    7: 17.35,
    7.5: 17.77,
    8: 18.19,
    8.5: 18.61,
    9: 19.03,
    9.5: 19.43,
    10: 19.84
}

class RingBandGenerator:
    """Generate ring bands with Build123d"""
    
    @staticmethod
    def create_basic_band(ring_size_us, thickness, band_width):
        """Create a basic rectangular band - proper 3D ring with volume"""
        if ring_size_us not in US_RING_SIZES:
            raise ValueError(f"Size {ring_size_us} not supported")
        
        inner_diameter = US_RING_SIZES[ring_size_us]
        inner_radius = inner_diameter / 2
        
        # Create a torus-like ring by revolving a rectangle around the ring center
        with BuildPart() as ring:
            with BuildSketch(Plane.XZ) as profile:
                # Position rectangle at inner radius, with thickness extending outward
                center_x = inner_radius + thickness / 2
                Rectangle(
                    thickness,  # Radial thickness (how thick the band is from inside to outside)
                    band_width, # Height/width of the band
                    align=(Align.CENTER, Align.CENTER)
                ).move(Location((center_x, 0)))
            
            # Revolve 360 degrees around Y axis to create complete ring
            revolve(axis=Axis.Y)
        
        return ring.part
    
    @staticmethod
    def create_comfort_fit_band(ring_size_us, thickness, band_width, inner_radius_curve):
        """Create a comfort-fit band with rounded inner edge - proper 3D ring"""
        if ring_size_us not in US_RING_SIZES:
            raise ValueError(f"Size {ring_size_us} not supported")
        
        inner_diameter = US_RING_SIZES[ring_size_us]
        inner_radius = inner_diameter / 2
        
        # Validate radius
        max_radius = min(thickness, band_width) / 2 - 0.01
        if inner_radius_curve >= max_radius:
            inner_radius_curve = max_radius
        
        with BuildPart() as ring:
            with BuildSketch(Plane.XZ) as profile:
                center_x = inner_radius + thickness / 2
                RectangleRounded(
                    thickness, 
                    band_width,
                    inner_radius_curve,
                    align=(Align.CENTER, Align.CENTER)
                ).move(Location((center_x, 0)))
            
            # Revolve to create 3D ring with volume
            revolve(axis=Axis.Y)
        
        return ring.part
    
    @staticmethod
    def create_tapered_band(ring_size_us, thickness_top, thickness_bottom, band_width):
        """Create a tapered band (thicker on bottom/palm side) - proper 3D ring"""
        if ring_size_us not in US_RING_SIZES:
            raise ValueError(f"Size {ring_size_us} not supported")
        
        inner_diameter = US_RING_SIZES[ring_size_us]
        inner_radius = inner_diameter / 2
        
        with BuildPart() as ring:
            with BuildSketch(Plane.XZ) as profile:
                # Create trapezoid profile with proper 3D volume
                points = [
                    (inner_radius, -band_width/2),                           # Bottom inner
                    (inner_radius + thickness_bottom, -band_width/2),        # Bottom outer
                    (inner_radius + thickness_top, band_width/2),            # Top outer
                    (inner_radius, band_width/2),                            # Top inner
                ]
                
                with BuildLine() as trapezoid:
                    for i in range(len(points)):
                        Line(points[i], points[(i+1) % len(points)])
                
                make_face()
            
            # Revolve around Y axis to create 3D ring with tapered cross-section
            revolve(axis=Axis.Y)
        
        return ring.part
    
    @staticmethod
    def create_domed_band(ring_size_us, thickness, band_width, dome_height):
        """Create a band with domed outer surface"""
        if ring_size_us not in US_RING_SIZES:
            raise ValueError(f"Size {ring_size_us} not supported")
        
        inner_diameter = US_RING_SIZES[ring_size_us]
        inner_radius = inner_diameter / 2
        
        with BuildPart() as ring:
            with BuildSketch(Plane.XZ) as profile:
                bottom_inner = (inner_radius, -band_width/2)
                bottom_outer = (inner_radius + thickness, -band_width/2)
                center_peak = (inner_radius + thickness + dome_height, 0)
                top_outer = (inner_radius + thickness, band_width/2)
                top_inner = (inner_radius, band_width/2)
                
                with BuildLine() as dome_profile:
                    Line(bottom_inner, bottom_outer)
                    Bezier(bottom_outer, center_peak, top_outer)
                    Line(top_outer, top_inner)
                    Line(top_inner, bottom_inner)
                
                make_face()
            
            revolve(axis=Axis.Y)
        
        return ring.part


def build123d_to_glb(part):
    """Convert Build123d part to GLB format via STL"""
    # Create temporary STL file
    temp_stl = tempfile.NamedTemporaryFile(suffix='.stl', delete=False)
    temp_stl_path = temp_stl.name
    temp_stl.close()
    
    try:
        # Export to STL
        export_stl(part, temp_stl_path)
        
        # Load with trimesh
        mesh = trimesh.load(temp_stl_path)
        
        # Create temporary GLB file
        temp_glb = tempfile.NamedTemporaryFile(suffix='.glb', delete=False)
        temp_glb_path = temp_glb.name
        temp_glb.close()
        
        # Export to GLB
        mesh.export(temp_glb_path)
        
        return temp_glb_path
        
    finally:
        # Clean up STL file
        try:
            os.unlink(temp_stl_path)
        except:
            pass


@app.route('/')
def index():
    """Serve the main editor page"""
    return render_template('ring_band_editor.html')


@app.route('/generate', methods=['POST'])
def generate():
    """Generate ring band based on parameters"""
    try:
        data = request.json
        
        # Extract parameters
        band_type = data.get('band_type', 'basic')
        ring_size = float(data.get('ring_size', 8))
        thickness = float(data.get('thickness', 2.0))
        band_width = float(data.get('band_width', 3.0))
        
        # Create the appropriate band type
        generator = RingBandGenerator()
        
        if band_type == 'basic':
            ring = generator.create_basic_band(ring_size, thickness, band_width)
            
        elif band_type == 'comfort_fit':
            inner_curve = float(data.get('inner_curve', 0.5))
            ring = generator.create_comfort_fit_band(ring_size, thickness, band_width, inner_curve)
            
        elif band_type == 'tapered':
            thickness_top = float(data.get('thickness_top', 1.8))
            thickness_bottom = float(data.get('thickness_bottom', 2.5))
            ring = generator.create_tapered_band(ring_size, thickness_top, thickness_bottom, band_width)
            
        elif band_type == 'domed':
            dome_height = float(data.get('dome_height', 1.0))
            ring = generator.create_domed_band(ring_size, thickness, band_width, dome_height)
            
        else:
            return jsonify({'success': False, 'error': f'Unknown band type: {band_type}'})
        
        # Convert to GLB
        glb_path = build123d_to_glb(ring)
        
        # Get statistics
        inner_diameter = US_RING_SIZES[ring_size]
        
        stats = {
            'band_type': band_type,
            'ring_size_us': ring_size,
            'inner_diameter_mm': round(inner_diameter, 2),
            'thickness_mm': thickness,
            'band_width_mm': band_width,
        }
        
        # Read GLB file
        with open(glb_path, 'rb') as f:
            glb_data = f.read()
        
        # Clean up
        try:
            os.unlink(glb_path)
        except:
            pass
        
        # Return GLB file
        return send_file(
            io.BytesIO(glb_data),
            mimetype='model/gltf-binary',
            as_attachment=False,
            download_name='ring_band.glb'
        )
        
    except Exception as e:
        print(f"Error generating ring: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/export/<format>', methods=['POST'])
def export_file(format):
    """Export ring band to STEP or STL format"""
    try:
        data = request.json
        
        # Extract parameters
        band_type = data.get('band_type', 'basic')
        ring_size = float(data.get('ring_size', 8))
        thickness = float(data.get('thickness', 2.0))
        band_width = float(data.get('band_width', 3.0))
        
        # Create the appropriate band type
        generator = RingBandGenerator()
        
        if band_type == 'basic':
            ring = generator.create_basic_band(ring_size, thickness, band_width)
        elif band_type == 'comfort_fit':
            inner_curve = float(data.get('inner_curve', 0.5))
            ring = generator.create_comfort_fit_band(ring_size, thickness, band_width, inner_curve)
        elif band_type == 'tapered':
            thickness_top = float(data.get('thickness_top', 1.8))
            thickness_bottom = float(data.get('thickness_bottom', 2.5))
            ring = generator.create_tapered_band(ring_size, thickness_top, thickness_bottom, band_width)
        elif band_type == 'domed':
            dome_height = float(data.get('dome_height', 1.0))
            ring = generator.create_domed_band(ring_size, thickness, band_width, dome_height)
        else:
            return jsonify({'success': False, 'error': f'Unknown band type: {band_type}'})
        
        # Create temporary file
        if format.lower() == 'step':
            temp_file = tempfile.NamedTemporaryFile(suffix='.step', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            export_step(ring, temp_path)
            mimetype = 'application/step'
            filename = f'ring_band_{band_type}_size{ring_size}.step'
        elif format.lower() == 'stl':
            temp_file = tempfile.NamedTemporaryFile(suffix='.stl', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            export_stl(ring, temp_path)
            mimetype = 'model/stl'
            filename = f'ring_band_{band_type}_size{ring_size}.stl'
        else:
            return jsonify({'success': False, 'error': f'Unsupported format: {format}'}), 400
        
        # Send file
        response = send_file(
            temp_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
        # Clean up after sending
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(temp_path)
            except:
                pass
        
        return response
        
    except Exception as e:
        print(f"Error exporting: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/sizes')
def get_sizes():
    """Return available US ring sizes"""
    return jsonify({
        'sizes': [
            {'value': 7, 'label': 'US 7 (17.35mm)'},
            {'value': 7.5, 'label': 'US 7.5 (17.77mm)'},
            {'value': 8, 'label': 'US 8 (18.19mm)'},
            {'value': 8.5, 'label': 'US 8.5 (18.61mm)'},
            {'value': 9, 'label': 'US 9 (19.03mm)'},
            {'value': 9.5, 'label': 'US 9.5 (19.43mm)'},
            {'value': 10, 'label': 'US 10 (19.84mm)'},
        ]
    })


if __name__ == '__main__':
    import io
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    print("=" * 70)
    print("🎨 Ring Band Web Editor - Build123d Edition")
    print("=" * 70)
    print("\n🌐 Starting server on http://localhost:5003")
    print("📱 Open your browser and visit: http://localhost:5003")
    print("\n✨ Features:")
    print("   • Real-time 3D preview")
    print("   • 4 band profiles (Basic, Comfort-Fit, Tapered, Domed)")
    print("   • US ring sizing (7-10)")
    print("   • Export to STEP/STL formats")
    print("   • Build123d CAD-quality geometry")
    print("\n" + "=" * 70)
    
    app.run(host='0.0.0.0', port=5003, debug=True)
