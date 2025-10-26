# 🚀 Vercel Deployment Guide

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Git Repository**: Your code needs to be in a Git repository
3. **Vercel CLI** (optional): `npm i -g vercel`

## 🎯 Deployment Options

### **Option 1: Frontend-Only Version (Recommended)**

This version works perfectly on Vercel with full UI functionality:

```bash
# Use the demo.html as your main page
cp static/demo.html static/index.html
```

**Features:**
- ✅ Full parametric UI with all controls
- ✅ Real-time parameter preview
- ✅ Preset configurations
- ✅ Export JSON parameters
- ✅ Resizable layout
- ❌ No 3D file generation (parameters only)

### **Option 2: Serverless with Limited Backend**

Uses Vercel's Python serverless functions:

**Files needed:**
- `vercel.json` ✅
- `api/index.py` ✅
- `api/requirements.txt` ✅
- `static/index.html` ✅

**Limitations:**
- Heavy 3D libraries (trimesh, numpy) may exceed size limits
- File generation might timeout in serverless environment

## 🛠️ Deployment Steps

### **Method 1: Vercel Dashboard (Easiest)**

1. **Push to Git**:
```bash
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

2. **Connect Repository**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your Git repository
   - Vercel auto-detects settings

3. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete
   - Get your live URL!

### **Method 2: Vercel CLI**

1. **Install CLI**:
```bash
npm i -g vercel
```

2. **Deploy**:
```bash
cd D:\Python-CAD-3D
vercel
```

3. **Follow prompts**:
   - Link to existing project? (N for new)
   - Project name: `parametric-stone-setting`
   - Directory: `./` (current)
   - Override settings? (N)

### **Method 3: GitHub Integration**

1. **Push to GitHub**:
```bash
git remote add origin https://github.com/yourusername/parametric-stone-setting.git
git push -u origin main
```

2. **Auto-Deploy**:
   - Vercel will auto-deploy on every push
   - Get staging URLs for branches
   - Production URL for main branch

## ⚙️ Configuration Files

### **vercel.json**
```json
{
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.9"
    }
  },
  "routes": [
    { "src": "/api/(.*)", "dest": "/api/$1" },
    { "src": "/(.*)", "dest": "/static/$1" }
  ]
}
```

### **package.json**
```json
{
  "name": "parametric-stone-setting-generator",
  "version": "1.0.0",
  "main": "static/index.html"
}
```

## 🎨 Frontend-Only Setup

For the best Vercel experience, use the frontend-only version:

1. **Copy demo to index**:
```bash
cp static/demo.html static/index.html
```

2. **Update vercel.json**:
```json
{
  "routes": [
    { "src": "/(.*)", "dest": "/static/$1" }
  ]
}
```

3. **Deploy**:
```bash
vercel --prod
```

## 🔧 Troubleshooting

### **Common Issues:**

#### **Build Fails**
- Check file paths are correct
- Ensure all dependencies are listed
- Python packages may exceed size limits

#### **Functions Timeout**
- Heavy 3D processing may timeout (10s limit)
- Consider frontend-only approach
- Use external API for 3D generation

#### **Import Errors**
- Python paths may differ in serverless
- Check `sys.path.append()` statements
- Verify all modules are included

### **Solutions:**

#### **Size Optimization**
```bash
# Remove heavy dependencies for serverless
echo "flask" > api/requirements.txt
```

#### **Error Handling**
```python
try:
    from parametric_setting_core import generate_stone_setting
except ImportError:
    # Fallback for serverless
    pass
```

## 🎯 Recommended Architecture

### **Hybrid Approach:**

1. **Frontend on Vercel**: Full UI with parameter controls
2. **Backend elsewhere**: Heavy 3D processing on dedicated server
3. **API integration**: Connect via REST API

### **File Structure:**
```
├── vercel.json           # Vercel configuration
├── package.json          # Node.js metadata
├── static/
│   ├── index.html       # Main UI
│   └── demo.html        # Frontend-only version
├── api/
│   ├── index.py         # Serverless functions
│   └── requirements.txt # Python dependencies
└── README.md            # Documentation
```

## 🌐 Live Demo

Once deployed, you'll have:

- **Live URL**: `https://your-project.vercel.app`
- **Auto HTTPS**: SSL certificate included
- **Global CDN**: Fast worldwide access
- **Auto deploys**: Updates on Git push

## 📞 Support

For deployment issues:
- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Community](https://github.com/vercel/vercel/discussions)
- Check Vercel build logs for errors

---

**Ready to go live! 🚀✨**