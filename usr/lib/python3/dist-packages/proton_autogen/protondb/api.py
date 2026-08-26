# proton_autogen/protondb/api.py

import logging
import requests
from datetime import datetime

logger = logging.getLogger("proton-autogen.protondb")

class ProtonDBAPI:
    BASE_URL = "https://www.protondb.com/api/v1/reports/summaries"

    @staticmethod
    def get_app_info(app_id: str) -> dict:
        try:
            resp = requests.get(f"{ProtonDBAPI.BASE_URL}/{app_id}.json", timeout=5)
            resp.raise_for_status()
            data = resp.json()

            return {
                "app_id": app_id,
                "tier": data.get("tier", "pending"),
                "confidence": data.get("confidence", "unknown"),  # str, pas int
                "total_votes": data.get("total", 0),
                "score": data.get("score"),  # 0-1, bonus
                "notes": None,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.warning("ProtonDB API error for %s: %s", app_id, e)
            return {"app_id": app_id, "tier": "pending", "confidence": "unknown", "total_votes": 0}
