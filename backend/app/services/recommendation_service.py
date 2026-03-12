from typing import List, Dict
import pandas as pd
from .risk_service import RiskService
from .readiness_service import ReadinessService

class RecommendationService:
    def __init__(self, risk_service: RiskService, readiness_service: ReadinessService, wards_df: pd.DataFrame):
        self.risk_service = risk_service
        self.readiness_service = readiness_service
        self.wards_df = wards_df

    def suggest(self, ward_risk: List[Dict]) -> List[Dict]:
        out = []
        readiness = self.readiness_service.compute_readiness_by_ward()
        read_map = {r["ward_id"]: r["readiness_score"] for r in readiness}
        for r in ward_risk:
            actions = []
            if r["category"] == "high":
                actions = ["deploy pump trucks", "clear drainage systems", "send flood alerts", "prepare emergency response teams"]
            elif r["category"] == "medium":
                actions = ["clear drainage systems", "send flood alerts"]
            else:
                actions = ["monitor conditions"]
            out.append({
                "ward_id": r["ward_id"],
                "ward_name": r["ward_name"],
                "risk_category": r["category"],
                "readiness_score": read_map.get(r["ward_id"], 0),
                "actions": actions
            })
        return out
