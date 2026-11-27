#!/usr/bin/env python3

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = "N3oRay/proton-autogen"
TOKEN = os.environ.get("GH_TOKEN")

DATA_DIR = Path("traffic")
STATS_FILE = DATA_DIR / "clones.json"
BADGE_FILE = DATA_DIR / "clones-badge.json"


def parse_day(timestamp):
    """Convertit un timestamp GitHub en date UTC."""
    if isinstance(timestamp, (int, float)):
        return datetime.fromtimestamp(timestamp, timezone.utc).date().isoformat()

    # L'API renvoie normalement une date ISO, par exemple :
    # 2026-11-27T00:00:00Z
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return parsed.astimezone(timezone.utc).date().isoformat()


def fetch_clone_stats():
    if not TOKEN:
        raise RuntimeError(
            "Le secret TRAFFIC_TOKEN est absent ou vide (variable GH_TOKEN)."
        )

    url = f"https://api.github.com/repos/{REPO}/traffic/clones"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Échec de l'API GitHub ({error.code}): {details}"
        ) from error


def load_stats():
    if STATS_FILE.exists():
        with STATS_FILE.open(encoding="utf-8") as file:
            return json.load(file)

    return {
        "repository": REPO,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "daily": {},
    }


def main():
    DATA_DIR.mkdir(exist_ok=True)

    stats = load_stats()
    stats.setdefault("daily", {})

    response = fetch_clone_stats()

    # L'API renvoie une fenêtre mobile d'environ 14 jours.
    # Les dates déjà enregistrées sont remplacées, pas additionnées à nouveau.
    for entry in response.get("clones", []):
        day = parse_day(entry["timestamp"])
        stats["daily"][day] = {
            "clones": int(entry["count"]),
            "uniques": int(entry["uniques"]),
        }

    total_clones = sum(
        day["clones"] for day in stats["daily"].values()
    )

    stats["total_clones"] = total_clones
    stats["last_updated"] = datetime.now(timezone.utc).isoformat()

    with STATS_FILE.open("w", encoding="utf-8") as file:
        json.dump(stats, file, indent=2)
        file.write("\n")

    badge = {
        "schemaVersion": 1,
        "label": "clones cumulés suivis",
        "message": f"{total_clones:,}".replace(",", " "),
        "color": "blue",
    }

    with BADGE_FILE.open("w", encoding="utf-8") as file:
        json.dump(badge, file, indent=2)
        file.write("\n")

    print(f"Total de clones enregistrés : {total_clones}")


if __name__ == "__main__":
    main()