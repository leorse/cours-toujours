import random
import math
from typing import Dict, Any, List

class FractionGenerator:
    """
    Handles logic for 'Tom & Alice' fraction scenarios.
    Generates visual blueprints for Pizza, Grid, Cylinder types.
    """

    COLORS = {
        "Tom": "#3498db",   # Blue
        "Alice": "#e67e22", # Orange
        "Empty": "#ecf0f1", # Light Gray
        "PizzaCrust": "#f39c12",
        "GridLine": "#bdc3c7",
        "Liquid": "#3498db" # Generic liquid color if no specific owner
    }

    PHRASES = {
        "consume": ["boit", "mange", "consomme", "partage", "prend"],
        "container": {
            "CYLINDER": ["brique de lait", "bouteille de jus", "réservoir d'eau"],
            "PIZZA": ["pizza", "tarte", "quiche"],
            "GRID": ["tablette de chocolat", "gâteau rectangulaire", "terrain"]
        }
    }

    @staticmethod
    def parse_fraction(frac_str: str) -> float:
        try:
            if "/" in frac_str:
                n, d = map(int, frac_str.split("/"))
                return n / d
            return float(frac_str)
        except:
            return 0.0

    @staticmethod
    def get_rgb_visual_blueprint(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms high-level exercise data into low-level rendering data.
        """
        visual_type = data.get("visual", "CYLINDER")
        total_parts = data.get("parts", 1)
        participants = data.get("participants", [])

        # Normalize participant data
        people = []
        current_offset = 0.0 # 0 to 1 scale or simple counts
        
        # Calculate parts for each
        # We assume 'parts' is the denominator reference for Grid/Pizza slices
        # For Cylinder, it's just a continuous fill usually, but can be segmented.
        
        # Determine total occupied fraction to know 'remaining'
        total_occupied = 0.0

        processed_participants = []
        
        for p in participants:
            frac_val = FractionGenerator.parse_fraction(p["fraction"])
            # units occupied = frac_val * total_parts (if total_parts represents the whole integer count)
            # Actually usually 'parts' implies the visual subdivision count.
            
            # For rendering, we need start/end angles or percentages
            # We assume sequential filling
            
            start_ratio = total_occupied
            end_ratio = total_occupied + frac_val
            
            p_data = {
                "name": p["name"],
                "color": p.get("color", FractionGenerator.COLORS.get(p["name"], "#999")),
                "fraction_val": frac_val,
                "start_ratio": start_ratio,
                "end_ratio": end_ratio
            }
            processed_participants.append(p_data)
            total_occupied += frac_val

        blueprint = {
            "type": visual_type,
            "total_parts": total_parts, # e.g., 8 slices, 10 ticks
            "participants": processed_participants,
            "remaining_ratio": max(0.0, 1.0 - total_occupied)
        }

        if visual_type == "PIZZA":
            # Pizza specific: angles
            # 360 degrees total
            for p in blueprint["participants"]:
                p["start_angle"] = p["start_ratio"] * 360
                p["end_angle"] = p["end_ratio"] * 360
                p["is_large_arc"] = 1 if (p["end_angle"] - p["start_angle"]) > 180 else 0
                
                # Calculate coordinates for SVG path
                # Center (0,0) (conceptually), radius R
                # We'll let frontend handle R scaling, but we provide ready-to-use path commands or angles
                
        elif visual_type == "GRID":
            # Grid specific: determining cells
            # Try to find best RxC texturing
            r, c = FractionGenerator._best_grid_dims(total_parts)
            blueprint["rows"] = r
            blueprint["cols"] = c
            
            # Assign specific cells to people logic
            # Just fill sequentially 0..N-1
            total_cells = r * c
            cells_assigned = []
            
            current_cell_idx = 0
            for p in blueprint["participants"]:
                count = int(round(p["fraction_val"] * total_cells))
                assigned = []
                for _ in range(count):
                    if current_cell_idx < total_cells:
                        row = current_cell_idx // c
                        col = current_cell_idx % c
                        assigned.append({"r": row, "c": col})
                        current_cell_idx += 1
                p["cells"] = assigned
                
        elif visual_type == "CYLINDER":
            # Just height percentages
            pass

        return blueprint

    @staticmethod
    def _best_grid_dims(n: int):
        # Find factors of n to make a nice rectangle
        sqrt = int(math.sqrt(n))
        for i in range(sqrt, 0, -1):
            if n % i == 0:
                return i, n // i
        return 1, n
