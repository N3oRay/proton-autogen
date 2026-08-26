# proton_autogen/protondb/recommendations.py

TIER_RECOMMENDATIONS = {
    "borked": [
        "❌ Ce jeu ne fonctionne pas",
        "→ Essayez un titre alternatif ou attendez une amélioration de compatibilité"
    ],
    "bronze": [
        "🟫 Crashes, significant bugs, or doesn't run",
        "→ Manual tweaking may be required",
        "→ Check ProtonDB reports for workarounds"
    ],
    "silver": [
        "⚪ Runs but with minor issues",
        "→ May need tweaks (DXVK, ESYNC, etc.)",
        "→ See ProtonDB notes for profile suggestions"
    ],
    "gold": [
        "🟨 Runs with minor issues or needs configuration",
        "→ Recommended profile already applied",
        "→ Check ProtonDB for specific tweaks"
    ],
    "platinum": [
        "🟪 Runs perfectly with only minor issues",
        "→ Should work out of the box"
    ],
    "native": [
        "✅ Native Linux version detected",
        "→ May not need Proton at all"
    ],
    "pending": [
        "❓ Pas encore assez de rapports communautaires",
        "→ Essayez le jeu et publiez votre propre retour sur ProtonDB"
    ],
}
