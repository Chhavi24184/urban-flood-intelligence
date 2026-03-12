import pandas as pd
from typing import List, Dict, Tuple
from ..utils.grid import generate_grid_for_wards
from .risk_service import RiskService

class HotspotService:
    def __init__(self, rainfall_df: pd.DataFrame, elevation_df: pd.DataFrame, drainage_df: pd.DataFrame,
                 wards_df: pd.DataFrame, risk_service: RiskService):
        self.rainfall_df = rainfall_df
        self.elevation_df = elevation_df
        self.drainage_df = drainage_df
        self.wards_df = wards_df
        self.risk_service = risk_service

    def _nearest_value(self, df: pd.DataFrame, lat: float, lon: float, value_col: str) -> float:
        df = df.copy()
        df["dist"] = (df["lat"] - lat).abs() + (df["lon"] - lon).abs()
        idx = df["dist"].idxmin()
        return float(df.loc[idx, value_col])

    def compute_grid_risk(self) -> List[Dict]:
        grids = generate_grid_for_wards(self.wards_df, cells_per_side=5)
        out = []
        rref = self.rainfall_df["rainfall_mm"]
        dref = self.drainage_df["capacity_index"]
        eref = self.elevation_df["elevation_m"]
        for g in grids:
            lat, lon = g["center"]
            rainfall = self._nearest_value(self.rainfall_df, lat, lon, "rainfall_mm")
            drainage = self._nearest_value(self.drainage_df, lat, lon, "capacity_index")
            elevation = self._nearest_value(self.elevation_df, lat, lon, "elevation_m")
            score = self.risk_service.score(rainfall, drainage, elevation, rref, dref, eref)
            cat = self.risk_service.category(score)
            out.append({
                "ward_id": g["ward_id"],
                "lat": lat,
                "lon": lon,
                "score": round(score, 4),
                "category": cat
            })
        return out

    def compute_ward_risk(self) -> List[Dict]:
        out = []
        rref = self.rainfall_df["rainfall_mm"]
        dref = self.drainage_df["capacity_index"]
        eref = self.elevation_df["elevation_m"]
        for _, w in self.wards_df.iterrows():
            lat = (w["min_lat"] + w["max_lat"]) / 2.0
            lon = (w["min_lon"] + w["max_lon"]) / 2.0
            rainfall = self._nearest_value(self.rainfall_df, lat, lon, "rainfall_mm")
            drainage = self._nearest_value(self.drainage_df, lat, lon, "capacity_index")
            elevation = self._nearest_value(self.elevation_df, lat, lon, "elevation_m")
            score = self.risk_service.score(rainfall, drainage, elevation, rref, dref, eref)
            cat = self.risk_service.category(score)
            out.append({
                "ward_id": int(w["id"]),
                "ward_name": w["name"],
                "score": round(score, 4),
                "category": cat,
                "rainfall_mm": rainfall,
                "capacity_index": drainage,
                "elevation_m": elevation
            })
        return out
