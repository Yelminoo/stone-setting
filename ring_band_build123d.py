"""
Ring Band Generator using build123d with interactive viewer
Uses build123d's native visualization capabilities
"""

from build123d import *
import numpy as np

# Check if ocp_vscode viewer is available
try:
    from ocp_vscode import show
    VIEWER_AVAILABLE = True
    print("✅ OCP VS Code viewer available")
except ImportError:
    VIEWER_AVAILABLE = False
    print("⚠️  OCP viewer not available - will export files only")

# US Ring Size Chart (inner diameter in mm)
US_RING_SIZES = {
    7: 17.35,
    7.5: 17.75,
    8: 18.19,
    8.5: 18.53,
    9: 19.03,
    9.5: 19.41,
    10: 19.84
}

class RingBandDesigner:
    """Interactive ring band designer using build123d"""
    
    def __init__(self):
        self.current_ring = None
        
    def create_basic_band(
        self,
        ring_size_us=8,
        thickness=2.0,
        band_width=3.0
    ):
        """
        Create a basic ring band
        
        Parameters:
        - ring_size_us: US ring size (7-10)
        - thickness: Band thickness (mm)
        - band_width: Band height (mm)
        """
        
        if ring_size_us not in US_RING_SIZES:
            raise ValueError(f"Size {ring_size_us} not supported")
        
        inner_diameter = US_RING_SIZES[ring_size_us]
        inner_radius = inner_diameter / 2
        
        with BuildPart() as ring:
            # Create the cross-section (rectangle)
            with BuildSketch(Plane.XZ) as profile:
                with Locations((inner_radius + thickness/2, 0)):
                    Rectangle(thickness, band_width, align=(Align.CENTER, Align.CENTER))
            
            # Revolve around Y axis to create ring
            revolve(axis=Axis.Y)
        
        self.current_ring = ring.part
        
        print(f"✅ Basic Ring Band:")
        print(f"   US Size: {ring_size_us}")
        print(f"   Inner Diameter: {inner_diameter:.2f} mm")
        print(f"   Thickness: {thickness:.2f} mm")
        print(f"   Width: {band_width:.2f} mm")
        
        return ring.part
    
    def create_comfort_fit_band(
        self,
        ring_size_us=8,
        thickness=2.5,
        band_width=4.0,
        inner_radius_curve=1.5
    ):
        """
        Create a comfort-fit ring band with rounded inner surface
        
        Parameters:
        - ring_size_us: US ring size
        - thickness: Band thickness at center (mm)
        - band_width: Band height (mm)
        - inner_radius_curve: Radius of the inner curve for comfort (mm)
        """
        
        if ring_size_us not in US_RING_SIZES:
            raise ValueError(f"Size {ring_size_us} not supported")
        
        inner_diameter = US_RING_SIZES[ring_size_us]
        inner_radius = inner_diameter / 2
        
        with BuildPart() as ring:
            # Create comfort-fit profile (rounded rectangle)
            with BuildSketch(Plane.XZ) as profile:
                with Locations((inner_radius + thickness/2, 0)):
                    RectangleRounded(
                        thickness, 
                        band_width,
                        inner_radius_curve,
                        align=(Align.CENTER, Align.CENTER)
                    )
            
            # Revolve to create ring
            revolve(axis=Axis.Y)
        
        self.current_ring = ring.part
        
        print(f"✅ Comfort-Fit Ring Band:")
        print(f"   US Size: {ring_size_us}")
        print(f"   Inner Diameter: {inner_diameter:.2f} mm")
        print(f"   Thickness: {thickness:.2f} mm")
        print(f"   Width: {band_width:.2f} mm")
        print(f"   Inner Curve: {inner_radius_curve:.2f} mm")
        
        return ring.part
    
    def create_tapered_band(
        self,
        ring_size_us=8,
        thickness_top=1.8,
        thickness_bottom=2.5,
        band_width=4.0
    ):
        """
        Create a band that tapers (thicker on bottom/palm side)
        
        Parameters:
        - ring_size_us: US ring size
        - thickness_top: Thickness at top (mm)
        - thickness_bottom: Thickness at bottom (mm)
        - band_width: Band height (mm)
        """
        
        if ring_size_us not in US_RING_SIZES:
            raise ValueError(f"Size {ring_size_us} not supported")
        
        inner_diameter = US_RING_SIZES[ring_size_us]
        inner_radius = inner_diameter / 2
        
        with BuildPart() as ring:
            # Create tapered profile using polygon
            with BuildSketch(Plane.XZ) as profile:
                # Define trapezoid points (clockwise from bottom-left)
                points = [
                    (inner_radius, -band_width/2),                              # Bottom inner
                    (inner_radius + thickness_bottom, -band_width/2),           # Bottom outer
                    (inner_radius + thickness_top, band_width/2),               # Top outer
                    (inner_radius, band_width/2),                               # Top inner
                ]
                
                with BuildLine() as trapezoid:
                    Polyline(*points, close=True)
                
                make_face()
            
            # Revolve to create tapered ring
            revolve(axis=Axis.Y)
        
        self.current_ring = ring.part
        
        print(f"✅ Tapered Ring Band:")
        print(f"   US Size: {ring_size_us}")
        print(f"   Inner Diameter: {inner_diameter:.2f} mm")
        print(f"   Thickness Top: {thickness_top:.2f} mm")
        print(f"   Thickness Bottom: {thickness_bottom:.2f} mm")
        print(f"   Taper: {thickness_bottom - thickness_top:.2f} mm")
        print(f"   Width: {band_width:.2f} mm")
        
        return ring.part
    
    def create_domed_band(
        self,
        ring_size_us=8,
        thickness=2.5,
        band_width=4.0,
        dome_height=1.0
    ):
        """
        Create a band with domed (curved) outer surface
        
        Parameters:
        - ring_size_us: US ring size
        - thickness: Band thickness at edges (mm)
        - band_width: Band height (mm)
        - dome_height: Additional height of dome at center (mm)
        """
        
        if ring_size_us not in US_RING_SIZES:
            raise ValueError(f"Size {ring_size_us} not supported")
        
        inner_diameter = US_RING_SIZES[ring_size_us]
        inner_radius = inner_diameter / 2
        
        with BuildPart() as ring:
            # Create domed profile using spline
            with BuildSketch(Plane.XZ) as profile:
                # Create points for the dome
                bottom_inner = (inner_radius, -band_width/2)
                bottom_outer = (inner_radius + thickness, -band_width/2)
                center_peak = (inner_radius + thickness + dome_height, 0)
                top_outer = (inner_radius + thickness, band_width/2)
                top_inner = (inner_radius, band_width/2)
                
                with BuildLine() as dome_profile:
                    Line(bottom_inner, bottom_outer)
                    # Use Bezier for smoother dome curve
                    Bezier(bottom_outer, center_peak, top_outer)
                    Line(top_outer, top_inner)
                    Line(top_inner, bottom_inner)
                
                make_face()
            
            # Revolve to create domed ring
            revolve(axis=Axis.Y)
        
        self.current_ring = ring.part
        
        print(f"✅ Domed Ring Band:")
        print(f"   US Size: {ring_size_us}")
        print(f"   Inner Diameter: {inner_diameter:.2f} mm")
        print(f"   Thickness: {thickness:.2f} mm")
        print(f"   Dome Height: {dome_height:.2f} mm")
        print(f"   Width: {band_width:.2f} mm")
        
        return ring.part
    
    def show(self):
        """Display the current ring in build123d viewer"""
        if not self.current_ring:
            print("No ring created yet!")
            return
        
        if VIEWER_AVAILABLE:
            try:
                # Use ocp_vscode show() function
                show(self.current_ring)
                print("✅ Ring displayed in viewer")
            except Exception as e:
                print(f"⚠️  Viewer not active. Install 'OCP CAD Viewer' extension in VS Code.")
                print("   Or use export() to save as STEP/STL file.")
        else:
            print("⚠️  Viewer not available. Use export() to save as STEP or STL file.")
            print("   Then view in FreeCAD, OnShape, or other CAD software.")
    
    def export(self, filename, format='step'):
        """Export current ring to file"""
        if not self.current_ring:
            print("No ring to export!")
            return
        
        if format.lower() == 'step':
            export_step(self.current_ring, filename)
        elif format.lower() == 'stl':
            export_stl(self.current_ring, filename)
        else:
            raise ValueError(f"Format {format} not supported. Use 'step' or 'stl'")
        
        print(f"💾 Exported to: {filename}")


def interactive_demo():
    """Interactive demonstration of ring band designs"""
    
    print("=" * 70)
    print("💍 Build123d Ring Band Designer - Interactive Demo")
    print("=" * 70)
    
    designer = RingBandDesigner()
    
    # Create different styles
    print("\n1️⃣  Creating Basic Band (Size 8)...")
    ring1 = designer.create_basic_band(
        ring_size_us=8,
        thickness=2.0,
        band_width=3.0
    )
    
    print("\n2️⃣  Creating Comfort-Fit Band (Size 8.5)...")
    ring2 = designer.create_comfort_fit_band(
        ring_size_us=8.5,
        thickness=2.5,
        band_width=4.0,
        inner_radius_curve=0.8
    )
    
    print("\n3️⃣  Creating Tapered Band (Size 9)...")
    ring3 = designer.create_tapered_band(
        ring_size_us=9,
        thickness_top=1.8,
        thickness_bottom=2.5,
        band_width=4.0
    )
    
    print("\n4️⃣  Creating Domed Band (Size 9.5)...")
    ring4 = designer.create_domed_band(
        ring_size_us=9.5,
        thickness=2.5,
        band_width=4.5,
        dome_height=1.2
    )
    
    print("\n" + "=" * 70)
    print("💾 Exporting designs...")
    print("=" * 70)
    
    # Export all designs
    export_step(ring1, "output/ring_basic_size8_b3d.step")
    export_step(ring2, "output/ring_comfort_size8p5_b3d.step")
    export_step(ring3, "output/ring_tapered_size9_b3d.step")
    export_step(ring4, "output/ring_domed_size9p5_b3d.step")
    
    print("\n✅ All designs exported to output/ folder")
    
    # Show the last ring in viewer (if available)
    print("\n🔍 Displaying last design in viewer...")
    if VIEWER_AVAILABLE:
        try:
            show(ring4)
            print("✅ Design displayed in OCP VS Code viewer")
        except Exception as e:
            print(f"⚠️  Viewer not running: {str(e).split('RuntimeError:')[1] if 'RuntimeError' in str(e) else 'Viewer extension not active'}")
            print("   To view: Install 'OCP CAD Viewer' extension in VS Code and activate it")
            print("   Or: Open the STEP files in FreeCAD, OnShape, or other CAD software")
    else:
        print("⚠️  Viewer not available - view STEP files in FreeCAD or other CAD software")
    
    print("\n" + "=" * 70)
    print("✨ Demo complete! 4 ring bands created:")
    print("   - Basic Band (Size 8)")
    print("   - Comfort-Fit Band (Size 8.5)")
    print("   - Tapered Band (Size 9)")
    print("   - Domed Band (Size 9.5)")
    print("   All exported as STEP files in output/ folder")
    print("=" * 70)


if __name__ == "__main__":
    # Run interactive demo
    interactive_demo()
    
    # Example of creating and viewing a custom ring
    print("\n" + "=" * 70)
    print("📝 Custom Ring Example:")
    print("=" * 70)
    
    designer = RingBandDesigner()
    
    # Create your custom ring (use smaller radius to avoid validation error)
    my_ring = designer.create_comfort_fit_band(
        ring_size_us=8,
        thickness=3.0,
        band_width=5.0,
        inner_radius_curve=1.0  # Must be < min(thickness, band_width)/2
    )
    
    # Export it
    designer.export("output/my_custom_ring.step", format='step')
    designer.export("output/my_custom_ring.stl", format='stl')
    
    # Display in viewer (works in VS Code with OCP CAD Viewer extension)
    print("\n🎨 To view: Use designer.show() or open STEP files in CAD software")
    # Optionally show if viewer is running
    # designer.show()
