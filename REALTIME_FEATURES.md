# Real-Time Parametric Stone Setting Editor

## 🚀 New Features from JavaScript to Python Integration

This enhanced system brings real-time manipulation, parameter management, and advanced features from the JavaScript editor to the Python parametric setting system.

---

## ✨ Key Features

### 1. **Real-Time Transform Updates** 
- **Live X, Y, Z manipulation** of objects in 3D viewport
- Transform controls for translate, rotate, and scale modes
- Automatic sync of transformations to backend server
- Visual feedback with coordinate display

### 2. **Parameter Presets System**
- **Save current parameters** as named presets
- **Load presets** instantly from saved library
- **Delete presets** you no longer need
- Automatic preset list refresh
- Preset metadata (name, description, creation date)

### 3. **Live Preview Mode**
- **Auto-preview** with 500ms debounce on parameter changes
- Toggle auto-preview on/off
- Manual update button for fine control
- Optimized preview generation (faster than full model)

### 4. **Batch Generation**
- Generate **multiple variations** from parameter ranges
- Base parameters + variation arrays
- Parallel processing support
- Results tracking with success/error reporting

### 5. **Enhanced Export Options**
- **Export parameters** as JSON file
- **Download generated GLB** models
- Timestamped filenames to avoid collisions
- Stable filenames for consistent loading

### 6. **Collision Detection**
- Visual warning when objects overlap
- Real-time collision checking
- Penetration depth calculation

### 7. **Debug Mode**
- Show/hide coordinate markers
- Visual axes (X=red, Y=green, Z=blue)
- Transform display panel
- Status messages (success/error/info)

---

## 📡 New API Endpoints

### `/update_transform` (POST)
Real-time update of object transforms
```json
{
  "object_name": "Stone",
  "transform": {
    "position": {"x": 0, "y": 9.5, "z": 0},
    "rotation": {"x": 1.57, "y": 0, "z": 0},
    "scale": {"x": 1, "y": 1, "z": 1}
  }
}
```

### `/save_preset` (POST)
Save current parameters as named preset
```json
{
  "name": "my_custom_setting",
  "description": "6-prong halo with thin band",
  "params": { /* all stone setting parameters */ }
}
```

### `/load_preset/<preset_name>` (GET)
Load a saved preset by name

### `/list_presets` (GET)
Get list of all saved presets

### `/delete_preset/<preset_name>` (DELETE)
Delete a preset

### `/live_preview` (POST)
Generate quick preview for real-time parameter changes
```json
{
  "stone_width": 6.5,
  "stone_length": 6.5,
  "ring_outer_radius": 9.0,
  /* other parameters */
}
```

### `/batch_generate` (POST)
Generate multiple variations
```json
{
  "base_params": {
    "stone_shape": "round",
    "stone_width": 6.0,
    /* base parameters */
  },
  "variations": [
    {"prong_count": 4, "setting_height": 3.0},
    {"prong_count": 6, "setting_height": 3.5},
    {"prong_count": 8, "setting_height": 4.0}
  ]
}
```

---

## 🎮 User Interface Features

### Control Panel
- **Stone Parameters**: Shape, width, length, depth with live sliders
- **Ring Parameters**: Outer radius, tube radius with visual feedback
- **Prong Parameters**: Count, thickness, height with real-time update
- **Auto Preview**: Toggle for automatic regeneration
- **Debug Markers**: Show coordinate system and attachment points

### 3D Viewport
- **OrbitControls**: Rotate, pan, zoom camera
- **TransformControls**: Select and manipulate objects
- **Grid and Axes**: Spatial reference
- **Real-time Rendering**: Smooth 60 FPS animation
- **Shadow Mapping**: Realistic lighting

### Status Display
- Color-coded messages (success/error/info)
- Transform coordinates display
- Loading indicator with spinner
- Collision warnings

---

## 🔧 Technical Implementation

### Frontend (realtime_editor.html)
- **Three.js r160** for 3D rendering
- **OrbitControls** for camera manipulation
- **TransformControls** for object transforms
- **GLTFLoader** for loading generated models
- Modular ES6 imports
- Responsive CSS Grid layout

### Backend (app.py)
- **Flask REST API** with CORS support
- **Trimesh** for 3D geometry generation
- **JSON** parameter serialization
- File system storage for presets
- Timestamped output management
- Error handling and validation

### Data Flow
```
User Input → UI Sliders → getCurrentParams() → POST /live_preview
                                                    ↓
                                          parametric_setting_core.py
                                                    ↓
                                            Generate GLB File
                                                    ↓
                                          Return file path
                                                    ↓
                            Load with GLTFLoader → Render in Three.js
                                                    ↓
                            User Manipulates → TransformControls
                                                    ↓
                                POST /update_transform → Store state
```

---

## 📁 File Structure

```
Python-CAD-3D/
├── app.py                      # Flask server with new endpoints
├── parametric_setting_core.py  # Core geometry generator
├── realtime_editor.html        # New real-time editor UI
├── interactive_editor.html     # Original drag-and-drop editor
├── view.html                   # Simple GLB viewer
├── presets/                    # Saved parameter presets
│   ├── solitaire.json
│   ├── halo.json
│   └── vintage.json
└── output/                     # Generated GLB files
    ├── designer.glb           # Latest designer model
    ├── production.glb         # Latest production model
    └── preview.glb            # Latest preview model
```

---

## 🚦 Quick Start

### 1. Start the Server
```bash
cd d:\Python-CAD-3D
.venv\Scripts\Activate.ps1
python app.py
```

### 2. Open Real-Time Editor
```
http://localhost:5000/realtime.html
```

### 3. Adjust Parameters
- Use sliders to modify stone, ring, and prong dimensions
- Toggle **Auto Preview** to see changes instantly
- Click **Generate Full Model** for high-quality output

### 4. Save Your Work
- Click **Save Preset** to store current parameters
- Give it a name and description
- Load it later from the preset list

### 5. Export Results
- **Export JSON**: Download parameter file
- **Download GLB**: Get the 3D model file

---

## 🎯 Workflow Examples

### Example 1: Create Custom Setting
1. Load the real-time editor
2. Adjust stone size: 7mm width, 7mm length, 4.5mm depth
3. Set ring outer radius: 10mm
4. Choose 6 prongs
5. Click **Update Preview** to see result
6. Adjust until satisfied
7. Click **Generate Full Model**
8. Download GLB file

### Example 2: Design Variations
1. Set base parameters for your design
2. Use batch generate API:
```bash
curl -X POST http://localhost:5000/batch_generate \
  -H "Content-Type: application/json" \
  -d '{
    "base_params": {
      "stone_width": 6.0,
      "ring_outer_radius": 9.0
    },
    "variations": [
      {"prong_count": 4},
      {"prong_count": 6},
      {"prong_count": 8}
    ]
  }'
```
3. Compare generated variations

### Example 3: Save and Reuse
1. Create a design you like
2. Click **Save Preset**
3. Name it "my_engagement_ring"
4. Later, click **Refresh List**
5. Click **Load** on your preset
6. Modify and generate new variations

---

## 🎨 UI Color Scheme

- **Background**: Dark navy (#1a1a2e)
- **Panel**: Deep blue (#16213e)
- **Accent**: Teal (#4ecca3)
- **Gradient**: Purple to blue (#667eea → #764ba2)
- **Success**: Green (#4ecca3)
- **Error**: Red (#ff6b6b)
- **Info**: Cyan (#4ecdc4)

---

## ⚡ Performance Tips

1. **Enable Auto Preview** only when making fine adjustments
2. **Disable Debug Markers** for faster rendering
3. Use **Live Preview** for quick iterations
4. Use **Generate Full Model** only for final output
5. Lower **prong_taper_sections** for faster preview (add to params)

---

## 🔗 Integration with Python Backend

### Shared Parameters
All parameters from `interactive_editor.html` are now compatible with Python backend:
- Stone: shape, width, length, depth
- Ring: outer radius, inner radius, tube radius, thickness, profile
- Prongs: count, thickness (base/top), height
- Layout: Tubular ring at Z=0, stone at Y=radius+offset, horizontal prong connections

### Coordinate System Alignment
- **Z-axis**: Vertical (up)
- **XY-plane**: Horizontal
- **Ring**: Torus centered at origin (0, 0, 0)
- **Stone**: Positioned at (0, Y_offset, 0) with 90° X rotation
- **Prongs**: Connect horizontally from stone to ring

---

## 🐛 Debugging

### Enable Debug Mode
1. Check "Show Debug Markers" in UI
2. See coordinate axes and attachment points
3. View transform coordinates in panel

### Server Logs
```bash
# Terminal output shows:
- Function call banners
- Coordinate calculations
- Prong generation details
- File save confirmations
```

### Browser Console
```javascript
// Check loaded model
console.log(loadedModel);

// View current parameters
console.log(getCurrentParams());

// Monitor transform updates
transformControls.addEventListener('objectChange', () => {
  console.log('Transform changed');
});
```

---

## 📚 API Reference

### Parameter Types
```typescript
interface StoneParams {
  stone_shape: 'round' | 'princess' | 'oval' | 'emerald';
  stone_width: number;    // mm, 2-15
  stone_length: number;   // mm, 2-15
  stone_depth: number;    // mm, 1-10
}

interface RingParams {
  ring_outer_radius: number;    // mm, 5-15
  ring_inner_radius: number;    // mm, computed
  ring_tube_radius: number;     // mm, 0.3-2
  ring_thickness: number;       // mm, 1-5
  ring_profile: 'flat' | 'rounded';
}

interface ProngParams {
  prong_count: number;              // 3-8
  prong_thickness_base: number;     // mm, 0.3-2
  prong_thickness_top: number;      // mm, computed
  setting_height: number;           // mm, 1-8
}

interface Transform {
  position: {x: number, y: number, z: number};
  rotation: {x: number, y: number, z: number};  // radians
  scale: {x: number, y: number, z: number};
}
```

---

## 🎓 Advanced Features

### Custom Geometry Functions
```python
# In parametric_setting_core.py

def create_custom_prong_shape(params):
    """Create custom prong geometry"""
    # Your custom implementation
    pass

# Use in generate_stone_setting()
```

### WebSocket Support (Future)
```javascript
// Real-time collaboration
const ws = new WebSocket('ws://localhost:5000/ws');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  applyRemoteTransform(update);
};
```

### Material Customization
```javascript
// In realtime_editor.html
loadedModel.traverse((child) => {
  if (child.isMesh) {
    child.material = new THREE.MeshPhysicalMaterial({
      color: 0xffd700,  // Gold
      metalness: 0.9,
      roughness: 0.1
    });
  }
});
```

---

## 🤝 Contributing

### Adding New Parameters
1. Add UI control in `realtime_editor.html`
2. Update `getCurrentParams()` function
3. Add parameter to `parametric_setting_core.py`
4. Update API validation in `app.py`
5. Test end-to-end workflow

### Adding New Endpoints
1. Define route in `app.py`
2. Add corresponding UI function
3. Update this documentation
4. Add error handling

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🆘 Support

- **Issues**: File on GitHub repository
- **Documentation**: This README + code comments
- **Examples**: See `presets/` directory

---

## 🎉 Enjoy Creating Beautiful Stone Settings!

The real-time editor combines the best of both worlds:
- **Python**: Precise geometric calculations and production-ready output
- **JavaScript**: Interactive real-time visualization and manipulation

Happy designing! 💎✨
