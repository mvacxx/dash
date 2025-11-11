from __future__ import annotations

from datetime import date
from typing import Dict

import requests


class GoogleAdSenseClient:
    """Lightweight client for pulling earnings reports from the AdSense Management API."""

    def __init__(
        self,
        account_id: str,
        access_token: str,
    ) -> None:
        self.account_id = account_id
        self.access_token = access_token
        self.base_url = "https://adsense.googleapis.com/v2"

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def fetch_daily_earnings(self, day: date) -> float:
        payload = {
            "dateRange": {
                "startDate": day.isoformat(),
                "endDate": day.isoformat(),
            },
            "metrics": ["ESTIMATED_EARNINGS"],
            "timeZone": "UTC",
        }

        response = requests.post(
            f"{self.base_url}/{self.account_id}/reports:generate",
            headers=self._headers(),
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        rows = data.get("rows", [])
        if not rows:
            return 0.0
        first_row = rows[0]
        cells = first_row.get("cells", [])
        if not cells:
            return 0.0
        return float(cells[0].get("value", 0.0))
