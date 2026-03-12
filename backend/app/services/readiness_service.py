import pandas as pd
from typing import List, Dict
from sklearn.preprocessing import MinMaxScaler
from .risk_service import RiskService
from .hotspot_service import HotspotService

class ReadinessService:
    def __init__(self, elevation_df: pd.DataFrame, drainage_df: pd.DataFrame, wards_df: pd.DataFrame, risk_service: RiskService):
        self.elevation_df = elevation_df
        self.drainage_df = drainage_df
        self.wards_df = wards_df
        self.risk_service = risk_service

    def _nearest_value(self, df: pd.DataFrame, lat: float, lon: float, value_col: str) -> float:
        df = df.copy()
        df["dist"] = (df["lat"] - lat).abs() + (df["lon"] - lon).abs()
        idx = df["dist"].idxmin()
        return float(df.loc[idx, value_col])

    def compute_readiness_by_ward(self) -> List[Dict]:
        dref = self.drainage_df["capacity_index"]
        eref = self.elevation_df["elevation_m"]
        drain_scaler = MinMaxScaler()
        elev_scaler = MinMaxScaler()
        drain_scaler.fit(dref.to_numpy().reshape(-1, 1))
        elev_scaler.fit(eref.to_numpy().reshape(-1, 1))
        out = []
        for _, w in self.wards_df.iterrows():
            lat = (w["min_lat"] + w["max_lat"]) / 2.0
            lon = (w["min_lon"] + w["max_lon"]) / 2.0
            drainage = self._nearest_value(self.drainage_df, lat, lon, "capacity_index")
            elevation = self._nearest_value(self.elevation_df, lat, lon, "elevation_m")
            dn = float(drain_scaler.transform([[drainage]]).reshape(-1)[0])
            en = float(elev_scaler.transform([[elevation]]).reshape(-1)[0])
            hotspot = HotspotService(self._fake_rainfall(lat, lon), self.elevation_df, self.drainage_df, self.wards_df, self.risk_service)
            ward_risk = hotspot.compute_ward_risk()
            wr = [r for r in ward_risk if r["ward_id"] == int(w["id"])][0]["score"]
            readiness = int(round(100.0 * (0.4 * dn + 0.3 * en + 0.3 * (1.0 - wr))))
            out.append({
                "ward_id": int(w["id"]),
                "ward_name": w["name"],
                "readiness_score": readiness
            })
        return out

    def compute_readiness_by_ward_with_rainfall(self, rainfall_df: pd.DataFrame) -> List[Dict]:
        dref = self.drainage_df["capacity_index"]
        eref = self.elevation_df["elevation_m"]
        drain_scaler = MinMaxScaler()
        elev_scaler = MinMaxScaler()
        drain_scaler.fit(dref.to_numpy().reshape(-1, 1))
        elev_scaler.fit(eref.to_numpy().reshape(-1, 1))
        out = []
        hotspot = HotspotService(rainfall_df, self.elevation_df, self.drainage_df, self.wards_df, self.risk_service)
        ward_risk = hotspot.compute_ward_risk()
        for _, w in self.wards_df.iterrows():
            lat = (w["min_lat"] + w["max_lat"]) / 2.0
            lon = (w["min_lon"] + w["max_lon"]) / 2.0
            drainage = self._nearest_value(self.drainage_df, lat, lon, "capacity_index")
            elevation = self._nearest_value(self.elevation_df, lat, lon, "elevation_m")
            dn = float(drain_scaler.transform([[drainage]]).reshape(-1)[0])
            en = float(elev_scaler.transform([[elevation]]).reshape(-1)[0])
            wr = [r for r in ward_risk if r["ward_id"] == int(w["id"])][0]["score"]
            readiness = int(round(100.0 * (0.4 * dn + 0.3 * en + 0.3 * (1.0 - wr))))
            out.append({
                "ward_id": int(w["id"]),
                "ward_name": w["name"],
                "readiness_score": readiness
            })
        return out

    def _fake_rainfall(self, lat: float, lon: float) -> pd.DataFrame:
        return pd.DataFrame([{"lat": lat, "lon": lon, "rainfall_mm": 0.0}])
