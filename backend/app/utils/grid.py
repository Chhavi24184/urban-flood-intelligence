from typing import List, Dict
import pandas as pd

def generate_grid_for_wards(wards_df: pd.DataFrame, cells_per_side: int = 5) -> List[Dict]:
    out = []
    for _, w in wards_df.iterrows():
        min_lat = float(w["min_lat"])
        max_lat = float(w["max_lat"])
        min_lon = float(w["min_lon"])
        max_lon = float(w["max_lon"])
        lat_step = (max_lat - min_lat) / cells_per_side
        lon_step = (max_lon - min_lon) / cells_per_side
        for i in range(cells_per_side):
            for j in range(cells_per_side):
                lat = min_lat + (i + 0.5) * lat_step
                lon = min_lon + (j + 0.5) * lon_step
                out.append({
                    "ward_id": int(w["id"]),
                    "center": (lat, lon)
                })
    return out
