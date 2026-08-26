# proton_autogen/protondb/model.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class ProtonDBInfo:
    app_id: str
    tier: str  # native|platinum|gold|silver|bronze|borked|pending
    confidence: str  # "low" | "moderate" | "strong" | "unknown"
    total_votes: int
    score: Optional[float] = None
    notes: Optional[str] = None

    @property
    def emoji(self) -> str:
        tiers = {
            "native": "✅", "platinum": "🟪", "gold": "🟨",
            "silver": "⚪", "bronze": "🟫", "borked": "❌", "pending": "❓",
        }
        return tiers.get(self.tier, "❓")

    @property
    def color_css(self) -> str:
        colors = {
            "native": "#2ecc71", "platinum": "#9b59b6", "gold": "#f39c12",
            "silver": "#95a5a6", "bronze": "#a0522d", "borked": "#e74c3c", "pending": "#7f8c8d",
        }
        return colors.get(self.tier, "#7f8c8d")
