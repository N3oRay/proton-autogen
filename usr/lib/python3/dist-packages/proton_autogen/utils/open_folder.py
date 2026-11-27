#!/usr/bin/env python3

# open_folder.py
"""
« Ouvrir Dossier » : ouvre dans le gestionnaire de fichiers le répertoire qui
contient l'exécutable d'un jeu.

Logique pure (sans GTK) :
  - game_folder(game)        -> Path du dossier de l'exécutable (validé)
  - open_folder(path)        -> ouvre un dossier, renvoie la commande utilisée
  - open_game_folder(game)   -> les deux à la suite

Ouverture : `xdg-open`, puis `gio open` en secours. Dans un Flatpak, xdg-open
passe par le portail (le gestionnaire de fichiers de l'hôte s'ouvre). Les
commandes sont lancées détachées et sans attendre la fin du gestionnaire : on
attend seulement un court instant pour détecter un échec immédiat (code de
retour non nul) et passer à la commande suivante.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Mapping, Optional, Sequence, Union

# Délai pendant lequel on surveille un échec immédiat de la commande.
# Un gestionnaire de fichiers qui reste lancé dépasse ce délai : c'est un succès.
LAUNCH_GRACE_SECONDS = 1.5

# Commandes essayées dans l'ordre (la première trouvée dans le PATH et qui
# réussit l'emporte).
OPENERS: Sequence[Sequence[str]] = (
    ("xdg-open",),
    ("gio", "open"),
)


class OpenFolderError(Exception):
    """Échec attendu : message lisible, destiné à être affiché à l'utilisateur."""


def game_folder(game: Union[Mapping, str, os.PathLike]) -> Path:
    """Dossier contenant l'exécutable du jeu.

    `game` est la configuration d'un jeu (clé « path ») ou directement un chemin.
    Si le chemin désigne déjà un dossier existant, il est renvoyé tel quel.
    """
    raw = game.get("path") if isinstance(game, Mapping) else game
    if not raw:
        raise OpenFolderError("no executable path configured for this game")

    path = Path(os.path.expandvars(os.fspath(raw))).expanduser()

    folder = path if path.is_dir() else path.parent
    if not folder.is_dir():
        raise OpenFolderError(f"folder not found: {folder}")
    return folder


def open_folder(folder: Union[str, os.PathLike],
                openers: Optional[Sequence[Sequence[str]]] = None) -> str:
    """Ouvre `folder` dans le gestionnaire de fichiers.

    Renvoie la commande qui a fonctionné (ex. « xdg-open »).
    Lève OpenFolderError si le dossier est introuvable ou si aucune commande
    d'ouverture n'est disponible / n'a réussi.
    """
    folder = Path(folder)
    if not folder.is_dir():
        raise OpenFolderError(f"folder not found: {folder}")

    tried = []
    for command in (openers if openers is not None else OPENERS):
        executable = shutil.which(command[0])
        if executable is None:
            continue

        argv = [executable, *command[1:], str(folder)]
        try:
            process = subprocess.Popen(
                argv,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError as exc:
            tried.append(f"{command[0]}: {exc}")
            continue

        try:
            code = process.wait(timeout=LAUNCH_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            return " ".join(command)  # le gestionnaire tourne encore : succès

        if code == 0:
            return " ".join(command)
        tried.append(f"{command[0]}: exit code {code}")

    if tried:
        raise OpenFolderError("could not open the folder (" + "; ".join(tried) + ")")
    raise OpenFolderError("no way to open a folder found (install xdg-utils)")


def open_game_folder(game: Union[Mapping, str, os.PathLike],
                     openers: Optional[Sequence[Sequence[str]]] = None) -> Path:
    """Ouvre le dossier de l'exécutable du jeu et le renvoie."""
    folder = game_folder(game)
    open_folder(folder, openers=openers)
    return folder
