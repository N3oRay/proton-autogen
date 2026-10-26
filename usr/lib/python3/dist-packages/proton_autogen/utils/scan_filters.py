#!/usr/bin/env python3
# scan_filters.py
"""
Dossiers ignorés par la recherche automatique d'exécutables — SANS GTK.

La recherche (backend.find_windows_programs_ux_search) parcourt ~/Bureau,
~/Downloads, ~/Jeux et ~/Téléchargements. Pour ne pas descendre dans des
caches, des dépôts de code, des dossiers Steam internes, etc., elle ignore
les dossiers dont le NOM figure dans l'ensemble calculé ici.

Deux règles s'appliquent toujours, en plus de cet ensemble (voir backend) :
  - tout dossier caché (nom commençant par « . ») est ignoré ;
  - la comparaison est exacte, sensible à la casse (« bin » ≠ « Bin »).
C'est pourquoi aucun nom commençant par « . » n'apparaît dans les listes ci-dessous.

Personnaliser sans toucher au code
----------------------------------
Créez ~/.config/proton-autogen/scan-excludes.txt, un nom de dossier par ligne :

    # Les lignes vides et celles qui commencent par # sont ignorées.
    MesFilms            # ajoute « MesFilms » aux dossiers ignorés
    Backups/            # le « / » final est toléré
    -bin                # « - » : cesse d'ignorer « bin » (ignoré par défaut)
    -Resource

Les lignes sont appliquées dans l'ordre (la dernière gagne si un nom est à la
fois ajouté et retiré). Un fichier absent, illisible ou mal encodé ne casse
jamais la recherche : les valeurs par défaut s'appliquent.

La recherche est mise en cache pour la durée du processus : un changement du
fichier est pris en compte au prochain démarrage de proton-autogen.
"""

import os
import re
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from proton_autogen.utils.logger import StructuredLogger

logger = StructuredLogger("proton-autogen.scan_filters")


# Noms de dossiers ignorés par défaut, par thème. Chaque nom n'apparaît qu'UNE
# fois (un test le garantit). Reprise à l'identique de l'ancien ensemble
# `excluded_dirs` de backend.py, sans ses doublons ni ses noms de dossiers
# cachés (déjà couverts par la règle « dossier caché »).
EXCLUDED_DIR_CATEGORIES = {
    "cache et temporaires": (
        "cache", "tmp", "temp", "appcache", "configs",
    ),
    "développement": (
        "__pycache__", "node_modules", "JAVA", "www", "pipeline",
        "eclipse-workspace", "eclipse-installer",
    ),
    "dossiers personnels": (
        "Musique", "Modèles", "Images", "Vidéos", "customFiles", "docs", "bsa",
        "pdf", "Serene-Conky", "os", "steal",
    ),
    "jeux (hors bibliothèque)": (
        "dgVoodoo2", "deb-installer", "depotcache", "friends", "linux64", "linux32",
    ),
    "interne à Steam": (
        "steamui", "steamrt64", "steamrt32", "userdata", "ubuntu12_32",
        "ubuntu12_64", "resource", "package", "root", "sdk64", "bin64", "bin32",
        "bin", "clientui", "controller_base",
    ),
    "Proton": (
        "compatibilitytools.d",
    ),
    "sauvegardes": (
        "backup", "backups", "old", "recovery", "stockages", "zip", "tar",
    ),
    "bruit divers": (
        "drivers", "bios", "logs", "log", "mail", "personnel", "virus", "malware",
    ),
}

DEFAULT_EXCLUDED_DIRS = frozenset(
    name for names in EXCLUDED_DIR_CATEGORIES.values() for name in names
)

USER_EXCLUDES_FILE = Path.home() / ".config" / "proton-autogen" / "scan-excludes.txt"

_INLINE_COMMENT_RE = re.compile(r"\s+#.*$")

Rule = Tuple[str, str]   # ("add" | "remove", nom de dossier)


def parse_user_rules(text: str) -> List[Rule]:
    """Convertit le contenu du fichier utilisateur en règles ordonnées.

    Ignore sans erreur : lignes vides, commentaires, nom vide après « - », et
    les entrées contenant un « / » intérieur (un nom de dossier n'en contient
    jamais : elles ne pourraient correspondre à rien).
    """
    rules: List[Rule] = []

    for raw in text.splitlines():
        line = _INLINE_COMMENT_RE.sub("", raw).strip()

        if not line or line.startswith("#"):
            continue

        action = "add"
        if line.startswith("-"):
            action = "remove"
            line = line[1:].strip()

        name = line.rstrip("/").strip()

        if not name or "/" in name:
            continue

        rules.append((action, name))

    return rules


def apply_rules(defaults: Iterable[str], rules: Iterable[Rule]) -> frozenset:
    """Applique les règles dans l'ordre sur une copie de `defaults`."""
    excluded = set(defaults)

    for action, name in rules:
        if action == "add":
            excluded.add(name)
        else:
            excluded.discard(name)

    return frozenset(excluded)


def load_user_rules(path: Optional[os.PathLike] = None) -> List[Rule]:
    """Règles du fichier utilisateur ; liste vide si absent ou illisible."""
    path = Path(USER_EXCLUDES_FILE if path is None else path)

    try:
        if not path.is_file():
            return []
        return parse_user_rules(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        logger.warning(f"scan-excludes ignoré ({path}) : {exc}")
        return []


def get_excluded_dirs(path: Optional[os.PathLike] = None) -> frozenset:
    """Ensemble effectif : valeurs par défaut + personnalisation utilisateur."""
    rules = load_user_rules(path)

    if not rules:
        return DEFAULT_EXCLUDED_DIRS

    effective = apply_rules(DEFAULT_EXCLUDED_DIRS, rules)
    logger.debug(
        f"scan-excludes : {len(effective - DEFAULT_EXCLUDED_DIRS)} ajout(s), "
        f"{len(DEFAULT_EXCLUDED_DIRS - effective)} retrait(s)"
    )
    return effective
