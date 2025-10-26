# 🎨 Resizable UI Layout Guide

## ✨ New Split-Screen Features

### **🔄 Resizable Panels**
- **Drag the divider** between panels to resize
- **Real-time width indicator** shows current panel size
- **Smooth transitions** and visual feedback

### **🎯 Resize Controls**

#### **Drag to Resize**
1. **Hover** over the center divider (changes to resize cursor)
2. **Click and drag** left/right to adjust panel widths
3. **Release** to set the new layout

#### **Double-Click Reset**
- **Double-click** the divider to reset to default (400px)

#### **Width Constraints**
- **Minimum**: 300px (keeps controls usable)
- **Maximum**: 800px or 70% of screen (prevents viewer from being too small)

### **📱 Responsive Design**

#### **Desktop/Tablet (>768px)**
- **Side-by-side** layout with vertical divider
- **Horizontal** drag to resize
- **Full resize** control

#### **Mobile (<768px)**
- **Stacked** layout (controls on top, viewer below)
- **Horizontal** divider
- **Vertical** drag to adjust heights

### **🎨 Visual Feedback**

#### **Hover Effects**
- **Divider highlights** with gradient colors
- **Cursor changes** to resize indicator
- **Center grip** becomes visible

#### **Active Resizing**
- **Enhanced highlighting** during drag
- **Live width display** tooltip
- **Smooth animations** and transitions

### **⌨️ Keyboard Shortcuts**
- **Double-click divider**: Reset to default width
- **Escape** (future): Cancel resize operation

### **🔧 Technical Details**

#### **Layout System**
- **CSS Flexbox** for responsive panels
- **JavaScript** event handling for resize
- **Real-time** 3D viewport adjustment

#### **Performance**
- **Throttled** resize events for smooth performance
- **Hardware acceleration** for animations
- **Memory efficient** event handling

### **💡 Usage Tips**

#### **For Design Work**
- **Narrow controls** (300-400px) for more 3D preview space
- **Wide controls** (500-600px) for detailed parameter adjustment

#### **For Parameter Tweaking**
- **Medium width** (400-500px) for balanced workflow
- **Quick preset switching** with full parameter visibility

#### **For Presentation**
- **Minimal controls** width to maximize 3D viewer
- **Professional appearance** for client reviews

---

**Enjoy your new flexible workspace! 🎯✨**