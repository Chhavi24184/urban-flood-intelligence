import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np

class FloodRiskModel:
    def __init__(self):
        self.scaler_rain = MinMaxScaler()
        self.scaler_drain = MinMaxScaler()
        self.scaler_elev = MinMaxScaler()

    def fit(self, rainfall_ref: pd.Series, drainage_ref: pd.Series, elevation_ref: pd.Series):
        self.scaler_rain.fit(rainfall_ref.to_numpy().reshape(-1, 1))
        self.scaler_drain.fit(drainage_ref.to_numpy().reshape(-1, 1))
        self.scaler_elev.fit(elevation_ref.to_numpy().reshape(-1, 1))

    def score(self, rainfall_value: float, drainage_capacity_value: float, elevation_value: float) -> float:
        rfv = float(self.scaler_rain.transform(np.array([[rainfall_value]])).reshape(-1)[0])
        dfv = float(1.0 - self.scaler_drain.transform(np.array([[drainage_capacity_value]])).reshape(-1)[0])
        efv = float(1.0 - self.scaler_elev.transform(np.array([[elevation_value]])).reshape(-1)[0])
        return 0.5 * rfv + 0.3 * dfv + 0.2 * efv

    def category(self, score: float) -> str:
        if score < 0.33:
            return "low"
        if score < 0.66:
            return "medium"
        return "high"
