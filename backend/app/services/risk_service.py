import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

class RiskService:
    def __init__(self, scaler_rain: MinMaxScaler, scaler_drain: MinMaxScaler, scaler_elev: MinMaxScaler):
        self.scaler_rain = scaler_rain
        self.scaler_drain = scaler_drain
        self.scaler_elev = scaler_elev

    def normalize_series(self, values: np.ndarray, scaler: MinMaxScaler) -> np.ndarray:
        arr = values.reshape(-1, 1)
        return scaler.fit_transform(arr).reshape(-1)

    def compute_factors(self, rainfall: pd.Series, drainage_capacity: pd.Series, elevation: pd.Series):
        rf = self.normalize_series(rainfall.to_numpy(), self.scaler_rain)
        dc_norm = self.normalize_series(drainage_capacity.to_numpy(), self.scaler_drain)
        df = 1.0 - dc_norm
        ev_norm = self.normalize_series(elevation.to_numpy(), self.scaler_elev)
        ef = 1.0 - ev_norm
        return rf, df, ef

    def score(self, rainfall_value: float, drainage_capacity_value: float, elevation_value: float,
              rainfall_ref: pd.Series, drainage_ref: pd.Series, elevation_ref: pd.Series) -> float:
        rf, df, ef = self.compute_factors(rainfall_ref, drainage_ref, elevation_ref)
        rfv = float(self._scale_value(rainfall_value, rainfall_ref, self.scaler_rain))
        dfv = float(1.0 - self._scale_value(drainage_capacity_value, drainage_ref, self.scaler_drain))
        efv = float(1.0 - self._scale_value(elevation_value, elevation_ref, self.scaler_elev))
        # Updated weights for more realistic urban flood risk:
        # Rainfall (40%), Drainage (30%), Elevation (30%)
        return 0.4 * rfv + 0.3 * dfv + 0.3 * efv

    def _scale_value(self, value: float, ref: pd.Series, scaler: MinMaxScaler) -> float:
        arr = ref.to_numpy().reshape(-1, 1)
        scaler.fit(arr)
        return scaler.transform(np.array([[value]])).reshape(-1)[0]

    def category(self, score: float) -> str:
        if score < 0.33:
            return "low"
        if score < 0.66:
            return "medium"
        return "high"
