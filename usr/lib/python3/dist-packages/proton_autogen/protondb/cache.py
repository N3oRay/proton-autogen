# proton_autogen/protondb/cache.py

import json
from pathlib import Path
from datetime import datetime

class ProtonDBCache:
    CACHE_DIR = Path.home() / ".cache" / "proton-autogen" / "protondb"

    @staticmethod
    def get_cached(app_id: str) -> dict:
        """Retourne data en cache si < 24h"""
        cache_file = ProtonDBCache.CACHE_DIR / f"{app_id}.json"

        if cache_file.exists():
            with open(cache_file, "r") as f:
                data = json.load(f)
                created = datetime.fromisoformat(data["timestamp"])
                if (datetime.now() - created).total_seconds() < 86400:
                    return data
        return None

    @staticmethod
    def save(app_id: str, data: dict):
        """Sauvegarde en cache"""
        ProtonDBCache.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = ProtonDBCache.CACHE_DIR / f"{app_id}.json"
        with open(cache_file, "w") as f:
            json.dump(data, f)
