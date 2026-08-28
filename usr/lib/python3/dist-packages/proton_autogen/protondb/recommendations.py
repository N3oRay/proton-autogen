# proton_autogen/protondb/recommendations.py

from proton_autogen.i18n import tr

# Chaque tier pointe vers 2 ou 3 clés i18n : un résumé + 1-2 conseils.
# Les valeurs elles-mêmes (dans les fichiers de locale) portent déjà
# la flèche "→" sur les lignes de conseil, comme avant. L'emoji du
# tier n'est pas répété ici : il est déjà affiché juste au-dessus par
# dashboard_dialogs.py::_build_protondb_text() (info.emoji + tier).
_TIER_RECOMMENDATION_KEYS = {
    "borked": ["protondb_tier_borked_summary", "protondb_tier_borked_tip1"],
    "bronze": ["protondb_tier_bronze_summary", "protondb_tier_bronze_tip1", "protondb_tier_bronze_tip2"],
    "silver": ["protondb_tier_silver_summary", "protondb_tier_silver_tip1", "protondb_tier_silver_tip2"],
    "gold": ["protondb_tier_gold_summary", "protondb_tier_gold_tip1", "protondb_tier_gold_tip2"],
    "platinum": ["protondb_tier_platinum_summary", "protondb_tier_platinum_tip1"],
    "native": ["protondb_tier_native_summary", "protondb_tier_native_tip1"],
    "pending": ["protondb_tier_pending_summary", "protondb_tier_pending_tip1"],
}


def get_tier_recommendations(tier: str) -> list[str]:
    """Retourne les lignes de recommandation traduites pour un tier
    ProtonDB donné. Retombe sur 'pending' si le tier est inconnu
    (ex. valeur historique absente du schéma actuel)."""
    keys = _TIER_RECOMMENDATION_KEYS.get(tier, _TIER_RECOMMENDATION_KEYS["pending"])
    return [tr(k) for k in keys]
