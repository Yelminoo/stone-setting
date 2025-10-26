import json
import os
from pathlib import Path
from parametric_setting_core import generate_stone_setting

def main():
    # Load parameters
    with open("example_params.json", "r") as f:
        params = json.load(f)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    designer_path = output_dir / "designer.glb"
    production_path = output_dir / "production.glb"

    generate_stone_setting(
        stone_shape=params["stone_shape"],
        stone_length=params["stone_length"],
        stone_width=params["stone_width"],
        stone_depth=params["stone_depth"],
        prong_count=params["prong_count"],
        prong_thickness_base=params["prong_thickness_base"],
        prong_thickness_top=params["prong_thickness_top"],
        setting_height=params["setting_height"],
        prong_base_style=params.get("prong_base_style", "individual"),
        prong_base_width=params.get("prong_base_width", 1.2),
        prong_base_height=params.get("prong_base_height", 1.0),
        gallery_radius=params.get("gallery_radius", None),
        base_type=params.get("base_type", "minimal"),
        ring_outer_radius=params.get("ring_outer_radius", 8.5),
        ring_inner_radius=params.get("ring_inner_radius", 5.0),
        ring_thickness=params.get("ring_thickness", 2.0),
        designer_filename=str(designer_path),
        production_filename=str(production_path)
    )

if __name__ == "__main__":
    main()
