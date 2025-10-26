# 💎 Parametric Stone Setting Generator

A web-based tool for creating parametric 3D stone settings for jewelry design. Generate customizable prong settings with different stone shapes, prong configurations, and base styles.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Web Server
```bash
python app.py
```

### 3. Open Web Interface
Navigate to: **http://localhost:5000**

## 🎯 Features

### **Stone Parameters**
- **Shape**: Round, Princess, Radiant
- **Size**: Length, Width, Depth (mm)
- **Positioning**: Automatic centering

### **Prong Configuration**
- **Count**: 2, 4, 6, or 8 prongs
- **Thickness**: Base and top thickness
- **Height**: Setting height control
- **Tilt**: Automatic inward tilt for stone security

### **Prong Base Styles**
- **Individual**: Each prong has its own base
- **Shared**: Prongs connected with bridges
- **Gallery**: Traditional gallery rail design

### **Base Options**
- **None**: Just prongs (for pendants/earrings)
- **Minimal**: Small platform base
- **Ring**: Full ring with finger hole

### **Output Files**
- **Designer GLB**: Includes stone for visualization
- **Production GLB**: Manufacturing-ready, watertight

## 🎨 Web Interface

### **Real-time Parameter Control**
- Slider controls with live value display
- Dropdown menus for categorical options
- Instant parameter validation

### **Quick Presets**
- **Solitaire**: Classic 4-prong round diamond
- **Halo**: 6-prong setting for halo rings  
- **Vintage**: Art deco princess cut design

### **3D Preview**
- Real-time 3D visualization
- Orbit controls (rotate, zoom, pan)
- Professional lighting setup
- Shadow rendering

### **Export Options**
- Generate 3D models (GLB files)
- Export parameter configurations
- Download production files

## 📁 File Structure

```
├── app.py                 # Flask web server
├── ui.html               # Web interface
├── view.html             # 3D viewer
├── main.py               # Command-line interface
├── parametric_setting_core.py  # Core 3D generation
├── requirements.txt      # Dependencies
├── examples/             # Preset configurations
│   ├── stone_setting_only.json
│   ├── ring_setting.json
│   └── shared_prong_base.json
└── output/              # Generated 3D files
    ├── designer.glb
    └── production.glb
```

## 🔧 API Endpoints

### **Generate Setting**
```http
POST /generate
Content-Type: application/json

{
  "stone_shape": "round",
  "stone_length": 6.5,
  "stone_width": 6.5,
  "stone_depth": 4.0,
  "prong_count": 4,
  "prong_thickness_base": 0.8,
  "prong_thickness_top": 0.5,
  "setting_height": 3.5,
  "prong_base_style": "gallery",
  "prong_base_width": 1.2,
  "prong_base_height": 1.0,
  "base_type": "minimal"
}
```

### **Get Presets**
```http
GET /presets
```

### **Health Check**
```http
GET /health
```

## 💻 Command Line Usage

For batch processing or automation:

```bash
# Edit parameters in example_params.json
python main.py
```

## 🛠️ Technical Details

### **3D Libraries**
- **Trimesh**: 3D geometry processing
- **NumPy**: Mathematical operations
- **Three.js**: Web 3D visualization

### **Web Framework**
- **Flask**: Python web server
- **CORS**: Cross-origin resource sharing
- **RESTful API**: JSON-based communication

### **File Formats**
- **GLB**: Binary glTF for 3D models
- **JSON**: Parameter configurations
- **HTML/CSS/JS**: Web interface

## 📐 Parameter Ranges

| Parameter | Min | Max | Default | Unit |
|-----------|-----|-----|---------|------|
| Stone Length | 3.0 | 15.0 | 6.5 | mm |
| Stone Width | 3.0 | 15.0 | 6.5 | mm |
| Stone Depth | 2.0 | 10.0 | 4.0 | mm |
| Prong Base Thickness | 0.3 | 2.0 | 0.8 | mm |
| Prong Top Thickness | 0.2 | 1.5 | 0.5 | mm |
| Setting Height | 1.5 | 8.0 | 3.5 | mm |
| Base Width | 0.5 | 3.0 | 1.2 | mm |
| Ring Outer Radius | 6.0 | 15.0 | 8.5 | mm |
| Ring Inner Radius | 3.0 | 10.0 | 5.0 | mm |

## 🎯 Use Cases

### **Jewelry Designers**
- Rapid prototyping of stone settings
- Client visualization and approval
- Design iteration and refinement

### **Manufacturers**
- Production-ready 3D models
- CNC/3D printing preparation
- Quality control and validation

### **Students/Educators**
- Learn parametric design principles
- Understand jewelry construction
- Explore 3D modeling concepts

## 🚀 Advanced Usage

### **Custom Presets**
Create your own preset configurations:

```json
{
  "name": "My Custom Setting",
  "description": "Custom configuration",
  "params": {
    "stone_shape": "radiant",
    "prong_count": 8,
    "prong_base_style": "gallery",
    "base_type": "ring"
  }
}
```

### **Batch Generation**
Generate multiple variations:

```python
from parametric_setting_core import generate_stone_setting

for count in [4, 6, 8]:
    generate_stone_setting(
        prong_count=count,
        designer_filename=f'setting_{count}_prong_designer.glb',
        production_filename=f'setting_{count}_prong_production.glb'
    )
```

## 📞 Support

For issues, questions, or contributions:
- Check the generated GLB files in the `output/` directory
- Verify parameters are within valid ranges
- Use the 3D viewer to inspect results
- Export parameter files for sharing configurations

---

**Happy designing! 💎✨**