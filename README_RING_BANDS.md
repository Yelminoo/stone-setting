# Ring Band Generator - Build123d Edition

## Overview
Professional CAD-quality ring band generator using Build123d (OpenCASCADE kernel) with support for multiple band profiles and US standard ring sizing.

## Features

### 4 Band Profiles
1. **Basic Band** - Simple rectangular cross-section
2. **Comfort-Fit Band** - Rounded inner edges for comfort
3. **Tapered Band** - Variable thickness (thicker toward palm)
4. **Domed Band** - Curved outer surface with Bezier profile

### US Standard Ring Sizing
- Sizes: 7, 7.5, 8, 8.5, 9, 9.5, 10
- Accurate inner diameter measurements (mm)
- Size 8 = 18.19mm inner diameter

## Installation

### Required Packages
```bash
pip install build123d ocp-vscode
```

### Optional: OCP CAD Viewer Extension
For viewing designs directly in VS Code:
1. Install "OCP CAD Viewer" extension in VS Code
2. Activate the extension
3. Use `designer.show()` to display rings

## Usage

### Basic Usage
```python
from ring_band_build123d import RingBandDesigner

designer = RingBandDesigner()

# Create a basic band
ring = designer.create_basic_band(
    ring_size_us=8,
    thickness=2.0,
    band_width=3.0
)

# Export to STEP format
designer.export("my_ring.step", format='step')

# View in VS Code (requires OCP CAD Viewer extension)
designer.show()
```

### Comfort-Fit Band
```python
ring = designer.create_comfort_fit_band(
    ring_size_us=8.5,
    thickness=2.5,
    band_width=4.0,
    inner_radius_curve=0.8  # Rounded inner edge
)
```

### Tapered Band
```python
ring = designer.create_tapered_band(
    ring_size_us=9,
    thickness_top=1.8,      # Top surface
    thickness_bottom=2.5,   # Palm side (thicker)
    band_width=4.0
)
```

### Domed Band
```python
ring = designer.create_domed_band(
    ring_size_us=9.5,
    thickness=2.5,
    band_width=4.5,
    dome_height=1.2  # Curved outer surface
)
```

## File Formats

### STEP Format (.step)
- Industry-standard CAD format
- Preserves exact geometry
- Best for: FreeCAD, OnShape, Fusion 360, SolidWorks
- Recommended for professional use

### STL Format (.stl)
- Mesh/tessellation format
- Good for 3D printing
- Can be imported into any 3D software

## Viewing Your Designs

### Option 1: VS Code with OCP CAD Viewer
```python
designer.show()  # Displays in VS Code
```

### Option 2: FreeCAD (Free & Open Source)
1. Download: https://www.freecad.org/
2. Open STEP file: `File → Open`
3. View, measure, modify as needed

### Option 3: OnShape (Web-based, Free)
1. Visit: https://www.onshape.com/
2. Upload STEP file
3. View in browser

## Running the Demo
```bash
python ring_band_build123d.py
```

This creates:
- `ring_basic_size8_b3d.step` - Basic band, size 8
- `ring_comfort_size8p5_b3d.step` - Comfort-fit band, size 8.5
- `ring_tapered_size9_b3d.step` - Tapered band, size 9
- `ring_domed_size9p5_b3d.step` - Domed band, size 9.5

## Parameter Guidelines

### Thickness
- Typical: 1.5mm - 3.0mm
- Thin: < 1.5mm (delicate)
- Heavy: > 3.0mm (statement piece)

### Band Width
- Narrow: 2-3mm
- Standard: 3-5mm
- Wide: 6-10mm

### Inner Radius Curve (Comfort-Fit)
- Must be < min(thickness, band_width) / 2
- Typical: 0.5mm - 1.0mm
- Automatic validation included

### Dome Height
- Subtle: 0.5mm - 0.8mm
- Standard: 1.0mm - 1.5mm
- Dramatic: > 1.5mm

## Technical Details

### Build123d Constructs Used
- `BuildPart` - 3D solid modeling
- `BuildSketch` - 2D profile creation
- `revolve()` - Revolution around Y-axis
- `Bezier` - Smooth curved surfaces
- `RectangleRounded` - Comfort-fit profiles

### Coordinate System
- **X-axis**: Radial direction
- **Y-axis**: Revolution axis (vertical)
- **Z-axis**: Ring width direction
- Profile created in XZ plane, revolved around Y

### Precision
- OpenCASCADE kernel (industry standard)
- STEP format preserves exact geometry
- No mesh approximation in STEP files

## Integration with Stone Settings

You can combine ring bands with stone settings:

```python
# Create band
from ring_band_build123d import RingBandDesigner
band_designer = RingBandDesigner()
band = band_designer.create_basic_band(ring_size_us=8, thickness=2.0, band_width=3.0)

# Create stone setting (from stone_setting_build123d.py)
from stone_setting_build123d import create_stone_setting_b3d
setting = create_stone_setting_b3d(
    stone_shape='round',
    stone_size=5.0,
    prong_count=4
)

# Combine them using build123d operations
# (Advanced: requires positioning and union operations)
```

## Troubleshooting

### "Viewer not available"
- Install OCP CAD Viewer extension in VS Code
- Or: Export to STEP and view in FreeCAD/OnShape

### "width and height must be > 2*radius"
- Reduce `inner_radius_curve` parameter
- Must be less than half of smallest dimension
- Automatic validation will adjust if needed

### Large File Sizes
- STEP files are small (< 10KB typically)
- STL files are larger (mesh format)
- GLB exports can be 100KB+ depending on tessellation

## Comparison: Trimesh vs Build123d

### Trimesh Version (`ring_band_generator.py`)
- ✅ Exports GLB for web viewing
- ✅ Works with Three.js viewer
- ❌ Manual vertex/face construction
- ❌ Less precise for complex curves

### Build123d Version (`ring_band_build123d.py`)
- ✅ CAD-quality precision
- ✅ Industry-standard STEP format
- ✅ Complex curves (Bezier, splines)
- ✅ Native CAD operations
- ❌ Requires conversion for web viewing

## Best Practices

1. **Export STEP files** for archival and professional use
2. **Use comfort-fit** for rings worn daily
3. **Tapered bands** are more comfortable (thicker on palm side)
4. **Test sizing** - print a sizing band first
5. **Document parameters** used for each design

## US Ring Size Reference

| US Size | Inner Diameter (mm) | Circumference (mm) |
|---------|--------------------|--------------------|
| 7       | 17.35              | 54.51              |
| 7.5     | 17.75              | 55.76              |
| 8       | 18.19              | 57.15              |
| 8.5     | 18.53              | 58.22              |
| 9       | 19.03              | 59.79              |
| 9.5     | 19.41              | 60.98              |
| 10      | 19.84              | 62.33              |

## License
Part of the Python-CAD-3D project.

## Support
For issues or questions, check:
- Build123d docs: https://build123d.readthedocs.io/
- FreeCAD forum: https://forum.freecad.org/
- This project's documentation
