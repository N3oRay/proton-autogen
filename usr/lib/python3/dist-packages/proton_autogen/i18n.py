# i18n.py
import os
import json
import locale
import sys
from typing import Optional

# ------------------------------------------------------------------------------------
# LOCALES : chargement paresseux
#
# Chaque langue vit dans son propre fichier locales/<code>.json et n'est
# chargée en mémoire que lors de sa première utilisation (set_language(),
# tr(), ou détection). "en" est toujours chargée en premier car elle sert
# de langue de repli (fallback) pour les clés manquantes.
# ------------------------------------------------------------------------------------

_LOCALES_DIR = os.path.join(os.path.dirname(__file__), "locales")

# Cache des langues déjà chargées : {code: {key: text}}
_LANG_CACHE: dict[str, dict] = {}

# Codes de langues disponibles, déduits des fichiers présents sur disque.
# Ne charge AUCUN contenu — juste les noms de fichiers — donc reste très
# léger même appelé au démarrage.
def _discover_available_langs() -> set[str]:
    try:
        return {
            fname[:-5]  # retire ".json"
            for fname in os.listdir(_LOCALES_DIR)
            if fname.endswith(".json")
        }
    except OSError:
        # Dossier locales/ absent (installation cassée) : au moins "en" doit exister
        return {"en"}


AVAILABLE_LANGS = _discover_available_langs()


def _load_lang_file(code: str) -> dict:
    """Charge le fichier JSON d'une langue. Lève une exception si absent/invalide,
    laissant l'appelant décider du repli."""
    path = os.path.join(_LOCALES_DIR, f"{code}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_lang_table(code: str) -> dict:
    """Retourne la table de traduction d'une langue, en la chargeant et la
    mettant en cache au besoin. Replie sur 'en' si le fichier est manquant
    ou corrompu."""
    if code in _LANG_CACHE:
        return _LANG_CACHE[code]

    try:
        table = _load_lang_file(code)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[i18n] WARNING: échec du chargement de '{code}' ({e}), repli sur 'en'")
        if code == "en":
            # Cas critique : même "en" est illisible, on ne peut rien faire de plus
            table = {}
        else:
            return _get_lang_table("en")

    _LANG_CACHE[code] = table
    return table


def _check_translation_completeness(lang_codes: Optional[list] = None) -> bool:
    """Vérifie que chaque groupe de traductions possède les mêmes clés
    que sa langue de référence 'en'.

    Les fichiers peuvent être organisés par domaine, par exemple :
        desc_en.json / desc_fr.json / desc_de.json
        stats_en.json / stats_fr.json / stats_de.json

    Retourne True si toutes les traductions sont complètes, sinon False.
    """

    valid = True

    print("[i18n] Checking translation completeness...")

    # Regroupe les fichiers par préfixe :
    # desc_en -> desc
    # stats_en -> stats
    # en -> ""
    groups: dict[str, set[str]] = {}

    for code in AVAILABLE_LANGS:
        if "_" in code:
            prefix, lang = code.rsplit("_", 1)
        else:
            prefix, lang = "", code

        groups.setdefault(prefix, set()).add(lang)

    # Si une liste de langues est explicitement fournie,
    # on filtre les langues demandées.
    requested_langs = set(lang_codes) if lang_codes is not None else None

    for prefix, langs in sorted(groups.items()):
        reference_code = f"{prefix}_en" if prefix else "en"

        if "en" not in langs:
            print(
                f"[i18n] WARNING: groupe '{prefix or 'default'}' "
                f"— langue de référence '{reference_code}' absente"
            )
            valid = False
            continue

        reference_keys = set(_get_lang_table(reference_code).keys())

        for lang in sorted(langs):
            if lang == "en":
                continue

            code = f"{prefix}_{lang}" if prefix else lang

            if requested_langs is not None and lang not in requested_langs:
                continue

            table = _get_lang_table(code)
            keys = set(table.keys())

            missing = reference_keys - keys
            extra = keys - reference_keys

            if missing:
                valid = False
                print(
                    f"[i18n] WARNING: langue '{code}' — "
                    f"clés manquantes: {sorted(missing)}"
                )

            if extra:
                valid = False
                print(
                    f"[i18n] WARNING: langue '{code}' — "
                    f"clés en trop: {sorted(extra)}"
                )

    if valid:
        print("[i18n] OK: toutes les traductions sont complètes.")
    else:
        print("[i18n] ERROR: des problèmes de traduction ont été détectés.")

    return valid

def check_translations_cli() -> int:
    """Exécute la validation des traductions depuis la CLI.

    Retourne 0 si tout est valide, 1 en cas d'erreur.
    """
    return 0 if _check_translation_completeness() else 1


# ------------------------------------------------------------------------------------
# DÉTECTION / SÉLECTION DE LANGUE
# ------------------------------------------------------------------------------------

def detect_help_env_lang() -> str:
    """
    Détecte la langue pour --help-env :
    priorité = CLI > env LANGUAGE/LANG > défaut en
    """
    for arg in sys.argv:
        if arg.startswith("--") and arg[2:] in AVAILABLE_LANGS:
            return arg[2:]

    lang_env = (os.environ.get("LANGUAGE") or os.environ.get("LANG") or "").lower()
    for code in AVAILABLE_LANGS:
        if lang_env.startswith(code):
            return code

    return "en"


def _get_system_locale() -> Optional[str]:
    """Récupère la locale système via les variables d'environnement,
    puis via le module locale en dernier recours."""

    # LANGUAGE peut être une liste "fr_FR:en_US:en" -> on prend le 1er élément
    raw = (
        os.environ.get("LANGUAGE")
        or os.environ.get("LC_ALL")
        or os.environ.get("LC_MESSAGES")
        or os.environ.get("LANG")
    )

    if raw:
        return raw.split(":")[0]

    # Fallback : API moderne, remplace getdefaultlocale() (supprimée en 3.13)
    try:
        loc = locale.getlocale()
        if loc and loc[0]:
            return loc[0]
    except Exception:
        pass

    return None


def detect_language() -> str:
    """
    Détecte la langue du système.
    Retourne une langue supportée (fallback "en").
    """
    system_lang = _get_system_locale()

    if not system_lang:
        return "en"

    # Exemple:
    # fr_FR.UTF-8 -> fr
    # zh_CN.UTF-8 -> zh
    # en_US.UTF-8 -> en
    normalized = (
        system_lang
        .lower()
        .replace("-", "_")
        .split(".")[0]
    )

    lang = normalized.split("_")[0]

    return lang if lang in AVAILABLE_LANGS else "en"


CURRENT_LANG = "en"


def set_language(lang: Optional[str]) -> None:
    global CURRENT_LANG

    if not lang or not isinstance(lang, str):
        CURRENT_LANG = detect_language()
        return

    lang = lang.lower().replace("-", "_").split("_")[0]
    CURRENT_LANG = lang if lang in AVAILABLE_LANGS else "en"


def detect_cli_language() -> Optional[str]:
    """Recherche une langue forcée via --<lang>."""
    for arg in sys.argv:
        if arg.startswith("--"):
            code = arg[2:].lower()

            if code in AVAILABLE_LANGS:
                return code

    return None

def init_language(forced_lang: Optional[str] = None) -> None:
    """Initialise la langue de l'application."""

    if forced_lang:
        set_language(forced_lang)
        return

    cli_lang = detect_cli_language()

    if cli_lang:
        set_language(cli_lang)
        return

    set_language(detect_language())

def init_language_ori() -> None:
    """Initialise automatiquement la langue depuis le système."""
    set_language(detect_language())


def get_language() -> str:
    return CURRENT_LANG


def tr(key: str, **kwargs) -> str:
    """Traduit une clé, avec repli sur l'anglais si absente."""
    lang_table = _get_lang_table(CURRENT_LANG)
    text = lang_table.get(key)

    if text is None:
        text = _get_lang_table("en").get(key, key)

    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            # Évite un crash si un placeholder attendu manque dans kwargs
            return text

    return text
