# Ring Band Web Editor - Build123d Edition

## 🎨 Professional CAD-Quality Web-Based Ring Designer

A modern, interactive web application for designing ring bands with real-time 3D preview, powered by Build123d's OpenCASCADE kernel.

## 🚀 Features

### Interactive 3D Viewer
- **Real-time rendering** using Three.js WebGL
- **OrbitControls** for intuitive navigation (drag to rotate, scroll to zoom)
- **Professional materials** with metalness and roughness
- **Dynamic lighting** with multiple light sources
- **Smooth animations** and responsive interface

### 4 Professional Band Profiles

1. **Basic Band** (Rectangular)
   - Simple, classic rectangular cross-section
   - Clean lines, modern aesthetic
   - Parameters: thickness, band width

2. **Comfort-Fit Band** (Rounded Inner)
   - Rounded inner edges using `RectangleRounded`
   - More comfortable for daily wear
   - Auto-validates curve radius to prevent geometry errors
   - Parameters: thickness, band width, inner curve radius

3. **Tapered Band** (Thicker on Palm)
   - Variable thickness - thinner on top, thicker on palm side
   - Trapezoid profile for comfort and durability
   - Distributes weight for better balance
   - Parameters: thickness top, thickness bottom, band width

4. **Domed Band** (Curved Outer)
   - Elegant curved outer surface using Bezier curves
   - Classic jewelry design aesthetic
   - Smooth, flowing profile
   - Parameters: thickness, band width, dome height

### US Standard Ring Sizing
- **7 sizes**: US 7, 7.5, 8, 8.5, 9, 9.5, 10
- **Accurate dimensions**: Inner diameter in mm
- **Easy selection**: Dropdown with size and diameter
- **Reference chart** in documentation

### CAD-Quality Export
- **STEP format**: Industry-standard CAD (4-5KB files)
  - Preserves exact geometry
  - Compatible with: FreeCAD, OnShape, Fusion 360, SolidWorks, Rhino
  - Best for professional jewelry CAD work
  
- **STL format**: 3D printing ready
  - Mesh/tessellation format
  - Compatible with all 3D printing slicers
  - Good for rapid prototyping

### Live Statistics
- Real-time parameter display
- Band type, ring size, dimensions
- Inner diameter calculation
- Instant updates on parameter changes

## 📦 Installation

### Prerequisites
```bash
# Python 3.10 or higher
python --version

# Install required packages
pip install build123d flask flask-cors trimesh
```

### Quick Start
```bash
# Navigate to project directory
cd Python-CAD-3D

# Start the server
python ring_band_web_editor.py

# Open browser
# Visit: http://localhost:5003
```

## 🎯 Usage Guide

### 1. Select Band Profile
Choose from the dropdown:
- **Basic Band**: Simple rectangular band
- **Comfort-Fit**: Rounded inner edge
- **Tapered**: Variable thickness
- **Domed**: Curved outer surface

### 2. Choose Ring Size
Select US size (7-10) from dropdown
- Displays inner diameter in mm
- Standard US ring sizing chart

### 3. Adjust Dimensions

#### Basic Band
- **Thickness**: 1.0 - 5.0mm (default: 2.0mm)
- **Band Width**: 2.0 - 10.0mm (default: 3.0mm)

#### Comfort-Fit Band
- Same as Basic, plus:
- **Inner Curve**: 0.3 - 1.5mm (default: 0.5mm)
- Auto-limited to prevent geometry errors
- Must be < min(thickness, width) / 2

#### Tapered Band
- **Thickness Top**: 1.0 - 4.0mm (default: 1.8mm)
- **Thickness Bottom**: 1.5 - 5.0mm (default: 2.5mm)
- **Band Width**: 2.0 - 10.0mm (default: 4.0mm)
- Recommend: bottom > top for comfort

#### Domed Band
- **Thickness**: 1.0 - 5.0mm (default: 2.5mm)
- **Band Width**: 2.0 - 10.0mm (default: 4.5mm)
- **Dome Height**: 0.3 - 2.5mm (default: 1.0mm)
- Higher dome = more dramatic curve

### 4. Generate Ring
Click "🔄 Generate Ring Band" button
- 3D model appears in viewer
- Statistics panel updates
- Ready to export

### 5. Export Design
Click format buttons:
- **📐 STEP**: For CAD software
- **🖨️ STL**: For 3D printing

Files download automatically with descriptive names:
```
ring_band_basic_size8.step
ring_band_comfort_fit_size8p5.stl
```

## 🎨 3D Viewer Controls

### Mouse Controls
- **Left Click + Drag**: Rotate view
- **Right Click + Drag**: Pan view
- **Scroll Wheel**: Zoom in/out
- **Double Click**: Reset view (if supported)

### Viewing Tips
- Zoom in to see fine details
- Rotate to view from all angles
- Pan to center the design
- Check inner curve profile from side view

## 🏗️ Architecture

### Backend (Flask + Build123d)
```
ring_band_web_editor.py
├── Flask web server (port 5003)
├── RingBandGenerator class
│   ├── create_basic_band()
│   ├── create_comfort_fit_band()
│   ├── create_tapered_band()
│   └── create_domed_band()
├── build123d_to_glb() - Conversion pipeline
└── Routes:
    ├── GET  /           - Serve HTML
    ├── POST /generate   - Create 3D model
    ├── POST /export/step - Export STEP
    ├── POST /export/stl  - Export STL
    └── GET  /sizes      - Ring size data
```

### Frontend (Three.js + Vanilla JS)
```
templates/ring_band_editor.html
├── Three.js WebGL renderer
├── OrbitControls
├── GLTFLoader
├── Real-time parameter UI
├── Dynamic form generation
└── Export functionality
```

### Data Flow
```
User Input → Flask API → Build123d CAD
    ↓                         ↓
Parameters              Part object
    ↓                         ↓
JSON Request           STL export
    ↓                         ↓
Flask Response         Trimesh load
    ↓                         ↓
GLB Binary             GLB export
    ↓                         ↓
Three.js Loader        3D Viewer
    ↓
Rendered Ring
```

## 🔧 Technical Details

### Build123d Integration
- **OpenCASCADE kernel**: Industry-standard CAD
- **Parametric modeling**: All dimensions adjustable
- **Precise geometry**: No approximations in STEP files
- **Complex curves**: Bezier, splines, fillets

### Conversion Pipeline
```python
Build123d Part → STL (temp) → Trimesh → GLB → Web Viewer
```

Why this pipeline:
1. Build123d exports clean STL
2. Trimesh handles mesh operations
3. GLB is Three.js native format
4. Efficient web transmission

### Material Rendering
```javascript
{
    color: 0xE8E8E8,     // Bright silver
    metalness: 0.9,      // High metallic
    roughness: 0.2,      // Low roughness (shiny)
}
```

### Performance
- **Generation time**: 1-3 seconds per ring
- **GLB file size**: 50-150KB
- **STEP file size**: 4-5KB
- **STL file size**: varies by tessellation

## 📊 Ring Size Reference

| US Size | Inner Diameter (mm) | Circumference (mm) | UK/AU Size |
|---------|--------------------|--------------------|------------|
| 7       | 17.35              | 54.51              | N          |
| 7.5     | 17.77              | 55.76              | O          |
| 8       | 18.19              | 57.15              | P          |
| 8.5     | 18.61              | 58.22              | Q          |
| 9       | 19.03              | 59.79              | R          |
| 9.5     | 19.43              | 60.98              | S          |
| 10      | 19.84              | 62.33              | T          |

## 🎓 Design Guidelines

### Thickness Recommendations
- **Delicate**: 1.5mm - 2.0mm (women's fashion rings)
- **Standard**: 2.0mm - 2.5mm (everyday wear)
- **Heavy**: 2.5mm - 3.5mm (men's rings, statement pieces)
- **Chunky**: 3.5mm+ (bold designs)

### Band Width Recommendations
- **Narrow**: 2-3mm (delicate, feminine)
- **Standard**: 3-5mm (universal, balanced)
- **Wide**: 6-8mm (bold, masculine)
- **Statement**: 8-10mm (architectural designs)

### Profile Selection Guide

**Basic Band** - Best for:
- Modern, minimalist designs
- Engraving projects
- Budget-conscious projects
- Clean, architectural aesthetic

**Comfort-Fit** - Best for:
- Daily wear rings (wedding bands)
- Active lifestyle
- Sensitive skin
- Maximum comfort priority

**Tapered Band** - Best for:
- Wedding bands
- All-day wear
- Rings with top detail/stones
- Ergonomic design

**Domed Band** - Best for:
- Classic jewelry aesthetic
- Vintage-inspired designs
- Elegant, refined look
- Traditional wedding bands

## 🚨 Troubleshooting

### Ring Not Generating
**Symptoms**: Click generate, nothing happens
**Solutions**:
1. Check browser console (F12) for errors
2. Ensure server is running (check terminal)
3. Try refreshing page (Ctrl+R)
4. Check parameter values are valid

### "width and height must be > 2*radius" Error
**Cause**: Comfort-fit curve radius too large
**Solution**:
- Reduce inner curve slider
- Auto-validation should prevent this
- Max curve = min(thickness, width) / 2 - 0.01mm

### Export Button Stuck on "Exporting..."
**Cause**: Server timeout or error
**Solutions**:
1. Wait 30 seconds for timeout
2. Check server terminal for errors
3. Try generating ring again
4. Restart server if persistent

### Viewer Shows Black Screen
**Cause**: WebGL not available or material issue
**Solutions**:
1. Update graphics drivers
2. Try different browser (Chrome, Firefox, Edge)
3. Check WebGL support: https://get.webgl.org/
4. Disable hardware acceleration (last resort)

### Server Won't Start (Port 5003 in use)
**Solution**:
```bash
# Windows
Stop-Process -Name python -Force

# Or change port in code
app.run(host='0.0.0.0', port=5004, debug=True)
```

## 🔌 API Reference

### POST /generate
Generate ring band and return GLB model

**Request**:
```json
{
  "band_type": "basic",
  "ring_size": 8.0,
  "thickness": 2.0,
  "band_width": 3.0
}
```

**Response**: Binary GLB file (model/gltf-binary)

### POST /export/step
Export ring as STEP file

**Request**: Same as /generate
**Response**: Binary STEP file (application/step)

### POST /export/stl
Export ring as STL file

**Request**: Same as /generate
**Response**: Binary STL file (model/stl)

### GET /sizes
Get available ring sizes

**Response**:
```json
{
  "sizes": [
    {"value": 7, "label": "US 7 (17.35mm)"},
    ...
  ]
}
```

## 🎯 Future Enhancements

### Planned Features
- [ ] More ring sizes (5-13)
- [ ] Custom inner diameter input
- [ ] Pattern/texture options
- [ ] Stone setting integration
- [ ] Material presets (gold, platinum, titanium)
- [ ] Engraving preview
- [ ] Band combining (stack multiple bands)
- [ ] Save/load designs (JSON)
- [ ] Share designs (URL parameters)
- [ ] Screenshot/render export

### Advanced CAD Features
- [ ] Filet edges
- [ ] Channel cut (for stone channel)
- [ ] Milgrain edges
- [ ] Celtic knot patterns
- [ ] Custom profile import (SVG)

## 📝 Comparison: Web Editor vs Desktop Script

### Web Editor (`ring_band_web_editor.py`)
✅ Browser-based, no software install
✅ Real-time 3D preview
✅ Intuitive sliders and dropdowns
✅ Immediate visual feedback
✅ Share URL with others
❌ Requires internet/local server
❌ Limited to implemented features

### Desktop Script (`ring_band_build123d.py`)
✅ Full Build123d power
✅ Programmable/scriptable
✅ Custom modifications easy
✅ No browser required
✅ Batch processing possible
❌ Need Python knowledge
❌ No visual preview (unless using viewer)

**Recommendation**: 
- **Designers/Clients**: Use web editor
- **Engineers/Developers**: Use desktop script
- **Both**: Best of both worlds!

## 📚 Related Documentation
- `README_RING_BANDS.md` - Desktop script guide
- `ring_band_build123d.py` - Python implementation
- Build123d docs: https://build123d.readthedocs.io/
- Three.js docs: https://threejs.org/docs/

## 🤝 Integration Examples

### Combine with Stone Settings
```python
# In ring_band_web_editor.py, add:
from stone_setting_build123d import create_stone_setting_b3d

def create_ring_with_stone(ring_params, stone_params):
    # Create band
    band = generator.create_basic_band(
        ring_params['ring_size'],
        ring_params['thickness'],
        ring_params['band_width']
    )
    
    # Create setting
    setting = create_stone_setting_b3d(
        stone_shape=stone_params['shape'],
        stone_size=stone_params['size'],
        prong_count=stone_params['prongs']
    )
    
    # Position and combine
    # (requires additional Build123d operations)
    
    return combined_ring
```

## 📄 License
Part of the Python-CAD-3D project.

## 🙏 Credits
- **Build123d**: OpenCASCADE Python wrapper
- **Three.js**: 3D rendering engine
- **Flask**: Python web framework
- **Trimesh**: Mesh processing library

---

**Made with ❤️ for jewelry designers and CAD enthusiasts**

Need help? Open an issue or check the troubleshooting section above.
