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


def _check_translation_completeness(lang_codes: Optional[list] = None) -> None:
    """Vérifie que toutes les langues définissent les mêmes clés que 'en'.

    Charge toutes les langues demandées en mémoire (donc plus coûteux que le
    fonctionnement normal) — à utiliser en dev/CI, pas au démarrage de l'app.
    """
    reference_keys = set(_get_lang_table("en").keys())
    codes = lang_codes if lang_codes is not None else sorted(AVAILABLE_LANGS)

    for lang_code in codes:
        if lang_code == "en":
            continue
        table = _get_lang_table(lang_code)
        missing = reference_keys - set(table.keys())
        extra = set(table.keys()) - reference_keys
        if missing:
            print(f"[i18n] WARNING: langue '{lang_code}' — clés manquantes: {sorted(missing)}")
        if extra:
            print(f"[i18n] WARNING: langue '{lang_code}' — clés en trop: {sorted(extra)}")


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
