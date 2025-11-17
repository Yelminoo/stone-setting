# Stone Setting Generator - build123d Version

## Overview
This is a complete rewrite of the stone setting generator using **build123d**, a modern Python CAD library.

## Files Created

### 1. `stone_setting_build123d.py`
Core CAD functions using build123d:
- `create_ring_b3d()` - Ring band with torus shape
- `create_brilliant_cut_diamond_b3d()` - Round diamond
- `create_princess_cut_diamond_b3d()` - Square diamond
- `create_radiant_cut_diamond_b3d()` - Octagonal (beveled square) diamond
- `create_single_prong_b3d()` - Individual tapered prong
- `create_prongs_b3d()` - Complete prong assembly
- `create_stone_setting_b3d()` - Main function to generate complete setting

### 2. `editor_app_build123d.py`
Flask web server for interactive editing (runs on port 5002)

## Usage

### Command Line
```bash
python stone_setting_build123d.py
```
Generates STEP and STL files with default parameters in `output/` folder.

### Web Interface
```bash
python editor_app_build123d.py
```
Open browser at: http://127.0.0.1:5002

## Advantages of build123d

1. **Modern API** - Clean, Pythonic syntax
2. **Parametric** - Easy to modify dimensions
3. **Native Python** - No external dependencies on OpenSCAD
4. **STEP Export** - Industry-standard CAD format
5. **Open CASCADE** - Based on professional CAD kernel
6. **Type Hints** - Better IDE support

## Key Features

- **Multiple Stone Shapes**: Round, Princess, Radiant
- **Parametric Design**: All dimensions adjustable
- **Clearance Management**: Prevents prong-stone collision
- **Export Formats**: STEP, STL
- **Web Interface**: Real-time 3D preview

## Parameters

```python
create_stone_setting_b3d(
    stone_size=6.0,          # Diameter (round) or side (square) in mm
    stone_depth=7.2,         # Total stone depth in mm
    prong_count=4,           # Number of prongs (2, 4, 6, 8)
    prong_thickness_base=0.4, # Base width in mm
    prong_thickness_top=0.3, # Top width in mm
    setting_height=3.0,      # Stone height above ring in mm
    ring_size=8.5,           # Inner radius in mm
    ring_thickness=1.0,      # Band thickness in mm
    stone_shape='round'      # 'round', 'princess', or 'radiant'
)
```

## Comparison with Original

| Feature | Original (trimesh) | build123d Version |
|---------|-------------------|-------------------|
| CAD Library | trimesh | build123d (OpenCASCADE) |
| Export Formats | GLB, STL | STEP, STL |
| Parametric | Yes | Yes |
| Web Editor | Yes (port 5001) | Yes (port 5002) |
| Stone Shapes | Round, Princess, Radiant | Round, Princess, Radiant |
| Industry Standard | GLB (graphics) | STEP (CAD) |

## Next Steps

1. Run the build123d version to compare quality
2. Both versions can run simultaneously (different ports)
3. Choose which version works better for your workflow

## Installation

```bash
pip install build123d
```

All dependencies installed automatically.
