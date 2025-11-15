# Quick Start Guide - Real-Time Parametric Editor

## 🚀 Get Started in 5 Minutes

### Step 1: Start the Server (1 minute)

```powershell
# Navigate to project directory
cd d:\Python-CAD-3D

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Start Flask server
python app.py
```

**Expected Output:**
```
🚀 Starting Parametric Stone Setting Generator Server
📱 Web UI: http://localhost:5000
🔧 API: http://localhost:5000/generate
👁️ Viewer: http://localhost:5000/view.html
 * Running on http://127.0.0.1:5000
```

---

### Step 2: Open Real-Time Editor (30 seconds)

Open your browser and navigate to:
```
http://localhost:5000/realtime.html
```

You'll see:
- **Left Panel**: Controls and parameters
- **Right Side**: 3D viewport with grid and axes

---

### Step 3: Create Your First Design (2 minutes)

#### Basic Stone Setting
1. **Adjust Stone Size**
   - Drag "Width" slider to 7.0mm
   - Drag "Length" slider to 7.0mm
   - Drag "Depth" slider to 4.5mm

2. **Adjust Ring Size**
   - Drag "Outer Radius" slider to 10.0mm
   - Drag "Tube Radius" slider to 1.2mm

3. **Set Prong Configuration**
   - Drag "Prong Count" slider to 6
   - Drag "Base Thickness" slider to 0.8mm

4. **Generate Preview**
   - Check "Auto Preview" checkbox
   - Watch as the model updates automatically!

---

### Step 4: Save Your Design (1 minute)

1. **Save as Preset**
   - Click "Save Preset" button
   - Enter name: "my_first_setting"
   - Enter description: "6-prong round 7mm"
   - Click OK

2. **Generate Full Model**
   - Click "🚀 Generate Full Model" button
   - Wait 2-3 seconds for generation
   - Model appears in viewport

3. **Download Model**
   - Click "📥 Download GLB" button
   - File saves to your downloads folder

---

### Step 5: Try Different Variations (30 seconds)

1. **Load Built-in Presets**
   - Click "Refresh List" in Presets section
   - Click "Load" on any preset
   - Model updates automatically

2. **Experiment with Parameters**
   - Try different prong counts: 4, 6, 8
   - Try different stone shapes: Round, Princess, Oval
   - Watch auto-preview update in real-time

---

## 🎨 Interface Tour

### Left Panel Sections

#### 📦 Presets
- **Refresh List**: Update preset library
- **Save Preset**: Store current parameters
- **Preset List**: Click to load saved designs
- **Delete**: Remove unwanted presets

#### 💎 Stone Parameters
- **Shape**: Round, Princess, Oval, Emerald
- **Width**: 2-15mm (horizontal size)
- **Length**: 2-15mm (vertical size when viewed from top)
- **Depth**: 1-10mm (height of stone)

#### 🔗 Ring Parameters
- **Outer Radius**: 5-15mm (ring size)
- **Tube Radius**: 0.3-2mm (ring band thickness)

#### 🦅 Prong Parameters
- **Prong Count**: 3-8 prongs
- **Base Thickness**: 0.3-2mm (prong width)
- **Setting Height**: 1-8mm (stone elevation)

#### ⚡ Actions
- **Generate Full Model**: Create production-ready GLB
- **Update Preview**: Manual preview refresh
- **Export JSON**: Download parameter file
- **Download GLB**: Get generated model

### Right Side (3D Viewport)
- **Grid**: Shows XY plane (horizontal)
- **Axes**: X=Red, Y=Green, Z=Blue
- **Model**: Your generated stone setting
- **Mouse Controls**:
  - **Left Click + Drag**: Rotate camera
  - **Right Click + Drag**: Pan camera
  - **Scroll Wheel**: Zoom in/out

---

## 🎯 Common Tasks

### Task 1: Create Engagement Ring Setting
```
Parameters:
- Stone Shape: Round
- Width: 6.5mm
- Length: 6.5mm
- Depth: 4.0mm
- Ring Outer Radius: 8.5mm
- Ring Tube Radius: 1.0mm
- Prong Count: 4
- Base Thickness: 0.8mm
- Setting Height: 3.5mm

Steps:
1. Enter parameters above
2. Check "Auto Preview"
3. Click "Save Preset" → Name: "classic_solitaire"
4. Click "Generate Full Model"
5. Click "Download GLB"
```

### Task 2: Create Halo Setting
```
Parameters:
- Stone Shape: Round
- Width: 5.0mm
- Length: 5.0mm
- Depth: 3.5mm
- Ring Outer Radius: 7.5mm
- Ring Tube Radius: 0.8mm
- Prong Count: 6
- Base Thickness: 0.6mm
- Setting Height: 2.8mm

Steps:
1. Enter parameters above
2. Watch auto-preview update
3. Save as "halo_setting"
4. Generate and download
```

### Task 3: Create Princess Cut Setting
```
Parameters:
- Stone Shape: Princess
- Width: 6.0mm
- Length: 6.0mm
- Depth: 4.2mm
- Ring Outer Radius: 9.0mm
- Ring Tube Radius: 1.2mm
- Prong Count: 4
- Base Thickness: 1.0mm
- Setting Height: 4.0mm

Steps:
1. Enter parameters above
2. Enable "Show Debug Markers" to see coordinates
3. Adjust until satisfied
4. Save as "vintage_princess"
```

---

## 🔧 Keyboard Shortcuts

(Note: Three.js default controls)

| Key | Action |
|-----|--------|
| **Mouse Left + Drag** | Rotate camera around center |
| **Mouse Right + Drag** | Pan camera |
| **Mouse Wheel** | Zoom in/out |
| **Ctrl + Click** | (Future: Select object) |

---

## 💡 Pro Tips

### 1. Use Auto-Preview for Fine-Tuning
- Enable auto-preview when making small adjustments
- Disable for large parameter changes to avoid excessive requests

### 2. Save Frequently
- Save presets often during exploration
- Use descriptive names: "round_6mm_4prong" not "test1"

### 3. Generate Full Model Only When Ready
- Use preview for iterations (faster)
- Generate full model for final output (slower but production-ready)

### 4. Organize Your Presets
- Create naming convention: `style_stone_prongs` (e.g., "solitaire_round_4prong")
- Add descriptions to remember design intent

### 5. Export Parameters for Records
- Export JSON for each final design
- Keep parameter files for client records
- Use timestamped filenames for versions

---

## 🐛 Troubleshooting

### Problem: Model Doesn't Appear
**Solution:**
1. Check browser console (F12) for errors
2. Verify server is running (check terminal)
3. Click "Update Preview" manually
4. Try refreshing the page

### Problem: Auto-Preview Not Working
**Solution:**
1. Make sure "Auto Preview" checkbox is checked
2. Wait 500ms after slider change
3. Check server terminal for errors
4. Try manual "Update Preview" button

### Problem: Can't Save Preset
**Solution:**
1. Verify server is running
2. Check terminal for permission errors
3. Ensure `presets/` directory exists
4. Try different preset name (avoid special characters)

### Problem: Download Fails
**Solution:**
1. Generate model first (click "Generate Full Model")
2. Check `output/` directory exists
3. Verify file `output/designer.glb` was created
4. Check browser download settings

### Problem: Slow Generation
**Solution:**
1. Use "Update Preview" for quick iterations
2. Lower prong count temporarily
3. Disable debug markers
4. Check server CPU usage
5. Use "Generate Full Model" only for final output

---

## 📱 Mobile Access

Access from other devices on same network:
```
http://192.168.X.X:5000/realtime.html
```

Replace X.X with your computer's IP address (shown in server startup).

**Note**: Transform controls may not work optimally on mobile. Desktop recommended.

---

## 🎓 Next Steps

### Beginner
1. ✅ Complete this quick start
2. Try all preset examples
3. Create 3-5 of your own designs
4. Learn parameter relationships

### Intermediate
1. Use batch generation API (see REALTIME_FEATURES.md)
2. Customize parameters programmatically
3. Integrate with external tools
4. Create parameter templates

### Advanced
1. Modify `parametric_setting_core.py` for custom geometry
2. Add new API endpoints in `app.py`
3. Enhance UI in `realtime_editor.html`
4. Contribute features back to project

---

## 📚 Additional Resources

- **Full Feature Documentation**: `REALTIME_FEATURES.md`
- **Feature Comparison**: `FEATURE_COMPARISON.md`
- **API Reference**: Docstrings in `app.py`
- **Code Examples**: `presets/` directory

---

## 🆘 Getting Help

1. **Check Documentation**: Read feature guides
2. **Browser Console**: Check for JavaScript errors (F12)
3. **Server Logs**: Check terminal output
4. **Test Basic**: Try with default parameters first
5. **File Issue**: Report bugs on GitHub

---

## ✅ Checklist

### First-Time Setup
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Server starts without errors
- [ ] Browser opens `realtime.html`
- [ ] 3D viewport shows grid and axes

### Every Design Session
- [ ] Server running
- [ ] Auto-preview enabled
- [ ] Parameters set correctly
- [ ] Preview looks good
- [ ] Preset saved
- [ ] Full model generated
- [ ] GLB downloaded
- [ ] Parameters exported (optional)

---

## 🎉 Success Indicators

You're doing it right if:
- ✅ Model updates within 1-2 seconds of slider change
- ✅ Presets load instantly
- ✅ No errors in status area
- ✅ Downloaded GLB opens in 3D viewer
- ✅ Parameters export to valid JSON

---

## 🚀 You're Ready!

Start creating beautiful stone settings with the power of:
- **Real-time visualization** 👁️
- **Python precision** 🎯
- **Preset management** 💾
- **Production export** 📦

**Happy designing!** 💎✨
