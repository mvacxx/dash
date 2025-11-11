from __future__ import annotations

from datetime import date
from typing import Dict, Optional

import json
import requests


class FacebookAdsClient:
    """Minimal client for retrieving daily spend from the Facebook Marketing API."""

    def __init__(
        self,
        access_token: str,
        account_id: str,
        api_version: str = "v18.0",
        business_id: Optional[str] = None,
    ) -> None:
        self.access_token = access_token
        self.account_id = account_id
        self.api_version = api_version
        self.business_id = business_id
        self.base_url = f"https://graph.facebook.com/{api_version}"

    def _request(self, path: str, params: Dict[str, str]) -> Dict:
        response = requests.get(
            f"{self.base_url}/{path}",
            params={**params, "access_token": self.access_token},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        if "error" in payload:
            raise RuntimeError(payload["error"])  # type: ignore[arg-type]
        return payload

    def fetch_daily_metrics(self, day: date) -> Dict[str, float]:
        """Return spend and revenue approximation for a specific day."""

        params: Dict[str, str] = {
            "time_range": json.dumps({"since": day.isoformat(), "until": day.isoformat()}),
            "time_increment": "1",
            "fields": "spend,actions",  # include purchase actions for revenue estimation
        }
        if self.business_id:
            params["business_id"] = self.business_id

        payload = self._request(f"act_{self.account_id}/insights", params)
        data = payload.get("data", [])
        if not data:
            return {"spend": 0.0, "revenue": 0.0}

        entry = data[0]
        spend = float(entry.get("spend", 0.0))
        revenue = 0.0
        for action in entry.get("actions", []) or []:
            if action.get("action_type") in {"offsite_conversion", "offsite_conversion.purchase"}:
                revenue += float(action.get("value", 0.0))
        return {"spend": spend, "revenue": revenue}
