
#!/usr/bin/env python3

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = "N3oRay/proton-autogen"
TOKEN = os.environ["GH_TOKEN"]

DATA_DIR = Path("traffic")
STATS_FILE = DATA_DIR / "clones.json"
BADGE_FILE = DATA_DIR / "clones-badge.json"


def fetch_clone_stats():
    url = f"https://api.github.com/repos/{REPO}/traffic/clones"

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())


def load_stats():
    if STATS_FILE.exists():
        with STATS_FILE.open() as file:
            return json.load(file)

    return {
        "repository": REPO,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "daily": {},
    }


def main():
    DATA_DIR.mkdir(exist_ok=True)

    stats = load_stats()
    response = fetch_clone_stats()

    # Merge par date : une journée n'est jamais additionnée deux fois.
    for entry in response.get("clones", []):
        date = datetime.fromtimestamp(
            entry["timestamp"], timezone.utc
        ).strftime("%Y-%m-%d")

        stats["daily"][date] = {
            "clones": entry["count"],
            "uniques": entry["uniques"],
        }

    total_clones = sum(
        day["clones"] for day in stats["daily"].values()
    )

    total_daily_uniques = sum(
        day["uniques"] for day in stats["daily"].values()
    )

    stats["total_clones"] = total_clones
    stats["total_daily_uniques"] = total_daily_uniques
    stats["last_updated"] = datetime.now(
        timezone.utc
    ).isoformat()

    with STATS_FILE.open("w") as file:
        json.dump(stats, file, indent=2)

    badge = {
        "schemaVersion": 1,
        "label": "lifetime clones",
        "message": f"{total_clones:,}".replace(",", " "),
        "color": "blue",
    }

    with BADGE_FILE.open("w") as file:
        json.dump(badge, file, indent=2)

    print(f"Total clones: {total_clones}")
    print(f"Daily unique cloners summed: {total_daily_uniques}")


if __name__ == "__main__":
    main()

