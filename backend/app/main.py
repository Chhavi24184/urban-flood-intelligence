from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler

from .services.risk_service import RiskService
from .services.hotspot_service import HotspotService
from .services.readiness_service import ReadinessService
from .services.recommendation_service import RecommendationService


# -----------------------------
# Request Model
# -----------------------------
class SimulateRainfallRequest(BaseModel):
    percent_increase: float = 0.0


# -----------------------------
# Load Data
# -----------------------------
base_dir = Path(__file__).resolve().parent
data_dir = base_dir / "data"

rainfall_df = pd.read_csv(data_dir / "rainfall.csv")
elevation_df = pd.read_csv(data_dir / "elevation.csv")
drainage_df = pd.read_csv(data_dir / "drainage.csv")
wards_df = pd.read_csv(data_dir / "wards.csv")


# -----------------------------
# Initialize Services
# -----------------------------
scaler_rain = MinMaxScaler()
scaler_elev = MinMaxScaler()
scaler_drain = MinMaxScaler()

risk_service = RiskService(scaler_rain, scaler_drain, scaler_elev)

hotspot_service = HotspotService(
    rainfall_df,
    elevation_df,
    drainage_df,
    wards_df,
    risk_service
)

readiness_service = ReadinessService(
    elevation_df,
    drainage_df,
    wards_df,
    risk_service
)

recommendation_service = RecommendationService(
    risk_service,
    readiness_service,
    wards_df
)


# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI()


# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Root
# -----------------------------
@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/wards-metadata")
def get_wards_metadata():
    return {"wards": wards_df.to_dict(orient="records")}


# -----------------------------
# Ward Readiness
# -----------------------------
@app.get("/wards")
def get_wards():
    readiness = readiness_service.compute_readiness_by_ward()
    return {"wards": readiness}


# -----------------------------
# Flood Risk
# -----------------------------
@app.get("/flood-risk")
def get_flood_risk(level: str = Query(default="grid")):

    if level == "grid":
        grid = hotspot_service.compute_grid_risk()
        return {"grid": grid}

    ward_risk = hotspot_service.compute_ward_risk()
    return {"wards": ward_risk}


# -----------------------------
# Rainfall Simulation
# -----------------------------
@app.post("/simulate-rainfall")
def simulate_rainfall(req: SimulateRainfallRequest):

    percent = req.percent_increase

    # modify rainfall
    df = rainfall_df.copy()
    df["rainfall_mm"] = df["rainfall_mm"] * (1 + percent / 100)

    rainfall_factor = 1 + percent / 100

    sim_hotspot = HotspotService(
        df,
        elevation_df,
        drainage_df,
        wards_df,
        risk_service
    )

    ward_risk = sim_hotspot.compute_ward_risk()

    # amplify risk based on rainfall increase
    for w in ward_risk:

        w["score"] = min(1.0, w["score"] * rainfall_factor)

        if w["score"] < 0.33:
            w["category"] = "low"
        elif w["score"] < 0.66:
            w["category"] = "medium"
        else:
            w["category"] = "high"

    return {"wards": ward_risk}


# -----------------------------
# Recommendations
# -----------------------------
@app.get("/recommendations")
def get_recommendations():

    ward_risk = hotspot_service.compute_ward_risk()

    recs = recommendation_service.suggest(ward_risk)

    return {"recommendations": recs}